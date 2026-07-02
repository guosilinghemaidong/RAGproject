from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from vector_stores import VectorStoreService
from langchain_core.documents import Document
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from file_history_store import get_history


def print_prompt(prompt):
    """调试用：打印最终拼装后的 prompt 内容"""
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


class RagService(object):
    def __init__(self):
        # 初始化向量服务，使用 DashScope 嵌入模型
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )

        # 构建 prompt 模板，包含三个变量：
        #   {context}  - 从向量库检索到的参考资料
        #   {history}  - 历史对话消息列表（由 MessagesPlaceholder 占位）
        #   {input}    - 用户当前提问
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的已知参考资料为主,"
                "简洁和专业的回答我的问题.参考资料如下:{context}"),
                ("system", "并且我提供历史对话记录,如下:"),
                MessagesPlaceholder("history"),  # 占位符，运行时会被替换为历史消息列表
                ("user", "请回答用户提问:{input}")
            ]
        )

        self.chat_model = ChatTongyi(model_name=config.chat_model_name)

        self.chain = self.__get_chain()

    def __get_chain(self):
        """
        构建完整的 RAG 执行链
        流程：用户输入 → 检索文档 → 拼装 prompt → 调用大模型 → 解析输出
        外层再包裹 RunnableWithMessageHistory 实现多轮对话历史记录
        """
        retriever = self.vector_service.get_retriever()

        def format_document(docs:list[Document]):
            """将检索到的 Document 列表格式化为纯文本字符串"""
            if not docs:
                return "没有相关参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str

        # ----------------------------------------------------------------
        # 问题修复一：retriever 在链中收不到纯字符串
        # ----------------------------------------------------------------
        # 原因：在 dict 链结构中，retriever 直接接收到的输入不是纯字符串，
        #       导致 DashScopeEmbeddings.embed_query() 报错：
        #       "input.texts should be array"
        # 解决：用 RunnablePassthrough.assign 从输入字典中单独提取 input 字段，
        #       确保传给 retriever 的是纯字符串
        extract_input = RunnablePassthrough.assign(
            query=lambda x: x["input"] if isinstance(x, dict) else x
        )

        # ----------------------------------------------------------------
        # 问题修复二：prompt 模板缺少 history 变量导致 KeyError
        # ----------------------------------------------------------------
        # 原因：RunnableWithMessageHistory 会将 history 注入到输入字典中，
        #       但 dict 链结构只传递显式定义的 key（input、context），
        #       history 被丢弃 → prompt 报 KeyError: 'history'
        #       如果直接用 RunnablePassthrough() 透传 history，
        #       会把整个输入字典传给 history → 报 "should be a list of base messages"
        # 解决：用 lambda 从输入字典中只提取 history 的值（消息列表）
        chain = (
                {
                    "input": RunnablePassthrough(),                                    # 透传用户输入
                    "context": extract_input | (lambda x: x["query"]) | retriever | format_document,  # 检索 → 格式化
                    "history": lambda x: x.get("history", [])                         # 提取历史消息列表
                } | self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
        )

        # 用 RunnableWithMessageHistory 包裹链，实现多轮对话
        #   get_history          - 根据 session_id 获取历史消息存储实例
        #   input_messages_key   - 指定用户输入对应的字典 key
        #   history_messages_key - 指定历史消息对应的字典 key
        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        return conversation_chain

if __name__ == '__main__':
    # session_id 用于区分不同用户的对话历史
    session_config = {
        "configurable":{
            "session_id": "user_001"
        }
    }
    res = RagService().chain.invoke({"input":"我鞋码40码,尺码推荐"}, session_config)
    print(res)
