from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from vector_stores import VectorStoreService
from langchain_core.documents import Document
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.tongyi import ChatTongyi




def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


class RagService(object):
    def __init__(self):
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的已知参考资料为主,"
                "简洁和专业的回答我的问题.参考资料如下:{context}"),
                ("user", "请回答用户提问:{input}")
            ]
        )

        self.chat_model = ChatTongyi(model_name=config.chat_model_name)

        self.chain = self.__get_chain()

    def __get_chain(self):
        #获取最终执行连
        retriever = self.vector_service.get_retriever()

        def format_document(docs:list[Document]):
            if not docs:
                return "没有相关参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str




        chain = (
            {
                "input":RunnablePassthrough(),
                "context":retriever | format_document
            } | self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
        )

        return chain

if __name__ == '__main__':
    res = RagService().chain.invoke("我身高170厘米,尺码推荐")
    print(res)