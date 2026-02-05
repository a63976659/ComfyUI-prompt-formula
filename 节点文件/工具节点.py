# 工具节点.py
import os
import random
import folder_paths
import numpy as np
import hashlib
import torch
import torch.nn.functional as F
import re
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
                "文本内容": ("STRING", {"default": "输入图像文件名"}),
                "图像文件": ([""] + 图像文件列表, {"image_upload": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "状态")
    FUNCTION = "加载条件图像"
    CATEGORY = "📕提示词公式/工具节点"
    OUTPUT_NODE = True
    DESCRIPTION = "根据加载图像的文件名（截取第一个符号前）在文本内容中搜索。\n 若文本包含该关键字则输出图像，否则不输出。支持连续文本匹配。"
    
    def 加载条件图像(self, 文本内容, 图像文件, prompt=None, extra_pnginfo=None):
        状态 = "未选中图像"
        图像输出 = None
        预览结果 = {"ui": {}}

        if 图像文件:
            name_part, _ = os.path.splitext(os.path.basename(图像文件))
            split_pattern = r'[ \(\)\[\]\{\}\-_,\.，。、\（\）\【\】\—\s]'
            search = re.search(split_pattern, name_part)
            match_name = name_part[:search.start()] if search else name_part

            预览图像 = self.加载图像(图像文件)
            if 预览图像:
                图像张量, _, _, _ = self.处理图像和遮罩(预览图像)
                if match_name and match_name in 文本内容:
                    状态 = f"✔ 匹配成功！内容包含: {match_name}"
                    图像输出 = 图像张量
                else:
                    状态 = f"❌ 匹配失败。关键字 '{match_name}' 不在内容中。"
                预览结果 = self.保存图像(图像张量, "条件文本图像预览", prompt, extra_pnginfo)
            else:
                状态 = "文件读取失败"
        
        return {"ui": 预览结果["ui"], "result": (图像输出, 状态)}

class 批量输出同名图像(基础图像加载器):
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        return {
            "required": {
                "文本内容1": ("STRING", {"default": "输入图像文件名"}),
                "图像目录1": ("STRING", {"default": input_dir}),
                "文本内容2": ("STRING", {"default": "输入图像文件名"}),
                "图像目录2": ("STRING", {"default": input_dir}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "状态")
    FUNCTION = "加载匹配图像"
    CATEGORY = "📕提示词公式/工具节点"
    DESCRIPTION = "分别在两个目录中搜索匹配文本的图像。\n先处理第1组，再处理第2组。\n匹配成功的图像将按顺序合并为一个 Batch 输出，状态文本中的序号连续递增。"
    
    def _处理单组数据(self, 文本内容, 图像目录, 起始序号):
        """
        内部辅助函数：处理单个目录的匹配逻辑
        返回: (图像张量列表, 匹配信息列表, 下一个序号)
        """
        找到的张量 = []
        匹配信息 = []
        当前序号 = 起始序号

        if not 图像目录 or not os.path.exists(图像目录):
            print(f"目录跳过或不存在: {图像目录}")
            return [], [], 当前序号

        图像扩展名 = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
        所有文件 = sorted(os.listdir(图像目录)) # 排序确保顺序稳定
        split_pattern = r'[ \(\)\[\]\{\}\-_,\.，。、\（\）\【\】\—\s]'

        for 文件名 in 所有文件:
            name_part, ext_part = os.path.splitext(文件名)
            if ext_part.lower() in 图像扩展名:
                search = re.search(split_pattern, name_part)
                match_name = name_part[:search.start()] if search else name_part
                
                # 核心匹配逻辑
                if match_name and match_name in 文本内容: 
                    try:
                        图像路径 = os.path.join(图像目录, 文件名)
                        图像 = Image.open(图像路径)
                        张量, _, _, _ = self.处理图像和遮罩(图像)
                        找到的张量.append(张量)
                        
                        # 构建状态：图像n是文件名(无后缀)
                        匹配信息.append(f"图像{当前序号}是{name_part}")
                        当前序号 += 1
                    except Exception as e:
                        print(f"加载失败 {文件名}: {str(e)}")
        
        return 找到的张量, 匹配信息, 当前序号

    def 加载匹配图像(self, 文本内容1, 图像目录1, 文本内容2, 图像目录2):
        # 1. 处理第一组
        张量列表1, 信息列表1, 序号2 = self._处理单组数据(文本内容1, 图像目录1, 1)
        
        # 2. 处理第二组 (起始序号接在第一组后面)
        张量列表2, 信息列表2, _ = self._处理单组数据(文本内容2, 图像目录2, 序号2)

        # 3. 合并结果
        总图像张量列表 = 张量列表1 + 张量列表2
        总信息列表 = 信息列表1 + 信息列表2

        if not 总图像张量列表:
            return (None, "两组路径均未找到匹配图像。")
        
        # 生成状态字符串
        状态 = "，".join(总信息列表)
        
        # 4. 统一尺寸并合并 Batch
        try:
            # 以第一张匹配到的图为基准尺寸
            基准 = 总图像张量列表[0]
            目标H, 目标W = 基准.shape[1], 基准.shape[2]
            最终列表 = []
            
            for img in 总图像张量列表:
                if img.shape[1] != 目标H or img.shape[2] != 目标W:
                    # 如果尺寸不一致，进行插值调整
                    img_p = img.permute(0, 3, 1, 2)
                    img_p = F.interpolate(img_p, size=(目标H, 目标W), mode='bilinear', align_corners=False)
                    img = img_p.permute(0, 2, 3, 1)
                最终列表.append(img)
            
            最终批次 = torch.cat(最终列表, dim=0)
            return (最终批次, 状态)
        except Exception as e:
            return (None, f"合并过程出错: {str(e)}")

class 提取视频帧:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像序列": ("IMAGE",),
                "选择帧": (["开始帧", "结束帧"], {"default": "结束帧"}),
            }
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("帧图像",)
    FUNCTION = "提取指定帧"
    CATEGORY = "📕提示词公式/工具节点"
    DESCRIPTION = "从输入的图像 Batch（视频序列）中提取第一帧或最后一帧。\n 常用于获取视频的起始参考图或末尾状态。"
    
    def 提取指定帧(self, 图像序列, 选择帧):
        if 图像序列 is None or len(图像序列) == 0:
            return (图像序列,)
        if 选择帧 == "开始帧":
            return (图像序列[:1],)
        else:
            return (图像序列[-1:],)

    @classmethod
    def IS_CHANGED(cls, 图像序列, 选择帧):
        return float("NaN")

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
    DESCRIPTION = "根据布尔值决定是否交换两个输入字符串的顺序。\n 用于在不同工作流分支间快速切换提示词或路径。"
    
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
    DESCRIPTION = "根据布尔值决定是否交换两组图像输入的顺序。\n 适用于 A/B 测试或条件控制图像流向。"
    
    def 切换输入(self, 反转, 图像1=None, 图像2=None):
        return (图像2, 图像1) if 反转 else (图像1, 图像2)

class 合并多组提示词:
    @classmethod
    def INPUT_TYPES(cls):
        optional_inputs = {"分隔符": (["逗号", "句号", "斜杠", "换行", "无"], {"default": "逗号"})}
        for i in range(1, 51):
            optional_inputs[f"提示词{i}"] = ("STRING", {"default": "", "forceInput": True})
        return {"required": {}, "optional": optional_inputs}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("合并提示词",)
    FUNCTION = "合并提示词"
    CATEGORY = "📕提示词公式/工具节点"
    DESCRIPTION = "将最多 50 组提示词字符串按选定的分隔符拼接成一个完整的长文本。\n 自动忽略空输入。"
    
    def 合并提示词(self, 分隔符="逗号", **kwargs):
        提示词列表 = []
        for i in range(1, 51):
            key = f"提示词{i}"
            if key in kwargs and kwargs[key] and isinstance(kwargs[key], str) and kwargs[key].strip():
                提示词列表.append(kwargs[key].strip())
        分隔符映射 = {"逗号": ", ", "句号": "。", "斜杠": "/", "换行": "\n", "无": ""}
        return (分隔符映射.get(分隔符, ", ").join(提示词列表),)