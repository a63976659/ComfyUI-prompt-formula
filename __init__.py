# __init__.py
import os
import sys
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入常量配置
from 常量配置 import *

# 导入工具函数
from 工具函数 import (
    clean_text, apply_weight, load_presets, save_preset, 
    delete_preset, load_history, save_to_history, 
    get_history_options, validate_history,
    register_preset_folder, initialize_files
)

# 确保初始化
try:
    register_preset_folder()
    initialize_files()
except Exception as e:
    logging.warning(f"初始化失败: {str(e)}")

# 导入通用提示词公式节点
try:
    from 通用提示词公式 import (
        提示词预设,
        视频提示词公式,
        图像提示词公式,
        随机提示词人像,
        历史记录和预设管理,
        提示词保存为预设
    )
except Exception as e:
    logging.error(f"导入通用提示词公式节点失败: {str(e)}")
    # 创建空的占位符类
    class 节点占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING",)
        FUNCTION = "placeholder"
        CATEGORY = "📃提示词公式"
        def placeholder(self, **kwargs):
            return ("节点加载失败",)
    
    提示词预设 = 视频提示词公式 = 图像提示词公式 = 随机提示词人像 = 历史记录和预设管理 = 提示词保存为预设 = 节点占位符

# 导入千问提示词公式节点
try:
    from 千问提示词公式 import (
        LOGO生成,
        艺术字体生成,
        海报生成,
        千问图像,
        表情包生成
    )
except Exception as e:
    logging.error(f"导入千问提示词公式节点失败: {str(e)}")
    LOGO生成 = 艺术字体生成 = 海报生成 = 千问图像 = 表情包生成 = 节点占位符

# 导入工具节点
try:
    from 工具节点 import (
        字符串输入反转,
        图像输入反转, 
        合并多组提示词
    )
except Exception as e:
    logging.error(f"导入工具节点失败: {str(e)}")
    # 创建空的占位符类
    class 工具节点占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING",)
        FUNCTION = "placeholder"
        CATEGORY = "📃提示词公式/工具节点"
        def placeholder(self, **kwargs):
            return ("工具节点加载失败",)
    
    字符串输入反转 = 图像输入反转 = 合并多组提示词 = 工具节点占位符

# 节点映射表
NODE_CLASS_MAPPINGS = {
    "提示词预设": 提示词预设,
    "视频提示词公式": 视频提示词公式,
    "图像提示词公式": 图像提示词公式,
    "随机提示词人像": 随机提示词人像,
    "历史记录和预设管理": 历史记录和预设管理,
    "提示词保存为预设": 提示词保存为预设,
    "LOGO生成": LOGO生成,
    "艺术字体生成": 艺术字体生成,
    "海报生成": 海报生成,
    "千问图像": 千问图像,
    "表情包生成": 表情包生成,
    # 工具节点
    "字符串输入反转": 字符串输入反转,
    "图像输入反转": 图像输入反转,
    "合并多组提示词": 合并多组提示词,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "提示词预设": "提示词预设",
    "视频提示词公式": "视频提示词公式",
    "图像提示词公式": "图像提示词公式",
    "随机提示词人像": "随机提示词人像",
    "历史记录和预设管理": "历史记录和预设管理",
    "提示词保存为预设": "提示词保存为预设",
    "LOGO生成": "LOGO生成",
    "艺术字体生成": "艺术字体生成",
    "海报生成": "海报生成",
    "千问图像": "千问图像",
    "表情包生成": "表情包生成",
    # 工具节点
    "字符串输入反转": "字符串输入反转",
    "图像输入反转": "图像输入反转",
    "合并多组提示词": "合并多组提示词",
}

# 模块信息
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("📃 提示词公式节点包已加载")
print(f"✅ 已加载 {len(NODE_CLASS_MAPPINGS)} 个节点")
print("🔧 工具节点已添加到 '📃提示词公式/工具节点' 分类")