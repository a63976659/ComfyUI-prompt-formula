# -*- coding: utf-8 -*-
import torch
import numpy as np
import os
import random
import time
from PIL import Image, ImageOps
import folder_paths 

class 图像遮罩预览节点:
    def __init__(self):
        # 恢复到最标准的 temp 临时目录模式，保证 UI 绝对能正常显示预览
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "图像": ("IMAGE",),
                "image": ("STRING", {"default": ""}), 
            },
            "optional": {
                "遮罩": ("MASK",),  
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("图像", "遮罩")
    OUTPUT_NODE = True 
    FUNCTION = "execute"
    CATEGORY = "📕提示词公式/工具节点"

    def execute(self, 图像, image="", 遮罩=None):
        results = []
        edited_mask = None
        
        # === 1. 后台静默读取手绘遮罩缓存 ===
        if image and isinstance(image, str) and image.strip() != "":
            try:
                try:
                    image_path = folder_paths.get_annotated_filepath(image)
                except AttributeError:
                    if "/" in image or "\\" in image:
                        image_path = os.path.join(folder_paths.get_input_directory(), image)
                    else:
                        image_path = os.path.join(folder_paths.get_input_directory(), "clipspace", image)
                        
                if os.path.exists(image_path):
                    i = Image.open(image_path)
                    i = ImageOps.exif_transpose(i)
                    if 'A' in i.getbands():
                        mask_np = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                        edited_mask = 1.0 - torch.from_numpy(mask_np) 
                        if len(图像.shape) > 0 and len(edited_mask.shape) == 2:
                            edited_mask = edited_mask.unsqueeze(0).repeat(图像.shape[0], 1, 1)
            except Exception as e:
                print(f"读取编辑遮罩缓存失败: {e}")

        # === 2. 确定最终输出的遮罩 ===
        out_mask = 遮罩
        has_valid_mask = False
        
        if edited_mask is not None:
            out_mask = edited_mask
            has_valid_mask = True
        elif 遮罩 is not None:
            has_valid_mask = True
            
        if out_mask is None:
            B, H, W, _ = 图像.shape
            out_mask = torch.zeros((B, H, W), dtype=torch.float32, device=图像.device)
            has_valid_mask = False

        # === 3. 将原图与遮罩融合成一张带有 Alpha 通道的 RGBA 图像输出 ===
        if 图像 is not None:
            images_np = (图像.cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
            
            if has_valid_mask and out_mask is not None:
                mask_np = out_mask.cpu().numpy()
                if len(mask_np.shape) == 4:
                    mask_np = mask_np[:, :, :, 0]
                alpha_np = ((1.0 - mask_np) * 255.0).clip(0, 255).astype(np.uint8)
            else:
                B, H, W = images_np.shape[0], images_np.shape[1], images_np.shape[2]
                alpha_np = np.full((B, H, W), 255, dtype=np.uint8)

            # 动态文件名，彻底杜绝前端缓存死结
            run_prefix = f"_temp_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

            for i in range(images_np.shape[0]):
                rgb = images_np[i]
                alpha = alpha_np[i]
                rgba = np.concatenate([rgb, alpha[..., np.newaxis]], axis=-1)
                img_obj = Image.fromarray(rgba, mode='RGBA')
                
                filename = f"preview_img_{run_prefix}_{i:05}.png"
                img_obj.save(os.path.join(self.output_dir, filename))
                
                # 回归正常 temp 类型
                results.append({"filename": filename, "subfolder": "", "type": self.type})

        return { "ui": { "images": results }, "result": (图像, out_mask) }