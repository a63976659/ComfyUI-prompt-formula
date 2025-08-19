import os
import re
import time
from pathlib import Path
import json
from datetime import datetime
import logging

# 引入ComfyUI的路径管理和工具
import folder_paths

# 获取插件当前文件夹路径
PLUGIN_DIR = Path(__file__).parent.resolve()
# 定义预设文件夹为插件目录下的提示词预设文件夹子文件夹
PRESET_DIR = PLUGIN_DIR / "提示词预设文件夹"
# 确保预设文件夹存在
PRESET_DIR.mkdir(parents=True, exist_ok=True)

# 在ComfyUI的路径管理中注册预设文件夹，增加对JSON格式的支持
if "prompt_presets" not in folder_paths.folder_names_and_paths:
    folder_paths.folder_names_and_paths["prompt_presets"] = (
        [str(PRESET_DIR)],  # 预设文件夹路径
        [".txt", ".json"]  # 支持的预设文件扩展名，增加JSON格式
    )

# 历史记录文件存储在插件目录下
HISTORY_FILE = PLUGIN_DIR / "prompt_history.json"
MAX_HISTORY_COUNT = 10

# 常量配置 - 提取可复用选项列表
VISUAL_STYLES = [
    "无", "像素风格", "油画风格", "版画风格", "壁画风格",
    "素描风格", "黑白电影风格", "科幻风格", "抽象风格", "迷幻风格",
    "文艺复兴", "水彩风格", "赛博朋克风格", "写实风格", "动漫风格",
    "黑白动画风格", "浮世绘风格", "点彩派风格", "蒸汽朋克风格",
    "皮克斯风格", "吉卜力风格", "迪士尼风格", "美漫风格",
    "故障艺术风格", "全息投影效果", "数据可视化风格", "UI界面风格", 
    "毛毡风格", "3D卡通风格", "木偶动画风格", "3D游戏风格", "黏土风格", "二次元风格", "低多边形风格",
    "中式传统风格", "中国水墨风格", "印度风格", "阿拉伯风格", "印第安风格", "非洲部落风格", "东南亚风格"
]

CAMERA_MOVEMENTS = [
    "无", "固定镜头", "推近镜头", "拉远镜头", "快速推近", "快速拉远", "俯视角度", "仰视角度", 
    "上移镜头", "下移镜头", "左摇镜头", "右摇镜头", "上仰镜头", "下俯镜头", "前进后退交替", 
    "前进后退循环", "右弧线移动(半圈)", "左弧线移动(半圈)", "水平快速平移", "水平环绕", 
    "环绕+拉近", "环绕+翻转", "原地旋转", "俯视旋转", "垂直升降 + 停顿", "对角上升", 
    "对角下移推进", "对角穿越", "镜头抖动", "冲击震动", "贝塞尔拉远", "贝塞尔拉近"
]

COMPOSITION_STYLES = [
    "无", "黄金分割构图", "对称构图", "三分法构图", 
    "对角线构图", "三角形构图", "S形构图", "框式构图", 
    "放射式构图", "紧凑式构图", "留白构图", "X形构图", 
    "L形构图", "隧道构图", "中心构图", "平衡构图", 
    "右侧重构图", "左侧重构图", "短边构图"
]

SHOT_TYPES = [
    "无", "大远景", "远景", "全景", "中景", 
    "中近景", "半身景", "近景", "特写", "大特写"
]

LIGHT_SOURCE_TYPES = [
    "无", "日光", "人工光", "月光", "实用光", "火光", 
    "荧光", "阴天光", "晴天光", "呼吸光", "霓虹流动光",
    "晚霞余晖", "月光冷辉", "清晨薄雾光", "闪烁星光",
    "聚光扫射", "扫描激光", "雷暴闪光", "流动极光",
    "脉动光", "摇曳光", "能量波动光", "闪烁光",
    "跳动火焰", "数据流光", "扩散光波", "旋转光晕",
    "跳跃光点", "流光飞舞"
]

LIGHT_TYPE = [
    "无", "柔光", "强光", "顶光", "侧光", "背光", 
    "底光", "边缘光", "剪影", "低对比度", "高对比度"
]

TIME_PERIODS = [
    "无", "白天", "夜晚", "黄昏", "日落", "黎明", "日出"
]

CAMERA_ANGLES = [
    "无", "过肩镜头角度拍摄", "高角度拍摄", "低角度拍摄", 
    "倾斜角度拍摄", "航拍", "俯视角度"
]

LENS_TYPES = [
    "无", "微距", "中焦距", "广角", "长焦", "望远", "超广角-鱼眼"
]

SHOT_COMPOSITIONS = [
    "无", "干净的单人镜头", "双人镜头", "三人镜头", 
    "群像镜头", "定场镜头"
]

CHARACTER_MOVEMENTS = [
    "无", "机械舞步", "蹦跳前进", "悠闲散步", "滑板滑行", "足球带球", 
    "网球挥拍", "游泳姿势", "跳绳", "打乒乓球", "滑雪滑行", "篮球运球", 
    "优雅旋转", "轻盈跳跃", "翩翩起舞", "舞步滑动", "身体波浪",
    "慢跑前进", "快速奔跑", "跳跃前进", "侧身移动", "后退行走",
    "太极拳式", "武术招式", "空翻动作", "踢腿动作", "格斗姿势",  
    "瑜伽姿势", "拉伸动作", "俯卧撑式", "深蹲动作", "举重姿势",
    "网球", "羽毛球", "跳绳", "乒乓球", "滑雪", "篮球", 
    "骑车姿势", "拉丁舞", "侧手翻", "玩手机", "打电话"
]

