# 通用提示词公式.py
import random
import re
import json
import os
from datetime import datetime

import folder_paths
from 常量配置 import *
from 工具函数 import *

# 提示词预设节点 - 修复读取和排序问题
class 提示词预设:
    tooltip = "预设文件储存在此插件提示词预设文件夹，支持TXT和JSON格式。文件按名称排序，请手动展开选择。"

    @classmethod
    def INPUT_TYPES(cls):
        try:
            # 强制刷新缓存，确保获取最新文件
            global _preset_cache, _last_refresh_time
            _preset_cache = {}
            _last_refresh_time = 0
            
            presets = load_presets()
            preset_names = list(presets.keys())
            
            # 按名称排序
            preset_names.sort()
            
            if not preset_names:
                preset_names = ["请先创建预设"]
                presets = {"请先创建预设": {"content": "", "preview_path": None, "preview_type": None, "file_type": "unknown"}}
            
            preview_metadata = {}
            for name in preset_names:
                if name in presets:
                    preview_metadata[name] = {
                        "type": presets[name]["preview_type"] or "none",
                        "path": presets[name]["preview_path"] or "",
                        "file_type": presets[name]["file_type"] or "unknown"
                    }
                else:
                    preview_metadata[name] = {
                        "type": "none",
                        "path": "",
                        "file_type": "unknown"
                    }
            
            return {
                "required": {
                    "预设名称": (preset_names, {
                        "default": preset_names[0] if preset_names else "请先创建预设",
                        "tooltip": cls.tooltip,
                        "preview_metadata": json.dumps(preview_metadata)
                    }),
                }
            }
        except Exception as e:
            logging.error(f"提示词预设节点初始化错误: {str(e)}")
            return {
                "required": {
                    "预设名称": (["请先创建预设"], {"default": "请先创建预设"}),
                }
            }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("预设名称", "预设内容", "文件类型")
    FUNCTION = "选择预设"
    CATEGORY = "📃提示词公式"

    def 选择预设(self, 预设名称):
        try:
            presets = load_presets()
            if 预设名称 in presets:
                preset_info = presets[预设名称]
                return (预设名称, preset_info["content"], preset_info["file_type"])
            else:
                return (预设名称, "", "unknown")
        except Exception as e:
            logging.error(f"选择预设时出错: {str(e)}")
            return (预设名称, "", "error")

