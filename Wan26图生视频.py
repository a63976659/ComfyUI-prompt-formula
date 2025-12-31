# 新增节点文件：Wan26图生视频.py

import re
from 常量配置 import *
from 工具函数 import clean_text

class Wan26图生视频:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "场景描述": ("STRING", {
                    "multiline": True,
                    "default": "这是一个充满童趣的童话场景。",
                    "display_name": "场景描述"
                }),
                "主角A引用名": ("STRING", {
                    "multiline": False,
                    "default": "A",
                    "display_name": "主角A引用名"
                }),
                "主角A动作": ("STRING", {
                    "multiline": True,
                    "default": "在草地上蹦跳着玩耍",
                    "display_name": "主角A动作"
                }),
                "主角B引用名": ("STRING", {
                    "multiline": False,
                    "default": "B",
                    "display_name": "主角B引用名"
                }),
                "主角B动作": ("STRING", {
                    "multiline": True,
                    "default": "在旁边的一颗苹果树下弹奏钢琴",
                    "display_name": "主角B动作"
                }),
                "运镜方式": (CAMERA_MOVEMENTS, {
                    "default": "无",
                    "display_name": "运镜方式"
                }),
                "主角A台词": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "主角A台词"
                }),
                "主角B台词": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "主角B台词"
                }),
                "其他元素动作": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "其他元素动作"
                }),
                "镜头目标": ("STRING", {
                    "multiline": False,
                    "default": "主体",
                    "display_name": "镜头目标"
                }),
                "运镜速度": (["极慢速", "慢速", "中速", "快速", "极快速"], {
                    "default": "中速",
                    "display_name": "运镜速度"
                }),
                "运镜时长": ("FLOAT", {
                    "default": 3.0,
                    "min": 1.0,
                    "max": 15.0,
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "运镜时长(秒)"
                }),
                "人物动态效果": (CHARACTER_DYNAMIC_EFFECTS, {
                    "default": "无",
                    "display_name": "人物动态效果"
                }),
                "环境动态效果": (ENVIRONMENT_DYNAMIC_EFFECTS, {
                    "default": "无",
                    "display_name": "环境动态效果"
                }),
                "附加描述": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "附加描述"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("Wan提示词", "完整提示词", "技术说明")
    FUNCTION = "生成Wan提示词"
    CATEGORY = "📕提示词公式/图转视频"

    def 生成Wan提示词(self, 场景描述, 主角A引用名, 主角A动作, 主角B引用名, 主角B动作, 运镜方式,
                    主角A台词="", 主角B台词="", 其他元素动作="", 镜头目标="主体",
                    运镜速度="中速", 运镜时长=3.0, 附加描述="",
                    人物动态效果="无", 环境动态效果="无"):
        
        try:
            # 清理所有输入文本
            场景描述_清理 = clean_text(场景描述)
            主角A引用名_清理 = clean_text(主角A引用名) or "A"
            主角A动作_清理 = clean_text(主角A动作)
            主角A台词_清理 = clean_text(主角A台词)
            主角B引用名_清理 = clean_text(主角B引用名) or "B"
            主角B动作_清理 = clean_text(主角B动作)
            主角B台词_清理 = clean_text(主角B台词)
            其他元素动作_清理 = clean_text(其他元素动作)
            镜头目标_清理 = clean_text(镜头目标) or "主体"
            附加描述_清理 = clean_text(附加描述)
            
            # 格式化运镜时长
            运镜时长格式化 = f"{运镜时长:.1f}"
            
            # 1. 生成Wan2.6格式提示词（结构化格式）
            Wan提示词 = self._生成Wan结构化提示词(
                场景描述_清理, 
                主角A引用名_清理, 主角A动作_清理, 主角A台词_清理,
                主角B引用名_清理, 主角B动作_清理, 主角B台词_清理,
                其他元素动作_清理
            )
            
            # 2. 生成运镜提示词（参考视频运镜提示词节点）
            运镜提示词 = self._生成运镜提示词(
                运镜方式, 镜头目标_清理, 运镜速度, 运镜时长格式化
            )
            
            # 3. 生成动态效果提示词
            动态效果提示词 = self._生成动态效果提示词(
                人物动态效果, 环境动态效果, 运镜时长
            )
            
            # 4. 组合完整提示词
            完整提示词 = self._组合完整提示词(
                Wan提示词, 运镜提示词, 动态效果提示词, 附加描述_清理
            )
            
            # 5. 生成技术说明
            技术说明 = self._生成技术说明(
                主角A引用名_清理, 主角B引用名_清理, 运镜方式, 运镜速度, 运镜时长格式化,
                人物动态效果, 环境动态效果
            )
            
            return (Wan提示词, 完整提示词, 技术说明)
            
        except Exception as e:
            import logging
            logging.error(f"Wan26图生视频生成错误: {str(e)}")
            error_msg = f"生成提示词时出错: {str(e)}"
            return (error_msg, error_msg, error_msg)

    def _生成Wan结构化提示词(self, 场景描述, 主角A引用, 主角A动作, 主角A台词, 
                           主角B引用, 主角B动作, 主角B台词, 其他元素动作):
        """生成符合Wan2.6格式的结构化提示词"""
        
        组件 = []
        
        # 1. 场景描述（必填）
        if 场景描述:
            # 确保场景描述以句号结束
            if not 场景描述.endswith(('。', '.', '!', '！', '?', '？')):
                场景描述 += '。'
            组件.append(场景描述)
        
        # 2. 主角A部分
        if 主角A引用 and 主角A引用.strip():
            主角A部分 = self._生成主角部分(主角A引用, 主角A动作, 主角A台词)
            if 主角A部分:
                组件.append(主角A部分)
        
        # 3. 其他元素动作（如果有）
        if 其他元素动作:
            组件.append(其他元素动作)
        
        # 4. 主角B部分
        if 主角B引用 and 主角B引用.strip():
            主角B部分 = self._生成主角部分(主角B引用, 主角B动作, 主角B台词)
            if 主角B部分:
                组件.append(主角B部分)
        
        # 组合所有组件
        if not 组件:
            return ""
        
        提示词 = "，".join(组件)
        
        # 清理多余的标点
        提示词 = re.sub(r'，。', '。', 提示词)
        提示词 = re.sub(r'\s+', ' ', 提示词).strip()
        
        return 提示词

    def _生成主角部分(self, 主角引用, 动作, 台词):
        """生成单个主角的部分：@主角 + 动作 + 台词"""
        部分 = []
        
        if 主角引用:
            # 确保主角引用以@开头
            if not 主角引用.startswith('@'):
                主角引用 = f"@{主角引用}"
            
            # 如果有动作，组合动作
            if 动作:
                部分.append(f"{主角引用} {动作}")
            else:
                部分.append(主角引用)
        
        # 添加台词（如果有）
        if 台词:
            # 处理台词格式
            台词 = 台词.strip()
            if 台词.startswith('"') and 台词.endswith('"'):
                # 已经是双引号格式
                台词文本 = 台词
            else:
                # 添加双引号
                台词文本 = f'"{台词}"'
            
            # 判断是否需要添加"说："
            if 动作 and any(关键字 in 动作 for 关键字 in ["说", "说道", "喊道", "喊道", "问"]):
                # 动作中已经包含说的动作
                部分.append(台词文本)
            else:
                部分.append(f"说：{台词文本}")
        
        return "，".join(部分) if 部分 else ""

    def _生成运镜提示词(self, 运镜方式, 镜头目标, 运镜速度, 运镜时长):
        """生成运镜提示词（参考视频运镜提示词节点）"""
        if not 运镜方式 or 运镜方式 == "无":
            return ""
        
        # 获取运镜描述
        运镜描述 = CAMERA_MOVEMENT_DESCRIPTIONS.get(运镜方式, 运镜方式)
        if not 运镜描述:
            return f"{运镜方式}，历时{运镜时长}秒"
        
        # 替换目标占位符
        if "{target}" in 运镜描述:
            运镜描述 = 运镜描述.replace("{target}", 镜头目标)
        
        # 添加速度描述
        速度描述映射 = {
            "极慢速": "极其缓慢平稳",
            "慢速": "缓慢平稳", 
            "中速": "速度适中",
            "快速": "快速流畅",
            "极快速": "极速迅猛"
        }
        速度描述 = 速度描述映射.get(运镜速度, "速度适中")
        
        return f"{运镜描述}，{速度描述}，历时{运镜时长}秒"

    def _生成动态效果提示词(self, 人物效果, 环境效果, 运镜时长):
        """生成动态效果提示词"""
        效果组件 = []
        
        # 人物动态效果
        if 人物效果 and 人物效果 != "无":
            人物描述 = DYNAMIC_EFFECT_DESCRIPTIONS.get(人物效果, 人物效果)
            if 人物描述:
                效果组件.append(人物描述)
        
        # 环境动态效果
        if 环境效果 and 环境效果 != "无":
            环境描述 = DYNAMIC_EFFECT_DESCRIPTIONS.get(环境效果, 环境效果)
            if 环境描述:
                效果组件.append(环境描述)
        
        if not 效果组件:
            return ""
        
        # 格式化时长
        时长格式化 = f"{运镜时长:.1f}"
        
        return f"同时，{''.join(效果组件)}，持续约{时长格式化}秒"

    def _组合完整提示词(self, Wan提示词, 运镜提示词, 动态效果提示词, 附加描述):
        """组合完整提示词"""
        组件 = []
        
        # 1. Wan结构化提示词
        if Wan提示词:
            组件.append(Wan提示词)
        
        # 2. 运镜提示词
        if 运镜提示词:
            组件.append(运镜提示词)
        
        # 3. 动态效果提示词
        if 动态效果提示词:
            组件.append(动态效果提示词)
        
        # 4. 附加描述
        if 附加描述:
            组件.append(附加描述)
        
        if not 组件:
            return ""
        
        完整提示词 = "，".join(组件)
        
        # 最终清理
        完整提示词 = re.sub(r'，\s+，', '，', 完整提示词)
        完整提示词 = re.sub(r'\s+', ' ', 完整提示词).strip()
        
        return 完整提示词

    def _生成技术说明(self, 主角A, 主角B, 运镜方式, 运镜速度, 运镜时长,
                    人物效果, 环境效果):
        """生成技术说明"""
        技术要点 = []
        
        # 主角信息
        if 主角A and 主角A != "A":
            技术要点.append(f"主角A: {主角A}")
        if 主角B and 主角B != "B":
            技术要点.append(f"主角B: {主角B}")
        
        # 运镜信息
        if 运镜方式 and 运镜方式 != "无":
            技术要点.append(f"运镜方式: {运镜方式}")
            技术要点.append(f"运镜速度: {运镜速度}")
            技术要点.append(f"运镜时长: {运镜时长}秒")
        
        # 动态效果信息
        if 人物效果 and 人物效果 != "无":
            技术要点.append(f"人物动态: {人物效果}")
        if 环境效果 and 环境效果 != "无":
            技术要点.append(f"环境动态: {环境效果}")
        
        # Wan2.6专用说明
        技术要点.append("格式: @主角 + 动作 + 台词 + 场景")
        技术要点.append("支持双主角合拍")
        
        return " | ".join(技术要点) if 技术要点 else "Wan2.6格式提示词已生成"