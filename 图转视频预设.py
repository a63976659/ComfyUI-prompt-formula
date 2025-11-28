# 图转视频预设.py
import re
import logging
from 常量配置 import *
from 工具函数 import clean_text  # 添加这行导入

class 视频首尾帧转场:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "首帧描述": ("STRING", {
                    "multiline": False,  # 改为单行输入
                    "default": "一朵含苞待放的荷花，清晨露珠挂在花瓣上",
                    "display_name": "首帧描述"
                }),
                "尾帧描述": ("STRING", {
                    "multiline": False,  # 改为单行输入
                    "default": "绽放的荷花特写，花瓣完全展开露出花蕊",
                    "display_name": "尾帧描述"
                }),
                "主要转场方式": (TRANSITION_TYPES, {
                    "default": "运镜提示词转场",
                    "display_name": "主要转场方式"
                }),
                "转场时长": ("FLOAT", {
                    "default": 3.0, 
                    "min": 1.0, 
                    "max": 10.0, 
                    "step": 0.1,  # 步进改为0.1
                    "display": "slider",
                    "display_name": "转场时长(秒)"
                }),
                "运动平滑度": (TRANSITION_SMOOTHNESS, {
                    "default": "平滑",
                    "display_name": "运动平滑度"
                }),
            },
            "optional": {
                # 运动转场专用参数
                "运动子类型": (MOTION_TRANSITION_SUBTYPES, {
                    "default": "缩放转场",
                    "display_name": "运动子类型"
                }),
                "运动方向": (MOTION_DIRECTIONS, {
                    "default": "向前",
                    "display_name": "运动方向"
                }),
                
                # 变形转场专用参数
                "变形子类型": (MORPH_TRANSITION_SUBTYPES, {
                    "default": "有机变形",
                    "display_name": "变形子类型"
                }),
                
                # 遮挡物转场专用参数
                "遮挡物类型": (OCCLUSION_TYPES, {
                    "default": "云雾遮挡",
                    "display_name": "遮挡物类型"
                }),
                
                # 新增：首帧主体和尾帧主体描述
                "首帧主体": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "display_name": "首帧主体"
                }),
                "尾帧主体": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "display_name": "尾帧主体"
                }),
                
                # 通用可选参数
                "转场节奏": (TRANSITION_RHYTHMS, {
                    "default": "缓入缓出",
                    "display_name": "转场节奏"
                }),
                "视觉连贯性": (VISUAL_CONSISTENCY, {
                    "default": "风格统一",
                    "display_name": "视觉连贯性"
                }),
                "附加转场描述": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "附加转场描述"
                }),
                # 已取消"运镜提示词"输入组件
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("转场提示词", "完整提示词", "技术说明")
    FUNCTION = "生成转场提示词"
    CATEGORY = "📕提示词公式/图转视频"

    def 生成转场提示词(self, 首帧描述, 尾帧描述, 主要转场方式, 转场时长, 运动平滑度,
                    运动子类型="缩放转场", 运动方向="向前", 变形子类型="有机变形",
                    遮挡物类型="云雾遮挡", 首帧主体="", 尾帧主体="",
                    转场节奏="缓入缓出", 视觉连贯性="风格统一", 附加转场描述=""):
        
        try:
            # 清理输入文本
            首帧描述_清理 = clean_text(首帧描述)
            尾帧描述_清理 = clean_text(尾帧描述)
            附加描述_清理 = clean_text(附加转场描述)
            首帧主体_清理 = clean_text(首帧主体)
            尾帧主体_清理 = clean_text(尾帧主体)
            
            # 自动提取主体（如果用户没有手动输入）
            if not 首帧主体_清理 and 首帧描述_清理:
                首帧主体_清理 = self._extract_main_subject(首帧描述_清理)
            if not 尾帧主体_清理 and 尾帧描述_清理:
                尾帧主体_清理 = self._extract_main_subject(尾帧描述_清理)
            
            # 确保主体不为空
            首帧主体_清理 = 首帧主体_清理 or "图像1主体"
            尾帧主体_清理 = 尾帧主体_清理 or "图像2主体"
            
            # 根据转场方式生成对应的提示词
            转场提示词 = self._generate_transition_prompt(
                主要转场方式, 运动子类型, 运动方向, 变形子类型, 遮挡物类型,
                转场时长, 运动平滑度, 转场节奏, 视觉连贯性,
                首帧主体_清理, 尾帧主体_清理
            )
            
            # 生成完整提示词
            完整提示词 = self._generate_full_prompt(
                首帧描述_清理, 尾帧描述_清理, 转场提示词, 附加描述_清理
            )
            
            # 生成技术说明
            技术说明 = self._generate_technical_note(
                主要转场方式, 转场时长, 运动平滑度, 转场节奏,
                首帧主体_清理, 尾帧主体_清理
            )
            
            return (转场提示词, 完整提示词, 技术说明)
            
        except Exception as e:
            logging.error(f"视频首尾帧转场生成错误: {str(e)}")
            error_msg = f"生成转场提示词时出错: {str(e)}"
            return (error_msg, error_msg, error_msg)

    def _extract_main_subject(self, description):
        """从描述中自动提取主要主体 - 优化版本"""
        if not description:
            return "主体"
        
        # 移除标点符号
        cleaned_desc = re.sub(r'[，。！？；,\.!?;]', ' ', description)
        
        # 尝试多种提取模式，按优先级排序
        patterns = [
            # 模式1: 量词 + 形容词 + 名词 (如: "一朵含苞待放的荷花")
            r'(?:一个|一朵|一只|一座|一件|一张|一台)([\u4e00-\u9fa5]{2,10}?(?:的)?[\u4e00-\u9fa5]{2,10})',
            # 模式2: 直接的名词短语 (如: "绽放的荷花特写")
            r'([\u4e00-\u9fa5]{2,6}的[\u4e00-\u9fa5]{2,10})',
            # 模式3: 形容词 + 名词 (如: "美丽的花朵")
            r'([\u4e00-\u9fa5]{2,6}[\u4e00-\u9fa5]{2,8})',
            # 模式4: 单独的名词 (至少2个字符)
            r'([\u4e00-\u9fa5]{2,10})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, cleaned_desc)
            if matches:
                # 选择第一个匹配且长度适中的结果
                for match in matches:
                    subject = match.strip()
                    if 2 <= len(subject) <= 12:  # 限制长度范围
                        # 进一步清理，去除可能的修饰词
                        subject = self._refine_subject(subject)
                        if subject:
                            return subject
        
        # 如果所有模式都失败，返回描述的前几个词
        words = cleaned_desc.split()
        if words:
            # 取前2-3个词作为主体
            candidate = ' '.join(words[:min(3, len(words))])
            if len(candidate) <= 15:
                return candidate
        
        return "主体"

    def _refine_subject(self, subject):
        """进一步精炼提取的主体"""
        # 去除常见的修饰前缀
        modifiers = ['美丽的', '漂亮的', '可爱的', '大大的', '小小的', '一朵', '一个', '一只']
        for modifier in modifiers:
            if subject.startswith(modifier):
                subject = subject[len(modifier):]
                break
        
        # 去除常见的修饰后缀
        modifiers_suffix = ['特写', '镜头', '画面', '图像', '照片']
        for modifier in modifiers_suffix:
            if subject.endswith(modifier):
                subject = subject[:-len(modifier)]
                break
        
        return subject.strip()

    def _generate_transition_prompt(self, 主要方式, 运动子类型, 运动方向, 变形子类型, 
                                  遮挡物类型, 时长, 平滑度, 节奏, 连贯性,
                                  首帧主体, 尾帧主体):
        """生成具体的转场提示词"""
        
        # 如果主要转场方式为"无"，直接返回空字符串
        if 主要方式 == "无":
            return ""
        
        # 安全获取描述映射
        平滑度描述 = TRANSITION_SMOOTHNESS_DESCRIPTIONS.get(平滑度, "平滑自然")
        节奏描述 = TRANSITION_RHYTHM_DESCRIPTIONS.get(节奏, "缓入缓出")
        
        # 格式化时长，保留一位小数
        时长格式化 = f"{时长:.1f}"
        
        # 根据主要转场方式生成对应的提示词
        if 主要方式 == "运镜提示词转场":
            return self._generate_motion_transition(运动子类型, 运动方向, 时长格式化, 平滑度描述, 节奏描述)
            
        elif 主要方式 == "交叉溶解转场":
            return f"通过柔和的交叉溶解效果自然转场，溶解时长约{时长格式化}秒，{平滑度描述}，{节奏描述}"
            
        elif 主要方式 == "运动匹配转场":
            方向描述 = f"向{运动方向}" if 运动方向 and 运动方向 != "无" else ""
            运动描述 = 运动子类型 if 运动子类型 and 运动子类型 != "无" else "镜头运动"
            return f"保持{运动描述}{方向描述}的连贯性，{节奏描述}无缝衔接，{平滑度描述}"
            
        elif 主要方式 == "形态变形转场":
            return self._generate_morph_transition(变形子类型, 时长格式化, 平滑度描述)
            
        elif 主要方式 == "遮挡物转场":
            return self._generate_occlusion_transition(遮挡物类型, 时长格式化, 节奏描述)
            
        elif 主要方式 == "主体变形转场":
            return self._generate_subject_morph_transition(首帧主体, 尾帧主体, 时长格式化, 平滑度描述, 节奏描述)
            
        elif 主要方式 == "画面渐变转场":
            return self._generate_scene_transition(首帧主体, 尾帧主体, 时长格式化, 平滑度描述, 节奏描述)
            
        elif 主要方式 == "主体遮挡转场":
            return self._generate_subject_occlusion_transition(首帧主体, 尾帧主体, 时长格式化, 节奏描述)
            
        elif 主要方式 == "多重转场组合":
            return self._generate_multi_transition(运动子类型, 变形子类型, 时长格式化, 平滑度描述, 节奏描述)
        
        else:
            return ""

    def _generate_motion_transition(self, 子类型, 方向, 时长, 平滑度, 节奏):
        """生成运动转场提示词"""
        if not 子类型 or 子类型 == "无":
            return f"镜头运动转场，历时{时长}秒，{平滑度}，{节奏}"
            
        方向描述 = f"向{方向}" if 方向 and 方向 != "无" else ""
        
        运动描述 = {
            "缩放转场": f"镜头缓慢{方向描述}缩放，历时{时长}秒，{平滑度}，{节奏}",
            "平移转场": f"镜头{方向描述}平移运动，历时{时长}秒，{平滑度}，{节奏}",
            "旋转转场": f"镜头{方向描述}旋转，历时{时长}秒，{平滑度}，{节奏}",
            "弧线运动": f"镜头沿弧线轨迹{方向描述}运动，历时{时长}秒，{平滑度}，{节奏}",
            "复合运动": f"镜头结合缩放和平移的复合运动{方向描述}，历时{时长}秒，{平滑度}，{节奏}"
        }
        
        return 运动描述.get(子类型, f"镜头运动转场，历时{时长}秒，{平滑度}，{节奏}")

    def _generate_morph_transition(self, 子类型, 时长, 平滑度):
        """生成形态变形转场提示词"""
        if not 子类型 or 子类型 == "无":
            return f"形态变形转场，历时{时长}秒，变形过程{平滑度}"
        
        变形描述 = {
            "有机变形": f"通过流畅的有机形态变形过程转场，历时{时长}秒，变形过程{平滑度}",
            "几何变形": f"通过几何形状的平滑变形转场，历时{时长}秒，变形过程{平滑度}",
            "粒子变形": f"通过粒子解构与重组的方式变形转场，历时{时长}秒，{平滑度}",
            "流体变形": f"通过流体动力学般的变形转场，历时{时长}秒，{平滑度}",
            "抽象变形": f"通过抽象艺术形态的创造性变形转场，历时{时长}秒，{平滑度}"
        }
        
        return 变形描述.get(子类型, f"形态变形转场，历时{时长}秒，{平滑度}")

    def _generate_occlusion_transition(self, 遮挡类型, 时长, 节奏):
        """生成遮挡物转场提示词"""
        if not 遮挡类型 or 遮挡类型 == "无":
            return f"遮挡物转场，历时{时长}秒，{节奏}"
        
        # 安全获取遮挡描述
        遮挡描述 = OCCLUSION_DESCRIPTIONS.get(遮挡类型, f"遮挡物转场，历时{时长}秒，{节奏}")
        return 遮挡描述.replace("{时长}", str(时长)).replace("{节奏}", 节奏)

    def _generate_subject_morph_transition(self, 首帧主体, 尾帧主体, 时长, 平滑度, 节奏):
        """生成主体变形转场提示词"""
        return f"{首帧主体}通过流畅的形态变形过程逐渐演变为{尾帧主体}，历时{时长}秒，变形过程{平滑度}，{节奏}"

    def _generate_scene_transition(self, 首帧主体, 尾帧主体, 时长, 平滑度, 节奏):
        """生成画面渐变转场提示词"""
        return f"从{首帧主体}通过自然的渐变效果转场到{尾帧主体}，历时{时长}秒，转场过程{平滑度}，{节奏}"

    def _generate_subject_occlusion_transition(self, 首帧主体, 尾帧主体, 时长, 节奏):
        """生成主体遮挡转场提示词"""
        return f"利用{首帧主体}移动到镜头前完全遮挡画面的瞬间切换到{尾帧主体}，历时{时长}秒，{节奏}"

    def _generate_multi_transition(self, 运动子类型, 变形子类型, 时长, 平滑度, 节奏):
        """生成多重转场组合提示词"""
        运动部分 = "镜头运动" if not 运动子类型 or 运动子类型 == "无" else 运动子类型
        变形部分 = "形态变形" if not 变形子类型 or 变形子类型 == "无" else 变形子类型
        return f"首先通过{运动部分}开始变化，中途结合{变形部分}强化效果，历时{时长}秒，{平滑度}，{节奏}，整个过程流畅如一体"

    def _generate_full_prompt(self, 首帧, 尾帧, 转场, 附加描述):
        """生成完整提示词"""
        组件 = []
        
        if 首帧:
            组件.append(首帧)
        
        # 处理转场提示词
        if 转场:
            组件.append(转场)
        
        if 尾帧:
            组件.append(尾帧)
        
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

    def _generate_technical_note(self, 主要方式, 时长, 平滑度, 节奏, 首帧主体, 尾帧主体):
        """生成技术说明"""
        技术要点 = []
        
        if 主要方式 and 主要方式 != "无":
            # 格式化时长，保留一位小数
            时长格式化 = f"{时长:.1f}"
            技术要点.append(f"转场时长: {时长格式化}秒")
            技术要点.append(f"运动质量: {平滑度}")
            技术要点.append(f"节奏控制: {节奏}")
        
        # 新增主体信息
        if 首帧主体 and 首帧主体 != "图像1主体":
            技术要点.append(f"首帧主体: {首帧主体}")
        if 尾帧主体 and 尾帧主体 != "图像2主体":
            技术要点.append(f"尾帧主体: {尾帧主体}")
        
        if 主要方式 in ["运镜提示词转场", "运动匹配转场"]:
            技术要点.append("建议使用一致的摄像机运动参数")
        
        if 主要方式 == "交叉溶解转场":
            技术要点.append("确保首尾帧色彩和光照风格一致")
        
        if 主要方式 == "形态变形转场":
            技术要点.append("需要相似的主体形状以获得最佳效果")
        
        if 主要方式 in ["主体变形转场", "主体遮挡转场"]:
            技术要点.append("需要清晰的主体定义")
        
        return " | ".join(技术要点) if 技术要点 else "无特殊技术要求"


class 视频运镜提示词:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "运镜方式": (CAMERA_MOVEMENTS, {
                    "default": "推近镜头",
                    "display_name": "运镜方式"
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
                    "max": 10.0, 
                    "step": 0.1,  # 步进也改为0.1以保持一致
                    "display": "slider",
                    "display_name": "运镜时长(秒)"
                }),
            },
            "optional": {
                "附加运镜描述": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "附加运镜描述"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("运镜提示词", "技术说明")
    FUNCTION = "生成运镜提示词"
    CATEGORY = "📕提示词公式/图转视频"

    def 生成运镜提示词(self, 运镜方式, 镜头目标, 运镜速度, 运镜时长, 附加运镜描述=""):
        
        try:
            # 清理输入文本
            镜头目标_清理 = clean_text(镜头目标) or "主体"
            附加描述_清理 = clean_text(附加运镜描述)
            
            # 格式化时长，保留一位小数
            运镜时长格式化 = f"{运镜时长:.1f}"
            
            # 生成运镜提示词
            运镜提示词 = self._generate_camera_movement_prompt(
                运镜方式, 镜头目标_清理, 运镜速度, 运镜时长格式化
            )
            
            # 添加附加描述
            if 附加描述_清理:
                运镜提示词 = f"{运镜提示词}，{附加描述_清理}"
            
            # 生成技术说明
            技术说明 = self._generate_technical_note(
                运镜方式, 运镜速度, 运镜时长格式化
            )
            
            return (运镜提示词, 技术说明)
            
        except Exception as e:
            logging.error(f"视频运镜提示词生成错误: {str(e)}")
            error_msg = f"生成运镜提示词时出错: {str(e)}"
            return (error_msg, error_msg)

    def _generate_camera_movement_prompt(self, 运镜方式, 镜头目标, 速度, 时长):
        """生成运镜提示词"""
        if not 运镜方式 or 运镜方式 == "无":
            return ""
            
        # 获取基础运镜描述
        movement_desc = CAMERA_MOVEMENT_DESCRIPTIONS.get(运镜方式, "")
        if not movement_desc:
            return f"{运镜方式}，历时{时长}秒"
        
        # 替换目标占位符
        movement_desc = movement_desc.replace("{target}", 镜头目标)
        
        # 添加速度和时长信息
        速度描述 = self._get_speed_description(速度)
        
        return f"{movement_desc}，{速度描述}，历时{时长}秒"

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

    def _generate_technical_note(self, 运镜方式, 运镜速度, 运镜时长):
        """生成技术说明"""
        技术要点 = []
        
        if 运镜方式 and 运镜方式 != "无":
            技术要点.append(f"运镜方式: {运镜方式}")
            技术要点.append(f"运镜速度: {运镜速度}")
            技术要点.append(f"运镜时长: {运镜时长}秒")
        
        # 根据运镜方式提供特定建议
        if 运镜方式 in ["推近镜头", "拉远镜头", "快速推近", "快速拉远"]:
            技术要点.append("注意焦点平滑转移")
        
        if 运镜方式 in ["水平环绕", "原地旋转", "俯视旋转"]:
            技术要点.append("保持主体在画面中心")
        
        if 运镜方式 in ["镜头抖动", "冲击震动"]:
            技术要点.append("控制抖动幅度避免过度")
        
        return " | ".join(技术要点) if 技术要点 else "无特殊技术要求"