"""
基于streamlit完成web网页上传
"""
import  streamlit as st


# 网页标题
st.title("知识库更新服务")


# 文件上传
uploader_file = st.file_uploader(
    "请选择要上传的文件",
    type=["txt"],
    accept_multiple_files=False,      #仅接受一个文件上传
)

if uploader_file is not None:
    # 提取文件信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size/1024
    st.subheader(f"文件名: {file_name}")
    st.write(f"文件格式: {file_type}" + " | " + f"文件大小: {file_size:.2f}KB")

    # get_values获取信息 -> bytes -> decode('utf-8')
    text= uploader_file.getvalue().decode('utf-8')
    st.write(text)