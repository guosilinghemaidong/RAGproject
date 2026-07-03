# RAG 智能知识库问答系统

基于 LangChain + Chroma + 通义千问 构建的 RAG（检索增强生成）智能问答系统，支持知识库上传、向量化检索、多轮对话。

## 🏗️ 项目架构
用户 → Streamlit Web 界面 ↓ RAG Chain（LangChain） ├── 向量检索（Chroma） ├── 历史对话（文件持久化） └── 大模型生成（通义千问 qwen3-max）

## ✨ 功能特性

- 📁 **知识库管理**：支持 `.txt` 文件上传，自动文本分块 + 向量化存储
- 💬 **智能问答**：基于 RAG 的知识问答，流式输出回答
- 🔄 **多轮对话**：支持上下文记忆，历史对话持久化到本地文件
- 📄 **参考来源**：展示回答引用的文档来源，可追溯
- 🎨 **美观界面**：Streamlit 构建，支持头像、流式输出、侧边栏导航

## 🛠️ 技术栈

| 模块 | 技术 |
|------|------|
| Web 框架 | Streamlit |
| RAG 框架 | LangChain |
| 向量数据库 | Chroma |
| 嵌入模型 | DashScope text-embedding-v4 |
| 大语言模型 | 通义千问 qwen3-max |
| 历史存储 | 本地 JSON 文件 |

## 📂 项目结构
├── app.py # Streamlit 统一入口（智能问答 + 知识库管理） ├── rag.py # RAG 链构建（检索 → 拼装 prompt → 大模型） ├── vector_stores.py # Chroma 向量存储服务 ├── knowledge_base.py # 知识库服务（文件上传、分块、向量化） ├── file_history_store.py # 对话历史持久化（基于 JSON 文件） ├── config_data.py # 全局配置 └── chroma_db/ # Chroma 向量数据库本地存储


## 🚀 快速开始

### 1. 安装依赖
bash pip install langchain langchain-core langchain-community langchain-chroma langchain-text-splitters pip install dashscope streamlit
### 2. 配置 API Key

设置环境变量：

### 3. 启动应用
bash streamlit run app.py

## 📝 核心流程

1. 用户上传 `.txt` 文件 → 文本分块 → DashScope 向量化 → 存入 Chroma
2. 用户提问 → DashScope 嵌入查询 → Chroma 相似度检索 → 获取参考文档
3. 参考文档 + 历史对话 + 用户问题 → 拼装 Prompt → 通义千问生成回答
4. 流式输出回答 + 展示参考来源
