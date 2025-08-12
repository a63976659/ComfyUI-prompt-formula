import os
import re
from pathlib import Path
import json
from datetime import datetime
import logging

# 引入ComfyUI的路径管理和工具
import folder_paths

# 获取插件当前文件夹路径
PLUGIN_DIR = Path(__file__).parent.resolve()
# 定义模板文件夹为插件目录下的Template子文件夹
TEMPLATE_DIR = PLUGIN_DIR / "Template"
# 确保模板文件夹存在
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# 在ComfyUI的路径管理中注册模板文件夹
if "prompt_templates" not in folder_paths.folder_names_and_paths:
    folder_paths.folder_names_and_paths["prompt_templates"] = (
        [str(TEMPLATE_DIR)],  # 模板文件夹路径
        [".txt"]  # 支持的模板文件扩展名
    )

# 历史记录文件存储在插件目录下
HISTORY_FILE = PLUGIN_DIR / "prompt_history.json"
MAX_HISTORY_COUNT = 10

# 初始化必要的目录和文件
def initialize_files():
    # 创建默认模板（如果不存在）
    default_templates = {
        "默认.txt": """girl,1girl,solo,brown hair,black hair,bare shoulders,
brown eyes,lips,covering,covering breasts,realistic,
Figure curve,Light and shadow art""",
        
        "电影风格.txt": """一位身着少数民族服饰的黑发苗族少女站在云雾缭绕的山顶，
周围是古老的石雕和飘扬的经幡，
她缓缓转身，衣袖随风舞动，
逆光拍摄，暖色调，水墨画风格""",
        
        "动漫风格.txt": """Ultra wide angle shooting, a girl dressed in an ancient mage costume, Hanfu, handsome,
with gestures forming spells, martial arts and fairy tale atmosphere,
carrying a sky filled with water vapor, game characters, water waves,
without looking at the camera, writing calligraphy,
surrounded by long and transparent scrolls, floating transparent Hanzi,
dynamic action style, rotation, magical realism,
the highest quality, masterpiece, CG, HDR, high-definition,
extremely fine, detailed face Superheroes, heroes,
detail ultra high definition, OC rendering, Taoist runes""",
        
        "产品展示.txt": """The design illustration of a cute pig doll model showcases a fashionable and modern aesthetic style.
The core part of the illustration is the doll itself, highlighting its ability to immerse users in a fantastical ancient-style scene.
The background is an ancient-style architectural landscape with bird chirping and fragrant flowers,
while the foreground is shrouded in soft and dreamy colorful clouds.
The soft and blurry clouds in the background create depth and add a sense of multi-layeredness.
The exquisite lighting effects enhance the vitality of the entire scene"""
    }
    
    for name, content in default_templates.items():
        file_path = TEMPLATE_DIR / name
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
    
    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

# 获取模板的预览媒体文件路径
def get_template_preview(template_name):
    template_path = folder_paths.get_full_path("prompt_templates", f"{template_name}.txt")
    if not template_path:
        return None, None
        
    base_path = os.path.splitext(template_path)[0]
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

# 加载所有模板（使用folder_paths管理）
def load_templates():
    templates = {}
    template_files = folder_paths.get_filename_list("prompt_templates")
    
    for template_file in template_files:
        try:
            template_path = folder_paths.get_full_path("prompt_templates", template_file)
            if not template_path:
                continue
                
            with open(template_path, "r", encoding="utf-8") as f:
                template_name = os.path.splitext(template_file)[0]
                preview_path, preview_type = get_template_preview(template_name)
                templates[template_name] = {
                    "content": f.read().strip(),
                    "preview_path": preview_path,
                    "preview_type": preview_type
                }
        except Exception as e:
            logging.error(f"读取模板文件 {template_file} 出错: {str(e)}")
    return templates

# 保存模板为txt文件
def save_template(template_name, content):
    if not template_name.endswith(".txt"):
        template_name += ".txt"
    
    save_dir = folder_paths.folder_names_and_paths["prompt_templates"][0][0]
    file_path = os.path.join(save_dir, template_name)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        folder_paths.refresh_folder("prompt_templates")
        return os.path.splitext(template_name)[0]
    except Exception as e:
        logging.error(f"保存模板文件出错: {str(e)}")
        return None

