# 工具节点.py
import os
import random
import folder_paths
import numpy as np
import hashlib
import torch
from PIL import Image, ImageSequence, ImageOps

# 定义任意类型，用于支持多种输入类型
any_typ = "任意"

# 基础预览类（参考ComfyUI的标准做法）
class 基础预览类:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = ""

    def 获取唯一文件名(self, 文件名前缀):
        os.makedirs(self.output_dir, exist_ok=True)
        文件名 = 文件名前缀 + self.prefix_append
        计数器 = 1
        while True:
            文件 = f"{文件名}_{计数器:04d}.png"
            完整路径 = os.path.join(self.output_dir, 文件)
            if not os.path.exists(完整路径):
                return 完整路径, 文件
            计数器 += 1

    def 保存图像(self, 图像, 文件名前缀, prompt=None, extra_pnginfo=None):
        结果列表 = []
        
        try:
            if isinstance(图像, torch.Tensor):
                if len(图像.shape) == 4:  # 批量图像
                    for i in range(图像.shape[0]):
                        完整输出路径, 文件 = self.获取唯一文件名(文件名前缀)
                        img = Image.fromarray(np.clip(图像[i].cpu().numpy() * 255, 0, 255).astype(np.uint8))
                        img.save(完整输出路径)        
                        结果列表.append({"filename": 文件, "subfolder": "", "type": self.type})
                else:
                    完整输出路径, 文件 = self.获取唯一文件名(文件名前缀)
                    img = Image.fromarray(np.clip(图像.cpu().numpy() * 255, 0, 255).astype(np.uint8))
                    img.save(完整输出路径)
                    结果列表.append({"filename": 文件, "subfolder": "", "type": self.type})
            else:
                完整输出路径, 文件 = self.获取唯一文件名(文件名前缀)
                图像.save(完整输出路径)
                结果列表.append({"filename": 文件, "subfolder": "", "type": self.type})

            return {
                "ui": {"images": 结果列表},
            }
        except Exception as e:
            print(f"保存图像错误: {e}")
            return {"ui": {}}

# 基础图像加载器类
class 基础图像加载器:
    @classmethod
    def 获取图像文件列表(cls):
        """获取输入目录中的所有图像文件"""
        输入目录 = folder_paths.get_input_directory()
        os.makedirs(输入目录, exist_ok=True)
        文件列表 = []
        for 文件 in os.listdir(输入目录):
            文件路径 = os.path.join(输入目录, 文件)
            if os.path.isfile(文件路径) and 文件.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif')):
                文件列表.append(文件)
        return sorted(文件列表)

    def 加载图像(self, 图像文件):
        """加载图像文件"""
        if not 图像文件:
            return None
            
        输入目录 = folder_paths.get_input_directory()
        完整路径 = os.path.join(输入目录, 图像文件)
        
        if os.path.isfile(完整路径):
            return Image.open(完整路径)
        return None

    def 图像转张量(self, 图像):
        """将PIL图像转换为ComfyUI张量"""
        if 图像 is None:
            return None

        图像RGB = 图像.convert('RGB')
        输出图像列表 = []

        for 帧 in ImageSequence.Iterator(图像RGB):
            帧 = ImageOps.exif_transpose(帧)

            if 帧.mode == 'I':
                帧 = 帧.point(lambda i: i * (1 / 255))
            if 帧.mode != 'RGB':
                帧 = 帧.convert('RGB')

            图像数组 = np.array(帧).astype(np.float32) / 255.0
            if len(图像数组.shape) == 3:
                图像张量 = torch.from_numpy(图像数组)[None,]
            else:
                图像张量 = torch.from_numpy(图像数组).unsqueeze(0)
            输出图像列表.append(图像张量)

        return torch.cat(输出图像列表, dim=0) if len(输出图像列表) > 1 else 输出图像列表[0]

    def 处理图像和遮罩(self, 图像):
        """处理图像和生成遮罩"""
        if 图像 is None:
            return None, None, 64, 64

        宽度, 高度 = 图像.size
        
        # 转换为RGB
        图像RGB = 图像.convert('RGB')
        图像张量 = self.图像转张量(图像RGB)
        
        # 生成遮罩
        遮罩 = None
        if 'A' in 图像.getbands():
            遮罩数组 = np.array(图像.getchannel('A')).astype(np.float32) / 255.0
            遮罩 = torch.from_numpy(遮罩数组).unsqueeze(0)
        else:
            遮罩 = torch.ones((1, 高度, 宽度), dtype=torch.float32)
        
        return 图像张量, 遮罩, 宽度, 高度

