# Wan25提示词公式.py
import re
import logging
from 常量配置 import *

from 工具函数 import clean_text

class Wan25图生视频:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "画面描述": ("STRING", {
                    "multiline": True,
                    "default": "一个美丽的场景，有主体在其中",
                    "display_name": "画面描述"
                }),
                "场景动效": (ENVIRONMENT_DYNAMIC_EFFECTS, {
                    "default": "无",
                    "display_name": "场景动效"
                }),
                "主体动作": ("STRING", {
                    "multiline": False,
                    "default": "自然站立",
                    "display_name": "主体动作"
                }),
                "运镜方式": (CAMERA_MOVEMENTS, {
                    "default": "推近镜头",
                    "display_name": "运镜方式"
                }),
                "镜头目标": ("STRING", {
                    "multiline": False,
                    "default": "主体",
                    "display_name": "镜头目标"
                }),
                "声音描述": ("STRING", {
                    "multiline": True,
                    "default": "清晰的对话声",
                    "display_name": "声音描述（人声）"
                }),
                "是否添加音效": (["是", "否"], {
                    "default": "是",
                    "display_name": "是否添加音效"
                }),
                "背景音乐": (BACKGROUND_MUSIC_STYLES, {
                    "default": "无",
                    "display_name": "背景音乐"
                }),
                "视觉连贯性": (VISUAL_CONSISTENCY, {
                    "default": "风格统一",
                    "display_name": "视觉连贯性"
                }),
                "音效细节": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "display_name": "音效细节"
                }),
                "运镜速度": (["极慢速", "慢速", "中速", "快速", "极快速"], {
                    "default": "中速",
                    "display_name": "运镜速度"
                }),
                "运镜时长": ("FLOAT", {
                    "default": 3.0,
                    "min": 1.0,
                    "max": 15.0,
                    "step": 1.0,
                    "display": "slider",
                    "display_name": "运镜时长(秒)"
                }),
                "附加描述": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "display_name": "附加描述"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("视觉提示词", "声音提示词", "完整提示词")
    FUNCTION = "生成Wan25提示词"
    CATEGORY = "📕提示词公式/图转视频"
    DESCRIPTION = "可用于Wan2.5API节点"
    
    def 生成Wan25提示词(self, 画面描述, 场景动效, 主体动作, 运镜方式, 
                        镜头目标, 声音描述, 是否添加音效,
                        背景音乐="无", 视觉连贯性="风格统一", 运镜时长=3.0,
                        音效细节="", 运镜速度="中速", 附加描述=""):
        
        try:
            # 清理输入文本
            画面描述_清理 = clean_text(画面描述)
            主体动作_清理 = clean_text(主体动作)
            镜头目标_清理 = clean_text(镜头目标) or "主体"
            声音描述_清理 = clean_text(声音描述)
            附加描述_清理 = clean_text(附加描述)
            音效细节_清理 = clean_text(音效细节)
            
            视觉提示词 = self._generate_visual_prompt(
                画面描述_清理, 场景动效, 主体动作_清理, 运镜方式, 
                镜头目标_清理, 视觉连贯性, 附加描述_清理,
                运镜速度, 运镜时长
            )
            
            声音提示词 = self._generate_sound_prompt(
                声音描述_清理, 是否添加音效, 背景音乐, 音效细节_清理
            )
            
            完整提示词 = self._generate_full_prompt(
                视觉提示词, 声音提示词
            )
            
            return (视觉提示词, 声音提示词, 完整提示词)
            
        except Exception as e:
            logging.error(f"Wan25图生视频提示词生成错误: {str(e)}")
            error_msg = f"生成提示词时出错: {str(e)}"
            return (error_msg, error_msg, error_msg)
    
    def _generate_visual_prompt(self, 画面描述, 场景动效, 主体动作, 运镜方式,
                               镜头目标, 视觉连贯性, 附加描述,
                               运镜速度="中速", 运镜时长=3.0):
        """生成视觉提示词"""
        组件 = []
        
        if 画面描述:
            组件.append(画面描述)
        
        if 主体动作 and 主体动作 != "无":
            组件.append(f"主体{主体动作}")
        
        if 场景动效 and 场景动效 != "无":
            动效描述 = DYNAMIC_EFFECT_DESCRIPTIONS.get(场景动效, 场景动效)
            组件.append(动效描述)
        
        if 运镜方式 and 运镜方式 != "无":
            运镜提示词 = self._generate_camera_movement_prompt(
                运镜方式, 镜头目标, 运镜速度, 运镜时长
            )
            if 运镜提示词:
                组件.append(运镜提示词)
        
        if 视觉连贯性 and 视觉连贯性 != "无":
            连贯性描述 = VISUAL_CONSISTENCY_DESCRIPTIONS.get(视觉连贯性, "保持视觉连贯性")
            组件.append(连贯性描述)
        
        if 附加描述:
            组件.append(附加描述)
        
        # 如果所有组件都为空，返回空字符串
        if not 组件:
            return ""
        
        视觉提示词 = "，".join(组件)
        
        # 最终清理
        视觉提示词 = re.sub(r',\s+,', ',', 视觉提示词)
        视觉提示词 = re.sub(r'\s+', ' ', 视觉提示词).strip()
        
        return 视觉提示词
    
    def _generate_camera_movement_prompt(self, 运镜方式, 镜头目标, 运镜速度, 运镜时长):
        """生成运镜提示词（与其他节点保持一致）"""
        if not 运镜方式 or 运镜方式 == "无":
            return ""
            
        # 获取基础运镜描述
        movement_desc = CAMERA_MOVEMENT_DESCRIPTIONS.get(运镜方式, "")
        if not movement_desc:
            return f"{运镜方式}，历时{运镜时长:.1f}秒"
        
        # 替换目标占位符
        movement_desc = movement_desc.replace("{target}", 镜头目标)
        
        # 添加速度和时长信息
        速度描述 = self._get_speed_description(运镜速度)
        
        return f"{movement_desc}，{速度描述}，历时{运镜时长:.1f}秒"
    
    def _get_speed_description(self, 速度):
        """获取速度描述（与其他节点保持一致）"""
        速度描述映射 = {
            "极慢速": "极其缓慢平稳",
            "慢速": "缓慢平稳", 
            "中速": "速度适中",
            "快速": "快速流畅",
            "极快速": "极速迅猛"
        }
        return 速度描述映射.get(速度, "速度适中")
    
    def _generate_sound_prompt(self, 声音描述, 是否添加音效, 背景音乐, 音效细节=""):
        """生成声音提示词"""
        组件 = []
        
        if 声音描述:
            组件.append(声音描述)
        
        if 是否添加音效 == "是":
            if 音效细节:
                组件.append(f"音效：{音效细节}")
            else:
                组件.append("添加环境音效")
        
        if 背景音乐 and 背景音乐 != "无":
            音乐描述 = BACKGROUND_MUSIC_DESCRIPTIONS.get(背景音乐, 背景音乐)
            if 音乐描述:
                组件.append(音乐描述)
        
        # 如果所有组件都为空，返回空字符串
        if not 组件:
            return ""
        
        声音提示词 = "，".join(组件)
        
        # 最终清理
        声音提示词 = re.sub(r',\s+,', ',', 声音提示词)
        声音提示词 = re.sub(r'\s+', ' ', 声音提示词).strip()
        
        return 声音提示词
    
    def _generate_full_prompt(self, 视觉提示词, 声音提示词):
        """生成完整提示词（视觉+声音）"""
        组件 = []
        
        if 视觉提示词:
            组件.append(f"【视觉】{视觉提示词}")
        
        if 声音提示词:
            组件.append(f"【声音】{声音提示词}")
        
        if not 组件:
            return ""
        
        return " ".join(组件)