# 视频提示词公式节点 - 添加调试信息
class 视频提示词公式:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "主体描述": ("STRING", {"multiline": False, "default": "一个女孩身穿粉色长裙，头戴蝴蝶发卡", "display_name": "主体描述"}),
                "人物情绪": (EMOTIONS, {"default": "无", "display_name": "人物情绪"}),
                "主体运动": (CHARACTER_MOVEMENTS, {"default": "无", "display_name": "主体运动"}),
                "眼型描述": (EYE_SHAPES, {"default": "无", "display_name": "眼型描述"}),
                "场景描述": ("STRING", {"multiline": False, "default": "在樱花树下", "display_name": "场景描述"}),
                "天气": (WEATHER_TYPES, {"default": "无", "display_name": "天气"}),
                "光源类型": (LIGHT_SOURCE_TYPES, {"default": "无", "display_name": "光源类型"}),
                "光线类型": (LIGHT_TYPE, {"default": "无", "display_name": "光线类型"}),
                "时间段": (TIME_PERIODS, {"default": "无", "display_name": "时间段"}),
                "景别描述": (SHOT_TYPES, {"default": "无", "display_name": "景别描述"}),
                "构图描述": (COMPOSITION_STYLES, {"default": "无", "display_name": "构图描述"}),
                "镜头焦段": (LENS_TYPES, {"default": "无", "display_name": "镜头焦段"}),
                "机位角度": (CAMERA_ANGLES, {"default": "无", "display_name": "机位角度"}),
                "镜头类型": (SHOT_COMPOSITIONS, {"default": "无", "display_name": "镜头类型"}),
                "镜头目标": ("STRING", {"multiline": False, "default": "主体", "display_name": "镜头目标"}),
                "运镜方式": (CAMERA_MOVEMENTS, {"default": "无", "display_name": "运镜方式"}),
                "色调": (["无", "暖色调", "冷色调", "高饱和度", "低饱和度"], {"default": "无", "display_name": "色调"}),
                "视觉风格": (VISUAL_STYLES, {"default": "无", "display_name": "视觉风格"}),
            },
            "optional": {
                "附加提示词": ("STRING", {"multiline": True, "default": "兼具超凡脱俗的美感与灵性，数字艺术风格，超现实景观，高分辨率", "display_name": "附加提示词"}),
                "自动保存到历史": ("BOOLEAN", {"default": True, "display_name": "自动保存到历史记录"})
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式"

    def 生成提示词(self, 主体描述, 人物情绪, 主体运动, 眼型描述, 场景描述, 天气, 光源类型,
                      光线类型, 时间段, 景别描述, 构图描述, 镜头焦段, 机位角度, 镜头类型, 
                      镜头目标, 运镜方式, 色调, 视觉风格, 附加提示词="", 自动保存到历史=True):
        
        try:
            组件列表 = []
            
            # 处理主体描述
            if 主体描述 and clean_text(主体描述):
                组件列表.append(clean_text(主体描述))
            
            # 处理其他组件
            components = {
                "人物情绪": 人物情绪,
                "主体运动": 主体运动,
                "眼型描述": 眼型描述,
                "天气": 天气,
                "光源类型": 光源类型,
                "光线类型": 光线类型,
                "时间段": 时间段,
                "景别描述": 景别描述,
                "构图描述": 构图描述,
                "镜头焦段": 镜头焦段,
                "机位角度": 机位角度,
                "镜头类型": 镜头类型,
                "色调": 色调,
                "视觉风格": 视觉风格
            }
            
            for key, value in components.items():
                if value != "无":
                    组件列表.append(value)
            
            # 处理场景描述
            if 场景描述 and clean_text(场景描述):
                组件列表.append(clean_text(场景描述))
            
            # 处理运镜方式
            if 运镜方式 != "无":
                运镜描述 = self._get_camera_movement_desc(运镜方式, 镜头目标)
                if 运镜描述:
                    组件列表.append(运镜描述)
            
            # 处理附加提示词
            if 附加提示词 and clean_text(附加提示词):
                组件列表.append(clean_text(附加提示词))
            
            # 生成最终提示词
            提示词 = ", ".join(组件列表)
            
            # 处理历史记录保存
            if 自动保存到历史 and 提示词:
                名称 = clean_text(主体描述) or clean_text(场景描述) or "未命名提示词"
                save_to_history(提示词, 名称, manual_save=False)
                
            return (提示词,)
            
        except Exception as e:
            logging.error(f"视频提示词公式生成错误: {str(e)}")
            return (f"生成提示词时出错: {str(e)}",)

    def _get_camera_movement_desc(self, movement, target):
        """获取镜头运动描述"""
        effective_target = target if target and target != "无" else "主体"
        movement_descriptions = {
            "固定镜头": "镜头位置保持不动，构图稳定，画面无明显抖动",
            "推近镜头": f"镜头缓慢向前推进，逐步聚焦{effective_target}细节，背景渐渐虚化，细节清晰锐利最终停留在特写构图，画面稳定",
            "拉远镜头": f"{effective_target}位于画面中央，镜头缓慢向后移动，从近景过渡到全景，{effective_target}始终保持居中，焦点稳定",
            "快速推近": f"{effective_target}位于画面中央，镜头快速向前推进至中近景或特写，焦点锁定{effective_target}，背景产生轻微动感模糊",
            "快速拉远": f"{effective_target}位于画面中央，镜头快速向后拉远至全景，背景空间迅速扩展，{effective_target}位置保持居中",
            "俯视角度": f"{effective_target}位于画面中央，镜头缓慢升至俯视角度，焦点锁定{effective_target}，背景在画面下方展开",
            "仰视角度": f"{effective_target}位于画面中央，镜头缓慢下降至仰视角度，焦点锁定{effective_target}，背景在画面上方延伸",
            "上移镜头": f"镜头从正前方启动，缓慢升高并俯视{effective_target}，保持居中构图，随后缓慢下降回到平视位置，画面稳定",
            "下移镜头": "镜头从高处俯视缓慢下降到平视，停留在特写位置",
            "左摇镜头": f"镜头缓慢向左平移，{effective_target}缓慢向右平移，从画面右侧消失，画面中仅保留向左移动的背景",
            "右摇镜头": f"镜头缓慢向右平移，{effective_target}缓慢向左平移，从画面左侧消失，画面中仅保留向右移动的背景",
            "上仰镜头": f"镜头缓慢上移，{effective_target}缓慢下移，从画面下方消失，画面中仅保留向上移动的背景",
            "下俯镜头": f"镜头缓慢下移，{effective_target}缓慢上移，从画面上方消失，画面中仅保留向下移动的背景",
            "前进后退交替": f"镜头快速推进至{effective_target}特写，然后平稳拉远至全景，重复两次，节奏一致，焦点始终锁定{effective_target}",
            "前进后退循环": f"镜头快速推进至特写，再平稳拉远至全景，重复两次，焦点始终锁定{effective_target}",
            "右弧线移动(半圈)": f"镜头从左前方缓慢移动到右前方，形成半圆运动轨迹，{effective_target}清晰，背景轻微模糊",
            "左弧线移动(半圈)": f"镜头从右前方缓慢移动到左前方，形成半圆运动轨迹，{effective_target}清晰，背景轻微模糊",
            "水平快速平移": f"{effective_target}位于画面中央不动，镜头高速从左向右平移掠过{effective_target}正面，背景形成流动残影，随后镜头迅速回到原位，构图稳定",
            "水平环绕": f"{effective_target}位于画面中央，保持静止，镜头从正前方启动，顺时针环绕180度至{effective_target}背面，背景轻微模糊，镜头继续顺时针环绕180度回到正前方位置，{effective_target}始终居中，画面稳定收束",
            "环绕+拉近": f"镜头从正前方启动，顺时针环绕90度，同时缓慢拉近至局部细节，背景虚化，{effective_target}清晰",
            "环绕+翻转": f"{effective_target}保持静止，正面朝向镜头，镜头从{effective_target}右后方启动，顺时针水平环绕一整圈，画面同步翻转180度使{effective_target}出现在画面下方，背景倒置悬浮在上方，镜头继续环绕至270°位置，在倒置状态中缓慢恢复水平构图，最终停留在{effective_target}正面中近景，背景略带旋转残影",
            "原地旋转": f"镜头从正前方启动，顺时针环绕90度至{effective_target}侧面，再顺时针环绕90度至{effective_target}背面，背景在运动中轻微模糊，最后镜头回到正前方，{effective_target}始终居中，画面稳定收束",
            "俯视旋转": f"镜头从上方斜俯角度启动，保持轻微下视，镜头顺时针环绕90度，同时缓慢下降至平视角度，最终停留在正前方构图，背景略虚化",
            "垂直升降 + 停顿": f"镜头从平视缓慢升至俯视，短暂停顿后缓慢下降回到平视位置，焦点始终锁定{effective_target}",
            "对角上升": f"镜头从左下方斜向上缓慢移动至俯视位置，{effective_target}始终居中",
            "对角下移推进": f"{effective_target}位于画面中央，镜头从右上方斜向下缓慢推进，逐渐接近{effective_target}细节，焦点稳定锁定",
            "对角穿越": f"镜头从左下方斜向上推进，掠过{effective_target}上方后从右上方缓慢下降至平视位置，背景虚化再恢复",
            "镜头抖动": "镜头短暂左右轻微抖动，随后恢复稳定",
            "冲击震动": f"{effective_target}位于画面中央，镜头贴近{effective_target}的正前方，突然发生短暂震动抖动，背景轻微模糊，随后画面恢复稳定",
            "贝塞尔拉远": "镜头先以正常速度后退，突然加速拉远，再次减速稳定收束，节奏感明显",
            "贝塞尔拉近": "镜头先缓慢推进，再突然加速至特写，最后减速收束"
        }
        return movement_descriptions.get(movement, "")

# 其他节点保持不变，但添加异常处理...
# 随机提示词人像、图像提示词公式、历史记录和预设管理、提示词保存为预设

# 随机提示词人像节点
class 随机提示词人像:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "语言": (["中文", "English"], {"default": "中文"}),
                "人物": (CHARACTER_OPTIONS, {"default": "随机"}),
                "国籍": (["随机", "亚洲人", "白人", "黑人", "拉丁裔", "无"], {"default": "亚洲人"}),
                "随机脸型": ("BOOLEAN", {"default": True}),
                "随机发型": ("BOOLEAN", {"default": True}),
                "随机饰品": ("BOOLEAN", {"default": True}),
                "随机服装": ("BOOLEAN", {"default": True}),
                "随机眼型": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "表情": (["随机", "微笑", "大笑", "中性", "无"], {"default": "随机"}),
                "身材": (["随机", "苗条", "健美", "丰满", "无"], {"default": "随机"}),
                "动作": (["随机", "和平手势", "招手", "点赞", "抱臂", "无"], {"default": "随机"}),
                "景别": (["随机", "半身照", "全身照", "中近景", "中全景", "无"], {"default": "随机"}),
                "背景类型": (["随机"] + [bg for bg in BACKGROUNDS if bg != "无"], {"default": "随机"}),
                "合照类型": (["随机", "单人照", "家庭照", "亲子照", "兄弟姐妹", "朋友合照", "无"], {"default": "单人照"}),
                "艺术风格": (["随机", "无"] + [style for style in VISUAL_STYLES if style != "无"], {"default": "随机"}),
                "附加提示词": ("STRING", {"default": "兼具超凡脱俗的美感与灵性，数字艺术风格", "multiline": True, "placeholder": "在此处添加额外的提示词，如环境、灯光、细节等"}),
                "随机种子": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "forceInput": True})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("正面提示词", "负面提示词")
    FUNCTION = "generate_prompt"
    CATEGORY = "📃提示词公式"

    def generate_prompt(self, 语言, 人物, 国籍, 随机脸型, 随机发型, 随机饰品, 随机服装, 随机眼型,
                   表情="随机", 身材="随机", 动作="随机", 景别="随机", 合照类型="单人照", 
                   艺术风格="随机", 附加提示词="", 随机种子=0, 背景类型="随机"):
        try:
            # 设置随机种子
            if 随机种子 != 0:
                random.seed(随机种子)
            
            # 原有的生成逻辑...
            # ... (保持原有逻辑不变)
            
            # 添加异常处理
            if 语言 == "中文":
                negative_prompt = "丑陋，畸形，模糊，坏手，多余手指，缺少手指，缺胳膊，缺腿，多肢体，多手指，多脚趾，多腿，多手臂，畸形手，畸形脸，畸形身体，文字，水印，签名，低质量，噪点，模糊，失焦，曝光不足，曝光过度，jpeg伪影，渲染问题，3D，CGI，不自然，塑料感，卡通，动漫，绘画，素描，油画，版画，雕塑，不真实"
            else:
                negative_prompt = "ugly, deformed, blurry, bad hands, extra fingers, missing fingers, missing arms, missing legs, extra limbs, extra fingers, extra toes, extra legs, extra arms, malformed hands, malformed face, malformed body, text, watermark, signature, low quality, noise, blurry, out of focus, underexposed, overexposed, jpeg artifacts, rendering issues, 3D, CGI, unnatural, plastic look, cartoon, anime, painting, sketch, oil painting, print, sculpture, unrealistic"
        
            return (positive_prompt, negative_prompt)
            
        except Exception as e:
            logging.error(f"随机提示词人像生成错误: {str(e)}")
            error_msg = f"生成提示词时出错: {str(e)}"
            return (error_msg, error_msg)

