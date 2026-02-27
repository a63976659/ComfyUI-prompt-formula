import os
import re

def get_preset_list(directory):
    """从指定目录获取 txt 预设文件列表，并按字母排序"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        return ["无"]
    files = [f for f in os.listdir(directory) if f.lower().endswith('.txt')]
    if not files:
        return ["无"]
    files.sort()
    return ["无"] + files

def sanitize_filename(name):
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|\n\r]', "", name).strip()

class 智能体对话预设:
    """智能体对话预设 - 支持读取和保存特定主体的对话指令"""
    
    @classmethod
    def INPUT_TYPES(cls):
        current_dir = os.path.dirname(__file__)
        plugin_root = os.path.dirname(current_dir)
        preset_dir = os.path.join(plugin_root, "提示词预设")
        subject_dir = os.path.join(preset_dir, "主体描述")
        system_dir = os.path.join(preset_dir, "系统指令")

        os.makedirs(subject_dir, exist_ok=True)
        os.makedirs(system_dir, exist_ok=True)

        subject_presets = get_preset_list(subject_dir)
        system_presets = get_preset_list(system_dir)
        
        return {
            "required": {
                "模式": (["使用预设", "手动输入"], {"default": "使用预设"}),
                
                # 预设模式组件
                "预设_主体描述": (subject_presets, {"default": "无"}),
                "预设_系统指令": (system_presets, {"default": "无"}),
                
                # 隐藏组件：供前端 JS 的 CSS 文本框传入数据使用
                "手动_主体描述": ("STRING", {"multiline": False, "default": ""}),
                "手动_系统指令": ("STRING", {"multiline": False, "default": ""}),
                "保存为预设": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("主体描述", "系统指令")
    FUNCTION = "处理预设"
    CATEGORY = "📕提示词公式/智能体"

    def 处理预设(self, 模式, 预设_主体描述, 预设_系统指令, 手动_主体描述, 手动_系统指令, 保存为预设):
        current_dir = os.path.dirname(__file__)
        plugin_root = os.path.dirname(current_dir)
        preset_dir = os.path.join(plugin_root, "提示词预设")
        subject_dir = os.path.join(preset_dir, "主体描述")
        system_dir = os.path.join(preset_dir, "系统指令")
        
        subject_out = ""
        system_out = ""
        
        # 1. 预设模式
        if 模式 == "使用预设":
            if 预设_主体描述 != "无":
                try:
                    with open(os.path.join(subject_dir, 预设_主体描述), 'r', encoding='utf-8') as f:
                        subject_out = f.read().strip()
                except Exception as e:
                    print(f"读取主体描述失败: {e}")

            if 预设_系统指令 != "无":
                try:
                    with open(os.path.join(system_dir, 预设_系统指令), 'r', encoding='utf-8') as f:
                        system_out = f.read().strip()
                except Exception as e:
                    print(f"读取系统指令失败: {e}")
            
        # 2. 手动输入模式
        elif 模式 == "手动输入":
            subject_out = 手动_主体描述
            system_out = 手动_系统指令
            
            # 如果开启了保存
            if 保存为预设:
                
                # ------ 单独处理主体描述的保存 ------
                if subject_out.strip():
                    # 以自身内容生成文件名
                    base_name_sub = sanitize_filename(subject_out.strip())
                    base_name_sub = base_name_sub[:6] if base_name_sub else "未命名"
                    
                    # 独立的防重名校验
                    filename_sub = f"{base_name_sub}.txt"
                    counter_sub = 1
                    while os.path.exists(os.path.join(subject_dir, filename_sub)):
                        filename_sub = f"{base_name_sub}_{counter_sub}.txt"
                        counter_sub += 1
                        
                    # 保存
                    os.makedirs(subject_dir, exist_ok=True)
                    with open(os.path.join(subject_dir, filename_sub), 'w', encoding='utf-8') as f:
                        f.write(subject_out)
                    print(f"✅ [智能体对话预设] 主体描述已保存为: {filename_sub}")


                # ------ 单独处理系统指令的保存 ------
                if system_out.strip():
                    # 以自身内容生成文件名
                    base_name_sys = sanitize_filename(system_out.strip())
                    base_name_sys = base_name_sys[:6] if base_name_sys else "未命名"
                    
                    # 独立的防重名校验
                    filename_sys = f"{base_name_sys}.txt"
                    counter_sys = 1
                    while os.path.exists(os.path.join(system_dir, filename_sys)):
                        filename_sys = f"{base_name_sys}_{counter_sys}.txt"
                        counter_sys += 1
                        
                    # 保存
                    os.makedirs(system_dir, exist_ok=True)
                    with open(os.path.join(system_dir, filename_sys), 'w', encoding='utf-8') as f:
                        f.write(system_out)
                    print(f"✅ [智能体对话预设] 系统指令已保存为: {filename_sys}")
                
        return (subject_out, system_out)