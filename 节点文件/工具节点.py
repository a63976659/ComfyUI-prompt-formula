# 工具节点.py
import os
import random
import folder_paths
import numpy as np
import hashlib
import torch
import torch.nn.functional as F
from PIL import Image, ImageSequence, ImageOps

# 定义任意类型
any_typ = "任意"

# ================= 基础类定义 =================

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

            return {"ui": {"images": 结果列表}}
        except Exception as e:
            print(f"保存图像错误: {e}")
            return {"ui": {}}

class 基础图像加载器:
    @classmethod
    def 获取图像文件列表(cls):
        输入目录 = folder_paths.get_input_directory()
        os.makedirs(输入目录, exist_ok=True)
        文件列表 = []
        for 文件 in os.listdir(输入目录):
            文件路径 = os.path.join(输入目录, 文件)
            if os.path.isfile(文件路径) and 文件.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif')):
                文件列表.append(文件)
        return sorted(文件列表)

    def 加载图像(self, 图像文件):
        if not 图像文件: return None
        输入目录 = folder_paths.get_input_directory()
        完整路径 = os.path.join(输入目录, 图像文件)
        if os.path.isfile(完整路径):
            return Image.open(完整路径)
        return None

    def 图像转张量(self, 图像):
        if 图像 is None: return None
        图像RGB = 图像.convert('RGB')
        输出图像列表 = []
        for 帧 in ImageSequence.Iterator(图像RGB):
            帧 = ImageOps.exif_transpose(帧)
            if 帧.mode == 'I': 帧 = 帧.point(lambda i: i * (1 / 255))
            if 帧.mode != 'RGB': 帧 = 帧.convert('RGB')
            图像数组 = np.array(帧).astype(np.float32) / 255.0
            if len(图像数组.shape) == 3: 图像张量 = torch.from_numpy(图像数组)[None,]
            else: 图像张量 = torch.from_numpy(图像数组).unsqueeze(0)
            输出图像列表.append(图像张量)
        return torch.cat(输出图像列表, dim=0) if len(输出图像列表) > 1 else 输出图像列表[0]

    def 处理图像和遮罩(self, 图像):
        if 图像 is None: return None, None, 64, 64
        宽度, 高度 = 图像.size
        图像RGB = 图像.convert('RGB')
        图像张量 = self.图像转张量(图像RGB)
        遮罩 = None
        if 'A' in 图像.getbands():
            遮罩数组 = np.array(图像.getchannel('A')).astype(np.float32) / 255.0
            遮罩 = torch.from_numpy(遮罩数组).unsqueeze(0)
        else:
            遮罩 = torch.ones((1, 高度, 宽度), dtype=torch.float32)
        return 图像张量, 遮罩, 宽度, 高度

# ================= 节点实现 =================

class 判断并输出加载的图像(基础图像加载器, 基础预览类):
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
    CATEGORY = "📕提示词公式/工具节点"
    OUTPUT_NODE = True
    
    def 加载条件图像(self, 文本内容, 目标文本, 图像文件, prompt=None, extra_pnginfo=None):
        状态 = "未包含目标文本"
        图像输出 = None
        if 图像文件:
            预览图像 = self.加载图像(图像文件)
            if 预览图像:
                图像张量, 遮罩, 宽度, 高度 = self.处理图像和遮罩(预览图像)
                if 目标文本 and 目标文本 in 文本内容:
                    状态 = f"包含目标文本 '{目标文本}'，已加载图像"
                    图像输出 = 图像张量
                else:
                    状态 = f"未包含目标文本 '{目标文本}'，不输出图像"
                预览结果 = self.保存图像(图像张量, "条件文本图像预览", prompt, extra_pnginfo)
            else:
                状态 = "图像文件加载失败"
                预览结果 = {"ui": {}}
        else:
            状态 = "未选择图像文件"
            预览结果 = {"ui": {}}
        return {"ui": 预览结果["ui"], "result": (图像输出, 状态)}

