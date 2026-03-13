# 提示词预设节点.py
import os
import glob
from server import PromptServer
from aiohttp import web

class 提示词预设:
    """提示词预设 - 从预设文件夹读取txt文件"""
    
    @classmethod
    def INPUT_TYPES(cls):
        # 递归获取预设文件列表
        # 修改路径：使用插件根目录下的"提示词预设"文件夹
        # 获取当前文件所在目录（节点文件夹）
        current_dir = os.path.dirname(__file__)
        # 获取插件根目录（节点文件夹的父目录）
        plugin_root = os.path.dirname(current_dir)
        # 构建预设目录路径（插件根目录下的"提示词预设"文件夹）
        预设目录 = os.path.join(plugin_root, "提示词预设")
        
        预设选项 = ["无"]  # 将"无"放在第一个
        
        # 如果预设目录不存在，创建它
        if not os.path.exists(预设目录):
            os.makedirs(预设目录)
        
        # 临时列表存储其他选项
        其他选项 = []
        
        # 递归扫描所有txt文件
        for 根目录, 目录列表, 文件列表 in os.walk(预设目录):
            for 文件名 in 文件列表:
                if 文件名.lower().endswith('.txt'):
                    # 获取相对于预设目录的路径
                    相对路径 = os.path.relpath(根目录, 预设目录)
                    if 相对路径 == '.':
                        显示名称 = os.path.splitext(文件名)[0]
                    else:
                        显示名称 = f"{相对路径}/{os.path.splitext(文件名)[0]}"
                    
                    其他选项.append(显示名称)
        
        # 对其他选项进行排序
        其他选项.sort()
        
        # 将排序后的其他选项添加到预设选项中
        预设选项.extend(其他选项)
        
        return {
            "required": {
                "预设文件": (预设选项, {"default": "无"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("提示词",)
    FUNCTION = "读取预设"
    CATEGORY = "📕提示词公式"

    def 读取预设(self, 预设文件):
        if 预设文件 == "无":
            return ("",)
        
        # 构建文件路径 - 使用插件根目录下的"提示词预设"文件夹
        # 获取当前文件所在目录（节点文件夹）
        current_dir = os.path.dirname(__file__)
        # 获取插件根目录（节点文件夹的父目录）
        plugin_root = os.path.dirname(current_dir)
        # 构建预设目录路径（插件根目录下的"提示词预设"文件夹）
        预设目录 = os.path.join(plugin_root, "提示词预设")
        
        if '/' in 预设文件:
            文件夹路径, 文件名 = 预设文件.rsplit('/', 1)
            文件路径 = os.path.join(预设目录, 文件夹路径, f"{文件名}.txt")
        else:
            文件路径 = os.path.join(预设目录, f"{预设文件}.txt")
        
        try:
            with open(文件路径, 'r', encoding='utf-8') as 文件:
                预设内容 = 文件.read().strip()
        except Exception as e:
            print(f"读取预设文件失败: {e}")
            预设内容 = ""
        
        return (预设内容,)

@PromptServer.instance.routes.get("/preset_preview/list")
async def 获取预设列表(请求):
    """获取所有预设文件及其内容"""
    # 修改路径：使用插件根目录下的"提示词预设"文件夹
    # 获取当前文件所在目录（节点文件夹）
    current_dir = os.path.dirname(__file__)
    # 获取插件根目录（节点文件夹的父目录）
    plugin_root = os.path.dirname(current_dir)
    # 构建预设目录路径（插件根目录下的"提示词预设"文件夹）
    预设目录 = os.path.join(plugin_root, "提示词预设")
    
    预设数据 = {}
    
    # 如果预设目录不存在，返回空数据
    if not os.path.exists(预设目录):
        return web.json_response(预设数据)
    
    for 根目录, 目录列表, 文件列表 in os.walk(预设目录):
        for 文件名 in 文件列表:
            if 文件名.lower().endswith('.txt'):
                基础文件名 = os.path.splitext(文件名)[0]
                相对路径 = os.path.relpath(根目录, 预设目录)
                if 相对路径 == '.':
                    显示名称 = 基础文件名
                else:
                    显示名称 = f"{相对路径}/{基础文件名}"
                
                # 读取预设内容
                try:
                    with open(os.path.join(根目录, 文件名), 'r', encoding='utf-8') as 文件:
                        完整内容 = 文件.read().strip()
                except Exception as e:
                    print(f"读取预设文件内容失败: {e}")
                    完整内容 = ""
                
                预设数据[显示名称] = {
                    "完整内容": 完整内容,
                    "路径": 显示名称
                }
    
    return web.json_response(预设数据)

# 节点注册
NODE_CLASS_MAPPINGS = {
    "提示词预设": 提示词预设,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "提示词预设": "提示词预设",
}