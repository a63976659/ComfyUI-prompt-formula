# 千问编辑.py
from 常量配置 import *


class 千问单图编辑_改变视角:
    """改变视角的提示词编辑"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "目标": (QIANWEN_TARGETS, {"default": "主体"}),
                "方向": (CAMERA_DIRECTIONS, {"default": "向左旋转"}),
                "角度": (CAMERA_ANGLES, {"default": "30度"}),
            },
            "optional": {
                "附加提示词": ("STRING", {"multiline": True, "default": "保持一致性，视角连贯"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("编辑提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问编辑"
    
    def 生成提示词(self, 目标, 方向, 角度, 附加提示词=""):
        提示词 = f"将{目标}{方向}{角度}。"
        
        if 附加提示词 and 附加提示词.strip():
            提示词 += f" {附加提示词.strip()}"
            
        return (提示词,)

class 千问单图编辑_改变镜头:
    """改变镜头类型的提示词编辑"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "目标": (["主体", "人物", "物品", "图像"], {"default": "主体"}),
                "镜头": (PROFESSIONAL_SHOT_TYPES, {"default": "航拍镜头"}),
            },
            "optional": {
                "附加提示词": ("STRING", {"multiline": True, "default": "构图精美，焦点清晰"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("编辑提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问编辑"
    
    def 生成提示词(self, 目标, 镜头, 附加提示词=""):
        # 构建镜头描述
        提示词 = f"将{目标}改为{镜头}拍摄。"
        
        # 添加附加提示词
        if 附加提示词 and 附加提示词.strip():
            提示词 += f" {附加提示词.strip()}"
            
        return (提示词,)

class 千问单图编辑_人物换动作:
    """更换人物动作的提示词编辑"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "角色": (CHARACTER_ROLES, {"default": "女孩"}),
                "动作": (CHARACTER_ACTIONS, {"default": "比耶手势"}),
            },
            "optional": {
                "附加提示词": ("STRING", {"multiline": True, "default": "表情自然，动作生动"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("编辑提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问编辑"
    
    def 生成提示词(self, 角色, 动作, 附加提示词=""):
        详细动作 = ACTION_DESCRIPTIONS.get(动作, 动作)
        提示词 = f"{角色}面对镜头，{详细动作}。"
        
        if 附加提示词 and 附加提示词.strip():
            提示词 += f" {附加提示词.strip()}"
            
        return (提示词,)

class 千问单图编辑_物品换材质:
    """更换物品材质的提示词编辑"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "目标": (QIANWEN_TARGETS, {"default": "物品"}),
                "材质": (MATERIAL_TYPES, {"default": "黄金"}),
            },
            "optional": {
                "附加提示词": ("STRING", {"multiline": True, "default": "材质质感真实，光影效果出色"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("编辑提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问编辑"
    
    def 生成提示词(self, 目标, 材质, 附加提示词=""):
        详细材质 = MATERIAL_DESCRIPTIONS.get(材质, 材质)
        提示词 = f"将{目标}转为{材质}材质，{详细材质}。"
        
        if 附加提示词 and 附加提示词.strip():
            提示词 += f" {附加提示词.strip()}"
            
        return (提示词,)

class 千问单图编辑_图像变文创产品:
    """将图像转换为文创产品的提示词编辑"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "目标": (QIANWEN_TARGETS, {"default": "主体"}),
                "样式": (CULTURAL_PRODUCT_STYLES, {"default": "手办模型"}),
            },
            "optional": {
                "附加提示词": ("STRING", {"multiline": True, "default": "设计精美，适合量产"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("编辑提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问编辑"
    
    def 生成提示词(self, 目标, 样式, 附加提示词=""):
        详细样式 = CULTURAL_PRODUCT_DESCRIPTIONS.get(样式, 样式)
        提示词 = f"将{目标}设计成{样式}，{详细样式}。"
        
        if 附加提示词 and 附加提示词.strip():
            提示词 += f" {附加提示词.strip()}"
            
        return (提示词,)

class 千问单图编辑_图像转绘:
    """图像画风转绘的提示词编辑"""
    
    @classmethod
    def INPUT_TYPES(cls):
        # 从VISUAL_STYLES中排除"无"选项
        转绘风格选项 = [风格 for 风格 in VISUAL_STYLES if 风格 != "无"]
        
        # 从COLOR_PRESETS中获取所有选项（包含"无"）
        色彩风格选项 = COLOR_PRESETS  # 直接使用原列表，包含"无"
        
        return {
            "required": {
                "转绘风格": (转绘风格选项, {"default": "油画风格"}),
                "色彩风格": (色彩风格选项, {"default": "无"}),  # 默认值为"无"
            },
            "optional": {
                "附加提示词": ("STRING", {"multiline": True, "default": "画风细腻，色彩和谐"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("编辑提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问编辑"
    
    def 生成提示词(self, 转绘风格, 色彩风格, 附加提示词=""):
        # 构建转绘风格部分
        提示词 = f"将图像转为{转绘风格}风格"
        
        # 构建色彩风格部分（如果色彩风格不是"无"）
        if 色彩风格 != "无" and 色彩风格 in COLOR_PRESETS_DETAILS and COLOR_PRESETS_DETAILS[色彩风格]:
            色彩信息 = COLOR_PRESETS_DETAILS[色彩风格]
            颜色描述 = []
            
            for i in range(len(色彩信息["colors"])):
                颜色 = 色彩信息["colors"][i]
                占比 = 色彩信息["percentages"][i]
                颜色描述.append(f"{颜色}({占比})")
            
            色彩描述 = "，".join(颜色描述)
            提示词 += f"，采用{色彩风格}配色方案：{色彩描述}"
        
        # 添加附加提示词
        if 附加提示词 and 附加提示词.strip():
            提示词 += f"。{附加提示词.strip()}"
        else:
            提示词 += "。"
            
        return (提示词,)

class 千问单图编辑_图像编辑:
    """图像编辑处理的提示词编辑"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "目标": (QIANWEN_TARGETS, {"default": "图像"}),
                "编辑类型": (IMAGE_EDITING_TYPES, {"default": "照片修复"}),
            },
            "optional": {
                "附加提示词": ("STRING", {"multiline": True, "default": "处理精细，效果自然"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("编辑提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问编辑"
    
    def 生成提示词(self, 目标, 编辑类型, 附加提示词=""):
        # 获取编辑类型的详细描述
        详细描述 = IMAGE_EDITING_DESCRIPTIONS.get(编辑类型, 编辑类型)
        
        # 构建提示词
        提示词 = f"对{目标}进行{编辑类型}处理，{详细描述}"
        
        # 添加附加提示词
        if 附加提示词 and 附加提示词.strip():
            提示词 += f"。{附加提示词.strip()}"
        else:
            提示词 += "。"
            
        return (提示词,)