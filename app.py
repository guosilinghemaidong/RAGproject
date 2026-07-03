import streamlit as st
import time
from rag import RagService
from knowledge_base import KnowledgeBaseService

# ========== 页面配置 ==========
st.set_page_config(
    page_title="RAG 智能知识库",
    page_icon="🤖",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    /* 主标题居中 */
    .main h1 { text-align: center; }
    /* 聊天气泡圆角 */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 12px 16px;
    }
    /* 侧边栏按钮悬停效果 */
    .stButton > button {
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ========== 侧边栏 ==========
with st.sidebar:
    st.title("🤖 RAG 智能知识库")
    st.divider()
    # 功能选择
    page = st.radio(
        "选择功能",
        ["💬 智能问答", "📁 知识库管理"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("基于 LangChain + Chroma + 通义千问")

# ========== 智能问答页面 ==========
if page == "💬 智能问答":
    st.header("💬 智能问答")

    # session_id 配置
    session_config = {
        "configurable": {
            "session_id": "user_001"
        }
    }

    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "你好，我是智能客服，有什么可以帮你的？"}]

    # 初始化 RAG 服务
    if "rag" not in st.session_state:
        st.session_state["rag"] = RagService()

    # 清空对话按钮
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "对话已清空，请重新提问。"}]
        st.rerun()

    # 渲染历史对话（带头像）
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # 用户输入
    prompt = st.chat_input("请输入你的问题...")
    if prompt:
        # 显示用户消息（带头像）
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 流式输出 AI 回复（带头像）
        with st.chat_message("assistant", avatar="🤖"):
            res_stream = st.session_state["rag"].chain.stream({"input": prompt}, session_config)
            full_response = st.write_stream(res_stream)

            # 展示参考文档来源
            docs = st.session_state["rag"].vector_service.get_retriever().invoke(prompt)
            if docs:
                with st.expander("📄 参考来源"):
                    for i, doc in enumerate(docs, 1):
                        source = doc.metadata.get("source", "未知来源")
                        st.markdown(f"**来源 {i}**：`{source}`")
                        st.caption(doc.page_content[:100] + "...")

        st.session_state.messages.append({"role": "assistant", "content": full_response})



# ========== 知识库管理页面 ==========
elif page == "📁 知识库管理":
    st.header("📁 知识库管理")

    # 初始化知识库服务
    if "service" not in st.session_state:
        st.session_state["service"] = KnowledgeBaseService()

    st.info("支持上传 `.txt` 文件，系统将自动分块并向量化存入 Chroma 数据库")

    uploader_file = st.file_uploader(
        "请选择要上传的文件",
        type=["txt"],
        accept_multiple_files=False,
    )

    if uploader_file is not None:
        file_name = uploader_file.name
        file_size = uploader_file.size / 1024

        col1, col2 = st.columns(2)
        with col1:
            st.metric("文件名", file_name)
        with col2:
            st.metric("文件大小", f"{file_size:.2f} KB")

        text = uploader_file.getvalue().decode("utf-8")

        with st.spinner("正在上传并向量化..."):
            time.sleep(1)
            result = st.session_state["service"].upload_by_str(text, file_name)

        if "成功" in result:
            st.success(result)
        else:
            st.warning(result)
