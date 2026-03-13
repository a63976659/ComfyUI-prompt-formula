# -*- coding: utf-8 -*-
import torch
import torch.nn.functional as F
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
                "image": ("STRING", {"default": ""}), 
                "遮罩颜色": (["黑色", "白色", "红色", "绿色", "蓝色"], {"default": "黑色", "tooltip": "图像合并遮罩时的覆盖颜色"}),
            },
            "optional": {
                "图像": ("IMAGE",),
                "遮罩": ("MASK",),  
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("图像", "遮罩", "图像合并遮罩")
    OUTPUT_NODE = True 
    FUNCTION = "execute"
    CATEGORY = "📕提示词公式/工具节点"

    DESCRIPTION = """🖼️ 图像遮罩预览与编辑节点

【核心功能】
1. 节点预览：预览图像和遮罩，或任意一种。
2. 遮罩编辑：对图像的遮罩进行编辑。
3. 双路断线缓存：断开输入后，仍可以使用缓存数据继续工作。
4. 图像遮罩混合：将遮罩与颜色叠加到原图，输出实心图。"""

    def execute(self, image="", 遮罩颜色="黑色", 图像=None, 遮罩=None, unique_id=None):
        results = []
        
        # === 0. 缓存目录初始化 ===
        cache_dir = os.path.join(folder_paths.get_temp_directory(), "mask_preview_cache")
        os.makedirs(cache_dir, exist_ok=True)
        safe_id = str(unique_id) if unique_id else "default"
        img_cache_path = os.path.join(cache_dir, f"img_tensor_{safe_id}.pt")
        mask_cache_path = os.path.join(cache_dir, f"mask_tensor_{safe_id}.pt") 

        # === 1. 优先提取 edited_mask (手绘遮罩) ===
        edited_mask = None
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
                    else:
                        # 🌟 核心修复：没有Alpha通道，说明你在编辑器里点了Clear！
                        # 此时强制生成一个全为0（空白）的遮罩，告知后端“用户要求清空”
                        W, H = i.size
                        edited_mask = torch.zeros((1, H, W), dtype=torch.float32)
            except Exception as e:
                print(f"读取手绘遮罩失败: {e}")

        # === 2. 独裁清理：如果存在手绘动作（哪怕是Clear），立即斩断外部遮罩缓存 ===
        if edited_mask is not None:
            if os.path.exists(mask_cache_path):
                try: os.remove(mask_cache_path)
                except: pass

        # === 3. 外部遮罩接收与智能缓存 ===
        ext_mask = None
        if 遮罩 is not None and isinstance(遮罩, torch.Tensor) and 遮罩.numel() > 0:
            torch.save(遮罩.clone().cpu(), mask_cache_path)
            ext_mask = 遮罩.clone()
        elif edited_mask is None: # 只有没手绘干扰时，才去读断线缓存
            if os.path.exists(mask_cache_path):
                try: ext_mask = torch.load(mask_cache_path)
                except: pass

        # === 4. 图像兜底生成机制 (终极防爆) ===
        if 图像 is not None:
            torch.save(图像.clone().cpu(), img_cache_path)
        else:
            if os.path.exists(img_cache_path):
                try: 图像 = torch.load(img_cache_path)
                except: pass
                
            # 如果加载缓存失败，或者压根没连过图像，强制无脑兜底，绝不 raise ValueError！
            if 图像 is None:
                ref_mask = edited_mask if edited_mask is not None else ext_mask
                if ref_mask is not None:
                    tmp_m = ref_mask
                    if len(tmp_m.shape) == 2:
                        tmp_m = tmp_m.unsqueeze(0)
                    B, m_H, m_W = tmp_m.shape[0], tmp_m.shape[-2], tmp_m.shape[-1]
                else:
                    B, m_H, m_W = 1, 512, 512 # 最恶劣情况下，强行生成 512x512 画布
                
                图像 = torch.zeros((B, m_H, m_W, 3), dtype=torch.float32)
                torch.save(图像.clone().cpu(), img_cache_path)
                
        # 确保全部张量在同一个设备计算
        calc_device = 图像.device

        # === 5. 尺寸自适应与双路遮罩合并 ===
        B, img_H, img_W = 图像.shape[0], 图像.shape[1], 图像.shape[2]
        
        hand_mask = None
        if edited_mask is not None:
            hand_mask = edited_mask.clone().to(calc_device)
            if len(hand_mask.shape) == 2:
                hand_mask = hand_mask.unsqueeze(0)
            _, h_H, h_W = hand_mask.shape
            if h_H != img_H or h_W != img_W:
                hand_mask = F.interpolate(hand_mask.unsqueeze(1), size=(img_H, img_W), mode='nearest-exact').squeeze(1)
            if B > hand_mask.shape[0]:
                hand_mask = hand_mask.repeat((B + hand_mask.shape[0] - 1) // hand_mask.shape[0], 1, 1)[:B]
            elif hand_mask.shape[0] > B:
                hand_mask = hand_mask[:B]

        e_mask = None
        if ext_mask is not None:
            e_mask = ext_mask.clone().to(calc_device)
            if len(e_mask.shape) == 2:
                e_mask = e_mask.unsqueeze(0)
            _, m_H, m_W = e_mask.shape
            if m_H != img_H or m_W != img_W:
                e_mask = F.interpolate(e_mask.unsqueeze(1), size=(img_H, img_W), mode='nearest-exact').squeeze(1)
            if B > e_mask.shape[0]:
                e_mask = e_mask.repeat((B + e_mask.shape[0] - 1) // e_mask.shape[0], 1, 1)[:B]
            elif e_mask.shape[0] > B:
                e_mask = e_mask[:B]

        if hand_mask is not None and e_mask is not None:
            out_mask = torch.maximum(hand_mask, e_mask)
            has_valid_mask = True
        elif hand_mask is not None:
            out_mask = hand_mask
            has_valid_mask = True
        elif e_mask is not None:
            out_mask = e_mask
            has_valid_mask = True
        else:
            out_mask = torch.zeros((B, img_H, img_W), dtype=torch.float32, device=calc_device)
            has_valid_mask = False

        # === 6. 计算“图像合并遮罩” (Alpha Blending) ===
        color_map = {
            "黑色": [0.0, 0.0, 0.0],
            "白色": [1.0, 1.0, 1.0],
            "红色": [1.0, 0.0, 0.0],
            "绿色": [0.0, 1.0, 0.0],
            "蓝色": [0.0, 0.0, 1.0]
        }
        rgb_color = color_map.get(遮罩颜色, [0.0, 0.0, 0.0])
        fill_color = torch.tensor(rgb_color, dtype=torch.float32, device=calc_device)

        blend_factor = out_mask.unsqueeze(-1) 
        img_channels = 图像.shape[-1]

        if img_channels == 4:
            img_rgb = 图像[..., :3]
            img_a = 图像[..., 3:]
            out_rgb = img_rgb * (1 - blend_factor) + fill_color * blend_factor
            out_a = torch.maximum(img_a, blend_factor)
            masked_image_tensor = torch.cat((out_rgb, out_a), dim=-1)
        else:
            masked_image_tensor = 图像 * (1 - blend_factor) + fill_color * blend_factor

        # === 7. 生成 UI 预览图 ===
        if 图像 is not None:
            images_np = (图像.cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
            
            mask_np_for_ui = out_mask.cpu().numpy()
            if len(mask_np_for_ui.shape) == 4:
                mask_np_for_ui = mask_np_for_ui[:, :, :, 0]
            alpha_np = ((1.0 - mask_np_for_ui) * 255.0).clip(0, 255).astype(np.uint8)

            run_prefix = f"_temp_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

            for i in range(images_np.shape[0]):
                rgb_arr = images_np[i][..., :3] 
                alpha_arr = alpha_np[i]
                
                rgba = np.concatenate([rgb_arr, alpha_arr[..., np.newaxis]], axis=-1)
                img_obj = Image.fromarray(rgba, mode='RGBA')
                
                filename = f"preview_img_{run_prefix}_{i:05}.png"
                img_obj.save(os.path.join(self.output_dir, filename))
                
                results.append({"filename": filename, "subfolder": "", "type": self.type})


        return { "ui": { "images": results }, "result": (图像, out_mask, masked_image_tensor) }
