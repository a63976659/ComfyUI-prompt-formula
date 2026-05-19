# -*- coding: utf-8 -*-
import torch
import numpy as np
import os
import random
from PIL import Image
import folder_paths # ComfyUI 原生模块，用于获取临时目录

class 智能预览图像及遮罩:
    def __init__(self):
        # 获取系统临时目录，用于存放预览图
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        # 生成一个随机前缀，避免文件名冲突
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 使用通配符 "*" 接收任何类型的输入 (图像或遮罩)
                "输入数据": ("*",), 
            },
            "hidden": {
                "prompt": "PROMPT", 
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    # 定义为 OUTPUT_NODE 让 ComfyUI 知道这是个末端预览节点
    OUTPUT_NODE = True
    FUNCTION = "execute"
    CATEGORY = "📕提示词公式/工具节点"
    
    DESCRIPTION = """
    智能预览节点：
    可以连接图像(IMAGE)或遮罩(MASK)。
    - 自动识别输入类型。
    - 如果是遮罩，自动转换为灰度图像预览。
    - 如果是图像，直接显示。
    """

    def execute(self, 输入数据, prompt=None, extra_pnginfo=None):
        if 输入数据 is None:
            return {"ui": {"images": []}}

        images = 输入数据

        # === 1. 数据类型与维度处理 ===
        # 如果是 List (某些节点输出可能是列表)，尝试取第一个
        if isinstance(images, list):
            if len(images) > 0:
                images = images[0]
            else:
                return {"ui": {"images": []}}

        # 确保是 Tensor
        if not isinstance(images, torch.Tensor):
            # 如果不是 Tensor (可能是 None 或其他)，返回空
            return {"ui": {"images": []}}

        # === 2. 核心逻辑：判断输入是图像还是遮罩 ===
        # 图像通常是 [Batch, Height, Width, Channels] -> 4维
        # 遮罩通常是 [Batch, Height, Width] -> 3维
        
        if len(images.shape) == 3:
            # Case A: 遮罩处理 [B, H, W]
            # 扩展为 [B, H, W, 1]
            images = images.unsqueeze(-1)
            # 重复3次变成 [B, H, W, 3] (RGB灰度)
            images = images.repeat(1, 1, 1, 3)
        elif len(images.shape) == 2:
            # Case B: 单张无Batch遮罩 [H, W] (极少见但防报错)
            images = images.unsqueeze(0).unsqueeze(-1).repeat(1, 1, 1, 3)

        # === 3. 数据归一化 ===
        # 确保数据在 0-1 之间
        # 如果最大值 > 1.0 (比如 255)，则除以 255
        if images.max() > 1.0:
            images = images.float() / 255.0
            
        images = torch.clamp(images, 0, 1)

        # === 4. 转换为 Numpy 准备保存 ===
        # 移动到 CPU 并转为 uint8
        images_np = (images.cpu().numpy() * 255.0).astype(np.uint8)

        results = []
        
        # === 5. 保存预览图 ===
        for i in range(images_np.shape[0]):
            img_array = images_np[i]
            
            # 再次检查维度，确保是 [H, W, 3]
            # 如果是 [H, W, 1] 转为 [H, W] 以便 PIL 处理
            if img_array.shape[-1] == 1:
                img_array = img_array.squeeze(-1)
                
            img = Image.fromarray(img_array)
            
            # 生成临时文件名
            filename = f"preview_{self.prefix_append}_{i:05}.png"
            full_path = os.path.join(self.output_dir, filename)
            
            # 保存图片
            img.save(full_path)
            
            # 添加到返回列表
            results.append({
                "filename": filename,
                "subfolder": "",
                "type": self.type
            })

        # 返回 UI 数据结构
        return { "ui": { "images": results } }