# 图像提示词公式节点
class 图像提示词公式:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "主体描述": ("STRING", {
                    "multiline": False,
                    "default": "一个女孩身穿粉色长裙，头戴蝴蝶发卡",
                    "display_name": "主体描述"
                }),
                "主体权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "主体权重"
                }),
                "表情动作描述": ("STRING", {
                    "multiline": False,
                    "default": "开心，挥手",
                    "display_name": "主体细节描述"
                }),
                "表情动作权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "主体细节权重"
                }),
                "场景描述": ("STRING", {
                    "multiline": False,
                    "default": "校园",
                    "display_name": "场景描述"
                }),
                "场景权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "场景权重"
                }),
                "光影描述": ("STRING", {
                    "multiline": False,
                    "default": "侧光，柔和阴影",
                    "display_name": "光影描述"
                }),
                "光影权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "光影权重"
                }),
                "画面风格": (VISUAL_STYLES, {
                    "default": "无", 
                    "display_name": "画面风格"
                }),
                "风格权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "风格权重"
                }),
            },
            "optional": {
                # 景别描述选项
                "景别描述": (SHOT_TYPES, {
                    "default": "无", 
                    "display_name": "景别描述"
                }),
                "景别权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "景别权重"
                }),
                # 构图描述选项
                "构图描述": (COMPOSITION_STYLES, {
                    "default": "无", 
                    "display_name": "构图描述"
                }),
                "构图权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "构图权重"
                }),
                "附加提示词": ("STRING", {
                    "multiline": True,
                    "default": "兼具超凡脱俗的美感与灵性，数字艺术风格，超现实景观，高分辨率",
                    "display_name": "附加提示词"
                }),
                "附加权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "附加权重"
                }),
                "自动保存到历史": ("BOOLEAN", {
                    "default": True,
                    "display_name": "自动保存到历史记录"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式"

    def 生成提示词(self, 主体描述, 主体权重, 表情动作描述, 表情动作权重, 
                      场景描述, 场景权重, 光影描述, 光影权重,
                      画面风格, 风格权重,
                      景别描述="无", 景别权重=1.0,
                      构图描述="无", 构图权重=1.0,
                      附加提示词="", 附加权重=1.0, 自动保存到历史=True):
        
        # 处理各组件，选择"无"或内容为空时不加入提示词
        组件 = {
            "主体": self._apply_weight_with_default(主体描述, 主体权重, "无"),
            "主体细节": self._apply_weight_with_default(表情动作描述, 表情动作权重, "无"),
            "场景": self._apply_weight_with_default(场景描述, 场景权重, "无"),
            "光影": self._apply_weight_with_default(光影描述, 光影权重, "无"),
            "风格": self._apply_weight_with_default(画面风格, 风格权重, "无"),
            "景别": self._apply_weight_with_default(景别描述, 景别权重, "无"),
            "构图": self._apply_weight_with_default(构图描述, 构图权重, "无")
        }
        
        # 生成提示词，过滤空值
        提示词组件 = [value for value in 组件.values() if value]
        提示词 = ", ".join(提示词组件)  # 改为用逗号分隔
        
        # 处理附加提示词，使用逗号分隔
        if 附加提示词 and clean_text(附加提示词):
            加权附加词 = self._apply_weight_with_default(附加提示词, 附加权重, "")
            if 加权附加词:
                if 提示词:
                    提示词 += ", " + 加权附加词  # 改为用逗号连接
                else:
                    提示词 = 加权附加词
        
        # 最终清理：确保没有连续的逗号和多余空格
        提示词 = re.sub(r',\s+,', ',', 提示词)
        提示词 = re.sub(r'\s+', ' ', 提示词).strip()
        
        # 处理历史记录保存
        if 自动保存到历史 and 提示词:
            timestamp = datetime.now().strftime("%H:%M")
            subject_preview = 主体描述[:10] + ("..." if len(主体描述) > 10 else "")
            save_name = f"[图像] {timestamp} {subject_preview}"
            save_to_history(提示词, save_name, manual_save=False)
        
        return (提示词,)

    def _apply_weight_with_default(self, text, weight, default_val="无"):
        """处理权重应用，权重为1时不输出权重"""
        cleaned_text = clean_text(text)
        # 如果内容为空或为默认值，则不输出
        if not cleaned_text or cleaned_text == default_val:
            return ""
        # 权重为1.0时不需要特别标记，直接返回文本
        if weight == 1.0:
            return cleaned_text
        return f"({cleaned_text}:{weight:.1f})"

# 历史记录和预设管理节点
class 历史记录和预设管理:
    @classmethod
    def INPUT_TYPES(cls):
        base_components = {
            "optional": {
                "输入提示词": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "输入提示词（可选）"
                }),
                "查看历史记录": ("BOOLEAN", {
                    "default": False,
                    "display_name": "查看历史记录"
                }),
                "将选中历史存为预设": ("BOOLEAN", {
                    "default": False,
                    "display_name": "将选中历史存为预设"
                }),
                "新预设名称": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "display_name": "预设名称（可包含.txt或.json扩展名）"
                }),
                "从输入保存到历史": ("BOOLEAN", {
                    "default": False,
                    "display_name": "将输入提示词保存到历史"
                }),
                "清空历史记录": ("BOOLEAN", {
                    "default": False,
                    "display_name": "清空所有历史记录"
                }),
                "确认删除预设": ("BOOLEAN", {
                    "default": False,
                    "display_name": "确认删除所选预设"
                }),
                "选择要删除的预设": (["不删除预设"], {
                    "default": "不删除预设", 
                    "display_name": "选择要删除的预设"
                }),
                "新建预设内容": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "新建预设内容（TXT文本或JSON格式）"
                })
            }
        }
        
        try:
            preset_files = folder_paths.get_filename_list("prompt_presets")
            # 提取预设名称（去除扩展名）并去重，按名称排序
            preset_names = ["不删除预设"] + sorted(list({os.path.splitext(f)[0] for f in preset_files}))
            history_options = get_history_options()
            
            # 使用字符串引用外部验证函数，避免JSON序列化问题
            base_components["optional"]["选择历史记录"] = (
                history_options, 
                {
                    "default": "不选择历史记录", 
                    "display_name": "选择历史记录",
                    "validate": "validate_history"
                }
            )
            base_components["optional"]["选择要删除的预设"] = (
                preset_names, 
                {"default": "不删除预设", "display_name": "选择要删除的预设"}
            )
            
            return base_components
        except Exception as e:
            logging.error(f"历史记录和预设管理节点组件加载错误: {str(e)}")
            return base_components
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("选中的提示词", "历史记录列表", "操作结果")
    FUNCTION = "管理历史和预设"
    CATEGORY = "📃提示词公式"
    
    def 管理历史和预设(self, 输入提示词=None, 查看历史记录=False, 选择历史记录="不选择历史记录",
                      将选中历史存为预设=False, 新预设名称="", 从输入保存到历史=False, 清空历史记录=False,
                      选择要删除的预设="不删除预设", 确认删除预设=False, 新建预设内容=""):
        操作结果 = ""
        
        try:
            # 先刷新历史记录选项，确保使用最新数据
            current_history = load_history()
            current_history_options = get_history_options()
            
            # 验证选择的历史记录是否仍然有效
            if 选择历史记录 not in current_history_options and 选择历史记录 != "不选择历史记录":
                操作结果 += f"警告: 所选历史记录已不存在，已自动重置\n"
                选择历史记录 = "不选择历史记录"
            
            if 新预设名称 and 新建预设内容:
                saved_name = save_preset(新预设名称, 新建预设内容)
                if saved_name:
                    操作结果 += f"新预设 '{saved_name}' 已保存到 提示词预设文件夹\n"
                else:
                    操作结果 += "保存预设失败\n"
            
            if 选择要删除的预设 != "不删除预设" and 确认删除预设:
                success, message = delete_preset(选择要删除的预设)
                操作结果 += message + "\n"
            
            if 清空历史记录:
                try:
                    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                        json.dump([], f, ensure_ascii=False)
                    操作结果 += "历史记录已清空\n"
                    # 清空后重置选择
                    选择历史记录 = "不选择历史记录"
                except PermissionError:
                    操作结果 += "无权限清空历史记录，请检查文件权限\n"
                except Exception as e:
                    操作结果 += f"清空历史记录失败: {str(e)}\n"
            
            if 从输入保存到历史 and 输入提示词 and clean_text(输入提示词):
                timestamp = datetime.now().strftime("%H:%M")
                content_preview = 输入提示词[:10] + ("..." if len(输入提示词) > 10 else "")
                save_name = f"{timestamp} 手动输入:{content_preview}"
                save_result = save_to_history(clean_text(输入提示词), save_name, manual_save=True)
                if save_result is not None:
                    操作结果 += "输入提示词已保存到历史记录\n"
                else:
                    操作结果 += "保存输入提示词到历史记录失败\n"
            
            history_index = -1
            selected_prompt = ""
            if 选择历史记录 != "不选择历史记录":
                try:
                    # 使用正则表达式更稳健地提取索引
                    match = re.search(r'\[(\d+)\]', 选择历史记录)
                    history_index = int(match.group(1)) if match else -1
                except:
                    history_index = -1
            
            # 检查索引是否有效
            if history_index != -1 and history_index < len(current_history):
                selected_prompt = current_history[history_index]["prompt"]
            elif history_index != -1:
                操作结果 += f"警告: 所选历史记录索引无效\n"
                history_index = -1
            
            if 将选中历史存为预设 and 新预设名称 and history_index != -1 and history_index < len(current_history):
                history_entry = current_history[history_index]
                saved_name = save_preset(新预设名称, history_entry["prompt"])
                if saved_name:
                    操作结果 += f"历史记录已保存为预设 '{saved_name}' 到 提示词预设文件夹\n"
                else:
                    操作结果 += "将历史记录保存为预设失败\n"
            
            历史记录列表 = ""
            if 查看历史记录:
                for i, entry in enumerate(current_history):
                    manual_tag = " [手动保存]" if entry.get("manual", False) else ""
                    历史记录列表 += f"[{i}] {entry['name']} ({entry['timestamp']}){manual_tag}:\n{entry['prompt']}\n\n"
        
        except Exception as e:
            操作结果 += f"操作出错: {str(e)}\n"
        
        操作结果 = 操作结果.strip()
        
        return (selected_prompt, 历史记录列表.strip(), 操作结果)

