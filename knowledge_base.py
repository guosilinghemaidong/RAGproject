"""
知识库
"""
import os
import config_data as config
import hashlib

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
        self.chroma = None         #向量存储实例Chroma向量库对象
        self.spliter = None        #文本分割器

    def upload_by_str(self,data,filename):
        """传入的字符串,进行向量化,存到向量数据库里"""
        pass



if __name__ == '__main__':
    # r1 = get_string_md5("周杰伦")
    # r2 = get_string_md5("周杰伦")
    # r3 = get_string_md5("周杰伦2")
    # print(r1)
    # print(r2)
    # print(r3)
    save_md5("7a8941058aaf4df5147042ce104568da")
    print(check_md5("7a8941058aaf4df5147042ce104568da"))