# 删除模板txt文件及相关预览文件
def delete_template(template_name):
    if not template_name:
        return False, "模板名称不能为空"
    
    default_templates = ["默认", "电影风格", "动漫风格", "产品展示"]
    if template_name in default_templates:
        return False, "默认模板不能删除"
    
    template_path = folder_paths.get_full_path("prompt_templates", f"{template_name}.txt")
    if not template_path:
        return False, f"模板 '{template_name}' 不存在"
    
    extensions = ['.txt', '.mp4', '.png', '.jpg', '.jpeg']
    deleted_files = []
    
    for ext in extensions:
        file_path = os.path.splitext(template_path)[0] + ext
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(os.path.basename(file_path))
            except Exception as e:
                return False, f"删除文件 {os.path.basename(file_path)} 失败: {str(e)}"
    
    folder_paths.refresh_folder("prompt_templates")
    
    if not deleted_files:
        return False, f"模板 '{template_name}' 不存在"
    
    return True, f"模板 '{template_name}' 及相关文件已成功删除"

# 读取历史记录
def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# 保存到历史记录
def save_to_history(prompt, name, manual_save=False):
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

# 提示词模板选择节点
class 提示词模板选择:
    tooltip = "模板文件储存在此插件Template文件夹，可通过历史记录和模板管理节点创建新模板。也可直接在Template文件夹中手动添加、编辑或删除.txt格式的模板文件。"

    @classmethod
    def INPUT_TYPES(cls):
        try:
            template_files = folder_paths.get_filename_list("prompt_templates")
            template_names = [os.path.splitext(f)[0] for f in template_files]
            
            if not template_names:
                template_names = ["默认"]
                templates = {"默认": {"content": "{主体}, {细节}, {场景}, {运镜}, {风格}", 
                                     "preview_path": None, "preview_type": None}}
            else:
                templates = load_templates()
            
            template_options = template_names
            
            preview_metadata = {}
            for name in template_names:
                preview_metadata[name] = {
                    "type": templates[name]["preview_type"] or "none",
                    "path": templates[name]["preview_path"] or ""
                }
            
            return {
                "required": {
                    "模板名称": (template_options, {
                        "default": template_options[0] if template_options else "默认",
                        "tooltip": "模板文件储存在此插件的Template文件夹中",  # 工具提示中添加存储位置信息
                        "preview_metadata": json.dumps(preview_metadata)
                    }),
                }
            }
        except Exception as e:
            logging.error(f"提示词模板选择节点初始化错误: {str(e)}")
            return {
                "required": {
                    "模板名称": (["默认"], {"default": "默认"}),
                }
            }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("模板名称", "模板内容")
    FUNCTION = "选择模板"
    CATEGORY = "📃提示词公式"

    def 选择模板(self, 模板名称):
        name = 模板名称
        
        templates = load_templates()
        template_info = templates.get(name, {"content": "{主体}, {细节}, {场景}, {运镜}, {风格}"})
        
        return (name, template_info["content"])

