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

    # 🌟 新增了第三个输出项："IMAGE" ("图像合并遮罩")
    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("图像", "遮罩", "图像合并遮罩")
    OUTPUT_NODE = True 
    FUNCTION = "execute"
    CATEGORY = "📕提示词公式/工具节点"

    # 🌟 新增的节点描述信息（支持多行排版）
    DESCRIPTION = """🖼️ 图像遮罩预览与编辑节点

【核心功能】
允许你在节点上直接预览图像，并调用系统原生编辑器手绘遮罩。自动处理图像尺寸变化防报错，支持将遮罩与原图合成透明底 (RGBA) 图像并输出。

【使用步骤】
1. 连接【图像】输入，并【运行一次】工作流（必须让图像先显示在节点上）。
2. 点击节点面板上的【🎨 编辑遮罩】按钮（或在图像上右键选择“在遮罩编辑器中打开”）。
3. 在弹出的编辑器中涂抹区域，点击左上角【保存】。
4. 再次运行工作流，即可向后方输出最新的遮罩与合成结果。

【输出端口说明】
• 图像：原始的 RGB 彩色图像。
• 遮罩：你手绘的遮罩（未手绘时输出防报错全黑遮罩）。
• 图像合并遮罩：带 Alpha 通道的 RGBA 图像（被遮罩涂抹的区域变为透明），可直接连入原生的“保存图像”保存为完美抠底的 PNG 图片。"""

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

        # === 2. 确定最终输出的遮罩与【尺寸安全校验】 ===
        out_mask = 遮罩
        has_valid_mask = False
        
        # 获取当前输入的图像尺寸
        B, img_H, img_W = 图像.shape[0], 图像.shape[1], 图像.shape[2]
        
        # 校验手绘缓存遮罩的尺寸
        if edited_mask is not None:
            mask_H, mask_W = edited_mask.shape[-2], edited_mask.shape[-1]
            if img_H != mask_H or img_W != mask_W:
                print(f"⚠️ 图像遮罩预览节点: 发现新图像尺寸({img_W}x{img_H})与旧遮罩缓存({mask_W}x{mask_H})不匹配，已自动清空失效遮罩！")
                edited_mask = None
            else:
                out_mask = edited_mask
                has_valid_mask = True
                
        # 校验外部连线输入的遮罩尺寸（双重保险）
        if not has_valid_mask and 遮罩 is not None:
            mask_H, mask_W = 遮罩.shape[-2], 遮罩.shape[-1]
            if img_H != mask_H or img_W != mask_W:
                print(f"⚠️ 图像遮罩预览节点: 输入的遮罩尺寸({mask_W}x{mask_H})与图像尺寸({img_W}x{img_H})不匹配，已忽略该遮罩以防报错！")
                out_mask = None
            else:
                out_mask = 遮罩
                has_valid_mask = True
            
        # 如果遮罩被清空或未连入，生成完全匹配新图尺寸的防报错全黑底层遮罩
        if out_mask is None:
            out_mask = torch.zeros((B, img_H, img_W), dtype=torch.float32, device=图像.device)
            has_valid_mask = False

        # === 3. 将原图与遮罩融合成一张带有 Alpha 通道的 RGBA 图像 ===
        # 用于前端预览以及新的“图像合并遮罩”输出
        if has_valid_mask and out_mask is not None:
            mask_np = out_mask.cpu().numpy()
            if len(mask_np.shape) == 4:
                mask_np = mask_np[:, :, :, 0]
            alpha_np = ((1.0 - mask_np) * 255.0).clip(0, 255).astype(np.uint8)
            
            # 为第三个输出构建 Alpha Tensor (1代表实体，0代表透明镂空)
            alpha_tensor = (1.0 - out_mask).unsqueeze(-1)
        else:
            alpha_np = np.full((B, img_H, img_W), 255, dtype=np.uint8)
            alpha_tensor = torch.ones((B, img_H, img_W, 1), dtype=torch.float32, device=图像.device)

        # 🌟 合并为 RGBA (4通道) 图像张量
        if 图像.shape[-1] == 3:
            rgba_tensor = torch.cat([图像, alpha_tensor], dim=-1)
        elif 图像.shape[-1] == 4:
            # 如果原图已经带了 Alpha 通道，直接替换掉它的透明层
            rgba_tensor = torch.cat([图像[..., :3], alpha_tensor], dim=-1)
        else:
            rgba_tensor = 图像

        # === 4. 生成 UI 预览图 ===
        if 图像 is not None:
            images_np = (图像.cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
            run_prefix = f"_temp_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

            for i in range(images_np.shape[0]):
                rgb = images_np[i][..., :3] # 确保只取 RGB 三通道用于拼接
                alpha = alpha_np[i]
                
                rgba = np.concatenate([rgb, alpha[..., np.newaxis]], axis=-1)
                img_obj = Image.fromarray(rgba, mode='RGBA')
                
                filename = f"preview_img_{run_prefix}_{i:05}.png"
                img_obj.save(os.path.join(self.output_dir, filename))
                
                results.append({"filename": filename, "subfolder": "", "type": self.type})

        # 🌟 增加返回了 rgba_tensor
        return { "ui": { "images": results }, "result": (图像, out_mask, rgba_tensor) }