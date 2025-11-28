# 工具函数.py
import os
import re
import time
import json
import logging
from pathlib import Path
from datetime import datetime

import folder_paths

# 获取插件当前文件夹路径
PLUGIN_DIR = Path(__file__).parent.resolve()
# 定义预设文件夹 - 修复路径问题
PRESET_DIR = PLUGIN_DIR / "提示词预设"
# 确保预设文件夹存在
PRESET_DIR.mkdir(parents=True, exist_ok=True)

# 预设缓存及刷新机制
_preset_cache = {}
_last_refresh_time = 0
CACHE_TIMEOUT = 30

# 在ComfyUI的路径管理中注册预设文件夹
def register_preset_folder():
    """注册预设文件夹到ComfyUI"""
    if "prompt_presets" not in folder_paths.folder_names_and_paths:
        folder_paths.folder_names_and_paths["prompt_presets"] = (
            [str(PRESET_DIR)],
            [".txt", ".json"]
        )
    # 确保预设文件夹在ComfyUI的搜索路径中
    if str(PRESET_DIR) not in folder_paths.folder_names_and_paths["prompt_presets"][0]:
        folder_paths.folder_names_and_paths["prompt_presets"][0].append(str(PRESET_DIR))

# 调用注册函数
register_preset_folder()

def initialize_files():
    """初始化必要的目录和文件"""
    # 只确保预设文件夹存在
    PRESET_DIR.mkdir(parents=True, exist_ok=True)

def clean_text(text):
    """清理文本，去除多余符号和空格 - 增强安全性"""
    if text is None:
        return ""
    
    # 确保是字符串类型
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return ""
    
    # 清理文本
    cleaned = re.sub(r',', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned.strip())
    
    # 确保返回字符串，不为None
    return cleaned or ""

def apply_weight(text, weight, default_val="无"):
    """统一处理权重应用，支持默认值过滤 - 增强安全性"""
    if text is None:
        return ""
        
    cleaned_text = clean_text(text)
    if not cleaned_text or cleaned_text == default_val:
        return ""
    
    # 确保weight是数值类型
    try:
        weight_float = float(weight)
    except (TypeError, ValueError):
        weight_float = 1.0
    
    if weight_float == 1.0:
        return cleaned_text
    
    return f"({cleaned_text}:{weight_float:.1f})"

def get_preset_preview(preset_name):
    """获取预设的预览媒体文件路径 - 增强安全性"""
    if not preset_name:
        return None, None
        
    # 首先尝试从注册的预设文件夹中查找
    txt_preset_path = folder_paths.get_full_path("prompt_presets", f"{preset_name}.txt")
    json_preset_path = folder_paths.get_full_path("prompt_presets", f"{preset_name}.json")
    
    base_path = None
    if txt_preset_path:
        base_path = os.path.splitext(txt_preset_path)[0]
    elif json_preset_path:
        base_path = os.path.splitext(json_preset_path)[0]
    else:
        # 如果通过folder_paths没找到，直接检查预设文件夹
        txt_path = PRESET_DIR / f"{preset_name}.txt"
        json_path = PRESET_DIR / f"{preset_name}.json"
        if txt_path.exists():
            base_path = str(txt_path.with_suffix(''))
        elif json_path.exists():
            base_path = str(json_path.with_suffix(''))
    
    if not base_path:
        return None, None
        
    for ext in ['.mp4']:
        preview_path = f"{base_path}{ext}"
        if os.path.exists(preview_path):
            return preview_path, 'video'
    
    for ext in ['.png', '.jpg', '.jpeg']:
        preview_path = f"{base_path}{ext}"
        if os.path.exists(preview_path):
            return preview_path, 'image'
    
    return None, None

