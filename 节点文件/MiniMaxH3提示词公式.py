# 新增节点文件：MiniMaxH3提示词公式.py
# MiniMax H3 通用全模态视频模型提示词公式节点
# 提示词结构：【参考素材说明】【核心创意】【画面过程描述】【整体要求补充】

import re
from 常量配置 import *
from 工具函数 import clean_text


def _获取H3运镜描述(运镜方式):
    """获取运镜方式的自然语言描述（复用现有运镜描述映射）"""
    if not 运镜方式 or 运镜方式 == "无":
        return ""

    运镜描述 = CAMERA_MOVEMENT_DESCRIPTIONS.get(运镜方式, "")
    if not 运镜描述:
        return 运镜方式

    # 替换目标占位符
    if "{target}" in 运镜描述:
        运镜描述 = 运镜描述.replace("{target}", "主体")

    return 运镜描述


def _获取影像风格文本(影像风格):
    """获取影像风格选项的专业描述文本"""
    if not 影像风格 or 影像风格 == "无":
        return ""
    return H3_IMAGE_STYLE_DESCRIPTIONS.get(影像风格, 影像风格)


def _组合整体要求(段落列表):
    """组合【整体要求补充】段落，段落列表为 (标题, 内容) 元组"""
    组件 = []
    for 标题, 内容 in 段落列表:
        内容 = clean_text(内容)
        if 内容:
            组件.append(f"▍{标题}\n{内容}")

    if not 组件:
        return ""

    return "【整体要求补充】\n" + "\n".join(组件)


def _清理换行(文本):
    """清理多余的连续空行和句读拼接瑕疵"""
    文本 = re.sub(r'\n\s*\n\s*\n', '\n\n', 文本)
    # 修正描述末尾标点与后续片段的拼接（如 "。，" → "。"）
    文本 = re.sub(r'([。．！？!?])\s*([，,])', r'\1', 文本)
    return 文本.strip()


# H3 背景音乐开关（官方手册：不要BGM时需显式声明，留空声音设计≠无BGM）
H3_BGM_OPTIONS = ["按声音设计描述", "不需要背景音乐"]
H3_BGM_NONE_TEXT = "非叙事性音乐：N/A，不要额外添加背景音乐。"


def _组装素材行(素材类型, 序号, 用途, 描述):
    """按官方格式组装素材行 '@图片N：用途——描述'，用途与描述均为空时返回 None"""
    描述_清理 = clean_text(描述)
    if 用途 and 用途 != "无":
        if 描述_清理:
            return f"@{素材类型}{序号}：{用途}——{描述_清理}"
        return f"@{素材类型}{序号}：{用途}"
    if 描述_清理:
        return f"@{素材类型}{序号}：{描述_清理}"
    return None


def _附加字数检查(技术说明, H3提示词):
    """提示词超过7000字符上限时，在技术说明中附加警告"""
    字数 = len(H3提示词)
    if 字数 > 7000:
        技术说明 += f" | ⚠️ 当前提示词{字数}字符，已超过7000字符上限，请精简内容"
    return 技术说明