# 判断并输出加载的图像 - 修改版（条件不满足时不输出图像）
class 判断并输出加载的图像(基础图像加载器, 基础预览类):
    """判断并输出加载的图像
    
    当文本内容包含目标文本时，从输入目录加载选择的图像并显示预览；
    当文本内容不包含目标文本时，不输出图像。
    无论条件是否满足，都会显示图像预览。
    """
    
    def __init__(self):
        基础预览类.__init__(self)
        self.prefix_append = "_条件文本图像_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
    
    @classmethod
    def INPUT_TYPES(cls):
        图像文件列表 = cls.获取图像文件列表()
        
        return {
            "required": {
                "文本内容": ("STRING", {"multiline": True, "default": "内容包含目标名称才会输出图像"}),
                "目标文本": ("STRING", {"default": "名称"}),
                "图像文件": ([""] + 图像文件列表, {"image_upload": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "状态")
    FUNCTION = "加载条件图像"
    CATEGORY = "📃提示词公式/工具节点"
    OUTPUT_NODE = True
    
    def 加载条件图像(self, 文本内容, 目标文本, 图像文件, prompt=None, extra_pnginfo=None):
        状态 = "未包含目标文本"
        图像输出 = None
        
        # 无论条件如何，都加载图像用于预览
        if 图像文件:
            预览图像 = self.加载图像(图像文件)
            if 预览图像:
                图像张量, 遮罩, 宽度, 高度 = self.处理图像和遮罩(预览图像)
                
                # 检查文本是否包含目标文本
                if 目标文本 and 目标文本 in 文本内容:
                    状态 = f"包含目标文本 '{目标文本}'，已加载图像"
                    图像输出 = 图像张量  # 条件满足时输出图像
                else:
                    状态 = f"未包含目标文本 '{目标文本}'，不输出图像"
                    # 条件不满足时不输出图像（图像输出保持为None）
                
                # 保存预览图像（无论条件是否满足都显示预览）
                预览结果 = self.保存图像(图像张量, "条件文本图像预览", prompt, extra_pnginfo)
            else:
                状态 = "图像文件加载失败"
                预览结果 = {"ui": {}}
        else:
            状态 = "未选择图像文件"
            预览结果 = {"ui": {}}
        
        # 返回结果，包括预览信息
        return {
            "ui": 预览结果["ui"],
            "result": (图像输出, 状态)  # 条件不满足时图像输出为None
        }

# 批量判断并输出同名图像 - 修改版（批量判断，多输出端口，条件不满足时不输出）
class 批量判断并输出同名图像(基础图像加载器):
    """批量判断并输出同名图像
    
    当文本内容包含目标文本时，从指定目录中查找同名图像文件并输出图像；
    当文本内容不包含目标文本时，不输出图像。
    支持批量判断，可以输入多个目标文本，用分隔符（，。、/ 或换行）分隔。
    最多输出前三个匹配的图像，每个图像使用一个独立的输出端口。
    不显示预览，只输出图像数据。
    条件不满足时，对应的输出端口不产生输出。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本内容": ("STRING", {"multiline": True, "default": "内容包含目标名称才会输出图像"}),
                "目标文本": ("STRING", {"multiline": True, "default": "可输入多个目标文本，用逗号、句号、顿号、斜杠或换行分隔"}),
                "图像目录": ("STRING", {"default": "S:\ComfyUI-aki-v1.6\ComfyUI\input"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("图像1", "图像2", "图像3", "状态")
    FUNCTION = "加载同名图像"
    CATEGORY = "📃提示词公式/工具节点"
    
    def 加载同名图像(self, 文本内容, 目标文本, 图像目录):
        状态 = ""
        
        # 分割目标文本
        目标文本列表 = self.分割目标文本(目标文本)
        
        if not 目标文本列表:
            状态 = "未输入目标文本"
            # 返回空元组表示不输出任何图像
            return (None, None, None, 状态)
        
        # 存储找到的图像
        找到的图像列表 = []
        
        # 遍历所有目标文本
        for 单个目标文本 in 目标文本列表:
            if len(找到的图像列表) >= 3:  # 最多输出3个图像
                break
                
            # 检查文本是否包含目标文本（不检查后缀）
            if self.包含文本_不检查后缀(文本内容, 单个目标文本):
                状态 += f"包含目标文本 '{单个目标文本}'，"
                
                # 在目录中查找同名图像文件
                图像路径 = self.查找图像文件(图像目录, 单个目标文本)
                
                if 图像路径:
                    try:
                        图像 = Image.open(图像路径)
                        图像张量, 遮罩, 宽度, 高度 = self.处理图像和遮罩(图像)
                        找到的图像列表.append(图像张量)
                        状态 += f"已加载图像{len(找到的图像列表)}: {os.path.basename(图像路径)}。"
                        
                    except Exception as e:
                        状态 += f"图像加载失败: {str(e)}。"
                else:
                    状态 += f"未找到与 '{单个目标文本}' 同名的图像文件。"
            else:
                状态 += f"未包含目标文本 '{单个目标文本}'。"
        
        # 如果没有找到任何图像，添加提示
        if len(找到的图像列表) == 0:
            状态 += "未找到任何匹配的图像。"
        else:
            状态 += f"共找到 {len(找到的图像列表)} 个匹配的图像。"
        
        # 根据找到的图像数量返回相应数量的输出
        # 如果某个位置没有图像，返回None表示不输出
        输出列表 = [None, None, None]
        for i, 图像张量 in enumerate(找到的图像列表):
            if i < 3:  # 确保不超过3个输出
                输出列表[i] = 图像张量
        
        return (输出列表[0], 输出列表[1], 输出列表[2], 状态)
    
    def 分割目标文本(self, 目标文本):
        """分割目标文本，支持多种分隔符"""
        if not 目标文本:
            return []
        
        # 定义分隔符
        分隔符 = [',', '，', '。', '、', '/', '\\', '\n', '\r\n']
        
        # 替换所有分隔符为统一的分隔符
        统一文本 = 目标文本
        for 分隔符字符 in 分隔符:
            统一文本 = 统一文本.replace(分隔符字符, '|')
        
        # 分割并清理
        文本列表 = 统一文本.split('|')
        文本列表 = [文本.strip() for 文本 in 文本列表 if 文本.strip()]
        
        return 文本列表
    
    def 包含文本_不检查后缀(self, 文本内容, 目标文本):
        """
        检查文本内容是否包含目标文本（不检查文件后缀）
        """
        # 移除目标文本可能的后缀
        基础名称 = 目标文本
        if '.' in 目标文本:
            基础名称 = 目标文本.split('.')[0]
        
        # 在文本中查找（支持多种分隔符）
        模式列表 = [
            基础名称,
            基础名称 + '.',
            基础名称 + '_',
            基础名称 + ' ',
            基础名称 + '-'
        ]
        
        return any(模式 in 文本内容 for 模式 in 模式列表)
    
    def 查找图像文件(self, 目录, 目标文本):
        """
        在目录中查找与目标文本同名的图像文件
        """
        if not os.path.exists(目录):
            return None
        
        # 获取目标文本的基础名称（不含后缀）
        基础名称 = 目标文本
        if '.' in 目标文本:
            基础名称 = 目标文本.split('.')[0]
        
        # 支持的图像格式
        图像扩展名列表 = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        
        # 查找匹配的文件
        for 文件名 in os.listdir(目录):
            文件基础名称 = os.path.splitext(文件名)[0]
            
            # 检查基础名称是否匹配
            if 文件基础名称 == 基础名称:
                文件扩展名 = os.path.splitext(文件名)[1].lower()
                if 文件扩展名 in 图像扩展名列表:
                    return os.path.join(目录, 文件名)
        
        return None

class 提取视频结束帧:
    """提取视频序列的最后一帧图像
    
    从输入的图像序列中提取最后一帧，占用极少计算资源。
    适用于从视频生成的图像序列中提取结束帧。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像序列": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("结束帧",)
    FUNCTION = "提取结束帧"
    CATEGORY = "📃提示词公式/工具节点"
    
    def 提取结束帧(self, 图像序列):
        # 检查输入是否为空
        if 图像序列 is None or len(图像序列) == 0:
            return (图像序列,)
        
        # 提取最后一帧（计算量极小）
        结束帧 = 图像序列[-1:]
        
        return (结束帧,)
    
    @classmethod
    def IS_CHANGED(cls, 图像序列):
        # 只有当输入改变时才重新执行
        return float("NaN")

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

class 空图像防报错:
    """空图像防报错
    
    检查输入图像是否为None，如果是None则不输出图像，
    如果不是None则正常输出图像。
    这样可以防止后续节点接收到None而报错。
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "图像": ("IMAGE", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("图像",)
    FUNCTION = "条件通过"
    CATEGORY = "📃提示词公式/工具节点"
    
    def 条件通过(self, 图像=None):
        # 如果输入图像为None，则不输出
        if 图像 is None:
            # 返回空元组表示不输出
            return ()
        
        # 如果输入图像有效，则正常输出
        return (图像,)