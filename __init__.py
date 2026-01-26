# __init__.py
import os
import sys
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入工具函数
from 工具函数 import (
    clean_text, apply_weight, load_presets, save_preset, 
    delete_preset,
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
    from 节点文件.通用提示词公式 import (
        视频提示词公式,
        图像提示词公式,
        随机提示词人像,
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
        CATEGORY = "📕提示词公式"
        def placeholder(self, **kwargs):
            return ("节点加载失败",)
    
    视频提示词公式 = 图像提示词公式 = 随机提示词人像 = 节点占位符

# 导入图转视频预设节点
try:
    from 节点文件.图转视频预设 import 视频首尾帧转场, 视频运镜提示词, 视频动效提示词, 视频首尾帧转场_增强版
except Exception as e:
    logging.error(f"导入图转视频预设节点失败: {str(e)}")
    # 创建空的占位符类
    class 视频转场占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING", "STRING", "STRING")
        RETURN_NAMES = ("转场提示词", "完整提示词", "技术说明")
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/图转视频"
        def placeholder(self, **kwargs):
            return ("视频转场节点加载失败", "", "")
    
    class 视频运镜占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING", "STRING")
        RETURN_NAMES = ("运镜提示词", "技术说明")
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/图转视频"
        def placeholder(self, **kwargs):
            return ("视频运镜节点加载失败", "")
    
    class 视频动效占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING", "STRING", "STRING")
        RETURN_NAMES = ("动效提示词", "完整提示词", "技术说明")
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/图转视频"
        def placeholder(self, **kwargs):
            return ("视频动效节点加载失败", "", "")
    
    class 视频转场增强版占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING", "STRING", "STRING")
        RETURN_NAMES = ("转场提示词", "完整提示词", "技术说明")
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/图转视频"
        def placeholder(self, **kwargs):
            return ("视频转场增强版节点加载失败", "", "")
    
    视频首尾帧转场 = 视频转场占位符
    视频运镜提示词 = 视频运镜占位符
    视频动效提示词 = 视频动效占位符
    视频首尾帧转场_增强版 = 视频转场增强版占位符

# 导入提示词预设节点
try:
    from 节点文件.提示词预设节点 import (
        提示词预设,
        NODE_CLASS_MAPPINGS as PRESET_NODES,
        NODE_DISPLAY_NAME_MAPPINGS as PRESET_DISPLAY_NAMES
    )
except Exception as e:
    logging.error(f"导入提示词预设节点失败: {str(e)}")
    # 创建空的占位符类
    class 提示词预设占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING",)
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式"
        def placeholder(self, **kwargs):
            return ("提示词预设节点加载失败",)
    
    提示词预设 = 提示词预设占位符
    PRESET_NODES = {}
    PRESET_DISPLAY_NAMES = {}

# 导入千问提示词公式节点
try:
    from 节点文件.千问提示词公式 import (
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
    from 节点文件.工具节点 import (
        字符串输入反转,
        图像输入反转,
        合并多组提示词,
        提取视频结束帧,
        空图像防报错,
        判断并输出加载的图像,
        批量判断并输出同名图像
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
        CATEGORY = "📕提示词公式/工具节点"
        def placeholder(self, **kwargs):
            return ("工具节点加载失败",)
    
    字符串输入反转 = 图像输入反转 = 合并多组提示词 = 提取视频结束帧 = 空图像防报错 = 判断并输出加载的图像 = 批量判断并输出同名图像 = 工具节点占位符

# 导入千问编辑节点
try:
    from 节点文件.千问编辑 import (
        千问单图编辑_改变视角,
        千问单图编辑_改变镜头, 
        千问单图编辑_人物换动作,
        千问单图编辑_物品换材质,
        千问单图编辑_图像变文创产品,
        千问单图编辑_图像转绘,
        千问单图编辑_图像编辑
    )
except Exception as e:
    logging.error(f"导入千问编辑节点失败: {str(e)}")
    # 创建空的占位符类
    class 千问编辑占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING",)
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/千问编辑"
        def placeholder(self, **kwargs):
            return ("千问编辑节点加载失败",)
    
    千问单图编辑_改变视角 = 千问单图编辑_改变镜头 = 千问单图编辑_人物换动作 = 千问单图编辑_物品换材质 = 千问单图编辑_图像变文创产品 = 千问单图编辑_图像转绘 = 千问单图编辑_图像编辑 = 千问编辑占位符

# ==================== 新增节点导入 ====================

# 导入视频动态带运镜节点
try:
    from 节点文件.视频动态带运镜 import 视频动态带运镜
except Exception as e:
    logging.error(f"导入视频动态带运镜节点失败: {str(e)}")
    class 视频动态带运镜占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING", "STRING", "STRING")
        RETURN_NAMES = ("动态提示词", "运镜提示词", "完整提示词")
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/图转视频"
        def placeholder(self, **kwargs):
            return ("视频动态带运镜节点加载失败", "", "")
    
    视频动态带运镜 = 视频动态带运镜占位符

# 导入Wan25提示词公式节点
try:
    import importlib.util
    import os
    # 动态导入包含点号的模块
    module_path = os.path.join(os.path.dirname(__file__), '节点文件', 'Wan2.5提示词公式.py')
    module_name = 'Wan2.5提示词公式'
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    Wan25提示词公式_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(Wan25提示词公式_module)
    Wan25图生视频 = Wan25提示词公式_module.Wan25图生视频
except Exception as e:
    logging.error(f"导入Wan25提示词公式节点失败: {str(e)}")
    class Wan25图生视频占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING", "STRING", "STRING")
        RETURN_NAMES = ("视觉提示词", "声音提示词", "完整提示词")
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/图转视频"
        def placeholder(self, **kwargs):
            return ("Wan25图生视频节点加载失败", "", "")
    
    Wan25图生视频 = Wan25图生视频占位符

# 导入Wan26图生视频节点
try:
    from 节点文件.Wan26图生视频 import Wan26图生视频
except Exception as e:
    logging.error(f"导入Wan26图生视频节点失败: {str(e)}")
    class Wan26图生视频占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING", "STRING", "STRING")
        RETURN_NAMES = ("Wan提示词", "完整提示词", "技术说明")
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/图转视频"
        def placeholder(self, **kwargs):
            return ("Wan26节点加载失败", "", "")
    
    Wan26图生视频 = Wan26图生视频占位符

# 导入Wan26多镜头节点
try:
    from 节点文件.Wan26多镜头 import Wan26多镜头
except Exception as e:
    logging.error(f"导入Wan26多镜头节点失败: {str(e)}")
    class Wan26多镜头占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("STRING", "STRING", "STRING")
        RETURN_NAMES = ("多镜头提示词", "完整提示词", "镜头结构表")
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/图转视频"
        def placeholder(self, **kwargs):
            return ("Wan26多镜头节点加载失败", "", "")
    
    Wan26多镜头 = Wan26多镜头占位符

# 导入裁剪节点
try:
    from 节点文件.裁剪节点 import 图像裁剪节点
except Exception as e:
    logging.error(f"导入裁剪节点失败: {str(e)}")
    class 图像裁剪占位符:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": {}}
        RETURN_TYPES = ("IMAGE",)
        RETURN_NAMES = ("图像",)
        FUNCTION = "placeholder"
        CATEGORY = "📕提示词公式/工具节点"
        def placeholder(self, **kwargs):
            return (None,)
    
    图像裁剪节点 = 图像裁剪占位符

# 节点映射表
NODE_CLASS_MAPPINGS = {
    # 基础新手节点
    "提示词预设": 提示词预设,
    "视频提示词公式": 视频提示词公式,
    "图像提示词公式": 图像提示词公式,
    "随机提示词人像": 随机提示词人像,
    "LOGO生成": LOGO生成,
    "艺术字体生成": 艺术字体生成,
    "海报生成": 海报生成,
    "千问图像": 千问图像,
    "表情包生成": 表情包生成,
    # 工具节点
    "字符串输入反转": 字符串输入反转,
    "图像输入反转": 图像输入反转,
    "合并多组提示词": 合并多组提示词,
    "提取视频结束帧": 提取视频结束帧,
    "空图像防报错": 空图像防报错,
    "判断并输出加载的图像": 判断并输出加载的图像,
    "批量判断并输出同名图像": 批量判断并输出同名图像,
    "图像裁剪节点": 图像裁剪节点,
    # 千问编辑
    "千问单图编辑-改变视角": 千问单图编辑_改变视角,
    "千问单图编辑-改变镜头": 千问单图编辑_改变镜头,
    "千问单图编辑-人物换动作": 千问单图编辑_人物换动作,
    "千问单图编辑-物品换材质": 千问单图编辑_物品换材质,
    "千问单图编辑-图像变文创产品": 千问单图编辑_图像变文创产品,
    "千问单图编辑-图像转绘": 千问单图编辑_图像转绘,
    "千问单图编辑-图像编辑": 千问单图编辑_图像编辑,
    # 图转视频预设节点
    "视频首尾帧转场": 视频首尾帧转场,
    "视频首尾帧转场-增强版": 视频首尾帧转场_增强版,
    "视频运镜提示词": 视频运镜提示词,
    "视频动效提示词": 视频动效提示词,
    # 新增节点
    "视频动态带运镜": 视频动态带运镜,
    "Wan25图生视频": Wan25图生视频,
    "Wan26图生视频": Wan26图生视频,
    "Wan26多镜头": Wan26多镜头,
}

# 合并预设节点映射
NODE_CLASS_MAPPINGS.update(PRESET_NODES)

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    # 基础新手节点
    "提示词预设": "提示词预设",
    "视频提示词公式": "视频提示词公式",
    "图像提示词公式": "图像提示词公式",
    "随机提示词人像": "随机提示词人像",
    "LOGO生成": "LOGO生成",
    "艺术字体生成": "艺术字体生成",
    "海报生成": "海报生成",
    "千问图像": "千问图像",
    "表情包生成": "表情包生成",
    # 工具节点
    "字符串输入反转": "字符串输入反转",
    "图像输入反转": "图像输入反转",
    "合并多组提示词": "合并多组提示词",
    "提取视频结束帧": "提取视频结束帧",
    "空图像防报错": "空图像防报错",
    "判断并输出加载的图像": "判断并输出加载的图像",
    "批量判断并输出同名图像": "批量判断并输出同名图像",
    "图像裁剪节点": "图像裁剪节点",
    # 千问编辑
    "千问单图编辑-改变视角": "千问单图编辑-改变视角",
    "千问单图编辑-改变镜头": "千问单图编辑-改变镜头",
    "千问单图编辑-人物换动作": "千问单图编辑-人物换动作",
    "千问单图编辑-物品换材质": "千问单图编辑-物品换材质",
    "千问单图编辑-图像变文创产品": "千问单图编辑-图像变文创产品",
    "千问单图编辑-图像转绘": "千问单图编辑-图像转绘",
    "千问单图编辑-图像编辑": "千问单图编辑-图像编辑",
    # 图转视频预设节点
    "视频首尾帧转场": "视频首尾帧转场",
    "视频首尾帧转场-增强版": "视频首尾帧转场-增强版",
    "视频运镜提示词": "视频运镜提示词",
    "视频动效提示词": "视频动效提示词",
    # 新增节点
    "视频动态带运镜": "视频动态带运镜",
    "Wan25图生视频": "Wan25图生视频",
    "Wan26图生视频": "Wan26图生视频",
    "Wan26多镜头": "Wan26多镜头",
}

# 合并预设节点显示名称
NODE_DISPLAY_NAME_MAPPINGS.update(PRESET_DISPLAY_NAMES)

# 模块信息
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# 网页资源目录
WEB_DIRECTORY = "./网页资源"

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("📕 提示词公式节点包已加载")
print(f"✅ 已加载 {len(NODE_CLASS_MAPPINGS)} 个节点")
print("🔧 工具节点已添加到 '📕提示词公式/工具节点' 分类")
print("🎬 图转视频预设节点已成功添加")
print("🎛️  视频首尾帧转场节点已启用动态组件控制")
print("✨ 视频动效提示词节点已添加 - 120+种动态效果")
print("📁 提示词预设节点，直接在节点上预览内容")
print("🚀 新增视频动态带运镜节点 - 动态+运镜一体化设计")
print("🎵 新增Wan25图生视频节点 - 支持视觉+音频同步生成")
print("✂️ 新增图像裁剪节点 - 快捷处理图像尺寸")
print("插件教程请查看 'https://www.bilibili.com/video/BV1nveMzcES4/' 复制链接用浏览器打开")
print("进群和小伙伴们一起共同进步 'QQ群202018000' 公告中有资源")