# 视频提示词公式节点
class 视频提示词公式:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "主体描述": ("STRING", {
                    "multiline": False,
                    "default": "一个女孩",
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
                "主体细节描述": ("STRING", {
                    "multiline": False,
                    "default": "精致的五官，柔和的灯光",
                    "display_name": "主体细节描述"
                }),
                "主体细节权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "主体细节权重"
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
                "运镜方式": ([
                    "无运镜", "右摇镜头", "左摇镜头", "上仰镜头", "下俯镜头",
                    "推近镜头", "拉远镜头", "上移镜头", "下移镜头",
                    "左弧线移动", "右弧线移动"
                ], {"default": "无运镜", "display_name": "运镜方式"}),
                "运镜权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "运镜权重"
                }),
                "画面风格": ([
                    "无风格", "像素风格", "中国水墨风格", "油画风格", "皮克斯风格",
                    "素描风格", "黑白电影风格", "科幻风格", "抽象风格", "迷幻风格",
                    "文艺复兴", "水彩风格", "赛博朋克风格", "写实风格", "动漫风格"
                ], {"default": "无风格", "display_name": "画面风格"}),
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
                "景别描述": ([
                    "不指定景别", "大远景", "远景", "全景", "中景", 
                    "中近景", "半身景", "近景", "特写", "大特写"
                ], {"default": "不指定景别", "display_name": "景别描述"}),
                "景别权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "景别权重"
                }),
                # 构图描述选项
                "构图描述": ([
                    "无描述", "黄金分割构图", "对称构图", "三分法构图", 
                    "对角线构图", "三角形构图", "S形构图", "框式构图", 
                    "放射式构图", "紧凑式构图", "留白构图", "X形构图", 
                    "L形构图", "隧道构图"
                ], {"default": "无描述", "display_name": "构图描述"}),
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

    def 生成提示词(self, 主体描述, 主体权重, 主体细节描述, 主体细节权重, 
                      场景描述, 场景权重, 光影描述, 光影权重, 
                      运镜方式, 运镜权重, 画面风格, 风格权重,
                      景别描述="不指定景别", 景别权重=1.0,
                      构图描述="无描述", 构图权重=1.0,
                      附加提示词=None, 附加权重=1.0, 自动保存到历史=True):
        # 使用默认视频模板内容，组件间用逗号分隔
        模板内容 = "{主体}, {主体细节}, {场景}, {光影}, {景别}, {构图}, {运镜}, {风格}"
        
        # 清理文本函数
        def 清理文本(文本):
            # 先去除原有逗号和多余空格，再处理
            cleaned = re.sub(r',', ' ', 文本)
            cleaned = re.sub(r'\s+', ' ', cleaned.strip())  # 合并多个空格
            return cleaned if cleaned else ""
        
        # 智能权重应用函数
        def 应用权重(文本, 权重):
            文本 = 清理文本(文本)
            if not 文本 or 权重 == 1.0:
                return 文本
            return f"({文本}:{权重:.1f})"
        
        # 处理各组件，选择默认选项时不加入提示词
        组件 = {
            "主体": 应用权重(主体描述, 主体权重),
            "主体细节": 应用权重(主体细节描述, 主体细节权重),
            "场景": 应用权重(场景描述, 场景权重),
            "光影": 应用权重(光影描述, 光影权重),
            "运镜": 应用权重(运镜方式 if 运镜方式 != "无运镜" else "", 运镜权重),
            "风格": 应用权重(画面风格 if 画面风格 != "无风格" else "", 风格权重),
            "景别": 应用权重(景别描述 if 景别描述 != "不指定景别" else "", 景别权重),
            "构图": 应用权重(构图描述 if 构图描述 != "无描述" else "", 构图权重)
        }
        
        # 生成提示词
        提示词 = 模板内容.format(**组件)
        
        # 处理附加提示词，使用逗号分隔
        if 附加提示词 and 清理文本(附加提示词):
            加权附加词 = 应用权重(清理文本(附加提示词), 附加权重)
            提示词 += ", " + 加权附加词
        
        # 最终清理：确保没有连续的逗号
        提示词 = re.sub(r',\s+,', ',', 提示词)  # 处理连续逗号
        提示词 = re.sub(r'\s+', ' ', 提示词).strip()  # 清理空格
        
        # 处理历史记录保存
        if 自动保存到历史:
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
                    "default": "一个女孩",
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
                "主体细节描述": ("STRING", {
                    "multiline": False,
                    "default": "精致的五官，细腻的皮肤",
                    "display_name": "主体细节描述"
                }),
                "主体细节权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "主体细节权重"
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
                "画面风格": ([
                    "无风格", "像素风格", "中国水墨风格", "油画风格", "皮克斯风格",
                    "素描风格", "黑白电影风格", "科幻风格", "抽象风格", "迷幻风格",
                    "文艺复兴", "水彩风格", "赛博朋克风格", "写实风格", "动漫风格"
                ], {"default": "无风格", "display_name": "画面风格"}),
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
                "景别描述": ([
                    "不指定景别", "大远景", "远景", "全景", "中景", 
                    "中近景", "半身景", "近景", "特写", "大特写"
                ], {"default": "不指定景别", "display_name": "景别描述"}),
                "景别权重": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 2.0, 
                    "step": 0.1,
                    "display": "slider",
                    "display_name": "景别权重"
                }),
                # 构图描述选项
                "构图描述": ([
                    "无描述", "黄金分割构图", "对称构图", "三分法构图", 
                    "对角线构图", "三角形构图", "S形构图", "框式构图", 
                    "放射式构图", "紧凑式构图", "留白构图", "X形构图", 
                    "L形构图", "隧道构图"
                ], {"default": "无描述", "display_name": "构图描述"}),
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

    def 生成提示词(self, 主体描述, 主体权重, 主体细节描述, 主体细节权重, 
                      场景描述, 场景权重, 光影描述, 光影权重,
                      画面风格, 风格权重,
                      景别描述="不指定景别", 景别权重=1.0,
                      构图描述="无描述", 构图权重=1.0,
                      附加提示词=None, 附加权重=1.0, 自动保存到历史=True):
        # 使用默认图像模板内容，组件间用逗号分隔
        模板内容 = "{主体}, {主体细节}, {场景}, {光影}, {景别}, {构图}, {风格}"
        
        # 清理文本函数
        def 清理文本(文本):
            # 先去除原有逗号和多余空格，再处理
            cleaned = re.sub(r',', ' ', 文本)
            cleaned = re.sub(r'\s+', ' ', cleaned.strip())  # 合并多个空格
            return cleaned if cleaned else ""
        
        # 智能权重应用函数
        def 应用权重(文本, 权重):
            文本 = 清理文本(文本)
            if not 文本 or 权重 == 1.0:
                return 文本
            return f"({文本}:{权重:.1f})"
        
        # 处理各组件，选择默认选项时不加入提示词
        组件 = {
            "主体": 应用权重(主体描述, 主体权重),
            "主体细节": 应用权重(主体细节描述, 主体细节权重),
            "场景": 应用权重(场景描述, 场景权重),
            "光影": 应用权重(光影描述, 光影权重),
            "风格": 应用权重(画面风格 if 画面风格 != "无风格" else "", 风格权重),
            "景别": 应用权重(景别描述 if 景别描述 != "不指定景别" else "", 景别权重),
            "构图": 应用权重(构图描述 if 构图描述 != "无描述" else "", 构图权重)
        }
        
        # 生成提示词
        提示词 = 模板内容.format(**组件)
        
        # 处理附加提示词，使用逗号分隔
        if 附加提示词 and 清理文本(附加提示词):
            加权附加词 = 应用权重(清理文本(附加提示词), 附加权重)
            提示词 += ", " + 加权附加词
        
        # 最终清理：确保没有连续的逗号
        提示词 = re.sub(r',\s+,', ',', 提示词)  # 处理连续逗号
        提示词 = re.sub(r'\s+', ' ', 提示词).strip()  # 清理空格
        
        # 处理历史记录保存
        if 自动保存到历史:
            timestamp = datetime.now().strftime("%H:%M")
            subject_preview = 主体描述[:10] + ("..." if len(主体描述) > 10 else "")
            save_name = f"[图像] {timestamp} {subject_preview}"
            save_to_history(提示词, save_name, manual_save=False)
        
        return (提示词,)
    
