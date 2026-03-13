import torch
import numpy as np
from PIL import Image, ImageOps
import folder_paths
import os

class 图像裁剪节点:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        # 定义允许的图像后缀名（全部转小写判断）
        valid_exts = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff')
        # 在读取文件时，只保留以这些后缀结尾的文件
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith(valid_exts)]
        
        return {
            "required": {
                "图像文件": (sorted(files), {"image_upload": True}),
                "预设": (["自定义", "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"], {"default": "自定义"}),
                "裁剪宽度": ("FLOAT", {"default": 512, "min": 16, "max": 16384, "step": 16, "display": "slider"}),
                "裁剪高度": ("FLOAT", {"default": 512, "min": 16, "max": 16384, "step": 16, "display": "slider"}),
                # 将原来的 "number" 改为 "slider"
                "裁剪X": ("INT", {"default": 0, "min": 0, "max": 16384, "step": 1, "display": "slider"}),
                "裁剪Y": ("INT", {"default": 0, "min": 0, "max": 16384, "step": 1, "display": "slider"}),
                # 将缩放比例移动到最后，以便在 UI 上显示在底部
                "缩放比例": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 1.0, "step": 0.01, "display": "slider"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("图像", "宽度", "高度")
    FUNCTION = "do_crop"
    CATEGORY = "📕提示词公式/工具节点"
    DESCRIPTION = "鼠标拖动裁剪框可以移动位置\n双击裁剪框裁剪框会跟随鼠标\n用鼠标再拖动一次裁剪框即可取消粘连。\nℹ️其它预设缩放会正常生效 \n 自定义模式下，极限宽高度，按比例缩放会有异常，请谨慎使用！"

    def do_crop(self, 图像文件, 预设, 缩放比例, 裁剪宽度, 裁剪高度, 裁剪X, 裁剪Y):
        img_path = folder_paths.get_annotated_filepath(图像文件)
        img = Image.open(img_path)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        
        orig_w, orig_h = img.size
        
        # 1. 尺寸处理 (使用前端传来的值)
        target_w = int(裁剪宽度)
        target_h = int(裁剪高度)

        # 强制 16 倍数对齐
        target_w = max(16, (target_w // 16) * 16)
        target_h = max(16, (target_h // 16) * 16)

        # 尺寸边界限制
        target_w = min(target_w, (orig_w // 16) * 16)
        target_h = min(target_h, (orig_h // 16) * 16)
        
        # 2. 坐标处理
        x = int(裁剪X)
        y = int(裁剪Y)

        # 坐标边界限制 (防止红框跑出图像外)
        x = max(0, min(x, orig_w - target_w))
        y = max(0, min(y, orig_h - target_h))
        
        # 3. 执行裁剪
        cropped_img = img.crop((x, y, x + target_w, y + target_h))
        
        # 4. 转 Tensor
        img_np = np.array(cropped_img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np)[None,]
        
        return {
            "ui": {"images": []},
            "result": (img_tensor, target_w, target_h)
        }