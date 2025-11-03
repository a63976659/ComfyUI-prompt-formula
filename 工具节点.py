# 工具节点.py

class 字符串输入反转:
    """专门用于字符串输入的反转节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "反转": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "字符串1": ("STRING", {"forceInput": True}),
                "字符串2": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("输出字符串1", "输出字符串2")
    FUNCTION = "切换输入"
    CATEGORY = "📃提示词公式/工具节点"
    
    def IS_CHANGED(self, **kwargs):
        return float("NaN")

    def 切换输入(self, 反转, 字符串1=None, 字符串2=None):
        if 反转:
            return (字符串2, 字符串1)
        else:
            return (字符串1, 字符串2)

class 图像输入反转:
    """专门用于图像输入的反转节点
    
    交换两个图像输入的位置。当反转开启时，图像1和图像2的值会互换输出。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "反转": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "图像1": ("IMAGE", {"forceInput": True}),
                "图像2": ("IMAGE", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("输出图像1", "输出图像2")
    FUNCTION = "切换输入"
    CATEGORY = "📃提示词公式/工具节点"
    
    def IS_CHANGED(self, **kwargs):
        return float("NaN")

    def 切换输入(self, 反转, 图像1=None, 图像2=None):
        if 反转:
            return (图像2, 图像1)
        else:
            return (图像1, 图像2)

class 合并多组提示词:
    """合并多组提示词，支持动态增加输入组
    
    将多个提示词输入合并为一个提示词。支持最多20组输入，可自定义分隔符。
    默认显示6组输入，当连接满时会自动显示更多输入组。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 基础输入配置 - 默认显示6组
        optional_inputs = {
            "分隔符": (["逗号", "句号", "斜杠", "换行"], {"default": "逗号"}),
        }
        
        # 添加6组默认输入
        for i in range(1, 7):
            optional_inputs[f"提示词{i}"] = ("STRING", {"default": "", "forceInput": True})
        
        # 添加额外的14组输入（总共20组）
        for i in range(7, 21):
            optional_inputs[f"提示词{i}"] = ("STRING", {"default": "", "forceInput": True})
        
        return {
            "required": {},
            "optional": optional_inputs
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("合并提示词",)
    FUNCTION = "合并提示词"
    CATEGORY = "📃提示词公式/工具节点"
    
    def 合并提示词(self, 分隔符="逗号", **kwargs):
        # 收集所有非空的提示词
        提示词列表 = []
        
        # 获取所有提示词参数
        for key, value in kwargs.items():
            if key.startswith("提示词") and value and value.strip():
                提示词列表.append(value.strip())
        
        # 根据选择的分隔符确定实际分隔符
        分隔符映射 = {
            "逗号": ", ",
            "句号": "。",
            "斜杠": "/",
            "换行": "\n"
        }
        实际分隔符 = 分隔符映射.get(分隔符, ", ")
        
        # 使用分隔符合并提示词
        合并结果 = 实际分隔符.join(提示词列表)
        return (合并结果,)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 检查是否有任何提示词输入发生变化
        for key, value in kwargs.items():
            if key.startswith("提示词") and value:
                return float("NaN")
        return 0.0