# 历史记录和模板管理节点 - 修复JSON序列化错误版本
class 历史记录和模板管理:
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
                "将选中历史存为模板": ("BOOLEAN", {
                    "default": False,
                    "display_name": "将选中历史存为模板"
                }),
                "新模板名称": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "display_name": "模板名称（保存时必填）"
                }),
                "从输入保存到历史": ("BOOLEAN", {
                    "default": False,
                    "display_name": "将输入提示词保存到历史"
                }),
                "清空历史记录": ("BOOLEAN", {
                    "default": False,
                    "display_name": "清空所有历史记录"
                }),
                "确认删除模板": ("BOOLEAN", {
                    "default": False,
                    "display_name": "确认删除所选模板"
                }),
                "选择要删除的模板": (["不删除模板"], {"default": "不删除模板", "display_name": "选择要删除的模板"}),
                "新建模板内容": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "display_name": "新建模板内容（使用合适的变量，建议用逗号分隔）"
                })
            }
        }
        
        try:
            template_files = folder_paths.get_filename_list("prompt_templates")
            template_names = ["不删除模板"] + [os.path.splitext(f)[0] for f in template_files]
            history_options = get_history_options()
            
            # 关键修复：使用字符串引用外部验证函数，避免JSON序列化问题
            base_components["optional"]["选择历史记录"] = (
                history_options, 
                {
                    "default": "不选择历史记录", 
                    "display_name": "选择历史记录",
                    "validate": "validate_history"  # 使用函数名称字符串而非函数对象
                }
            )
            base_components["optional"]["选择要删除的模板"] = (
                template_names, 
                {"default": "不删除模板", "display_name": "选择要删除的模板"}
            )
            
            return base_components
        except Exception as e:
            logging.error(f"历史记录和模板管理节点组件加载错误: {str(e)}")
            return base_components
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("选中的提示词", "历史记录列表", "操作结果")
    FUNCTION = "管理历史和模板"
    CATEGORY = "📃提示词公式"
    
    def 管理历史和模板(self, 输入提示词=None, 查看历史记录=False, 选择历史记录="不选择历史记录",
                      将选中历史存为模板=False, 新模板名称="", 从输入保存到历史=False, 清空历史记录=False,
                      选择要删除的模板="不删除模板", 确认删除模板=False, 新建模板内容=""):
        操作结果 = ""
        
        try:
            # 先刷新历史记录选项，确保使用最新数据
            current_history = load_history()
            current_history_options = get_history_options()
            
            # 验证选择的历史记录是否仍然有效
            if 选择历史记录 not in current_history_options and 选择历史记录 != "不选择历史记录":
                操作结果 += f"警告: 所选历史记录已不存在，已自动重置\n"
                选择历史记录 = "不选择历史记录"
            
            if 新模板名称 and 新建模板内容:
                saved_name = save_template(新模板名称, 新建模板内容)
                if saved_name:
                    操作结果 += f"新模板 '{saved_name}' 已保存到 Template 文件夹\n"
                else:
                    操作结果 += "保存模板失败\n"
            
            if 选择要删除的模板 != "不删除模板" and 确认删除模板:
                success, message = delete_template(选择要删除的模板)
                操作结果 += message + "\n"
            
            if 清空历史记录:
                with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False)
                操作结果 += "历史记录已清空\n"
                # 清空后重置选择
                选择历史记录 = "不选择历史记录"
            
            if 从输入保存到历史 and 输入提示词 and 输入提示词.strip():
                timestamp = datetime.now().strftime("%H:%M")
                content_preview = 输入提示词[:10] + ("..." if len(输入提示词) > 10 else "")
                save_name = f"{timestamp} 手动输入:{content_preview}"
                save_to_history(输入提示词.strip(), save_name, manual_save=True)
                操作结果 += "输入提示词已保存到历史记录\n"
            
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
            
            if 将选中历史存为模板 and 新模板名称 and history_index != -1 and history_index < len(current_history):
                history_entry = current_history[history_index]
                saved_name = save_template(新模板名称, history_entry["prompt"])
                if saved_name:
                    操作结果 += f"历史记录已保存为模板 '{saved_name}' 到 Template 文件夹\n"
                else:
                    操作结果 += "将历史记录保存为模板失败\n"
            
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
    "提示词模板选择": 提示词模板选择,
    "历史记录和模板管理": 历史记录和模板管理
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "视频提示词公式": "视频提示词公式",
    "图像提示词公式": "图像提示词公式",
    "提示词模板选择": "提示词模板选择",
    "历史记录和模板管理": "历史记录和模板管理"
}
    