class H3文生视频公式:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "视频时长": ("INT", {
                    "default": 5,
                    "min": 4,
                    "max": 15,
                    "step": 1,
                    "display": "slider",
                    "display_name": "视频时长(秒)"
                }),
                "核心创意": ("STRING", {
                    "multiline": True,
                    "default": "一支电影感短片。主角独自走在雨夜的街道上，霓虹灯在湿漉漉的地面上反射出斑驳光影。",
                    "display_name": "核心创意"
                }),
                "画面过程描述": ("STRING", {
                    "multiline": True,
                    "default": "0~3秒- 正向：镜头从雨滴落在水洼的特写开始，缓慢上摇至主角的背影，脚步踏过积水。- 反向：不要平稳广告式构图。\n3~5秒- 正向：主角回头望向镜头，霓虹灯光掠过面部，画面在余韵中结束。- 反向：不要切镜到别的场景。",
                    "display_name": "画面过程描述"
                }),
            },
            "optional": {
                "影像风格": (H3_IMAGE_STYLES, {
                    "default": "无",
                    "display_name": "影像风格"
                }),
                "声音设计": ("STRING", {
                    "multiline": True,
                    "default": "低沉电子乐，808 bass鼓点，雨声、脚步声",
                    "display_name": "声音设计"
                }),
                "背景音乐": (H3_BGM_OPTIONS, {
                    "default": "按声音设计描述",
                    "display_name": "背景音乐"
                }),
                "附加要求": ("STRING", {
                    "multiline": True,
                    "default": "只用硬切，保持色调全片一致",
                    "display_name": "附加要求"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("H3提示词", "技术说明")
    FUNCTION = "生成H3文生视频提示词"
    CATEGORY = "📕提示词公式/MiniMax H3"
    DESCRIPTION = ("MiniMax H3 纯文生视频提示词公式。可用于 MiniMax API 节点（模型名 MiniMax-H3），提示词不超过7000字符，视频生成为异步任务。\n"
                   "【画面过程描述】纯文字生成时描述要更具体：主体外观+场景细节+动作+风格；"
                   "推荐分层写法'大全景交代空间+中景承载动作+特写强调细节'；"
                   "画面中出现的文字/Logo/字幕必须写出原文（如'画面中出现英文：\"H3\"'）；少写比喻句，多写看得见的画面。\n"
                   "【声音设计】H3输出自带原生立体声，音乐/音效/人声统一在此描述："
                   "背景音乐（如'低沉电子乐，808 bass鼓点'）、环境音效（如'雨声、脚步声、木门吱呀声'）、"
                   "人物台词与音色（如'男主沙哑低声说：……'，TTS支持中英日韩法德西等11种语言）、"
                   "音画同步要求（如'随bass hit鼓点硬切'）。留空则不生成该段落。\n"
                   "【背景音乐】留空声音设计≠无BGM，H3默认会生成声音；明确不要背景音乐时选'不需要背景音乐'，"
                   "会自动写入官方推荐格式'非叙事性音乐：N/A'。\n"
                   "【附加要求】全局约束与补充指令：转场与节奏（如'只用硬切，不用淡入淡出'）、"
                   "禁止元素（如'不要切镜到别的场景、不要恐怖元素'）、一致性（如'保持人物与色调全片一致'）、"
                   "文字包装（如'文字不遮挡眼睛，每镜头只1个主文字'）。留空则不生成该段落。")

    def 生成H3文生视频提示词(self, 视频时长, 核心创意, 画面过程描述,
                         影像风格="无", 声音设计="", 背景音乐="按声音设计描述", 附加要求=""):
        try:
            # 清理输入文本
            核心创意_清理 = clean_text(核心创意)
            画面过程描述_清理 = clean_text(画面过程描述)
            时长格式化 = f"{视频时长:.0f}"

            组件 = []

            # 1. 参考素材说明（纯文生）
            组件.append("【参考素材说明】无参考素材（纯文字生成视频）。")

            # 2. 核心创意
            组件.append(f"【核心创意】{时长格式化}秒视频。{核心创意_清理}")

            # 3. 画面过程描述
            if 画面过程描述_清理:
                组件.append(f"【画面过程描述】{画面过程描述_清理}")

            # 4. 整体要求补充
            影像风格文本 = _获取影像风格文本(影像风格)
            整体要求 = _组合整体要求([
                ("影像风格（贯穿全片）", 影像风格文本),
                ("声音设计", 声音设计),
                ("背景音乐", H3_BGM_NONE_TEXT if 背景音乐 == "不需要背景音乐" else ""),
                ("附加要求", 附加要求)
            ])
            if 整体要求:
                组件.append(整体要求)

            H3提示词 = _清理换行("\n".join(组件))

            # 生成技术说明
            技术说明 = (f"模式: 文生视频 | 时长: {时长格式化}秒 | "
                       f"格式: 【参考素材说明】【核心创意】【画面过程描述】【整体要求补充】 | "
                       f"提示词上限7000字符 | 输出24FPS带原生双声道")
            技术说明 = _附加字数检查(技术说明, H3提示词)

            return (H3提示词, 技术说明)

        except Exception as e:
            import logging
            logging.error(f"H3文生视频生成错误: {str(e)}")
            error_msg = f"生成H3提示词时出错: {str(e)}"
            return (error_msg, error_msg)


class H3首尾帧公式:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "视频时长": ("INT", {
                    "default": 5,
                    "min": 4,
                    "max": 15,
                    "step": 1,
                    "display": "slider",
                    "display_name": "视频时长(秒)"
                }),
                "首帧画面描述": ("STRING", {
                    "multiline": True,
                    "default": "小女孩站在花田边，低头看着手中的蒲公英。",
                    "display_name": "首帧画面描述"
                }),
                "尾帧画面描述": ("STRING", {
                    "multiline": True,
                    "default": "小女孩已长大成人，站在同一片花田边，微笑着望向天空。",
                    "display_name": "尾帧画面描述"
                }),
                "演变过程描述": ("STRING", {
                    "multiline": True,
                    "default": "小女孩轻轻吹散蒲公英，种子随风飘远，画面随季节流转，她的身形逐渐长高，服饰与发型自然变化，最终成长为大人。",
                    "display_name": "演变过程描述"
                }),
            },
            "optional": {
                "运镜方式": (CAMERA_MOVEMENTS, {
                    "default": "无",
                    "display_name": "运镜方式"
                }),
                "声音设计": ("STRING", {
                    "multiline": True,
                    "default": "轻柔钢琴曲，风声、鸟鸣",
                    "display_name": "声音设计"
                }),
                "背景音乐": (H3_BGM_OPTIONS, {
                    "default": "按声音设计描述",
                    "display_name": "背景音乐"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("H3提示词", "技术说明")
    FUNCTION = "生成H3首尾帧提示词"
    CATEGORY = "📕提示词公式/MiniMax H3"
    DESCRIPTION = ("MiniMax H3 首帧/尾帧图生视频提示词公式。实际图片请在 MiniMax API 节点中分别以 first_frame / last_frame 传入（0~2张）。\n"
                   "首尾帧模式下 H3 不会自动加切镜，只补两帧之间的动作、光影、声音；输入图片宽高比需在5:2~2:5范围内。\n"
                   "【运镜方式】环绕运镜建议写'truck left+pan right'或'truck right+pan left'，不要直接写'环绕运镜'。\n"
                   "【声音设计】H3输出自带原生立体声，音乐/音效/人声统一在此描述："
                   "背景音乐（如'轻柔钢琴曲，缓慢节奏'）、环境音效（如'风声、鸟鸣、衣料摩擦声'）、"
                   "人物台词与音色（如'女主轻声说：……'，TTS支持中英日韩法德西等11种语言）。留空则不生成该段落。\n"
                   "【背景音乐】留空声音设计≠无BGM，H3默认会生成声音；明确不要背景音乐时选'不需要背景音乐'，"
                   "会自动写入官方推荐格式'非叙事性音乐：N/A'。")

    def 生成H3首尾帧提示词(self, 视频时长, 首帧画面描述, 尾帧画面描述, 演变过程描述,
                        运镜方式="无", 声音设计="", 背景音乐="按声音设计描述"):
        try:
            # 清理输入文本
            首帧_清理 = clean_text(首帧画面描述)
            尾帧_清理 = clean_text(尾帧画面描述)
            演变_清理 = clean_text(演变过程描述)
            时长格式化 = f"{视频时长:.0f}"

            组件 = []

            # 1. 核心创意
            组件.append(f"【核心创意】{时长格式化}秒视频。根据首帧图与尾帧图，生成从首帧到尾帧的完整演变过程。")

            # 2. 参考画面说明
            参考画面 = []
            if 首帧_清理:
                参考画面.append(f"- 首帧：{首帧_清理}")
            if 尾帧_清理:
                参考画面.append(f"- 尾帧：{尾帧_清理}")
            if 参考画面:
                组件.append("【参考画面说明】\n" + "\n".join(参考画面))

            # 3. 画面过程描述
            画面组件 = []
            if 演变_清理:
                画面组件.append(演变_清理)

            # 运镜描述
            运镜描述 = _获取H3运镜描述(运镜方式)
            if 运镜描述:
                画面组件.append(f"运镜：{运镜描述}")

            if 画面组件:
                组件.append("【画面过程描述】" + "\n".join(画面组件))

            # 4. 整体要求补充
            整体要求 = _组合整体要求([
                ("一致性要求", "保持首帧与尾帧的主体、场景、色调与输入图片一致，演变过程自然连贯"),
                ("声音设计", 声音设计),
                ("背景音乐", H3_BGM_NONE_TEXT if 背景音乐 == "不需要背景音乐" else "")
            ])
            if 整体要求:
                组件.append(整体要求)

            H3提示词 = _清理换行("\n".join(组件))

            # 生成技术说明
            图片数 = (1 if 首帧_清理 else 0) + (1 if 尾帧_清理 else 0)
            技术说明 = (f"模式: 首尾帧图生视频 | 时长: {时长格式化}秒 | 描述图片数: {图片数}张 | "
                       f"宽高比自动跟随输入图片原始比例（图片宽高比须为5:2~2:5） | "
                       f"API中图片以 first_frame / last_frame 传入，图片0~2张，宽高范围[256,5760] | "
                       f"提示词上限7000字符")
            技术说明 = _附加字数检查(技术说明, H3提示词)

            return (H3提示词, 技术说明)

        except Exception as e:
            import logging
            logging.error(f"H3首尾帧生成错误: {str(e)}")
            error_msg = f"生成H3提示词时出错: {str(e)}"
            return (error_msg, error_msg)


class H3图生视频公式:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "视频时长": ("INT", {
                    "default": 5,
                    "min": 4,
                    "max": 15,
                    "step": 1,
                    "display": "slider",
                    "display_name": "视频时长(秒)"
                }),
                "源图像描述": ("STRING", {
                    "multiline": True,
                    "default": "侠客站在雨中，斗笠压低，望着远处的客栈。",
                    "display_name": "源图像描述"
                }),
                "动态剧情描述": ("STRING", {
                    "multiline": True,
                    "default": "侠客缓缓抬头，雨滴顺着斗笠边缘滑落，衣袍随风摆动，他向前迈出一步。",
                    "display_name": "动态剧情描述"
                }),
            },
            "optional": {
                "运镜方式": (CAMERA_MOVEMENTS, {
                    "default": "无",
                    "display_name": "运镜方式"
                }),
                "影像风格": (H3_IMAGE_STYLES, {
                    "default": "无",
                    "display_name": "影像风格"
                }),
                "声音设计": ("STRING", {
                    "multiline": True,
                    "default": "雨声、脚步声，低沉弦乐渐入",
                    "display_name": "声音设计"
                }),
                "背景音乐": (H3_BGM_OPTIONS, {
                    "default": "按声音设计描述",
                    "display_name": "背景音乐"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("H3提示词", "技术说明")
    FUNCTION = "生成H3图生视频提示词"
    CATEGORY = "📕提示词公式/MiniMax H3"
    DESCRIPTION = ("MiniMax H3 单图图生视频提示词公式。实际图片请在 MiniMax API 节点中以 first_frame 传入（1张），宽高比自动跟随输入图片原始比例。\n"
                   "【源图像描述】描述输入图片的内容（主体、场景、色调等），帮助H3锚定视频起始画面。\n"
                   "【动态剧情描述】从图片内容开始的动态变化、剧情发展与画面演变。\n"
                   "【运镜方式】环绕运镜建议写'truck left+pan right'或'truck right+pan left'，不要直接写'环绕运镜'。\n"
                   "【声音设计】H3输出自带原生立体声，音乐/音效/人声统一在此描述："
                   "背景音乐（如'低沉电子乐，808 bass鼓点'）、环境音效（如'雨声、脚步声'）、"
                   "人物台词与音色（如'男主沙哑低声说：……'，TTS支持中英日韩法德西等11种语言）。留空则不生成该段落。\n"
                   "【背景音乐】留空声音设计≠无BGM，H3默认会生成声音；明确不要背景音乐时选'不需要背景音乐'，"
                   "会自动写入官方推荐格式'非叙事性音乐：N/A'。")

    def 生成H3图生视频提示词(self, 视频时长, 源图像描述, 动态剧情描述,
                         运镜方式="无", 影像风格="无", 声音设计="", 背景音乐="按声音设计描述"):
        try:
            # 清理输入文本
            源图像_清理 = clean_text(源图像描述)
            动态_清理 = clean_text(动态剧情描述)
            时长格式化 = f"{视频时长:.0f}"

            组件 = []

            # 1. 核心创意
            组件.append(f"【核心创意】{时长格式化}秒图生视频。根据输入图片，生成从图片内容开始的动态与剧情发展。")

            # 2. 参考画面说明
            if 源图像_清理:
                组件.append(f"【参考画面说明】\n- 输入图片（first_frame）：{源图像_清理}")

            # 3. 画面过程描述
            画面组件 = []
            if 动态_清理:
                画面组件.append(动态_清理)

            # 运镜描述
            运镜描述 = _获取H3运镜描述(运镜方式)
            if 运镜描述:
                画面组件.append(f"运镜：{运镜描述}")

            if 画面组件:
                组件.append("【画面过程描述】" + "\n".join(画面组件))

            # 4. 整体要求补充
            影像风格文本 = _获取影像风格文本(影像风格)
            整体要求 = _组合整体要求([
                ("影像风格（贯穿全片）", 影像风格文本),
                ("一致性要求", "保持主体、场景、色调与输入图片一致，动态自然流畅"),
                ("声音设计", 声音设计),
                ("背景音乐", H3_BGM_NONE_TEXT if 背景音乐 == "不需要背景音乐" else "")
            ])
            if 整体要求:
                组件.append(整体要求)

            H3提示词 = _清理换行("\n".join(组件))

            # 生成技术说明
            技术说明 = (f"模式: 单图图生视频 | 时长: {时长格式化}秒 | "
                       f"宽高比自动跟随输入图片原始比例（图片宽高比须为5:2~2:5） | "
                       f"API中图片以 first_frame 传入，图片1张，宽高范围[256,5760] | "
                       f"提示词上限7000字符")
            技术说明 = _附加字数检查(技术说明, H3提示词)

            return (H3提示词, 技术说明)

        except Exception as e:
            import logging
            logging.error(f"H3图生视频生成错误: {str(e)}")
            error_msg = f"生成H3提示词时出错: {str(e)}"
            return (error_msg, error_msg)


class H3全能参考公式:
    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "视频时长": ("INT", {
                "default": 5,
                "min": 4,
                "max": 15,
                "step": 1,
                "display": "slider",
                "display_name": "视频时长(秒)"
            }),
            "图片数量": ("INT", {
                "default": 3,
                "min": 0,
                "max": 9,
                "step": 1,
                "display": "slider",
                "display_name": "图片数量"
            }),
            "视频数量": ("INT", {
                "default": 2,
                "min": 0,
                "max": 3,
                "step": 1,
                "display": "slider",
                "display_name": "视频数量"
            }),
            "音频数量": ("INT", {
                "default": 1,
                "min": 0,
                "max": 3,
                "step": 1,
                "display": "slider",
                "display_name": "音频数量"
            }),
            "核心创意": ("STRING", {
                "multiline": True,
                "default": "一支电影感短片。参考图中的人物在雨夜街道行走，镜头参考视频1的运镜节奏。",
                "display_name": "核心创意"
            }),
            "画面过程描述": ("STRING", {
                "multiline": True,
                "default": "0~3秒：人物从远处走来，霓虹灯光掠过面部。\n3~5秒：人物停在镜头前，回头望向远方。",
                "display_name": "画面过程描述"
            }),
        }

        # 参考素材槽位：用途声明 + 描述（数量与官方手册上限一致：图片≤9 视频≤3 音频≤3）
        optional = {}
        for 序号 in range(1, 10):
            optional[f"参考图{序号}用途"] = (H3_ASSET_USAGES, {
                "default": "无",
                "display_name": f"参考图{序号}用途"
            })
            optional[f"参考图{序号}描述"] = ("STRING", {
                "multiline": True,
                "default": "",
                "display_name": f"参考图{序号}描述"
            })
        for 序号 in range(1, 4):
            optional[f"参考视频{序号}用途"] = (H3_ASSET_USAGES, {
                "default": "无",
                "display_name": f"参考视频{序号}用途"
            })
            optional[f"参考视频{序号}描述"] = ("STRING", {
                "multiline": True,
                "default": "",
                "display_name": f"参考视频{序号}描述"
            })
        for 序号 in range(1, 4):
            optional[f"参考音频{序号}用途"] = (H3_ASSET_USAGES, {
                "default": "无",
                "display_name": f"参考音频{序号}用途"
            })
            optional[f"参考音频{序号}描述"] = ("STRING", {
                "multiline": True,
                "default": "",
                "display_name": f"参考音频{序号}描述"
            })

        optional["启用参考规则约束"] = ("BOOLEAN", {
            "default": True,
            "display_name": "启用参考规则约束"
        })
        optional["影像风格"] = (H3_IMAGE_STYLES, {
            "default": "无",
            "display_name": "影像风格"
        })
        optional["声音设计"] = ("STRING", {
            "multiline": True,
            "default": "trap鼓点，808 bass + hi-hat roll，街头环境音",
            "display_name": "声音设计"
        })
        optional["背景音乐"] = (H3_BGM_OPTIONS, {
            "default": "按声音设计描述",
            "display_name": "背景音乐"
        })

        return {"required": required, "optional": optional}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("H3提示词", "技术说明")
    FUNCTION = "生成H3全能参考提示词"
    CATEGORY = "📕提示词公式/MiniMax H3"
    DESCRIPTION = ("MiniMax H3 全能参考模式提示词公式。参考素材在 MiniMax API 节点中按顺序传入，编号与 @图片N/@视频N/@音频N 对应。\n"
                   "【素材用途】官方手册要求写清每个素材的用途：人物参考（锁脸）/物体参考/场景参考/关键帧/风格参考/构图参考/故事版/"
                   "动作参考/运镜参考/音色参考/音频复用等，选中后按官方格式输出'@图片N：用途——描述'。\n"
                   "【素材描述】写明素材的参考维度，如'人物形象（脸、发型、服装轮廓、气质）'。"
                   "音色克隆/音频复用时，若对歌词/对白内容保持要求较高，强烈建议在描述中写出具体歌词文本。\n"
                   "【数量滑块】图片数量/视频数量/音频数量仅控制组件显隐（上限图片9/视频3/音频3，混合总数≤12），实际使用的素材以填写了用途或描述的槽位为准。\n"
                   "【声音设计】H3输出自带原生立体声，音乐/音效/人声统一在此描述："
                   "背景音乐风格（如'trap鼓点，808 bass + hi-hat roll'）、环境音效（如'街头环境音、雨声'）、"
                   "人物台词与音色（可配合音频参考素材做音色克隆，如'歌声与音频1一致'，TTS支持11种语言）。留空则不生成该段落。\n"
                   "【背景音乐】留空声音设计≠无BGM，H3默认会生成声音；明确不要背景音乐时选'不需要背景音乐'，"
                   "会自动写入官方推荐格式'非叙事性音乐：N/A'。")

    def 生成H3全能参考提示词(self, 视频时长, 图片数量=3, 视频数量=2, 音频数量=1,
                          核心创意="", 画面过程描述="",
                          启用参考规则约束=True, 影像风格="无", 声音设计="",
                          背景音乐="按声音设计描述", **素材输入):
        try:
            # 清理输入文本
            核心创意_清理 = clean_text(核心创意)
            画面过程描述_清理 = clean_text(画面过程描述)
            时长格式化 = f"{视频时长:.0f}"

            # 1. 组装参考素材说明（@图片N / @视频N / @音频N，按数量滑块截取）
            素材行 = []
            图片数 = 0
            视频数 = 0
            音频数 = 0

            for 序号 in range(1, int(图片数量) + 1):
                行 = _组装素材行("图片", 序号,
                             素材输入.get(f"参考图{序号}用途", "无"),
                             素材输入.get(f"参考图{序号}描述", ""))
                if 行:
                    素材行.append(行)
                    图片数 += 1

            for 序号 in range(1, int(视频数量) + 1):
                行 = _组装素材行("视频", 序号,
                             素材输入.get(f"参考视频{序号}用途", "无"),
                             素材输入.get(f"参考视频{序号}描述", ""))
                if 行:
                    素材行.append(行)
                    视频数 += 1

            for 序号 in range(1, int(音频数量) + 1):
                行 = _组装素材行("音频", 序号,
                             素材输入.get(f"参考音频{序号}用途", "无"),
                             素材输入.get(f"参考音频{序号}描述", ""))
                if 行:
                    素材行.append(行)
                    音频数 += 1

            if 素材行:
                参考素材说明 = "【参考素材说明】" + " ".join(素材行)
                if 启用参考规则约束:
                    参考素材说明 += " " + H3_REFERENCE_RULES
            else:
                参考素材说明 = "【参考素材说明】无参考素材。"

            组件 = [参考素材说明]

            # 2. 核心创意
            组件.append(f"【核心创意】{时长格式化}秒视频。{核心创意_清理}")

            # 3. 画面过程描述
            if 画面过程描述_清理:
                组件.append(f"【画面过程描述】{画面过程描述_清理}")

            # 4. 整体要求补充
            影像风格文本 = _获取影像风格文本(影像风格)
            整体要求 = _组合整体要求([
                ("影像风格（贯穿全片）", 影像风格文本),
                ("声音设计", 声音设计),
                ("背景音乐", H3_BGM_NONE_TEXT if 背景音乐 == "不需要背景音乐" else "")
            ])
            if 整体要求:
                组件.append(整体要求)

            H3提示词 = _清理换行("\n".join(组件))

            # 生成技术说明
            技术说明 = (f"模式: 全能参考 | 时长: {时长格式化}秒 | "
                       f"参考素材: 图片{图片数}张 视频{视频数}段 音频{音频数}段 | "
                       f"上限: 图片≤9 视频≤3 音频≤3(需配图片/视频) 混合总数≤12 | "
                       f"视频单段2~15秒、总时长≤15秒 | 单文件限制: 视频50MB/图片30MB/音频15MB | "
                       f"素材编号需与API传入顺序一致 | 提示词上限7000字符")
            技术说明 = _附加字数检查(技术说明, H3提示词)

            return (H3提示词, 技术说明)

        except Exception as e:
            import logging
            logging.error(f"H3全能参考生成错误: {str(e)}")
            error_msg = f"生成H3提示词时出错: {str(e)}"
            return (error_msg, error_msg)


class H3音画多镜头公式:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "总体描述": ("STRING", {
                    "multiline": True,
                    "default": "古装武侠悬疑短剧场景，侠客在雨夜客栈中追查一桩悬案。",
                    "display_name": "总体描述"
                }),
                "镜头数量": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "display": "slider",
                    "display_name": "镜头数量"
                }),
                "视频总时长": ("INT", {
                    "default": 15,
                    "min": 4,
                    "max": 15,
                    "step": 1,
                    "display": "slider",
                    "display_name": "视频总时长(秒)"
                }),
            },
            "optional": {
                # 镜头1
                "镜头1开始时间": ("STRING", {"multiline": False, "default": "0秒", "display_name": "镜头1开始时间"}),
                "镜头1结束时间": ("STRING", {"multiline": False, "default": "5秒", "display_name": "镜头1结束时间"}),
                "镜头1景别": (H3_SHOT_TYPES, {"default": "近景", "display_name": "镜头1景别"}),
                "镜头1描述": ("STRING", {"multiline": True, "default": "侠客推门而入，雨水顺着斗笠滴落，目光扫过店内众人。", "display_name": "镜头1描述"}),
                "镜头1运镜方式": (CAMERA_MOVEMENTS, {"default": "无", "display_name": "镜头1运镜方式"}),
                "镜头1台词": ("STRING", {"multiline": True, "default": "", "display_name": "镜头1台词"}),
                "镜头1声音设计": ("STRING", {"multiline": True, "default": "雨声、鼓点骤起", "display_name": "镜头1声音设计"}),

                # 镜头2
                "镜头2开始时间": ("STRING", {"multiline": False, "default": "5秒", "display_name": "镜头2开始时间"}),
                "镜头2结束时间": ("STRING", {"multiline": False, "default": "10秒", "display_name": "镜头2结束时间"}),
                "镜头2景别": (H3_SHOT_TYPES, {"default": "特写", "display_name": "镜头2景别"}),
                "镜头2描述": ("STRING", {"multiline": True, "default": "侠客手部特写，缓缓按住腰间刀柄，指节微微收紧。", "display_name": "镜头2描述"}),
                "镜头2运镜方式": (CAMERA_MOVEMENTS, {"default": "推近镜头", "display_name": "镜头2运镜方式"}),
                "镜头2台词": ("STRING", {"multiline": True, "default": "", "display_name": "镜头2台词"}),
                "镜头2声音设计": ("STRING", {"multiline": True, "default": "雨声、鼓点骤起", "display_name": "镜头2声音设计"}),

                # 镜头3
                "镜头3开始时间": ("STRING", {"multiline": False, "default": "10秒", "display_name": "镜头3开始时间"}),
                "镜头3结束时间": ("STRING", {"multiline": False, "default": "15秒", "display_name": "镜头3结束时间"}),
                "镜头3景别": (H3_SHOT_TYPES, {"default": "中景", "display_name": "镜头3景别"}),
                "镜头3描述": ("STRING", {"multiline": True, "default": "角落中的黑衣人起身，烛光在两人之间摇晃，气氛紧绷。", "display_name": "镜头3描述"}),
                "镜头3运镜方式": (CAMERA_MOVEMENTS, {"default": "固定镜头", "display_name": "镜头3运镜方式"}),
                "镜头3台词": ("STRING", {"multiline": True, "default": "", "display_name": "镜头3台词"}),
                "镜头3声音设计": ("STRING", {"multiline": True, "default": "雨声、鼓点骤起", "display_name": "镜头3声音设计"}),

                # 镜头4
                "镜头4开始时间": ("STRING", {"multiline": False, "default": "", "display_name": "镜头4开始时间"}),
                "镜头4结束时间": ("STRING", {"multiline": False, "default": "", "display_name": "镜头4结束时间"}),
                "镜头4景别": (H3_SHOT_TYPES, {"default": "无", "display_name": "镜头4景别"}),
                "镜头4描述": ("STRING", {"multiline": True, "default": "", "display_name": "镜头4描述"}),
                "镜头4运镜方式": (CAMERA_MOVEMENTS, {"default": "无", "display_name": "镜头4运镜方式"}),
                "镜头4台词": ("STRING", {"multiline": True, "default": "", "display_name": "镜头4台词"}),
                "镜头4声音设计": ("STRING", {"multiline": True, "default": "雨声、鼓点骤起", "display_name": "镜头4声音设计"}),

                # 镜头5
                "镜头5开始时间": ("STRING", {"multiline": False, "default": "", "display_name": "镜头5开始时间"}),
                "镜头5结束时间": ("STRING", {"multiline": False, "default": "", "display_name": "镜头5结束时间"}),
                "镜头5景别": (H3_SHOT_TYPES, {"default": "无", "display_name": "镜头5景别"}),
                "镜头5描述": ("STRING", {"multiline": True, "default": "", "display_name": "镜头5描述"}),
                "镜头5运镜方式": (CAMERA_MOVEMENTS, {"default": "无", "display_name": "镜头5运镜方式"}),
                "镜头5台词": ("STRING", {"multiline": True, "default": "", "display_name": "镜头5台词"}),
                "镜头5声音设计": ("STRING", {"multiline": True, "default": "雨声、鼓点骤起", "display_name": "镜头5声音设计"}),

                # 通用参数
                "转场效果": (H3_TRANSITIONS, {"default": "硬切", "display_name": "转场效果"}),
                "影像风格": (H3_IMAGE_STYLES, {
                    "default": "无",
                    "display_name": "影像风格"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("多镜头提示词", "完整提示词", "镜头结构表")
    FUNCTION = "生成H3音画多镜头提示词"
    CATEGORY = "📕提示词公式/MiniMax H3"
    DESCRIPTION = ("MiniMax H3 音画多镜头提示词公式。利用H3原生多镜头建模与音画同步能力，每个镜头可单独设计声音。可用于 MiniMax API 节点（模型名 MiniMax-H3）。\n"
                   "【镜头N台词】台词必须写明具体内容，写法：'角色名：台词内容'或'画外音：台词内容'；"
                   "一句台词跨镜头时写'接着上个镜头继续说'。台词长短须与镜头时长匹配（不要3秒镜头配大段台词）；"
                   "画面内说话写清是哪个角色，画面外说话写'画外音'。留空则该镜头无台词。\n"
                   "【镜头N声音设计】每个镜头独立的声音设计，H3输出自带原生立体声，音乐/音效/人声统一描述："
                   "该镜头的背景音乐（如'低沉弦乐渐入'）、音效（如'雨声、木门吱呀声、鼓点骤起'）、"
                   "音色（可配合音频参考素材做音色克隆，TTS支持11种语言）、音画同步（如'随snare鼓点切换'）。留空则该镜头不生成声音行。\n"
                   "【镜头N运镜方式】环绕运镜建议写'truck left+pan right'或'truck right+pan left'，不要直接写'环绕运镜'。\n"
                   "【切镜一致性】切镜时写明切到什么景别、主体是之前的哪个角色，有助于跨镜头一致性保持。")

    def 生成H3音画多镜头提示词(self, 总体描述, 镜头数量, 视频总时长,
                            镜头1开始时间="0秒", 镜头1结束时间="5秒", 镜头1景别="近景",
                            镜头1描述="", 镜头1运镜方式="无", 镜头1台词="", 镜头1声音设计="",
                            镜头2开始时间="5秒", 镜头2结束时间="10秒", 镜头2景别="特写",
                            镜头2描述="", 镜头2运镜方式="无", 镜头2台词="", 镜头2声音设计="",
                            镜头3开始时间="10秒", 镜头3结束时间="15秒", 镜头3景别="中景",
                            镜头3描述="", 镜头3运镜方式="无", 镜头3台词="", 镜头3声音设计="",
                            镜头4开始时间="", 镜头4结束时间="", 镜头4景别="无",
                            镜头4描述="", 镜头4运镜方式="无", 镜头4台词="", 镜头4声音设计="",
                            镜头5开始时间="", 镜头5结束时间="", 镜头5景别="无",
                            镜头5描述="", 镜头5运镜方式="无", 镜头5台词="", 镜头5声音设计="",
                            转场效果="硬切", 影像风格="无"):
        try:
            # 清理输入文本
            总体描述_清理 = clean_text(总体描述)
            总时长格式化 = f"{视频总时长:.0f}"

            # 汇总镜头数据
            原始镜头数据 = [
                {"序号": 1, "开始": 镜头1开始时间, "结束": 镜头1结束时间, "景别": 镜头1景别,
                 "描述": 镜头1描述, "运镜": 镜头1运镜方式, "台词": 镜头1台词, "声音": 镜头1声音设计},
                {"序号": 2, "开始": 镜头2开始时间, "结束": 镜头2结束时间, "景别": 镜头2景别,
                 "描述": 镜头2描述, "运镜": 镜头2运镜方式, "台词": 镜头2台词, "声音": 镜头2声音设计},
                {"序号": 3, "开始": 镜头3开始时间, "结束": 镜头3结束时间, "景别": 镜头3景别,
                 "描述": 镜头3描述, "运镜": 镜头3运镜方式, "台词": 镜头3台词, "声音": 镜头3声音设计},
                {"序号": 4, "开始": 镜头4开始时间, "结束": 镜头4结束时间, "景别": 镜头4景别,
                 "描述": 镜头4描述, "运镜": 镜头4运镜方式, "台词": 镜头4台词, "声音": 镜头4声音设计},
                {"序号": 5, "开始": 镜头5开始时间, "结束": 镜头5结束时间, "景别": 镜头5景别,
                 "描述": 镜头5描述, "运镜": 镜头5运镜方式, "台词": 镜头5台词, "声音": 镜头5声音设计},
            ]

            # 清理每个镜头字段，取前 镜头数量 个且有描述的镜头
            镜头数据 = []
            for 镜头 in 原始镜头数据[:镜头数量]:
                描述_清理 = clean_text(镜头["描述"])
                if not 描述_清理:
                    continue
                镜头数据.append({
                    "序号": 镜头["序号"],
                    "开始": clean_text(镜头["开始"]),
                    "结束": clean_text(镜头["结束"]),
                    "景别": 镜头["景别"],
                    "描述": 描述_清理,
                    "运镜": 镜头["运镜"],
                    "台词": clean_text(镜头["台词"]),
                    "声音": clean_text(镜头["声音"])
                })

            # 生成镜头文本（Shot N [时间] — 景别：描述，运镜。声音：xxx）
            镜头文本列表 = []
            for 镜头 in 镜头数据:
                时间戳 = ""
                if 镜头["开始"] and 镜头["结束"]:
                    时间戳 = f" [{镜头['开始']}~{镜头['结束']}]"

                景别部分 = f"{镜头['景别']}：" if 镜头["景别"] and 镜头["景别"] != "无" else ""

                描述部分 = 镜头["描述"].rstrip("。．！？!?,，")
                运镜描述 = _获取H3运镜描述(镜头["运镜"])
                if 运镜描述:
                    描述部分 += f"，运镜：{运镜描述}"

                镜头行 = f"Shot {镜头['序号']}{时间戳} — {景别部分}{描述部分}。"

                if 镜头["台词"]:
                    镜头行 += f"\n- 台词：{镜头['台词']}"

                if 镜头["声音"]:
                    镜头行 += f"\n- 声音：{镜头['声音']}"

                镜头文本列表.append(镜头行)

            # 多镜头提示词
            多镜头组件 = []
            if 转场效果 and 转场效果 != "无" and len(镜头数据) > 1:
                多镜头组件.append(f"镜头间使用{转场效果}。")
            多镜头组件.extend(镜头文本列表)
            多镜头提示词 = "\n".join(多镜头组件)

            # 完整提示词（四段式结构）
            组件 = []

            # 核心创意
            组件.append(f"【核心创意】{总时长格式化}秒多镜头视频。{总体描述_清理}")

            # 画面过程描述
            组件.append(f"【画面过程描述】\n{多镜头提示词}")

            # 整体要求补充
            影像风格文本 = _获取影像风格文本(影像风格)
            整体要求 = _组合整体要求([
                ("影像风格（贯穿全片）", 影像风格文本),
                ("一致性要求", "保持画面主体、场景、氛围等关键信息的一致性，确保镜头间连贯叙事")
            ])
            if 整体要求:
                组件.append(整体要求)

            完整提示词 = _清理换行("\n".join(组件))

            # 生成镜头结构表
            镜头结构表 = self._生成镜头结构表(镜头数据, 转场效果)
            字数 = len(完整提示词)
            if 字数 > 7000:
                镜头结构表 += f"\n⚠️ 当前完整提示词{字数}字符，已超过7000字符上限，请精简内容"

            return (多镜头提示词, 完整提示词, 镜头结构表)

        except Exception as e:
            import logging
            logging.error(f"H3音画多镜头生成错误: {str(e)}")
            error_msg = f"生成H3多镜头提示词时出错: {str(e)}"
            return (error_msg, error_msg, error_msg)

    def _生成镜头结构表(self, 镜头数据, 转场效果):
        """生成镜头结构表，用于技术说明"""
        结构行 = []

        结构行.append("镜头结构表：")
        结构行.append("序号 | 时间范围 | 景别 | 内容概要 | 台词 | 声音设计")
        结构行.append("-" * 60)

        for 镜头 in 镜头数据:
            时间范围 = f"{镜头['开始']}~{镜头['结束']}" if 镜头["开始"] and 镜头["结束"] else "时间未定"
            景别 = 镜头["景别"] if 镜头["景别"] != "无" else "-"
            台词 = 镜头["台词"] if 镜头["台词"] else "-"
            声音 = 镜头["声音"] if 镜头["声音"] else "-"
            结构行.append(f"{镜头['序号']} | {时间范围} | {景别} | {镜头['描述']} | {台词} | {声音}")

        if 转场效果 and 转场效果 != "无":
            结构行.append(f"\n转场方式：{转场效果}")

        return "\n".join(结构行)


class H3视频编辑公式:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "源视频描述": ("STRING", {
                    "multiline": True,
                    "default": "一段雨夜街道的实拍视频，主角撑伞走过霓虹灯牌下。",
                    "display_name": "源视频描述"
                }),
                "编辑指令": ("STRING", {
                    "multiline": True,
                    "default": "1. 将主角的雨伞换成红色\n2. 删除画面左侧的路人\n3. 增加一只黑猫从画面右侧跑过",
                    "display_name": "编辑指令"
                }),
            },
            "optional": {
                "保持不变声明": ("STRING", {
                    "multiline": True,
                    "default": "镜头运动轨迹、人物动作时序、光照氛围保持100%不变",
                    "display_name": "保持不变声明"
                }),
                "声音设计": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "声音设计"
                }),
                "背景音乐": (H3_BGM_OPTIONS, {
                    "default": "按声音设计描述",
                    "display_name": "背景音乐"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("H3提示词", "技术说明")
    FUNCTION = "生成H3视频编辑提示词"
    CATEGORY = "📕提示词公式/MiniMax H3"
    DESCRIPTION = ("MiniMax H3 视频精准编辑提示词公式（全能精准编辑与修改）。源视频在 MiniMax API 节点中传入，编号对应 @视频1。\n"
                   "【源视频描述】描述输入视频的内容（主体、场景、动作、色调等），帮助H3理解编辑对象。\n"
                   "【编辑指令】逐条列举修改点（增/删/改），每条一行，如'1. 将雨伞换成红色'；"
                   "H3具备高精度指令遵循能力，写清楚改什么、改成什么，可多条并行。\n"
                   "【保持不变声明】明确未编辑内容保持稳定，如'镜头运动轨迹、人物动作时序、光照氛围保持100%不变'，"
                   "可多条一行；留空则不生成该段落。\n"
                   "【声音设计】若需同步修改声音（如换台词/音色）在此描述；留空则不生成该段落。\n"
                   "【背景音乐】留空声音设计≠无BGM，H3默认会生成声音；明确不要背景音乐时选'不需要背景音乐'，"
                   "会自动写入官方推荐格式'非叙事性音乐：N/A'。")

    def 生成H3视频编辑提示词(self, 源视频描述, 编辑指令,
                          保持不变声明="", 声音设计="", 背景音乐="按声音设计描述"):
        try:
            # 清理输入文本（编辑指令按行拆分后再逐行清理，避免换行被压平）
            源视频_清理 = clean_text(源视频描述)
            保持_清理 = clean_text(保持不变声明)

            组件 = []

            # 1. 参考素材说明（@视频1：视频编辑）
            if 源视频_清理:
                组件.append(f"【参考素材说明】@视频1：视频编辑（{源视频_清理}）")
            else:
                组件.append("【参考素材说明】@视频1：视频编辑")

            # 2. 编辑指令（逐条列举修改点，按行拆分后逐行清理）
            指令行 = []
            for 行 in 编辑指令.split("\n"):
                行 = clean_text(行)
                if not 行:
                    continue
                # 已带序号的行不重复编号
                if re.match(r'^\d+[\.、\)）]', 行):
                    指令行.append(行)
                else:
                    指令行.append(f"{len(指令行) + 1}. {行}")
            if 指令行:
                组件.append("【编辑指令】\n" + "\n".join(指令行))

            # 3. 保持不变声明（未编辑内容保持稳定）
            if 保持_清理:
                组件.append(f"【保持不变声明】{保持_清理}")

            # 4. 整体要求补充
            整体要求 = _组合整体要求([
                ("一致性要求", "除上述编辑指令外，源视频的其余画面内容保持完全一致，编辑痕迹自然无穿帮"),
                ("声音设计", 声音设计),
                ("背景音乐", H3_BGM_NONE_TEXT if 背景音乐 == "不需要背景音乐" else "")
            ])
            if 整体要求:
                组件.append(整体要求)

            H3提示词 = _清理换行("\n".join(组件))

            # 生成技术说明
            技术说明 = (f"模式: 视频精准编辑 | "
                       f"格式: 【参考素材说明】@视频1：视频编辑 + 【编辑指令】逐条列举 + 【保持不变声明】 | "
                       f"源视频以 API 参考视频传入（单段2~15秒，单文件≤50MB） | "
                       f"提示词上限7000字符")
            技术说明 = _附加字数检查(技术说明, H3提示词)

            return (H3提示词, 技术说明)

        except Exception as e:
            import logging
            logging.error(f"H3视频编辑生成错误: {str(e)}")
            error_msg = f"生成H3提示词时出错: {str(e)}"
            return (error_msg, error_msg)
