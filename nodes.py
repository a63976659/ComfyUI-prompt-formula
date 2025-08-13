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
    "无", "像素风格", "中国水墨风格", "油画风格", "皮克斯风格",
    "素描风格", "黑白电影风格", "科幻风格", "抽象风格", "迷幻风格",
    "文艺复兴", "水彩风格", "赛博朋克风格", "写实风格", "动漫风格",
    "毛毡风格", "3D卡通风格", "木偶动画", "3D游戏", "黏土风格", "二次元", "黑白动画"
]

CAMERA_MOVEMENTS = [
    "无", "右摇镜头", "左摇镜头", "上仰镜头", "下俯镜头",
    "推近镜头", "拉远镜头", "上移镜头", "下移镜头",
    "左弧线移动", "右弧线移动", "手持镜头", "跟随镜头", "环绕运镜"
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
    "荧光", "阴天光", "混合光", "晴天光"
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
    "无", "街舞", "跑步", "散步", "滑滑板", "踢足球", 
    "网球", "羽毛球", "跳绳", "乒乓球", "滑雪", "篮球", 
    "橄榄球", "顶碗舞", "侧手翻", "玩手机", "打电话"
]

EMOTIONS = [
    "无", "愤怒", "恐惧", "高兴", "悲伤", "惊讶"
]

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
            # 尝试将内容解析为JSON
            try:
                # 如果内容是有效的JSON，直接保存
                json_data = json.loads(content)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # 如果不是有效的JSON，包装成带prompt键的对象
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({"prompt": content.strip()}, f, ensure_ascii=False, indent=2)
        else:  # .txt格式
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
        
        # 立即刷新缓存
        global _preset_cache, _last_refresh_time
        _preset_cache = _actual_load_presets()
        _last_refresh_time = time.time()
        
        folder_paths.refresh_folder("prompt_presets")
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
        # 对于预设文件，检查是否存在
        if ext in ['.txt', '.json']:
            preset_path = folder_paths.get_full_path("prompt_presets", f"{preset_name}{ext}")
        else:
            # 对于预览文件，直接构造路径
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
            try:
                os.remove(preset_path)
                deleted_files.append(os.path.basename(preset_path))
            except PermissionError:
                return False, f"无权限删除文件 {os.path.basename(preset_path)}，请检查文件权限"
            except Exception as e:
                return False, f"删除文件 {os.path.basename(preset_path)} 失败: {str(e)}"
    
    # 立即刷新缓存
    global _preset_cache, _last_refresh_time
    _preset_cache = _actual_load_presets()
    _last_refresh_time = time.time()
    
    folder_paths.refresh_folder("prompt_presets")
    
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
                      镜头类型, 镜头类型权重, 运镜方式, 运镜权重, 
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
            "运镜": apply_weight(运镜方式, 运镜权重),
            "色调": apply_weight(色调, 色调权重),
            "视觉风格": apply_weight(视觉风格, 风格权重)
        }
        
        # 生成提示词，过滤空值
        提示词组件 = [value for value in 组件.values() if value]
        提示词 = ", ".join(提示词组件)
        
        # 处理附加提示词，使用逗号分隔
        if 附加提示词 and clean_text(附加提示词):
            加权附加词 = apply_weight(clean_text(附加提示词), 附加权重)
            if 加权附加词:
                if 提示词:
                    提示词 += ", " + 加权附加词
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
        提示词 = ", ".join(提示词组件)
        
        # 处理附加提示词，使用逗号分隔
        if 附加提示词 and clean_text(附加提示词):
            加权附加词 = apply_weight(clean_text(附加提示词), 附加权重)
            if 加权附加词:
                if 提示词:
                    提示词 += ", " + 加权附加词
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

# 节点映射
NODE_CLASS_MAPPINGS = {
    "视频提示词公式": 视频提示词公式,
    "图像提示词公式": 图像提示词公式,
    "提示词预设": 提示词预设,
    "历史记录和预设管理": 历史记录和预设管理
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "视频提示词公式": "视频提示词公式",
    "图像提示词公式": "图像提示词公式",
    "提示词预设": "提示词预设",
    "历史记录和预设管理": "历史记录和预设管理"
}
    