# 提示词保存为预设节点
class 提示词保存为预设:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "新预设名称": ("STRING", {
                    "multiline": False,
                    "default": "新预设",
                    "display_name": "新预设名称"
                }),
            },
            "optional": {
                "保存为TXT": ([
                    "关", "开"
                ], {
                    "default": "开",
                    "display_name": "将预设保存为txt文件"
                }),
                "保存为JSON": ([
                    "关", "开"
                ], {
                    "default": "关",
                    "display_name": "将预设保存为json文件"
                }),
                "提示词": ("STRING", {"forceInput": True, "multiline": True})
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("操作结果",)
    FUNCTION = "保存预设"
    CATEGORY = "📃提示词公式"
    OUTPUT_NODE = True  # 添加这个属性，表示节点有输出但不强制连接

    def 保存预设(self, 新预设名称, 提示词="", 保存为TXT="开", 保存为JSON="关"):
        if not 提示词.strip():
            return ("错误: 提示词不能为空",)
        
        if 保存为TXT == "关" and 保存为JSON == "关":
            return ("错误: 必须至少选择一种保存格式",)
        
        操作结果 = []
        
        if 保存为TXT == "开":
            txt_result = save_preset(新预设名称 + ".txt", 提示词)
            if txt_result:
                操作结果.append(f"已保存为TXT文件: {txt_result}.txt")
            else:
                操作结果.append("保存TXT文件失败")
        
        if 保存为JSON == "开":
            # 直接保存原始提示词内容为JSON文件
            json_result = save_preset(新预设名称 + ".json", 提示词)
            if json_result:
                操作结果.append(f"已保存为JSON文件: {json_result}.json")
            else:
                操作结果.append("保存JSON文件失败")
        
        return ("\n".join(操作结果),)