def _actual_load_presets():
    """实际加载预设的函数（内部使用）"""
    presets = {}
    
    # 方法1: 通过ComfyUI的folder_paths获取
    try:
        preset_files = folder_paths.get_filename_list("prompt_presets")
        if preset_files:
            preset_files.sort()  # 按文件名排序
    except Exception as e:
        logging.warning(f"通过folder_paths获取预设文件失败: {str(e)}")
        preset_files = []
    
    # 方法2: 如果上面没找到，直接扫描预设文件夹
    if not preset_files:
        try:
            for ext in ['.txt', '.json']:
                for file_path in PRESET_DIR.glob(f"*{ext}"):
                    if file_path.is_file():
                        preset_files.append(file_path.name)
            if preset_files:
                preset_files.sort()
        except Exception as e:
            logging.error(f"直接扫描预设文件夹失败: {str(e)}")
            return presets
    
    for preset_file in preset_files:
        try:
            # 首先尝试通过folder_paths获取完整路径
            preset_path = folder_paths.get_full_path("prompt_presets", preset_file)
            if not preset_path:
                # 如果没找到，直接使用预设文件夹中的路径
                preset_path = PRESET_DIR / preset_file
                if not preset_path.exists():
                    continue
            
            file_name, file_ext = os.path.splitext(preset_file)
            preset_name = file_name
            
            content = ""
            if file_ext.lower() == ".txt":
                with open(preset_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
            elif file_ext.lower() == ".json":
                with open(preset_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    if isinstance(json_data, dict):
                        if "prompt" in json_data:
                            content = str(json_data["prompt"]).strip()
                        elif "content" in json_data:
                            content = str(json_data["content"]).strip()
                        elif "positive" in json_data:
                            content = str(json_data["positive"]).strip()
                        else:
                            for value in json_data.values():
                                if isinstance(value, str):
                                    content = value.strip()
                                    break
                    elif isinstance(json_data, str):
                        content = json_data.strip()
            
            preview_path, preview_type = get_preset_preview(preset_name)
            
            if content and preset_name not in presets:
                presets[preset_name] = {
                    "content": content,
                    "preview_path": preview_path,
                    "preview_type": preview_type,
                    "file_type": file_ext.lower()
                }
        
        except Exception as e:
            logging.error(f"读取预设文件 {preset_file} 出错: {str(e)}")
    
    return presets

def load_presets():
    """加载所有预设（使用缓存机制）"""
    global _preset_cache, _last_refresh_time
    now = time.time()
    if now - _last_refresh_time > CACHE_TIMEOUT or not _preset_cache:
        _preset_cache = _actual_load_presets()
        _last_refresh_time = now
    return _preset_cache.copy()

def save_preset(preset_name, content):
    """保存预设，支持TXT和JSON格式"""
    if not preset_name:
        return None
        
    if preset_name.endswith((".txt", ".json")):
        file_name = preset_name
        file_ext = os.path.splitext(preset_name)[1].lower()
        preset_base_name = os.path.splitext(preset_name)[0]
    else:
        file_ext = ".txt"
        file_name = f"{preset_name}{file_ext}"
        preset_base_name = preset_name
    
    try:
        save_dir = folder_paths.folder_names_and_paths["prompt_presets"][0][0]
        file_path = os.path.join(save_dir, file_name)
        
        if file_ext == ".json":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
        
        global _preset_cache, _last_refresh_time
        _preset_cache = _actual_load_presets()
        _last_refresh_time = time.time()
        
        return preset_base_name
    except Exception as e:
        logging.error(f"保存预设文件出错: {str(e)}")
    return None

def delete_preset(preset_name):
    """删除预设文件及相关预览文件"""
    if not preset_name:
        return False, "预设名称不能为空"
    
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
        except Exception as e:
            return False, f"删除文件 {preset_name}{ext} 失败: {str(e)}"
    
    global _preset_cache, _last_refresh_time
    _preset_cache = {}
    _last_refresh_time = 0
    
    if not deleted_files:
        return False, f"预设 '{preset_name}' 不存在"
    
    return True, f"预设 '{preset_name}' 及相关文件已成功删除"

# 初始化文件系统
initialize_files()