EMOTIONS = [
    "无", "微笑", "愤怒咆哮", "震惊瞪眼", "张口大笑", "兴奋尖叫",
    "痛哭流泪", "狂喜张扬", "鄙夷冷笑", "大声呼喊", "极度恐惧", "媚眼如丝"
]

# 新增颜色预设选项
COLOR_PRESETS = [
    "无", "奶油樱花", "香芋奶茶", "莫兰迪粉灰", "粉金大理石", "午夜芭蕾", 
    "金属工业粉", "赛博甜心", "热带果汁", "像素游戏", "老电影滤镜", 
    "70年代迪斯科", "维多利亚宫廷", "春日花园", "沙漠黄昏", "海盐冰淇淋", 
    "霓虹故障", "液态金属", "AI虚拟空间", "经典粉黑", "粉灰进阶"
]

# 颜色预设详细配置
COLOR_PRESETS_DETAILS = {
    "无": {},
    "奶油樱花": {
        "colors": ["#FFCDD2 (粉)", "#FFF9C4 (鹅黄)", "#E1F5FE (天蓝)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "香芋奶茶": {
        "colors": ["#E1C4FF (香芋紫)", "#FFE4E1 (肉粉)", "#F5F5DC (米白)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "莫兰迪粉灰": {
        "colors": ["#D4B8C7 (灰粉)", "#A7C4BC (灰绿)", "#E8D7D3 (暖灰)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "粉金大理石": {
        "colors": ["#C9A9A6 (干枯玫瑰)", "#D4C0B7 (沙石色)", "#B7A8A1 (高级灰)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "午夜芭蕾": {
        "colors": ["#D90368 (玫粉)", "#2E294E (深紫)", "#F1E9DA (象牙白)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "金属工业粉": {
        "colors": ["#ED254E (朱红粉)", "#404E5C (钢蓝)", "#C5CBE3 (银灰)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "赛博甜心": {
        "colors": ["#FF2E63 (荧光粉)", "#08D9D6 (青蓝)", "#252A34 (黑)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "热带果汁": {
        "colors": ["#FF5E78 (西瓜红)", "#FFCC00 (明黄)", "#00C4CC (湖蓝)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "像素游戏": {
        "colors": ["#FF6B6B (珊瑚粉)", "#4ECDC4 (薄荷绿)", "#FFE66D (柠檬黄)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "老电影滤镜": {
        "colors": ["#D48A6E (陶土粉)", "#6A6B83 (灰蓝)", "#E3DCCB (做旧白)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "70年代迪斯科": {
        "colors": ["#E64398 (亮粉)", "#4B0082 (靛蓝)", "#FFD700 (金色)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "维多利亚宫廷": {
        "colors": ["#C74375 (绛红)", "#5A3D2B (棕)", "#E6C229 (鎏金)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "春日花园": {
        "colors": ["#F7CAC9 (蔷薇粉)", "#92A8D1 (浅蓝)", "#88B04B (嫩绿)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "沙漠黄昏": {
        "colors": ["#E6B0AA (沙粉)", "#F5CBA7 (杏色)", "#A9CCE3 (雾蓝)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "海盐冰淇淋": {
        "colors": ["#FADADD (淡粉)", "#ACE1E6 (浅蓝绿)", "#F0EAD6 (奶油白)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "霓虹故障": {
        "colors": ["#FF00FF (品红)", "#00FFFF (青)", "#000000 (黑)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "液态金属": {
        "colors": ["#FF007F (玫粉)", "#00FF7F (碧绿)", "#C0C0C0 (银)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "AI虚拟空间": {
        "colors": ["#FF6EC7 (荧光粉)", "#6EFFFF (电子蓝)", "#1A1A1A (深灰)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "经典粉黑": {
        "colors": ["#FFB6C1 (浅粉)", "#000000 (黑)", "#FFFFFF (白)"],
        "percentages": ["60%", "30%", "10%"]
    },
    "粉灰进阶": {
        "colors": ["#E75480 (桃粉)", "#708090 (灰蓝)", "#F8F8FF (雪白)"],
        "percentages": ["60%", "30%", "10%"]
    }
}

# 视角方向选项
VIEW_DIRECTIONS = [
    "无", "正视图", "顶视图", "后视图", "左视图", "右视图", "侧视图"
]

# 颜色选项（字体颜色和背景颜色共用）
COLOR_OPTIONS = [
    "无", "黑色", "白色", "浅灰色", "深灰色", "浅蓝色", "深蓝色", "亮绿色", "深绿色", 
    "紫水晶", "翡翠", "霓虹蓝", "霓虹绿", "霓虹橙", "霓虹粉", "霓虹黄", "铂金", "玫瑰金", 
    "红宝石", "蓝宝石", "黄玉/托帕石", "黄色", "青色", "灰色", "浅红色", "浅绿色", "浅黄色", 
    "浅蓝色", "浅紫色", "浅青色", "浅白色", "爱丽丝蓝", "古董白", "碧绿色", "天蓝色", "米色", 
    "陶坯色", "杏仁白", "蓝紫罗兰", "硬木色", "军校蓝", "查特酒绿", "巧克力色", "矢车菊蓝", 
    "玉米丝色", "绯红色", "深蓝色", "深青色", "深金菊黄", "深灰色", "深绿色", "深卡其色", 
    "深洋红色", "深橄榄绿", "深橙色", "深兰花紫", "深红色", "深鲑鱼红", "深海绿色", "深石板蓝", 
    "深石板灰", "深绿松石", "深紫罗兰", "深粉红色", "深天蓝色", "暗淡灰", "道奇蓝", "耐火砖红", 
    "花卉白", "森林绿", "庚斯博罗灰", "幽灵白", "金菊黄", "黄绿色", "蜜瓜色", "艳粉色", "印度红", 
    "象牙色", "卡其色", "薰衣草红", "草坪绿", "柠檬绸", "浅蓝色", "浅珊瑚色", "浅青色", "浅金菊黄", 
    "浅灰色", "浅绿色", "浅粉红色", "浅鲑鱼红", "浅海绿色", "浅天蓝色", "浅石板灰", "浅钢蓝", 
    "浅黄色", "酸橙绿", "亚麻色", "中碧绿色", "中蓝色", "中兰花紫", "中紫色", "中海绿色", 
    "中石板蓝", "中春绿色", "中绿松石", "中紫红", "午夜蓝", "薄荷奶油", "雾玫瑰", "鹿皮鞋色", 
    "纳瓦白", "海军蓝", "旧蕾丝", "橄榄褐", "橙红色", "兰花紫", "苍白金菊黄", "苍白绿", 
    "苍白绿松石", "苍白紫红", "木瓜鞭色", "桃粉色", "秘鲁色", "李紫色", "粉末蓝", "丽贝卡紫", 
    "玫瑰褐", "皇家蓝", "鞍褐色", "鲑鱼红", "沙褐色", "海绿色", "贝壳色", "赭色", "石板灰"
]

# 海报类型选项
POSTER_TYPES = [
    "无", "产品海报", "品牌活动海报", "电影/戏剧海报", "音乐节海报", "展览海报", 
    "环保海报", "公共卫生海报", "社会议题海报", "学术讲座海报", "招聘海报", 
    "课程培训海报", "极简主义海报", "拼贴风海报", "政治宣传海报", "节气节日海报", 
    "个人作品集海报", "电商海报",
]

# 表情包布局选项
MEME_LAYOUTS = ["单个", "四宫格", "九宫格"]

# 预设缓存及刷新机制
_preset_cache = {}
_last_refresh_time = 0
CACHE_TIMEOUT = 30  # 缓存超时时间（秒）

# 初始化必要的目录和文件
def initialize_files():
    # 只确保历史记录文件存在
    if not HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)
        except PermissionError:
            logging.error("无权限创建历史记录文件，请检查文件夹权限")
        except Exception as e:
            logging.error(f"创建历史记录文件失败: {str(e)}")

# 工具函数：清理文本
def clean_text(text):
    """清理文本，去除多余符号和空格"""
    if not text:
        return ""
    cleaned = re.sub(r',', ' ', text)
    return re.sub(r'\s+', ' ', cleaned.strip()) or ""

# 工具函数：应用权重
def apply_weight(text, weight, default_val="无"):
    """统一处理权重应用，支持默认值过滤"""
    cleaned_text = clean_text(text)
    # 如果内容为空或为默认值"无"，则不输出
    if not cleaned_text or cleaned_text == default_val:
        return ""
    # 权重为1.0时不需要特别标记
    if weight == 1.0:
        return cleaned_text
    return f"({cleaned_text}:{weight:.1f})"

# 获取预设的预览媒体文件路径
def get_preset_preview(preset_name):
    # 检查TXT文件对应的预览
    txt_preset_path = folder_paths.get_full_path("prompt_presets", f"{preset_name}.txt")
    json_preset_path = folder_paths.get_full_path("prompt_presets", f"{preset_name}.json")
    
    # 确定基础路径（无论是TXT还是JSON）
    base_path = None
    if txt_preset_path:
        base_path = os.path.splitext(txt_preset_path)[0]
    elif json_preset_path:
        base_path = os.path.splitext(json_preset_path)[0]
    
    if not base_path:
        return None, None
        
    video_extensions = ['.mp4']
    image_extensions = ['.png', '.jpg', '.jpeg']
    
    for ext in video_extensions:
        preview_path = f"{base_path}{ext}"
        if os.path.exists(preview_path):
            return preview_path, 'video'
    
    for ext in image_extensions:
        preview_path = f"{base_path}{ext}"
        if os.path.exists(preview_path):
            return preview_path, 'image'
    
    return None, None

# 实际加载预设的函数（内部使用），支持TXT和JSON格式
def _actual_load_presets():
    presets = {}
    # 获取所有支持的预设文件（TXT和JSON）
    preset_files = folder_paths.get_filename_list("prompt_presets")
    
    for preset_file in preset_files:
        try:
            preset_path = folder_paths.get_full_path("prompt_presets", preset_file)
            if not preset_path:
                continue
                
            # 获取文件名和扩展名
            file_name, file_ext = os.path.splitext(preset_file)
            preset_name = file_name  # 预设名称不包含扩展名
            
            # 读取文件内容，根据扩展名处理
            content = ""
            if file_ext.lower() == ".txt":
                with open(preset_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
            elif file_ext.lower() == ".json":
                with open(preset_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    # 尝试从JSON中提取提示词内容
                    # 支持多种常见的键名，提高兼容性
                    if isinstance(json_data, dict):
                        # 优先检查"prompt"和"content"键
                        if "prompt" in json_data:
                            content = str(json_data["prompt"]).strip()
                        elif "content" in json_data:
                            content = str(json_data["content"]).strip()
                        # 检查"positive"键（常见于Stable Diffusion工作流）
                        elif "positive" in json_data:
                            content = str(json_data["positive"]).strip()
                        # 如果都没有，尝试使用第一个字符串值
                        else:
                            for value in json_data.values():
                                if isinstance(value, str):
                                    content = value.strip()
                                    break
                    # 如果JSON直接是字符串
                    elif isinstance(json_data, str):
                        content = json_data.strip()
            
            # 获取预览信息
            preview_path, preview_type = get_preset_preview(preset_name)
            
            # 只添加有内容的预设
            if content:
                # 如果已经存在同名预设（不同扩展名），保留第一个
                if preset_name not in presets:
                    presets[preset_name] = {
                        "content": content,
                        "preview_path": preview_path,
                        "preview_type": preview_type,
                        "file_type": file_ext.lower()  # 记录文件类型
                    }
        
        except Exception as e:
            logging.error(f"读取预设文件 {preset_file} 出错: {str(e)}")
    
    return presets

# 加载所有预设（使用缓存机制）
def load_presets():
    global _preset_cache, _last_refresh_time
    now = time.time()
    # 超过缓存时间或缓存为空时刷新
    if now - _last_refresh_time > CACHE_TIMEOUT or not _preset_cache:
        _preset_cache = _actual_load_presets()
        _last_refresh_time = now
    return _preset_cache.copy()  # 返回副本防止外部修改缓存

# 保存预设，支持TXT和JSON格式
def save_preset(preset_name, content):
    # 检查是否包含扩展名
    if preset_name.endswith((".txt", ".json")):
        file_name = preset_name
        file_ext = os.path.splitext(preset_name)[1].lower()
        preset_base_name = os.path.splitext(preset_name)[0]
    else:
        # 默认保存为TXT格式
        file_ext = ".txt"
        file_name = f"{preset_name}{file_ext}"
        preset_base_name = preset_name
    
    try:
        save_dir = folder_paths.folder_names_and_paths["prompt_presets"][0][0]
        file_path = os.path.join(save_dir, file_name)
        
        # 根据文件类型保存内容
        if file_ext == ".json":
            # 直接保存原始内容，不做任何处理
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)  # 原样写入不修改
        else:  # .txt格式保持原有逻辑
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
        
        # 立即刷新缓存
        global _preset_cache, _last_refresh_time
        _preset_cache = _actual_load_presets()
        _last_refresh_time = time.time()
        
        return preset_base_name
    except PermissionError:
        logging.error(f"无权限写入预设文件 {file_name}，请检查文件夹权限")
    except OSError as e:
        logging.error(f"预设文件操作失败: {str(e)}")
    except Exception as e:
        logging.error(f"保存预设文件出错: {str(e)}")
    return None

# 删除预设文件及相关预览文件，支持TXT和JSON
def delete_preset(preset_name):
    if not preset_name:
        return False, "预设名称不能为空"
    
    # 检查并删除所有可能的文件类型
    deleted_files = []
    for ext in ['.txt', '.json', '.mp4', '.png', '.jpg', '.jpeg']:
        try:
            if ext in ['.txt', '.json']:
                preset_path = folder_paths.get_full_path("prompt_presets", f"{preset_name}{ext}")
            else:
                txt_path = folder_paths.get_full_path("prompt_presets", f"{preset_name}.txt")
                json_path = folder_paths.get_full_path("prompt_presets", f"{preset_name}.json")
                base_path = None
                if txt_path:
                    base_path = os.path.splitext(txt_path)[0]
                elif json_path:
                    base_path = os.path.splitext(json_path)[0]
                
                if not base_path:
                    continue
                    
                preset_path = f"{base_path}{ext}"
            
            if preset_path and os.path.exists(preset_path):
                os.remove(preset_path)
                deleted_files.append(os.path.basename(preset_path))
        except PermissionError:
            return False, f"无权限删除文件 {preset_name}{ext}，请检查文件权限"
        except Exception as e:
            return False, f"删除文件 {preset_name}{ext} 失败: {str(e)}"
    
    # 强制刷新缓存
    global _preset_cache, _last_refresh_time
    _preset_cache = {}
    _last_refresh_time = 0
    
    if not deleted_files:
        return False, f"预设 '{preset_name}' 不存在"
    
    return True, f"预设 '{preset_name}' 及相关文件已成功删除"

# 读取历史记录
def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("历史记录文件格式错误，将创建新文件")
            # 备份损坏的文件
            try:
                backup_path = f"{HISTORY_FILE}.bak"
                os.rename(HISTORY_FILE, backup_path)
                logging.error(f"已将损坏的历史记录文件备份至 {backup_path}")
            except Exception as e:
                logging.error(f"备份历史记录文件失败: {str(e)}")
            return []
        except PermissionError:
            logging.error("无权限读取历史记录文件，请检查文件权限")
            return []
        except Exception as e:
            logging.error(f"读取历史记录文件失败: {str(e)}")
            return []
    return []

# 保存到历史记录
def save_to_history(prompt, name, manual_save=False):
    try:
        history = load_history()
        new_entry = {
            "prompt": prompt,
            "name": name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "manual": manual_save
        }
        history.insert(0, new_entry)
        if len(history) > MAX_HISTORY_COUNT:
            history = history[:MAX_HISTORY_COUNT]
            
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return history
    except PermissionError:
        logging.error("无权限写入历史记录文件，请检查文件权限")
    except Exception as e:
        logging.error(f"保存历史记录失败: {str(e)}")
    return None

# 获取历史记录选项列表
def get_history_options():
    try:
        history = load_history()
        options = ["不选择历史记录"]
        for i, entry in enumerate(history):
            preview = f"{entry['name']} ({entry['timestamp']})"
            if entry.get("manual", False):
                preview += " [手动保存]"
            options.append(f"[{i}] {preview}")
        return options
    except Exception as e:
        logging.error(f"获取历史记录选项错误: {str(e)}")
        return ["不选择历史记录"]

# 历史记录验证函数（用于解决JSON序列化问题）
def validate_history(v):
    history_options = get_history_options()
    return v in history_options or v == ""

# 初始化文件系统
initialize_files()

# 提示词预设节点
class 提示词预设:
    tooltip = "预设文件储存在此插件提示词预设文件夹，支持TXT和JSON格式。可通过历史记录和预设管理节点创建新预设，也可直接添加文件。"

    @classmethod
    def INPUT_TYPES(cls):
        try:
            preset_files = folder_paths.get_filename_list("prompt_presets")
            # 提取预设名称（去除扩展名）
            preset_names = list({os.path.splitext(f)[0] for f in preset_files})
            
            if not preset_names:
                preset_names = ["请先创建预设"]
                presets = {"请先创建预设": {"content": "", 
                                     "preview_path": None, "preview_type": None}}
            else:
                presets = load_presets()
            
            preset_options = preset_names
            
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
                    "预设名称": (preset_options, {
                        "default": preset_options[0] if preset_options else "请先创建预设",
                        "tooltip": "预设文件储存在此插件的提示词预设文件夹中，支持TXT和JSON格式",
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
        name = 预设名称
        
        presets = load_presets()
        # 如果没有预设，返回空内容
        preset_info = presets.get(name, {"content": "", "file_type": "unknown"})
        
        return (name, preset_info["content"], preset_info["file_type"])

# 视频提示词公式节点
class 视频提示词公式:
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
                "人物情绪": (EMOTIONS, {
                    "default": "无", 
                    "display_name": "人物情绪"
                }),
                "情绪权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "情绪权重"
                }),
                "主体运动": (CHARACTER_MOVEMENTS, {
                    "default": "无", 
                    "display_name": "主体运动"
                }),
                "运动权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "运动权重"
                }),
                "场景描述": ("STRING", {
                    "multiline": False,
                    "default": "在樱花树下",
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
                "光源类型": (LIGHT_SOURCE_TYPES, {
                    "default": "无", 
                    "display_name": "光源类型"
                }),
                "光源权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "光源权重"
                }),
                "光线类型": (LIGHT_TYPE, {
                    "default": "无", 
                    "display_name": "光线类型"
                }),
                "光线权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "光线权重"
                }),
                "时间段": (TIME_PERIODS, {
                    "default": "无", 
                    "display_name": "时间段"
                }),
                "时间段权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "时间段权重"
                }),
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
                "镜头焦段": (LENS_TYPES, {
                    "default": "无", 
                    "display_name": "镜头焦段"
                }),
                "焦段权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "焦段权重"
                }),
                "机位角度": (CAMERA_ANGLES, {
                    "default": "无", 
                    "display_name": "机位角度"
                }),
                "角度权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "角度权重"
                }),
                "镜头类型": (SHOT_COMPOSITIONS, {
                    "default": "无", 
                    "display_name": "镜头类型"
                }),
                "镜头类型权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "镜头类型权重"
                }),
                "镜头目标": ("STRING", {
                    "multiline": False,
                    "default": "主体",
                    "display_name": "镜头目标"
                }),
                "目标权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "目标权重"
                }),
                "运镜方式": (CAMERA_MOVEMENTS, {
                    "default": "无", 
                    "display_name": "运镜方式"
                }),
                "运镜权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "运镜权重"
                }),
                "色调": ([
                    "无", "暖色调", "冷色调", "高饱和度", "低饱和度"
                ], {
                    "default": "无", 
                    "display_name": "色调"
                }),
                "色调权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "色调权重"
                }),
                "视觉风格": (VISUAL_STYLES, {
                    "default": "无", 
                    "display_name": "视觉风格"
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
                "附加提示词": ("STRING", {
                    "multiline": True,
                    "default": "",
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

    def 生成提示词(self, 主体描述, 主体权重, 人物情绪, 情绪权重, 主体运动, 运动权重,
                      场景描述, 场景权重, 光源类型, 光源权重, 光线类型, 光线权重,
                      时间段, 时间段权重, 景别描述, 景别权重,
                      构图描述, 构图权重, 镜头焦段, 焦段权重, 机位角度, 角度权重,
                      镜头类型, 镜头类型权重, 镜头目标, 目标权重, 运镜方式, 运镜权重, 
                      色调, 色调权重,视觉风格, 风格权重,
                      附加提示词="", 附加权重=1.0, 自动保存到历史=True):
        # 更新预设内容，包含新增组件
        预设内容 = "{主体}, {人物情绪}, {主体运动}, {场景}, {光源类型}, {光线类型}, {时间段}, {景别}, {构图}, {镜头焦段}, {机位角度}, {镜头类型}, {运镜}, {色调}, {视觉风格}"
        
        # 处理各组件，选择"无"或内容为空时不加入提示词
        组件 = {
            "主体": apply_weight(主体描述, 主体权重),
            "人物情绪": apply_weight(人物情绪, 情绪权重),
            "主体运动": apply_weight(主体运动, 运动权重),
            "场景": apply_weight(场景描述, 场景权重),
            "光源类型": apply_weight(光源类型, 光源权重),
            "光线类型": apply_weight(光线类型, 光线权重),
            "时间段": apply_weight(时间段, 时间段权重),
            "景别": apply_weight(景别描述, 景别权重),
            "构图": apply_weight(构图描述, 构图权重),
            "镜头焦段": apply_weight(镜头焦段, 焦段权重),
            "机位角度": apply_weight(机位角度, 角度权重),
            "镜头类型": apply_weight(镜头类型, 镜头类型权重),
            "运镜": self._get_camera_movement_desc(运镜方式, 镜头目标, 运镜权重) if 运镜方式 != "无" else "",
            "色调": apply_weight(色调, 色调权重),
            "视觉风格": apply_weight(视觉风格, 风格权重)
        }
        
        # 生成提示词，过滤空值
        提示词组件 = [value for value in 组件.values() if value]
        提示词 = "\n".join(提示词组件)
        
        # 处理附加提示词，使用逗号分隔
        if 附加提示词 and clean_text(附加提示词):
            加权附加词 = apply_weight(clean_text(附加提示词), 附加权重)
            if 加权附加词:
                if 提示词:
                    提示词 += "\n" + 加权附加词
                else:
                    提示词 = 加权附加词
        
        # 最终清理：确保没有连续的逗号和多余空格
        提示词 = re.sub(r',\s+,', ',', 提示词)
        提示词 = re.sub(r'\s+', ' ', 提示词).strip()
        
        # 处理历史记录保存
        if 自动保存到历史 and 提示词:
            timestamp = datetime.now().strftime("%H:%M")
            subject_preview = 主体描述[:10] + ("..." if len(主体描述) > 10 else "")
            save_name = f"[视频] {timestamp} {subject_preview}"
            save_to_history(提示词, save_name, manual_save=False)
        
        return (提示词,)

    def _get_camera_movement_desc(self, movement, target, weight=1.0):
        effective_target = target if target and target != "无" else "主体"
        movement_descriptions = {
            "固定镜头": "镜头位置保持不动，构图稳定，画面无明显抖动。",
            "推近镜头": f"镜头缓慢向前推进，逐步聚焦{target}细节。背景渐渐虚化，细节清晰锐利。最终停留在特写构图，画面稳定。",
            "拉远镜头": f"{target}位于画面中央，镜头缓慢向后移动，从近景过渡到全景，{target}始终保持居中，焦点稳定。",
            "快速推近": f"{target}位于画面中央，镜头快速向前推进至中近景或特写，焦点锁定{target}，背景产生轻微动感模糊。",
            "快速拉远": f"{target}位于画面中央，镜头快速向后拉远至全景，背景空间迅速扩展，{target}位置保持居中。",
            "俯视角度": f"{target}位于画面中央，镜头缓慢升至俯视角度，焦点锁定{target}，背景在画面下方展开。",
            "仰视角度": f"{target}位于画面中央，镜头缓慢下降至仰视角度，焦点锁定{target}，背景在画面上方延伸。",
            "上移镜头": "镜头从正前方启动，缓慢升高并俯视{target}，保持居中构图。随后缓慢下降回到平视位置，画面稳定。",
            "下移镜头": "镜头从高处俯视缓慢下降到平视，停留在特写位置。",
            "左摇镜头": f"镜头缓慢向左平移，{target}缓慢向右平移，从画面右侧消失，画面中仅保留向左移动的背景。",
            "右摇镜头": f"镜头缓慢向右平移，{target}缓慢向左平移，从画面左侧消失，画面中仅保留向右移动的背景。",
            "上仰镜头": f"镜头缓慢上移，{target}缓慢下移，从画面下方消失，画面中仅保留向上移动的背景。",
            "下俯镜头": f"镜头缓慢下移，{target}缓慢上移，从画面上方消失，画面中仅保留向下移动的背景。",
            "前进后退交替": f"镜头快速推进至{target}特写，然后平稳拉远至全景，重复两次，节奏一致，焦点始终锁定{target}。",
            "前进后退循环": f"镜头快速推进至特写，再平稳拉远至全景，重复两次，焦点始终锁定{target}。",
            "右弧线移动(半圈)": f"镜头从左前方缓慢移动到右前方，形成半圆运动轨迹，{target}清晰，背景轻微模糊。",
            "左弧线移动(半圈)": f"镜头从右前方缓慢移动到左前方，形成半圆运动轨迹，{target}清晰，背景轻微模糊。",
            "水平快速平移": f"{target}位于画面中央不动，镜头高速从左向右平移掠过{target}正面，背景形成流动残影，随后镜头迅速回到原位，构图稳定。",
            "水平环绕": f"{target}位于画面中央，保持静止，镜头从正前方启动，顺时针环绕180度至{target}背面，背景轻微模糊。镜头继续顺时针环绕180度回到正前方位置，{target}始终居中，画面稳定收束。",
            "环绕+拉近": f"镜头从正前方启动，顺时针环绕90度，同时缓慢拉近至局部细节，背景虚化，{target}清晰。",
            "环绕+翻转": f"{target}保持静止，正面朝向镜头。镜头从{target}右后方启动，顺时针水平环绕一整圈，画面同步翻转180度使{target}出现在画面下方，背景倒置悬浮在上方。镜头继续环绕至270°位置，在倒置状态中缓慢恢复水平构图，最终停留在{target}正面中近景，背景略带旋转残影。",
            "原地旋转": f"镜头从正前方启动，顺时针环绕90度至{target}侧面，再顺时针环绕90度至{target}背面，背景在运动中轻微模糊。最后镜头回到正前方，{target}始终居中，画面稳定收束。",
            "俯视旋转": f"镜头从上方斜俯角度启动，保持轻微下视。镜头顺时针环绕90度，同时缓慢下降至平视角度，最终停留在正前方构图，背景略虚化。",
            "垂直升降 + 停顿": f"镜头从平视缓慢升至俯视，短暂停顿后缓慢下降回到平视位置，焦点始终锁定{target}。",
            "对角上升": f"镜头从左下方斜向上缓慢移动至俯视位置，{target}始终居中。",
            "对角下移推进": f"{target}位于画面中央，镜头从右上方斜向下缓慢推进，逐渐接近{target}细节，焦点稳定锁定。",
            "对角穿越": f"镜头从左下方斜向上推进，掠过{target}上方后从右上方缓慢下降至平视位置，背景虚化再恢复。",
            "镜头抖动": "镜头短暂左右轻微抖动，随后恢复稳定。",
            "冲击震动": f"{target}位于画面中央，镜头贴近{target}的正前方，突然发生短暂震动抖动，背景轻微模糊，随后画面恢复稳定。",
            "贝塞尔拉远": "镜头先以正常速度后退，突然加速拉远，再次减速稳定收束，节奏感明显。",
            "贝塞尔拉近": "镜头先缓慢推进，再突然加速至特写，最后减速收束。"
        }
        desc = movement_descriptions.get(movement, "")
        return f"({desc}:{weight:.1f})" if weight != 1.0 else desc

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
                    "default": "火车站",
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
                    "default": "",
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
        # 使用默认图像预设内容，组件间用逗号分隔
        预设内容 = "{主体}, {主体细节}, {场景}, {光影}, {景别}, {构图}, {风格}"
        
        # 处理各组件，选择"无"或内容为空时不加入提示词
        组件 = {
            "主体": apply_weight(主体描述, 主体权重),
            "主体细节": apply_weight(表情动作描述, 表情动作权重),
            "场景": apply_weight(场景描述, 场景权重),
            "光影": apply_weight(光影描述, 光影权重),
            "风格": apply_weight(画面风格, 风格权重),
            "景别": apply_weight(景别描述, 景别权重),
            "构图": apply_weight(构图描述, 构图权重)
        }
        
        # 生成提示词，过滤空值
        提示词组件 = [value for value in 组件.values() if value]
        提示词 = "\n".join(提示词组件)
        
        # 处理附加提示词，使用逗号分隔
        if 附加提示词 and clean_text(附加提示词):
            加权附加词 = apply_weight(clean_text(附加提示词), 附加权重)
            if 加权附加词:
                if 提示词:
                    提示词 += "\n" + 加权附加词
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
            # 提取预设名称（去除扩展名）并去重
            preset_names = ["不删除预设"] + list({os.path.splitext(f)[0] for f in preset_files})
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

# 更新LOGO生成节点（使用中文输出组件名称）
class LOGO生成:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "LOGO形象": ("STRING", {
                    "multiline": False,
                    "default": "一只可爱的飞行员猪头相",
                    "display_name": "LOGO形象"
                }),
                "LOGO文字": ("STRING", {
                    "multiline": False,
                    "default": "猪的飞行梦",
                    "display_name": "LOGO文字"
                }),
            },
            "optional": {
                "颜色预设": (list(COLOR_PRESETS_DETAILS.keys()), {
                    "default": "无",
                    "display_name": "颜色预设"
                }),
                "附加提示词": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "附加提示词"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("LOGO提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问"

    def 生成提示词(self, LOGO形象, LOGO文字, 颜色预设="无", 附加提示词=""):
        parts = [
            f"LOGO形象: {clean_text(LOGO形象)}",
            f"LOGO文字: {clean_text(LOGO文字)}"
        ]
        
        if 颜色预设 != "无":
            parts.append(f"配色方案: {颜色预设}")
            if 颜色预设 in COLOR_PRESETS_DETAILS:
                color_info = COLOR_PRESETS_DETAILS[颜色预设]
                parts.extend([
                    f"主色: {color_info['colors'][0]} (占比{color_info['percentages'][0]})",
                    f"辅色: {color_info['colors'][1]} (占比{color_info['percentages'][1]})",
                    f"点缀色: {color_info['colors'][2]} (占比{color_info['percentages'][2]})"
                ])
            
        if clean_text(附加提示词):
            parts.append(f"附加提示词: {clean_text(附加提示词)}")
            
        return ("\n".join(parts),)

# 更新艺术字体生成节点（使用中文输出组件名称）
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

# 更新海报生成节点（使用中文输出组件名称）
class 海报生成:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "主体": ("STRING", {
                    "multiline": False,
                    "default": "一个开爱的小猪坐在书桌前\n周围环绕智能书包、电竞耳机、笔记本电脑、手机等 “新装备”\n小猪穿着学生制服\n整体时尚写实，色彩明快吸睛",
                    "display_name": "主体"
                }),
                "海报主题文字": ("STRING", {
                    "multiline": False,
                    "default": "猪的飞行梦",
                    "display_name": "海报主题文字"
                }),
            },
            "optional": {
                "海报类型": (POSTER_TYPES, {
                    "default": "无",
                    "display_name": "海报类型"
                }),
                "背景描述": ("STRING", {
                    "multiline": False,
                    "default": "校园教室",
                    "display_name": "背景描述"
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
                    "default": "特效艺术文字：开学焕新！全场1折！",
                    "display_name": "附加提示词"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("海报提示词",)
    FUNCTION = "生成提示词"
    CATEGORY = "📃提示词公式/千问"

    def 生成提示词(self, 主体, 海报主题文字, 海报类型="无", 背景描述="", 字体颜色="无", 背景颜色="无", 附加提示词=""):
        parts = [
            f"主体: {clean_text(主体)}",
            f"海报主题文字: {clean_text(海报主题文字)}"
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

# 更新千问图像节点（使用中文输出组件名称）
class 千问图像:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "主体": ("STRING", {
                    "multiline": False,
                    "default": "一个年轻中国20岁少女",
                    "display_name": "主体"
                }),
            },
            "optional": {
                "细节": ("STRING", {
                    "multiline": True,
                    "default": "长发自然垂落，光泽柔顺，眼神清澈，透着一丝青春的俏皮，脸庞在柔和的光线下显得格外温暖，嘴角带着淡淡的微笑，穿着一件舒适的紫色jk海军制服",
                    "display_name": "细节"
                }),
                "场景": ("STRING", {
                    "multiline": False,
                    "default": "一个典型的宿舍环境，晾晒的内裤、丝袜、文胸内衣物随意挂在一旁",
                    "display_name": "场景"
                }),
                "景别": (SHOT_TYPES, {
                    "default": "无",
                    "display_name": "景别"
                }),
                "附加提示词": ("STRING", {
                    "multiline": True,
                    "default": "整体画面带有一种随性而真实的氛围，既有青春的活力，又透露出日常生活的朴实",
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

# 更新表情包生成节点（使用中文输出组件名称）
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

# 新增提示词保存为预设节点
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

    def 保存预设(self, 新预设名称, 提示词="", 保存为TXT="开", 保存为JSON="关"):
        if not 提示词.strip():
            return ("错误: 提示词不能为空",)
        
        if 保存为TXT == "关" and 保存为JSON == "关":
            return ("错误: 必须至少选择一种保存格式",)
        
        操作结果 = []
        
        def 保存文件(文件名, 内容):
            try:
                文件路径 = PRESET_DIR / 文件名
                with open(文件路径, 'w', encoding='utf-8') as f:
                    f.write(内容)
                return True
            except Exception as e:
                print(f"保存预设文件错误: {e}")
                return False
        
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

# 节点映射表
NODE_CLASS_MAPPINGS = {
    "提示词预设": 提示词预设,
    "视频提示词公式": 视频提示词公式,
    "图像提示词公式": 图像提示词公式,
    "历史记录和预设管理": 历史记录和预设管理,
    "提示词保存为预设": 提示词保存为预设,
    "LOGO生成": LOGO生成,
    "艺术字体生成": 艺术字体生成,
    "海报生成": 海报生成,
    "千问图像": 千问图像,
    "表情包生成": 表情包生成
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "提示词预设": "提示词预设",
    "视频提示词公式": "视频提示词公式",
    "图像提示词公式": "图像提示词公式",
    "历史记录和预设管理": "历史记录和预设管理",
    "提示词保存为预设": "提示词保存为预设",
    "LOGO生成": "LOGO生成",
    "艺术字体生成": "艺术字体生成",
    "海报生成": "海报生成",
    "千问图像": "千问图像",
    "表情包生成": "表情包生成"
}