class 批量判断并输出同名图像(基础图像加载器):
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        return {
            "required": {
                "文本内容": ("STRING", {"multiline": True, "default": "内容包含目标名称才会输出图像"}),
                "目标文本": ("STRING", {"multiline": True, "default": "可输入多个目标文本，用逗号、句号、顿号、斜杠或换行分隔"}),
                "图像目录": ("STRING", {"default": input_dir}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "状态")
    FUNCTION = "加载同名图像"
    CATEGORY = "📕提示词公式/工具节点"
    
    # 【新增】节点功能描述
    DESCRIPTION = """
    批量判断并输出同名图像 (优化版)：
    
    功能说明：
    1. 根据输入的“目标文本”，自动在指定目录下搜索同名的图像文件。
    2. 支持批量搜索：可一次性输入多个目标名称（用换行、逗号等分隔）。
    3. 智能输出：将所有找到的图像合并为一个批次（Batch）通过“图像”端口输出。
    
    核心优点：
    - ✅ 无数量限制：不再局限于输出3张，符合条件的全部输出。
    - ✅ 自动防报错：内置智能缩放算法，如果找到的多张图尺寸不一致，会自动调整为统一尺寸，防止合并时报错。
    - ✅ 灵活匹配：支持模糊匹配逻辑，自动忽略文件后缀。
    """
    
    def 加载同名图像(self, 文本内容, 目标文本, 图像目录):
        状态 = ""
        if not 图像目录:
            图像目录 = folder_paths.get_input_directory()
        
        if not os.path.exists(图像目录):
            return (None, f"目录不存在: {图像目录}")
        
        目标文本列表 = self.分割目标文本(目标文本)
        if not 目标文本列表:
            return (None, "未输入目标文本")
        
        找到的图像列表 = []
        已匹配文本 = []
        
        # 遍历所有目标文本 (不再限制数量)
        for 单个目标文本 in 目标文本列表:
            if self.包含文本_不检查后缀(文本内容, 单个目标文本):
                图像路径 = self.查找图像文件(图像目录, 单个目标文本)
                if 图像路径:
                    try:
                        图像 = Image.open(图像路径)
                        # 这里获取的是 [1, H, W, C] 的 Tensor
                        图像张量, _, _, _ = self.处理图像和遮罩(图像)
                        找到的图像列表.append(图像张量)
                        已匹配文本.append(单个目标文本)
                        状态 += f"✔ 已加载: {os.path.basename(图像路径)}\n"
                    except Exception as e:
                        状态 += f"❌ 加载失败: {str(e)}\n"
                else:
                    状态 += f"⚠ 未找到文件: {单个目标文本}\n"
        
        if not 找到的图像列表:
            return (None, 状态 + "未找到任何匹配图像。")
        
        # === 批量合并逻辑 (Batch) ===
        try:
            # 以第一张图的尺寸为基准
            基准图像 = 找到的图像列表[0] # [1, H, W, C]
            目标H, 目标W = 基准图像.shape[1], 基准图像.shape[2]
            
            处理后的列表 = []
            for img in 找到的图像列表:
                # 检查尺寸是否一致
                if img.shape[1] != 目标H or img.shape[2] != 目标W:
                    # 尺寸不一致，进行缩放
                    # ComfyUI Tensor是 [B, H, W, C]，interpolate 需要 [B, C, H, W]
                    img_permuted = img.permute(0, 3, 1, 2)
                    # 使用双线性插值缩放
                    img_resized = F.interpolate(img_permuted, size=(目标H, 目标W), mode='bilinear', align_corners=False)
                    # 转回 [B, H, W, C]
                    img = img_resized.permute(0, 2, 3, 1)
                处理后的列表.append(img)
            
            # 合并为一个 Batch Tensor
            最终图像 = torch.cat(处理后的列表, dim=0)
            状态 = f"成功合并 {len(处理后的列表)} 张图像。\n" + 状态
            
            return (最终图像, 状态)
            
        except Exception as e:
            return (None, f"合并图像时出错: {str(e)}")
    
    def 分割目标文本(self, 目标文本):
        if not 目标文本: return []
        分隔符 = [',', '，', '。', '、', '/', '\\', '\n', '\r\n']
        统一文本 = 目标文本
        for 分隔符字符 in 分隔符:
            统一文本 = 统一文本.replace(分隔符字符, '|')
        文本列表 = 统一文本.split('|')
        return [文本.strip() for 文本 in 文本列表 if 文本.strip()]
    
    def 包含文本_不检查后缀(self, 文本内容, 目标文本):
        基础名称 = 目标文本.split('.')[0] if '.' in 目标文本 else 目标文本
        模式列表 = [基础名称, 基础名称 + '.', 基础名称 + '_', 基础名称 + ' ', 基础名称 + '-']
        return any(模式 in 文本内容 for 模式 in 模式列表)
    
    def 查找图像文件(self, 目录, 目标文本):
        if not os.path.exists(目录): return None
        基础名称 = 目标文本.split('.')[0] if '.' in 目标文本 else 目标文本
        图像扩展名列表 = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        for 文件名 in os.listdir(目录):
            if os.path.splitext(文件名)[0] == 基础名称:
                if os.path.splitext(文件名)[1].lower() in 图像扩展名列表:
                    return os.path.join(目录, 文件名)
        return None

class 提取视频结束帧:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"图像序列": ("IMAGE",)}}
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("结束帧",)
    FUNCTION = "提取结束帧"
    CATEGORY = "📕提示词公式/工具节点"
    def 提取结束帧(self, 图像序列):
        if 图像序列 is None or len(图像序列) == 0: return (图像序列,)
        return (图像序列[-1:],)
    @classmethod
    def IS_CHANGED(cls, 图像序列): return float("NaN")

