# -*- coding: utf-8 -*-
import torch
import comfy.utils
import math

MAX_RESOLUTION = 16384

# ================= 核心算法函数 =================
def get_size(target):
    if target is None: return 0, 0
    if len(target.shape) == 4: return target.shape[2], target.shape[1]
    return target.shape[2], target.shape[1]

def common_upscale(samples, width, height, method, crop):
    if width == 0 and height == 0: return samples
    is_image = len(samples.shape) == 4
    if is_image: samples = samples.movedim(-1, 1)
    else: samples = samples.unsqueeze(1)
    s = comfy.utils.common_upscale(samples, width, height, method, crop)
    if is_image: return s.movedim(1, -1)
    return s.squeeze(1)

def scale_by(samples, multiplier, method):
    w, h = get_size(samples)
    return common_upscale(samples, round(w * multiplier), round(h * multiplier), method, "disabled")

def scale_dimensions(samples, width, height, method, crop):
    w, h = get_size(samples)
    if width == 0: width = max(1, round(w * height / h))
    elif height == 0: height = max(1, round(h * width / w))
    return common_upscale(samples, width, height, method, crop)

def scale_longer(samples, size, method):
    w, h = get_size(samples)
    if w >= h: t_w, t_h = size, round(h * size / w)
    else: t_h, t_w = size, round(w * size / h)
    return common_upscale(samples, t_w, t_h, method, "disabled")

def scale_shorter(samples, size, method):
    w, h = get_size(samples)
    if w <= h: t_w, t_h = size, round(h * size / w)
    else: t_h, t_w = size, round(w * size / h)
    return common_upscale(samples, t_w, t_h, method, "disabled")

def scale_total_pixels(samples, megapixels, method):
    w, h = get_size(samples)
    total = int(megapixels * 1024 * 1024)
    scale = math.sqrt(total / (w * h))
    return common_upscale(samples, round(w * scale), round(h * scale), method, "disabled")

def scale_match(samples, match, method, crop):
    if match is None: return samples
    t_w, t_h = get_size(match)
    return common_upscale(samples, t_w, t_h, method, crop)

def scale_to_multiple(samples, multiple, method):
    if multiple <= 1: return samples
    w, h = get_size(samples)
    t_w = (w // multiple) * multiple
    t_h = (h // multiple) * multiple
    if t_w == 0 or t_h == 0: return samples
    
    s_w = t_w / w
    s_h = t_h / h
    if s_w >= s_h:
        sc_w = t_w
        sc_h = int(math.ceil(h * s_w))
        if sc_h < t_h: sc_h = t_h
    else:
        sc_h = t_h
        sc_w = int(math.ceil(w * s_h))
        if sc_w < t_w: sc_w = t_w
        
    scaled = common_upscale(samples, sc_w, sc_h, method, "disabled")
    x0 = (sc_w - t_w) // 2
    y0 = (sc_h - t_h) // 2
    
    if len(scaled.shape) == 4: return scaled[:, y0:y0+t_h, x0:x0+t_w, :]
    else: return scaled[:, y0:y0+t_h, x0:x0+t_w]

# ================= 节点定义 =================
class 智能缩放图像及遮罩:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "调整类型": ([
                    "指定尺寸 (Dimensions)", 
                    "按系数 (Scale By)", 
                    "指定长边 (Longer Side)", 
                    "指定短边 (Shorter Side)", 
                    "指定宽度 (Width)", 
                    "指定高度 (Height)", 
                    "指定像素 (Megapixels)", 
                    "匹配图像 (Match Size)", 
                    "乘数调整 (To Multiple)"
                ], {"default": "指定尺寸 (Dimensions)"}),
                "插值方法": (["nearest-exact", "bilinear", "area", "bicubic", "lanczos"], {"default": "area"}),
            },
            "optional": {
                "图像或遮罩": ("*",), 
                "参考图像": ("*",), 
                "裁剪方式": (["disabled", "center"], {"default": "center"}),
                "宽度": ("INT", {"default": 512, "min": 0, "max": MAX_RESOLUTION, "step": 1}),
                "高度": ("INT", {"default": 512, "min": 0, "max": MAX_RESOLUTION, "step": 1}),
                "缩放系数": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0, "step": 0.01}),
                "指定长度": ("INT", {"default": 1024, "min": 1, "max": MAX_RESOLUTION, "step": 1}), 
                "百万像素": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0, "step": 0.01}),
                "放大": ("INT", {"default": 8, "min": 1, "max": 512, "step": 1}), 
            }
        }

    # 【修改】输出类型改为通用的 "*"
    RETURN_TYPES = ("*",)
    # 【修改】输出名称合并
    RETURN_NAMES = ("图像/遮罩",)
    FUNCTION = "execute"
    CATEGORY = "📕提示词公式/工具节点"
    
    DESCRIPTION = """
    调整类型功能说明：
    1. 指定尺寸/宽度/高度：强制缩放到特定像素。
    2. 按系数：按倍率缩放（如 0.5 或 2.0）。
    3. 指定长/短边：锁定一边长度，另一边按比例自适应。
    4. 指定像素：保持比例，将总像素数调整到近似值（如 1MP）。
    5. 匹配图像：将输入图像调整为与参考图像一致的大小。
    6. 乘数调整 (To Multiple)：【重要】将图像长宽调整为指定数值（如8）的整数倍。
       - 作用：修复非标准尺寸图像，防止 SD VAE 或视频模型因尺寸无法整除而报错。
       - 算法：保持比例缩放覆盖目标尺寸，并进行居中裁剪。
    """

    def execute(self, 调整类型, 插值方法, 图像或遮罩=None, 参考图像=None, 裁剪方式="center", 宽度=512, 高度=512, 缩放系数=1.0, 指定长度=1024, 百万像素=1.0, 放大=8):
        target = 图像或遮罩
        # 如果没有输入，返回空的元组
        if target is None: return (None,)

        def process_one(sample):
            if sample is None: return None
            # 严格对应前端选项字符串
            if "指定尺寸" in 调整类型: return scale_dimensions(sample, 宽度, 高度, 插值方法, 裁剪方式)
            elif "按系数" in 调整类型: return scale_by(sample, 缩放系数, 插值方法)
            elif "指定长边" in 调整类型: return scale_longer(sample, 指定长度, 插值方法)
            elif "指定短边" in 调整类型: return scale_shorter(sample, 指定长度, 插值方法)
            elif "指定宽度" in 调整类型: return scale_dimensions(sample, 宽度, 0, 插值方法, "disabled")
            elif "指定高度" in 调整类型: return scale_dimensions(sample, 0, 高度, 插值方法, "disabled")
            elif "指定像素" in 调整类型: return scale_total_pixels(sample, 百万像素, 插值方法)
            elif "匹配图像" in 调整类型: return scale_match(sample, 参考图像, 插值方法, 裁剪方式)
            elif "乘数调整" in 调整类型: return scale_to_multiple(sample, 放大, 插值方法)
            return sample

        # 【修改】不再区分 Image/Mask 返回，统一处理并返回
        result = process_one(target)
        return (result,)