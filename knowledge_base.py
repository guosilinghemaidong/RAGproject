"""
知识库
"""
import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime


def check_md5(md5_str: str):
    """检查md5字符串是否被处理"""
    if not os.path.exists(config.md5_path):
        #能进入表示文件不存在
        open(config.md5_path, "w" , encoding='utf-8').close()
        return False
    else:
        for line in open(config.md5_path, "r" , encoding='utf-8').readlines():
            line = line.strip()     #处理字符串前后空格与回车
            if line == md5_str:
                return True          #已处理
        return False

def save_md5(md5_str: str):
    """传入的md5文件保存"""
    with open(config.md5_path, "a" , encoding='utf-8') as f:
        f.write(md5_str + "\n")


def get_string_md5(input_str: str, encoding='utf-8'):
    """传入的字符串转换成md5"""
    #将字符串转换为bytes数组
    str_bytes = input_str.encode(encoding=encoding)
    #创建md5对象
    md5_obj = hashlib.md5()           #得到对象
    md5_obj.update(str_bytes)         #更新md5对象
    md5_hex= md5_obj.hexdigest()      #得到md5值
    return md5_hex
    pass

class KnowledgeBaseService(object):
    def __init__(self):
        os.makedirs(config.persist_directory, exist_ok=True)     #文件夹不存在创建,存在则跳过
        self.chroma = Chroma(
            collection_name=config.collection_name,       #数据库表名
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory,   #数据库本地文件夹
        )       #向量存储实例Chroma向量库对象

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,            #分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap,      #分割后文本段之间的重叠部分
            separators=config.separator,              #划分自然段落的分割符
            length_function=len,                     #计算长度的函数
        )        #文本分割器

    def upload_by_str(self,data,filename):
        """传入的字符串,进行向量化,存到向量数据库里"""
        #先得到md5值
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "[跳过]内容已存在"
        if len(data) > config.max_split_char_number:
            knowlege_chunks:list[str] = self.spliter.split_text(data)
        else:
            knowlege_chunks = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "用户"
        }

        self.chroma.add_texts(                  #加载内容到向量库
            texts=knowlege_chunks,
            metadatas=[metadata for _ in knowlege_chunks]
        )

        save_md5(md5_hex)
        return "[成功]内容已保存"




if __name__ == '__main__':
    service = KnowledgeBaseService()
    r = service.upload_by_str("周杰伦","testfile")
    print(r)