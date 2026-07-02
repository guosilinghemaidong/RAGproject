import time
import streamlit as st
from rag import RagService

# 标题
st.title("智能客服")
st.divider()

# session_id 配置，用于区分不同用户的对话历史
session_config = {
    "configurable": {
        "session_id": "user_001"
    }
}

# 初始化对话历史（只初始化一次，Streamlit 每次交互会重新执行整个脚本，
# session_state 用于跨 rerun 保持状态）
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "你好"}]

# 初始化 RAG 服务（避免每次 rerun 重复创建）
if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

# 渲染历史对话记录
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 用户输入框
prompt = st.chat_input()
if prompt:
    # 显示并记录用户消息
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 流式输出 AI 回复
    with st.spinner("AI思考中..."):
        res_stream = st.session_state["rag"].chain.stream({"input": prompt}, session_config)
        # write_stream 会逐字显示，返回值是拼接好的完整文本字符串
        full_response = st.chat_message("assistant").write_stream(res_stream)
        # 用完整文本来保存，而不是保存流对象
        st.session_state.messages.append({"role": "assistant", "content": full_response})
