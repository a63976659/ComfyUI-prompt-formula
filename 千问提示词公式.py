# 千问提示词公式.py
from 工具函数 import clean_text
from 常量配置 import *

class 基础千问节点:
    """千问节点的基类，提供通用功能"""
    
    @classmethod
    def 构建提示词(cls, **components):
        """构建千问格式的提示词"""
        parts = []
        for key, value in components.items():
            if value and clean_text(value) and value != "无":
                parts.append(f"{key}: {clean_text(value)}")
        return "\n".join(parts)

# LOGO生成节点
class LOGO生成(基础千问节点):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "LOGO形象": ("STRING", {"multiline": False, "default": "一只可爱的飞行员猪头像", "display_name": "LOGO形象"}),
                "LOGO文字": ("STRING", {"multiline": False, "default": "猪的飞行梦", "display_name": "LOGO文字"}),
            },
            "optional": {
                "颜色预设": (list(COLOR_PRESETS_DETAILS.keys()), {"default": "无", "display_name": "颜色预设"}),
                "附加提示词": ("STRING", {"multiline": True, "default": "", "display_name": "附加提示词"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("LOGO提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问"

    def 生成提示词(self, LOGO形象, LOGO文字, 颜色预设="无", 附加提示词=""):
        components = {
            "LOGO形象": LOGO形象,
            "LOGO文字": LOGO文字,
            "附加提示词": 附加提示词
        }
        
        if 颜色预设 != "无":
            components["配色方案"] = 颜色预设
            if 颜色预设 in COLOR_PRESETS_DETAILS:
                color_info = COLOR_PRESETS_DETAILS[颜色预设]
                components["主色"] = f"{color_info['colors'][0]} (占比{color_info['percentages'][0]})"
                components["辅色"] = f"{color_info['colors'][1]} (占比{color_info['percentages'][1]})"
                components["点缀色"] = f"{color_info['colors'][2]} (占比{color_info['percentages'][2]})"
            
        return (self.构建提示词(**components),)

# 艺术字体生成节点
class 艺术字体生成:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文字内容": ("STRING", {
                    "multiline": False,
                    "default": "猪的飞行梦",
                    "display_name": "文字内容"
                }),
                "字体风格": ("STRING", {
                    "multiline": False,
                    "default": "3D字体，游戏LOGO设计,立体字设计,创意金属字,C4D渲染,OC渲染,字迹厚重粗犷,字体要有力量感,笔锋明显,笔锋苍劲有力,要充满科技感,金属质感",
                    "display_name": "字体风格"
                }),
            },
            "optional": {
                "视角方向": (VIEW_DIRECTIONS, {
                    "default": "无",
                    "display_name": "视角方向"
                }),
                "排版方式": ("STRING", {
                    "multiline": False,
                    "default": "文字排版艺术",
                    "display_name": "排版方式"
                }),
                "字体颜色": (COLOR_OPTIONS, {
                    "default": "无",
                    "display_name": "字体颜色"
                }),
                "背景颜色": (COLOR_OPTIONS, {
                    "default": "无",
                    "display_name": "背景颜色"
                }),
                "附加提示词": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "附加提示词"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("艺术字体提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问"

    def 生成提示词(self, 文字内容, 字体风格, 视角方向="无", 排版方式="", 字体颜色="无", 背景颜色="无", 附加提示词=""):
        parts = [
            f"文字内容: {clean_text(文字内容)}",
            f"字体风格: {clean_text(字体风格)}"
        ]
        
        if 视角方向 != "无":
            parts.append(f"视角方向: {clean_text(视角方向)}")
            
        if clean_text(排版方式):
            parts.append(f"排版方式: {clean_text(排版方式)}")
            
        if 字体颜色 != "无":
            parts.append(f"字体颜色: {clean_text(字体颜色)}")
            
        if 背景颜色 != "无":
            parts.append(f"背景颜色: {clean_text(背景颜色)}")
            
        if clean_text(附加提示词):
            parts.append(f"附加提示词: {clean_text(附加提示词)}")
            
        return ("\n".join(parts),)

# 海报生成节点
class 海报生成:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "海报类型": (POSTER_TYPES, {
                    "default": "无",
                    "tooltip": "海报类型"
                }),
                "主体_前景描述": ("STRING", {
                    "multiline": True,
                    "default": "一个可爱的小猪坐在书桌前\n周围环绕智能书包、电竞耳机、笔记本电脑、手机等 \"新装备\"\n小猪穿着学生制服\n整体时尚写实，色彩明快吸睛",
                    "placeholder": "描述主体或前景内容...",
                    "tooltip": "主体(前景)描述"
                }),
                "海报主题文字": ("STRING", {
                    "multiline": False,
                    "default": "猪的飞行梦",
                    "tooltip": "海报主题文字"
                }),
                "副标题": ("STRING", {
                    "multiline": False,
                    "default": "开启新学期，追逐新梦想",
                    "tooltip": "副标题"
                }),
                "中部标语": ("STRING", {
                    "multiline": False,
                    "default": "彩色圆角框内：全场1折起！限时优惠！",
                    "tooltip": "中部标语"
                }),
                "活动亮点介绍": ("STRING", {
                    "multiline": True,
                    "default": "白色小字，居中四行\n• 新品首发，独家优惠\n• 满减活动，多买多省\n• 会员专享，额外福利\n• 礼品赠送，先到先得",
                    "placeholder": "输入活动亮点介绍...",
                    "tooltip": "活动亮点介绍"
                }),
                "底部日期与地点": ("STRING", {
                    "multiline": False,
                    "default": "2025年9月1日-9月30日 | 全国各大学校周边门店",
                    "tooltip": "底部日期与地点"
                }),
            },
            "optional": {
                "背景描述": ("STRING", {
                    "multiline": True,
                    "default": "校园教室背景\n阳光透过窗户洒进来\n墙上贴着学习海报和课程表\n书架上摆满书籍和文具",
                    "placeholder": "描述背景环境...",
                    "tooltip": "背景描述"
                }),
                "字体颜色": (COLOR_OPTIONS, {
                    "default": "无",
                    "tooltip": "字体颜色"
                }),
                "背景颜色": (COLOR_OPTIONS, {
                    "default": "无",
                    "tooltip": "背景颜色"
                }),
                "附加提示词": ("STRING", {
                    "multiline": True,
                    "default": "特效艺术文字,加入电商主题装饰元素",
                    "placeholder": "额外的要求...",
                    "tooltip": "附加提示词"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("海报提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问"

    def 生成提示词(self, 主体_前景描述, 海报主题文字, 副标题, 中部标语, 
                  活动亮点介绍, 底部日期与地点, 海报类型="无", 背景描述="", 
                  字体颜色="无", 背景颜色="无", 附加提示词=""):
        parts = [
            f"主体(前景)描述: {clean_text(主体_前景描述)}",
            f"海报主题文字: {clean_text(海报主题文字)}",
            f"副标题: {clean_text(副标题)}",
            f"中部标语: {clean_text(中部标语)}",
            f"活动亮点介绍: {clean_text(活动亮点介绍)}",
            f"底部日期与地点: {clean_text(底部日期与地点)}"
        ]
        
        if 海报类型 != "无":
            parts.append(f"海报类型: {clean_text(海报类型)}")
            
        if clean_text(背景描述):
            parts.append(f"背景描述: {clean_text(背景描述)}")
            
        if 字体颜色 != "无":
            parts.append(f"字体颜色: {clean_text(字体颜色)}")
            
        if 背景颜色 != "无":
            parts.append(f"背景颜色: {clean_text(背景颜色)}")
            
        if clean_text(附加提示词):
            parts.append(f"附加提示词: {clean_text(附加提示词)}")
            
        return ("\n".join(parts),)

# 千问图像节点
class 千问图像:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "主体": ("STRING", {
                    "multiline": False,
                    "default": "古代中国的仙女",
                    "display_name": "主体"
                }),
            },
            "optional": {
                "细节": ("STRING", {
                    "multiline": True,
                    "default": "身着飘逸丝绸长袍",
                    "display_name": "细节"
                }),
                "场景": ("STRING", {
                    "multiline": False,
                    "default": "飘浮于雾蒙蒙的山峰之上，脚踏七彩祥云",
                    "display_name": "场景"
                }),
                "景别": (SHOT_TYPES, {
                    "default": "无",
                    "display_name": "景别"
                }),
                "附加提示词": ("STRING", {
                    "multiline": True,
                    "default": "兼具超凡脱俗的美感与灵性，数字艺术风格，超现实景观，高分辨率",
                    "display_name": "附加提示词"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("千问图像提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问"

    def 生成提示词(self, 主体, 细节="", 场景="", 景别="无", 附加提示词=""):
        parts = [f"主体: {clean_text(主体)}"]
        
        if clean_text(细节):
            parts.append(f"细节: {clean_text(细节)}")
            
        if clean_text(场景):
            parts.append(f"场景: {clean_text(场景)}")
            
        if 景别 != "无":
            parts.append(f"景别: {clean_text(景别)}")
            
        if clean_text(附加提示词):
            parts.append(f"附加提示词: {clean_text(附加提示词)}")
            
        return ("\n".join(parts),)

# 表情包生成节点
class 表情包生成:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "主体": ("STRING", {
                    "multiline": False,
                    "default": "可爱的卡通猪角色",
                    "display_name": "主体"
                }),
                "详细内容": ("STRING", {
                    "multiline": True,
                    "default": "第一行第一格是不开心的动作，文字是'不开心'\n第一行第二格高兴动作，文字是'下班了'\n第一行第三格躺着动作，文字是'躺平了'\n第二行第一格振臂动作，文字是'努力啊'\n第二行第二格大笑动作，文字是'哈哈哈'\n第二行第三格竖大拇指动作，文字是'厉害'\n第三行第一格思考动作，文字是'无聊'\n第三行第二格生气动作，文字是'不加班'\n第三行第三格害羞动作，文字是'好尴尬'",
                    "placeholder": "详细描述（多宫格图像建议尺寸比例1：1）",
                    "display_name": "详细内容"
                }),
            },
            "optional": {
                "布局": (MEME_LAYOUTS, {
                    "default": "九宫格",
                    "display_name": "布局"
                }),
                "表情包风格": (VISUAL_STYLES, {
                    "default": "无",
                    "display_name": "表情包风格"
                }),
                "背景颜色": (COLOR_OPTIONS, {
                    "default": "无",
                    "display_name": "背景颜色"
                }),
                "附加提示词": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "附加提示词"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("表情包提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问"

    def 生成提示词(self, 主体, 详细内容, 布局="九宫格", 表情包风格="无", 背景颜色="无", 附加提示词=""):
        parts = [
            f"主体: {clean_text(主体)}",
            f"详细内容: {clean_text(详细内容)}"
        ]
        
        # 布局为单个时不输出布局信息
        if 布局 != "单个":
            parts.append(f"布局: {clean_text(布局)}")
            
        if 表情包风格 != "无":
            parts.append(f"表情包风格: {clean_text(表情包风格)}")
            
        if 背景颜色 != "无":
            parts.append(f"背景颜色: {clean_text(背景颜色)}")
            
        if clean_text(附加提示词):
            parts.append(f"附加提示词: {clean_text(附加提示词)}")
            
        return ("\n".join(parts),)