class 字符串输入反转:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"反转": ("BOOLEAN", {"default": False})},
            "optional": {"字符串1": ("STRING", {"forceInput": True}), "字符串2": ("STRING", {"forceInput": True})}
        }
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("输出字符串1", "输出字符串2")
    FUNCTION = "切换输入"
    CATEGORY = "📕提示词公式/工具节点"
    def IS_CHANGED(self, **kwargs): return float("NaN")
    def 切换输入(self, 反转, 字符串1=None, 字符串2=None):
        return (字符串2, 字符串1) if 反转 else (字符串1, 字符串2)

class 图像输入反转:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"反转": ("BOOLEAN", {"default": False})},
            "optional": {"图像1": ("IMAGE", {"forceInput": True}), "图像2": ("IMAGE", {"forceInput": True})}
        }
    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("输出图像1", "输出图像2")
    FUNCTION = "切换输入"
    CATEGORY = "📕提示词公式/工具节点"
    def IS_CHANGED(self, **kwargs): return float("NaN")
    def 切换输入(self, 反转, 图像1=None, 图像2=None):
        return (图像2, 图像1) if 反转 else (图像1, 图像2)

class 合并多组提示词:
    @classmethod
    def INPUT_TYPES(cls):
        optional_inputs = {"分隔符": (["逗号", "句号", "斜杠", "换行"], {"default": "逗号"})}
        for i in range(1, 51):
            optional_inputs[f"提示词{i}"] = ("STRING", {"default": "", "forceInput": True})
        return {"required": {}, "optional": optional_inputs}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("合并提示词",)
    FUNCTION = "合并提示词"
    CATEGORY = "📕提示词公式/工具节点"
    def 合并提示词(self, 分隔符="逗号", **kwargs):
        提示词列表 = []
        for i in range(1, 51):
            key = f"提示词{i}"
            if key in kwargs and kwargs[key] and isinstance(kwargs[key], str) and kwargs[key].strip():
                提示词列表.append(kwargs[key].strip())
        分隔符映射 = {"逗号": ", ", "句号": "。", "斜杠": "/", "换行": "\n"}
        return (分隔符映射.get(分隔符, ", ").join(提示词列表),)

