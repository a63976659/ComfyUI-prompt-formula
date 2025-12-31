# 视频动态带运镜.py
import re
import logging
from 常量配置 import *

from 工具函数 import clean_text

class 视频动态带运镜:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 基础描述组件
                "基础场景描述": ("STRING", {
                    "multiline": True,
                    "default": "一个美丽的场景，有主体在其中",
                    "display_name": "基础场景描述"
                }),
                # 动态效果核心组件
                "主体元素": ("STRING", {
                    "multiline": False,
                    "default": "人物",
                    "display_name": "主体元素"
                }),
                "动态类型": ([
                    "无", "人物动作", "动物行为", "物体运动", "自然现象", "特效动画"
                ], {
                    "default": "无",
                    "display_name": "动态类型"
                }),
                "具体动态": ("STRING", {
                    "multiline": False,
                    "default": "行走",
                    "display_name": "具体动态"
                }),
                "动态程度": ([
                    "轻微", "适中", "明显", "剧烈", "夸张"
                ], {
                    "default": "适中",
                    "display_name": "动态程度"
                }),
                "动态速度": ([
                    "极慢", "缓慢", "正常", "快速", "极快"
                ], {
                    "default": "正常",
                    "display_name": "动态速度"
                }),
                # 运镜组件
                "运镜方式": (CAMERA_MOVEMENTS, {
                    "default": "无",
                    "display_name": "运镜方式"
                }),
                # 新增：镜头目标组件
                "镜头目标": ("STRING", {
                    "multiline": False,
                    "default": "主体",
                    "display_name": "镜头目标"
                }),
            },
            "optional": {
                # 高级动态控制
                "多个主体": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "display_name": "多个主体（用逗号分隔）"
                }),
                # 保留：动态节奏
                "动态节奏": ([
                    "匀速", "缓入缓出", "先快后慢", "先慢后快", 
                    "弹性节奏", "脉冲式", "随机变化"
                ], {
                    "default": "匀速",
                    "display_name": "动态节奏"
                }),
                # 环境互动
                "与环境互动": ([
                    "无", "轻微互动", "中度互动", "强烈互动", "主导环境"
                ], {
                    "default": "无",
                    "display_name": "与环境互动"
                }),
                # 镜头高级参数
                "运镜速度": (["极慢速", "慢速", "中速", "快速", "极快速"], {
                    "default": "中速",
                    "display_name": "运镜速度"
                }),
                "运镜时长": ("FLOAT", {
                    "default": 3.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "运镜时长(秒)"
                }),
                # 新增：视觉连贯性组件
                "视觉连贯性": (VISUAL_CONSISTENCY, {
                    "default": "风格统一",
                    "display_name": "视觉连贯性"
                }),
                # 附加描述
                "附加动态描述": ("STRING", {
                    "multiline": False,  # 改为单行
                    "default": "",
                    "display_name": "附加描述"
                }),
                # 移除：技术参数说明组件
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("动态提示词", "运镜提示词", "完整提示词")
    FUNCTION = "生成动态运镜提示词"
    CATEGORY = "📕提示词公式/图转视频"
    
    def 生成动态运镜提示词(self, 基础场景描述, 主体元素, 动态类型, 具体动态, 
                         动态程度, 动态速度, 运镜方式, 镜头目标,
                         多个主体="", 动态节奏="匀速", 与环境互动="无", 
                         运镜速度="中速", 运镜时长=3.0, 视觉连贯性="风格统一",
                         附加动态描述=""):
        # 移除：技术参数说明参数
        
        try:
            # 清理输入文本
            基础描述_清理 = clean_text(基础场景描述)
            主体元素_清理 = clean_text(主体元素)
            具体动态_清理 = clean_text(具体动态)
            多个主体_清理 = clean_text(多个主体)
            附加描述_清理 = clean_text(附加动态描述)
            镜头目标_清理 = clean_text(镜头目标) or "主体"  # 默认值处理
            
            # 1. 生成动态描述提示词（移除动态方向参数）
            动态提示词 = self._generate_dynamic_description(
                主体元素_清理, 动态类型, 具体动态_清理, 
                动态程度, 动态速度, 多个主体_清理,
                动态节奏, 与环境互动  # 移除动态方向参数
            )
            
            # 2. 生成运镜提示词（使用镜头目标参数）
            运镜提示词 = self._generate_camera_movement_prompt(
                运镜方式, 镜头目标_清理, 运镜速度, 运镜时长
            )
            
            # 3. 获取视觉连贯性描述
            视觉连贯性描述 = ""
            if 视觉连贯性 and 视觉连贯性 != "无":
                视觉连贯性描述 = self._get_visual_consistency_description(视觉连贯性)
            
            # 4. 生成完整提示词（包含视觉连贯性）
            完整提示词 = self._generate_full_prompt(
                基础描述_清理, 动态提示词, 运镜提示词, 
                视觉连贯性描述, 附加描述_清理
            )
            
            return (动态提示词, 运镜提示词, 完整提示词)
            
        except Exception as e:
            logging.error(f"视频动态带运镜生成错误: {str(e)}")
            error_msg = f"生成提示词时出错: {str(e)}"
            return (error_msg, error_msg, error_msg)
    
    def _generate_dynamic_description(self, 主体, 动态类型, 具体动态, 
                                    程度, 速度, 多个主体="",
                                    节奏="匀速", 环境互动="无"):
        """生成动态描述提示词（移除动态方向相关代码）"""
        
        # 如果动态类型为"无"，返回空
        if 动态类型 == "无":
            return ""
        
        # 构建基础动态描述
        动态描述 = []
        
        # 处理主体（支持多个主体）
        if 多个主体:
            主体列表 = [主体_项.strip() for 主体_项 in 多个主体.split(",") if 主体_项.strip()]
            if 主体列表:
                主体文本 = "、".join(主体列表)
            else:
                主体文本 = 主体
        else:
            主体文本 = 主体
        
        # 1. 程度和速度修饰词
        程度映射 = {
            "轻微": "轻微地",
            "适中": "",  # 适中不添加修饰词
            "明显": "明显地",
            "剧烈": "剧烈地", 
            "夸张": "夸张地"
        }
        
        速度映射 = {
            "极慢": "极其缓慢地",
            "缓慢": "缓慢地",
            "正常": "",  # 正常速度不添加修饰词
            "快速": "快速地",
            "极快": "极速地"
        }
        
        程度词 = 程度映射.get(程度, "")
        速度词 = 速度映射.get(速度, "")
        
        # 2. 动态类型处理
        动态类型映射 = {
            "人物动作": "做出",
            "动物行为": "进行",
            "物体运动": "产生",
            "自然现象": "呈现",
            "特效动画": "展现"
        }
        
        动态动词 = 动态类型映射.get(动态类型, "进行")
        
        # 3. 节奏描述（保留）
        节奏映射 = {
            "匀速": "匀速",
            "缓入缓出": "缓入缓出",
            "先快后慢": "先快后慢",
            "先慢后快": "先慢后快", 
            "弹性节奏": "带有弹性节奏",
            "脉冲式": "脉冲式",
            "随机变化": "随机变化节奏"
        }
        
        节奏词 = 节奏映射.get(节奏, "")
        
        # 4. 环境互动描述
        互动映射 = {
            "轻微互动": "与环境轻微互动",
            "中度互动": "与环境自然互动", 
            "强烈互动": "与环境强烈互动",
            "主导环境": "主导环境变化"
        }
        
        互动词 = 互动映射.get(环境互动, "")
        
        # 构建动态描述句子
        句子组件 = []
        
        # 添加主体
        句子组件.append(主体文本)
        
        # 添加程度和速度修饰
        if 程度词 and 速度词:
            句子组件.append(f"{程度词}{速度词}{动态动词}{具体动态}")
        elif 程度词:
            句子组件.append(f"{程度词}{动态动词}{具体动态}")
        elif 速度词:
            句子组件.append(f"{速度词}{动态动词}{具体动态}")
        else:
            句子组件.append(f"{动态动词}{具体动态}")
        
        # 添加节奏（如果有）
        if 节奏词:
            句子组件.append(f"节奏{节奏词}")
        
        # 添加环境互动（如果有）
        if 互动词:
            句子组件.append(f"{互动词}")
        
        动态句子 = "".join(句子组件)
        
        # 清理多余的标点
        动态句子 = 动态句子.replace("，", "")
        
        return 动态句子
    
    def _generate_camera_movement_prompt(self, 运镜方式, 镜头目标, 运镜速度, 运镜时长):
        """生成运镜提示词（参考视频运镜提示词节点）"""
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
        """获取速度描述"""
        速度描述映射 = {
            "极慢速": "极其缓慢平稳",
            "慢速": "缓慢平稳", 
            "中速": "速度适中",
            "快速": "快速流畅",
            "极快速": "极速迅猛"
        }
        return 速度描述映射.get(速度, "速度适中")
    
    def _get_visual_consistency_description(self, 连贯性):
        """获取视觉连贯性描述（与视频首尾帧转场节点保持一致）"""
        # 使用常量配置中的描述映射
        return VISUAL_CONSISTENCY_DESCRIPTIONS.get(连贯性, "保持视觉连贯性")
    
    def _generate_full_prompt(self, 基础描述, 动态提示词, 运镜提示词, 
                             视觉连贯性描述="", 附加描述=""):
        """生成完整提示词（包含视觉连贯性）"""
        组件 = []
        
        # 1. 基础场景描述
        if 基础描述:
            组件.append(基础描述)
        
        # 2. 动态描述
        if 动态提示词:
            组件.append(动态提示词)
        
        # 3. 运镜描述
        if 运镜提示词:
            组件.append(运镜提示词)
            
            # 4. 视觉连贯性描述（如果有运镜描述且视觉连贯性不为空）
            if 视觉连贯性描述:
                组件.append(视觉连贯性描述)
        
        # 5. 附加描述
        if 附加描述:
            组件.append(附加描述)
        
        # 如果所有组件都为空，返回空字符串
        if not 组件:
            return ""
        
        完整提示词 = "，".join(组件)
        
        # 最终清理
        完整提示词 = re.sub(r',\s+,', ',', 完整提示词)
        完整提示词 = re.sub(r'\s+', ' ', 完整提示词).strip()
        
        return 完整提示词