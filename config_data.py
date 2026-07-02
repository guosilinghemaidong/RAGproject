
md5_path = "./md5.text"


# chroma
collection_name = "rag"
persist_directory = "./chroma_db"

# spliter
chunk_size = 1000
chunk_overlap = 100
separator = ["\n\n", "\n", ".", "!", "?","。","？","！", " ", ""]
max_split_char_number = 1000          # 每个分块的最大字符数
