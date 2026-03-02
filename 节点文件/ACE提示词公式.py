# ACE提示词公式.py
from 工具函数 import clean_text

# =============================================================================
# 常量定义
# =============================================================================

GENRE_MAPPING = {
    "无": "",
    "标准完整版 (Standard Full)": "Pop", 
    "C-Pop (华语流行)": "Mandopop",
    "K-Pop (韩国流行)": "K-Pop",
    "J-Pop (日本流行)": "J-Pop",
    "未来贝斯 (Future Bass)": "Future Bass",
    "赛博朋克 (Cyberpunk)": "Cyberpunk",
    "陷阱音乐 (Trap)": "Trap",
    "嘻哈/说唱 (Hip-Hop/Rap)": "Hip-Hop",
    "电子舞曲 (EDM)": "EDM",
    "流行 (Pop)": "Pop",
    "摇滚 (Rock)": "Rock",
    "金属 (Metal)": "Metal",
    "R&B (节奏蓝调)": "R&B",
    "爵士 (Jazz)": "Jazz",
    "故障艺术 (Glitch Hop)": "Glitch Hop",
    "中国风/古风 (Chinese Traditional)": "Chinese Traditional style",
    "电影配乐 (Cinematic)": "Cinematic Score",
    "民谣 (Folk)": "Folk",
    "雷鬼 (Reggae)": "Reggae",
    "灵魂乐 (Soul)": "Soul",
    "歌剧 (Opera)": "Opera"
}

# 融合连接词映射 (中文显示 -> 英文输出)
CONNECTOR_MAPPING = {
    "平滑过渡 (transitioning into)": "transitioning into",
    "混合交织 (blended with)": "blended with",
    "突然切换 (suddenly switching to)": "suddenly switching to",
    "逐渐演变 (evolving into)": "evolving into",
    "激烈碰撞 (clashing with)": "clashing with",
    "交替出现 (alternating with)": "alternating with"
}

MOOD_MAPPING = {
    "无": "",
    "高能/科技感 (High-Energy/Tech)": "high-energy, futuristic, tech-anthem",
    "欢快/高能量 (Upbeat/High Energy)": "high-energy, upbeat",
    "紧张/故障感 (Tense/Glitchy)": "tense, glitchy, error-signal inspired",
    "史诗/胜利 (Epic/Triumphant)": "epic, triumphant, melodic",
    "浪漫/温馨 (Romantic/Warm)": "romantic, warm, intimate",
    "悲伤/忧郁 (Sad/Melancholic)": "sad, melancholic, emotional",
    "黑暗/深沉 (Dark/Deep)": "dark, deep, atmospheric",
    "轻松/慵懒 (Chill/Laid-back)": "chill, laid-back, relaxing",
    "愤怒/侵略性 (Angry/Aggressive)": "angry, aggressive, forceful",
    "梦幻/空灵 (Dreamy/Ethereal)": "dreamy, ethereal, atmospheric"
}

INSTRUMENT_MAPPING = {
    "无": "",
    "超锯齿波合成器 (Heavy Supersaws)": "heavy supersaws",
    "故障音效 (Glitch Sounds)": "coding glitch sounds, error signals",
    "808贝斯 (808 Bass)": "deep 808 bass, rattling sub-bass",
    "合成器主导 (Synth-driven)": "synth-driven, lush synthesizers",
    "吉他失真 (Distorted Guitar)": "heavily distorted guitars",
    "原声吉他 (Acoustic Guitar)": "acoustic guitar",
    "钢琴叙事 (Piano Ballad)": "melodic piano accompaniment",
    "管弦乐团 (Orchestra)": "full orchestral arrangement",
    "强力鼓点 (Heavy Drums)": "powerful driving drum beat",
    "成功音效 (Success Chime)": "satisfying success chime sound effect",
    "中国乐器-古筝/琵琶": "traditional Chinese instruments, Pipa and Guzheng",
    "萨克斯风 (Saxophone)": "smooth saxophone melody"
}

VOCAL_MAPPING = {
    "无": "",
    "自动调音/电音 (Auto-tuned)": "auto-tuned ad-libs, glossy production",
    "女声-精致 (Female-Polished)": "polished female vocals",
    "男声-力量 (Male-Forceful)": "forceful male vocals",
    "说唱-快嘴 (Rap-Fast Flow)": "fast-paced rap flow",
    "女声-清亮 (Female-Clear)": "bright, clear female vocals",
    "女声-可爱/元气 (Female-Clear)": "cute, energetic female vocals", 
    "女声-空灵 (Female-Ethereal)": "breathy, ethereal female vocals",
    "男女对唱 (Duet)": "male and female duet",
    "机械/机器人 (Robotic)": "robotic, processed vocals",
    "合唱团 (Choir)": "epic choir backing",
    "耳语 (Whispered)": "whispered vocals"
}

RHYTHM_MAPPING = {
    "无": "",
    "快速/疾驰 (Fast-Paced)": "fast-paced, driving rhythm",
    "中速/律动 (Mid-tempo/Groovy)": "mid-tempo, groovy",
    "慢速 (Slow)": "slow tempo",
    "四四拍 (4-on-the-floor)": "relentless four-on-the-floor beat",
    "切分音 (Syncopated)": "syncopated complex rhythm"
}

SECTION_STYLES = [
    "抒情主歌 (Melodic Verse)", 
    "说唱主歌 (Rap Verse)", 
    "快嘴说唱 (Fast Flow Rap)",
    "陷阱说唱 (Aggressive Trap Rap)",
    "冷酷念白 (Spoken Word)", 
    "柔和导歌 (Melodic R&B)", 
    "情绪堆叠 (Atmospheric Build-up)",
    "流行爆发 (Pop Explosion)", 
    "洗脑副歌 (Anthemic Vocal)", 
    "电子跌落 (Future Bass Drop)",
    "重低音跌落 (Heavy Synth Drop)",
    "故障前奏 (Glitchy Error Sounds)",
    "钢琴独奏 (Piano Solo)", 
    "环境音效 (Ambient Sci-fi)", 
    "器乐独奏 (Instrumental Solo)", 
    "吉他独奏 (Guitar Solo)",
    "安静桥段 (Quiet Bridge)",
    "故障切片 (Vocal Chop)",
    "诗意主歌 (Poetic Verse)",
    "宏大副歌 (Grand Chorus)",
    "摇滚主歌 (Rock Verse)", 
    "钢琴渐弱 (Piano fade out)", 
    "故障淡出 (Glitch fade)", 
    "合成器渐弱 (Synth fade out)" 
]

# 核心处理逻辑（供两个节点类共用）
def process_ace_logic(主要流派, 融合流派A, 融合流派B, 
                      歌曲主题, 
                      情感氛围1, 情感氛围2, 
                      人声特色1, 人声特色2, 
                      乐器重点1, 乐器重点2, 
                      节奏速度, 额外风格关键词,
                      sections_data):
    
    # 辅助函数：收集非空选项
    def collect_options(mapping, *keys):
        values = []
        for k in keys:
            val = mapping.get(k, "")
            if val and val != "":
                values.append(val)
        return list(dict.fromkeys(values))

    # 辅助函数：自然语言连接
    def join_natural(items):
        if not items: return ""
        if len(items) == 1: return items[0]
        return ", ".join(items[:-1]) + " and " + items[-1]

    # 1. 构建系统指令 (Caption)
    genres = collect_options(GENRE_MAPPING, 主要流派, 融合流派A, 融合流派B)
    genre_str = join_natural(genres) if genres else "Pop"
    
    moods = collect_options(MOOD_MAPPING, 情感氛围1, 情感氛围2)
    mood_str = join_natural(moods)
    
    insts = collect_options(INSTRUMENT_MAPPING, 乐器重点1, 乐器重点2)
    inst_str = join_natural(insts)
    
    vocals = collect_options(VOCAL_MAPPING, 人声特色1, 人声特色2)
    vocal_str = join_natural(vocals)
    
    rhythm_str = RHYTHM_MAPPING.get(节奏速度, "")
    theme_str = clean_text(歌曲主题)
    extra_str = clean_text(额外风格关键词)
    
    caption_parts = []
    
    if mood_str:
        base = f"A {mood_str} {genre_str} track"
    else:
        base = f"A {genre_str} track"
    caption_parts.append(base)
    
    if theme_str:
        caption_parts.append(f"about {theme_str}")
        
    music_features = []
    if inst_str:
        music_features.append(f"featuring {inst_str}")
    if rhythm_str:
        music_features.append(f"driven by a {rhythm_str}")
    
    if music_features:
        caption_parts.append(" ".join(music_features))
        
    if vocal_str:
        caption_parts.append(f"delivered with {vocal_str}")
            
    if extra_str:
        caption_parts.append(extra_str)
        
    system_prompt = ". ".join(caption_parts) + "."
    
    # 2. 构建歌词与结构 (Lyrics)
    lyrics_blocks = []
    
    def get_desc_en(text):
        if not text: return ""
        if "(" in text and ")" in text:
            return text.split("(")[1].split(")")[0]
        return clean_text(text)

    def process_section(sec_type_raw, sec_desc_raw, sec_lyrics=None):
        if not sec_type_raw or sec_type_raw == "无": 
            return None
        
        if "Intro" in sec_type_raw: tag = "Intro"
        elif "Outro" in sec_type_raw: tag = "Outro"
        elif "(" in sec_type_raw: tag = sec_type_raw.split("(")[1].split(")")[0]
        else: tag = sec_type_raw

        desc_en = get_desc_en(sec_desc_raw)
        full_tag = f"[{tag} - {desc_en}]" if (desc_en and desc_en != "无") else f"[{tag}]"
        
        block = f"{full_tag}"
        if sec_lyrics and clean_text(sec_lyrics):
            block += f"\n{clean_text(sec_lyrics)}"
        
        return block

    for s_type, s_desc, s_lyric in sections_data:
        block = process_section(s_type, s_desc, s_lyric)
        if block: lyrics_blocks.append(block)
    
    lyrics_prompt = "\n\n".join(lyrics_blocks)
    
    return (system_prompt, lyrics_prompt)

# 公共INPUT_TYPES生成器
def get_common_inputs(include_presets=False):
    # 定义首尾特殊类型
    types_intro = ["Intro - 纯音乐", "Intro - 带人声", "Intro - 故障音效", "无"]
    types_outro = ["Outro - 淡出", "Outro - 骤停", "无"]

    # 通用段落类型，包含所有可能选项，最大化兼容性
    types_general = [
        "主歌 (Verse)", 
        "说唱 (Rap Verse)", 
        "导歌 (Pre-Chorus)", 
        "堆叠 (Build-up)", 
        "副歌 (Chorus)", 
        "跌落 (Drop)", 
        "桥段 (Bridge)", 
        "无"
    ]
    
    # 风格描述列表增加“无”
    styles_with_none = SECTION_STYLES + ["无"]

    # 选项列表
    full_genres = list(GENRE_MAPPING.keys())
    
    if include_presets:
        # 预设版：默认使用 Pop 标准结构
        genre_list = full_genres
        default_genre = "标准完整版 (Standard Full)"
        
        # 预设版的默认值 (Pop)
        default_sub_genre_a = "无"
        default_sub_genre_b = "无"
        default_theme = "workflow frustration, cyberpunk city..."
        default_mood1 = "浪漫/温馨 (Romantic/Warm)"
        default_mood2 = "无"
        default_vocal1 = "女声-清亮 (Female-Clear)"
        default_vocal2 = "无"
        default_inst1 = "钢琴叙事 (Piano Ballad)"
        default_inst2 = "无"
        default_rhythm = "中速/律动 (Mid-tempo/Groovy)"
        default_extra = "glossy production, satisfying success chime..."
        
        # 歌词结构默认值 (Pop)
        default_intro_type = "Intro - 纯音乐"
        default_intro_desc = "钢琴独奏 (Piano Solo)"
        default_intro_lyric = ""
        
        default_v1_type = "主歌 (Verse)"
        default_v1_desc = "抒情主歌 (Melodic Verse)"
        default_v1_lyric = "打开工作流，满屏红节点\n加载报错，心态直接要炸裂..."
        
        default_pre1_type = "导歌 (Pre-Chorus)"
        default_pre1_desc = "柔和导歌 (Melodic R&B)"
        default_pre1_lyric = "进度条在控制台悄悄亮起..."

        default_chorus1_type = "副歌 (Chorus)"
        default_chorus1_desc = "洗脑副歌 (Anthemic Vocal)"
        default_chorus1_lyric = "Model Path Fixer! 拯救你的 Workflow..."
        
        default_v2_type = "主歌 (Verse)"
        default_v2_desc = "抒情主歌 (Melodic Verse)"
        default_v2_lyric = "Fix it! Download it! Done."
        
        default_pre2_type = "导歌 (Pre-Chorus)"
        default_pre2_desc = "柔和导歌 (Melodic R&B)"
        default_pre2_lyric = "模型下错文件夹？那是过去式..."
        
        default_build_type = "堆叠 (Build-up)"
        default_build_desc = "情绪堆叠 (Atmospheric Build-up)"
        default_build_lyric = "没有冗余，零显存占用..."

        default_chorus2_type = "副歌 (Chorus)"
        default_chorus2_desc = "洗脑副歌 (Anthemic Vocal)"
        default_chorus2_lyric = "Model Path Fixer! 让报错都退后..."
        
        default_sec8_type = "副歌 (Chorus)"
        default_sec8_desc = "洗脑副歌 (Anthemic Vocal)"
        default_sec8_lyric = "Yeah... Path Fixed."
        
        default_sec9_type = "桥段 (Bridge)"
        default_sec9_desc = "吉他独奏 (Guitar Solo)"
        default_sec9_lyric = ""
        
        default_outro_type = "Outro - 淡出"
        default_outro_desc = "钢琴渐弱 (Piano fade out)"
        default_outro_lyric = ""

    else:
        # 手动版：默认使用 "Model Path Fixer" (Cyberpunk/Rap) 歌曲配置
        genre_list = [g for g in full_genres if g not in ["无", "标准完整版 (Standard Full)"]]
        default_genre = "C-Pop (华语流行)"
        
        default_sub_genre_a = "未来贝斯 (Future Bass)"
        default_sub_genre_b = "赛博朋克 (Cyberpunk)"
        default_theme = "workflow frustration, coding glitch, plugin features"
        default_mood1 = "高能/科技感 (High-Energy/Tech)"
        default_mood2 = "紧张/故障感 (Tense/Glitchy)"
        default_vocal1 = "说唱-快嘴 (Rap-Fast Flow)"
        default_vocal2 = "自动调音/电音 (Auto-tuned)"
        default_inst1 = "超锯齿波合成器 (Heavy Supersaws)"
        default_inst2 = "故障音效 (Glitch Sounds)"
        default_rhythm = "快速/疾驰 (Fast-Paced)"
        default_extra = "glossy production, satisfying success chime sound effect"
        
        # 歌词结构默认值 (Cyberpunk Rap)
        default_intro_type = "Intro - 故障音效"
        default_intro_desc = "故障前奏 (Glitchy Error Sounds)"
        default_intro_lyric = "[System Warning... Model Missing...]\nYeah... Fix it up. One click. Let’s go."
        
        default_v1_type = "说唱 (Rap Verse)"
        default_v1_desc = "陷阱说唱 (Aggressive Trap Rap)"
        default_v1_lyric = "打开工作流，满屏红节点\n加载报错，心态直接要炸裂\nUNET 还是 Diffusion，路径搞不清\n又是 split_files，文件夹乱成精\n别慌，看我操作，不用去 HuggingFace\n无需依赖库，原生代码最干脆\nURL 嗅探，自动锁定物理位\n不管前端传什么，我都让它精准归队"
        
        default_pre1_type = "导歌 (Pre-Chorus)"
        default_pre1_desc = "柔和导歌 (Melodic R&B)"
        default_pre1_lyric = "进度条在控制台悄悄亮起\nUI 界面显示下载百分比\n你可以关闭窗口，继续你的创作\n后台静默守护，绝不打扰你的动作"

        default_chorus1_type = "副歌 (Chorus)"
        default_chorus1_desc = "洗脑副歌 (Anthemic Vocal)"
        default_chorus1_lyric = "Model Path Fixer! 拯救你的 Workflow\n缺什么补什么，一键扫描不犯愁\n复制链接，中断下载，掌控在指尖\n拒绝 0KB 空文件，把效率拉满天"
        
        default_v2_type = "跌落 (Drop)"
        default_v2_desc = "电子跌落 (Future Bass Drop)"
        default_v2_lyric = "Fix it! Download it! Done."
        
        default_pre2_type = "说唱 (Rap Verse)"
        default_pre2_desc = "快嘴说唱 (Fast Flow Rap)"
        default_pre2_lyric = "模型下错文件夹？那是过去式\n智能纠错逻辑，打破注册表的固执\nText Encoders, VAE, 还是 LoRA\n识别链接关键词，直接物理锁住它\n不用梯子，内置镜像满速飞\n可视化交互，小白也能变大 V\n就算断网也不怕，手动复制直链\n这才是真正硬核的插件体验"
        
        default_build_type = "堆叠 (Build-up)"
        default_build_desc = "情绪堆叠 (Atmospheric Build-up)"
        default_build_lyric = "没有冗余，零显存占用\n只为那一瞬间的——\n全绿通过"

        default_chorus2_type = "副歌 (Chorus)"
        default_chorus2_desc = "洗脑副歌 (Anthemic Vocal)"
        default_chorus2_lyric = "Model Path Fixer! 让报错都退后\n不管是旧版菜单，还是新版顶头\n只要链接在 Note 里，我就能抓取\n完美修复路径，让灵感自由呼吸"
        
        default_sec8_type = "无"
        default_sec8_desc = "无"
        default_sec8_lyric = ""
        
        default_sec9_type = "无"
        default_sec9_desc = "无"
        default_sec9_lyric = ""
        
        default_outro_type = "Outro - 淡出"
        default_outro_desc = "合成器渐弱 (Synth fade out)"
        default_outro_lyric = "Yeah... Path Fixed.\nSystem Ready.\nComfyUI... let's generate."

    mood_list = list(MOOD_MAPPING.keys())
    inst_list = list(INSTRUMENT_MAPPING.keys())
    vocal_list = list(VOCAL_MAPPING.keys())

    return {
        "required": {
            "主要流派": (genre_list, {"default": default_genre}),
        },
        "optional": {
            "融合流派A": (full_genres, {"default": default_sub_genre_a}),
            "融合流派B": (full_genres, {"default": default_sub_genre_b}),
            
            "歌曲主题": ("STRING", {"multiline": False, "default": default_theme, "placeholder": "例如: workflow frustration, cyberpunk city..."}),
            
            "情感氛围1": (mood_list, {"default": default_mood1}),
            "情感氛围2": (mood_list, {"default": default_mood2}),
            
            "人声特色1": (vocal_list, {"default": default_vocal1}),
            "人声特色2": (vocal_list, {"default": default_vocal2}),
            
            "乐器重点1": (inst_list, {"default": default_inst1}),
            "乐器重点2": (inst_list, {"default": default_inst2}),
            
            "节奏速度": (list(RHYTHM_MAPPING.keys()), {"default": default_rhythm}),
            "额外风格关键词": ("STRING", {"multiline": False, "default": default_extra, "placeholder": "例如: glossy production, satisfying success chime..."}),
            
            # --- 歌词与结构 ---
            "前奏_类型": (types_intro, {"default": default_intro_type}),
            "前奏_描述": (styles_with_none, {"default": default_intro_desc}),
            "前奏_歌词": ("STRING", {"multiline": True, "default": default_intro_lyric, "placeholder": "前奏人声/念白/倒计时..."}),

            "段落1_类型": (types_general, {"default": default_v1_type}),
            "段落1_风格描述": (styles_with_none, {"default": default_v1_desc}),
            "段落1_歌词": ("STRING", {"multiline": True, "default": default_v1_lyric}),

            "段落2_类型": (types_general, {"default": default_pre1_type}),
            "段落2_风格描述": (styles_with_none, {"default": default_pre1_desc}),
            "段落2_歌词": ("STRING", {"multiline": True, "default": default_pre1_lyric}),

            "段落3_类型": (types_general, {"default": default_chorus1_type}),
            "段落3_风格描述": (styles_with_none, {"default": default_chorus1_desc}),
            "段落3_歌词": ("STRING", {"multiline": True, "default": default_chorus1_lyric}),
            
            "段落4_类型": (types_general, {"default": default_v2_type}),
            "段落4_风格描述": (styles_with_none, {"default": default_v2_desc}),
            "段落4_歌词": ("STRING", {"multiline": True, "default": default_v2_lyric}),

            "段落5_类型": (types_general, {"default": default_pre2_type}),
            "段落5_风格描述": (styles_with_none, {"default": default_pre2_desc}),
            "段落5_歌词": ("STRING", {"multiline": True, "default": default_pre2_lyric}),

            "段落6_类型": (types_general, {"default": default_build_type}),
            "段落6_风格描述": (styles_with_none, {"default": default_build_desc}),
            "段落6_歌词": ("STRING", {"multiline": True, "default": default_build_lyric}),

            "段落7_类型": (types_general, {"default": default_chorus2_type}),
            "段落7_风格描述": (styles_with_none, {"default": default_chorus2_desc}),
            "段落7_歌词": ("STRING", {"multiline": True, "default": default_chorus2_lyric}),

            "段落8_类型": (types_general, {"default": default_sec8_type}),
            "段落8_风格描述": (styles_with_none, {"default": default_sec8_desc}),
            "段落8_歌词": ("STRING", {"multiline": True, "default": default_sec8_lyric}),

            "段落9_类型": (types_general, {"default": default_sec9_type}),
            "段落9_风格描述": (styles_with_none, {"default": default_sec9_desc}),
            "段落9_歌词": ("STRING", {"multiline": True, "default": default_sec9_lyric}),

            "尾奏_类型": (types_outro, {"default": default_outro_type}),
            "尾奏_描述": (styles_with_none, {"default": default_outro_desc}),
            "尾奏_歌词": ("STRING", {"multiline": True, "default": default_outro_lyric, "placeholder": "尾奏人声/念白..."}),
        }
    }

# =============================================================================
# 节点类 1: 原始/手动版 (无前端交互，无"无"选项)
# =============================================================================
class ACE提示词公式:
    DESCRIPTION = """此节点专为 ACE-Step 1.5 模型设计，针对华语流行音乐优化。
    
【结构说明】
本节点预设了 10 个段落 (Intro -> Outro)，这是生成一首标准 3-4 分钟完整流行歌曲的标准结构。
如果您只需要生成短曲，可将不需要的段落类型选择为“无”。

【使用提示】
- 歌词框内已预置了参考歌词，可直接运行测试。
- 歌曲名《全绿通过》为智能模型路径修复插件制作：https://github.com/a63976659/ComfyUI-Any-Path-Repair
- ✨防止可能出现的歌曲创作或版权纠纷，使用插件提供的默认歌词生成歌曲，版权归插件作者所有。"""

    @classmethod
    def INPUT_TYPES(cls):
        return get_common_inputs(include_presets=False)

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("系统指令(Caption)", "歌词提示词(Lyrics)")
    FUNCTION = "generate_ace_prompt"
    CATEGORY = "📕提示词公式/ACE音乐"

    def generate_ace_prompt(self, 主要流派, 融合流派A, 融合流派B, 
                          歌曲主题, 
                          情感氛围1, 情感氛围2, 
                          人声特色1, 人声特色2, 
                          乐器重点1, 乐器重点2, 
                          节奏速度, 额外风格关键词,
                          前奏_类型, 前奏_描述, 前奏_歌词,
                          段落1_类型, 段落1_风格描述, 段落1_歌词,
                          段落2_类型, 段落2_风格描述, 段落2_歌词,
                          段落3_类型, 段落3_风格描述, 段落3_歌词,
                          段落4_类型, 段落4_风格描述, 段落4_歌词,
                          段落5_类型, 段落5_风格描述, 段落5_歌词,
                          段落6_类型, 段落6_风格描述, 段落6_歌词,
                          段落7_类型, 段落7_风格描述, 段落7_歌词,
                          段落8_类型, 段落8_风格描述, 段落8_歌词,
                          段落9_类型, 段落9_风格描述, 段落9_歌词,
                          尾奏_类型, 尾奏_描述, 尾奏_歌词):
        
        sections = [
            (前奏_类型, 前奏_描述, 前奏_歌词),
            (段落1_类型, 段落1_风格描述, 段落1_歌词),
            (段落2_类型, 段落2_风格描述, 段落2_歌词),
            (段落3_类型, 段落3_风格描述, 段落3_歌词),
            (段落4_类型, 段落4_风格描述, 段落4_歌词),
            (段落5_类型, 段落5_风格描述, 段落5_歌词),
            (段落6_类型, 段落6_风格描述, 段落6_歌词),
            (段落7_类型, 段落7_风格描述, 段落7_歌词),
            (段落8_类型, 段落8_风格描述, 段落8_歌词),
            (段落9_类型, 段落9_风格描述, 段落9_歌词),
            (尾奏_类型, 尾奏_描述, 尾奏_歌词)
        ]

        return process_ace_logic(主要流派, 融合流派A, 融合流派B, 
                          歌曲主题, 
                          情感氛围1, 情感氛围2, 
                          人声特色1, 人声特色2, 
                          乐器重点1, 乐器重点2, 
                          节奏速度, 额外风格关键词,
                          sections)

# =============================================================================
# 节点类 2: 预设/动态版 (连接前端JS，含"无"和预设)
# =============================================================================
class ACE提示词预设:
    DESCRIPTION = """此节点支持 ACE-Step 1.5 音乐提示词的【动态预设功能】。
    
- 配合前端脚本使用，选择"主要流派"会自动填充风格和结构。
- 选择"无"或"标准完整版"可解锁自由编辑模式。
- **默认状态**：已配置为“标准完整版”，确保初次加载时所有段落均为激活状态。"""

    @classmethod
    def INPUT_TYPES(cls):
        return get_common_inputs(include_presets=True)

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("系统指令(Caption)", "歌词提示词(Lyrics)")
    FUNCTION = "generate_ace_prompt"
    CATEGORY = "📕提示词公式/ACE音乐"

    def generate_ace_prompt(self, 主要流派, 融合流派A, 融合流派B, 
                          歌曲主题, 
                          情感氛围1, 情感氛围2, 
                          人声特色1, 人声特色2, 
                          乐器重点1, 乐器重点2, 
                          节奏速度, 额外风格关键词,
                          前奏_类型, 前奏_描述, 前奏_歌词,
                          段落1_类型, 段落1_风格描述, 段落1_歌词,
                          段落2_类型, 段落2_风格描述, 段落2_歌词,
                          段落3_类型, 段落3_风格描述, 段落3_歌词,
                          段落4_类型, 段落4_风格描述, 段落4_歌词,
                          段落5_类型, 段落5_风格描述, 段落5_歌词,
                          段落6_类型, 段落6_风格描述, 段落6_歌词,
                          段落7_类型, 段落7_风格描述, 段落7_歌词,
                          段落8_类型, 段落8_风格描述, 段落8_歌词,
                          段落9_类型, 段落9_风格描述, 段落9_歌词,
                          尾奏_类型, 尾奏_描述, 尾奏_歌词):
        
        sections = [
            (前奏_类型, 前奏_描述, 前奏_歌词),
            (段落1_类型, 段落1_风格描述, 段落1_歌词),
            (段落2_类型, 段落2_风格描述, 段落2_歌词),
            (段落3_类型, 段落3_风格描述, 段落3_歌词),
            (段落4_类型, 段落4_风格描述, 段落4_歌词),
            (段落5_类型, 段落5_风格描述, 段落5_歌词),
            (段落6_类型, 段落6_风格描述, 段落6_歌词),
            (段落7_类型, 段落7_风格描述, 段落7_歌词),
            (段落8_类型, 段落8_风格描述, 段落8_歌词),
            (段落9_类型, 段落9_风格描述, 段落9_歌词),
            (尾奏_类型, 尾奏_描述, 尾奏_歌词)
        ]

        return process_ace_logic(主要流派, 融合流派A, 融合流派B, 
                          歌曲主题, 
                          情感氛围1, 情感氛围2, 
                          人声特色1, 人声特色2, 
                          乐器重点1, 乐器重点2, 
                          节奏速度, 额外风格关键词,
                          sections)

# =============================================================================
# 节点类 3: 高级流派融合 (已激活逻辑 + 中文选项)
# =============================================================================
class ACE高级流派融合:
    DESCRIPTION = """此节点用于生成【结构化风格融合】的系统指令。
    
不同于标准节点的“整体风格”，此节点允许你明确指定“主歌”和“副歌”使用完全不同的流派。
例如：主歌是“说唱”，副歌突然变成“歌剧”。
    
**使用方法**：
代替其它音乐节点的系统指令使用。"""

    @classmethod
    def INPUT_TYPES(cls):
        # 获取流派列表，移除"无"和"标准完整版"
        genre_list = [g for g in GENRE_MAPPING.keys() if g not in ["无", "标准完整版 (Standard Full)"]]
        
        return {
            "required": {
                "整体基调": (genre_list, {"default": "C-Pop (华语流行)"}),
                
                # 修复参数名不一致：移除键名中的 (Verse) 和 (Chorus)
                "主歌风格": (genre_list, {"default": "嘻哈/说唱 (Hip-Hop/Rap)"}),
                "主歌形容词": ("STRING", {"default": "aggressive, fast-paced", "placeholder": "例如: aggressive, fast-paced..."}),
                
                "副歌风格": (genre_list, {"default": "歌剧 (Opera)"}),
                "副歌形容词": ("STRING", {"default": "grand, emotional, soaring", "placeholder": "例如: grand, emotional..."}),
                
                # 使用中文显示的连接词列表
                "融合连接词": (list(CONNECTOR_MAPPING.keys()), {"default": "平滑过渡 (transitioning into)"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("结构化系统指令(Caption)",)
    FUNCTION = "generate_complex_caption"
    CATEGORY = "📕提示词公式/ACE音乐"
    
    def generate_complex_caption(self, 整体基调, 主歌风格, 主歌形容词, 
                               副歌风格, 副歌形容词, 融合连接词):
        
        # 1. 映射中文选项到英文 Prompt
        main_genre = GENRE_MAPPING.get(整体基调, "Pop")
        verse_genre = GENRE_MAPPING.get(主歌风格, "Rap")
        chorus_genre = GENRE_MAPPING.get(副歌风格, "Pop")
        
        # 2. 映射连接词 (中文 -> 英文)
        connector_eng = CONNECTOR_MAPPING.get(融合连接词, "transitioning into")
        
        # 3. 清理文本输入
        verse_adj = clean_text(主歌形容词)
        chorus_adj = clean_text(副歌形容词)
        
        # 4. 构建高级融合 Prompt 公式
        # 公式逻辑：[整体基调] + [主歌描述] + [连接词] + [副歌描述]
        
        # Part A: 整体定义
        prompt = f"A experimental {main_genre} track."
        
        # Part B: 主歌描述
        if verse_adj:
            prompt += f" The verse features {verse_adj} {verse_genre} elements,"
        else:
            prompt += f" The verse features {verse_genre} elements,"
            
        # Part C: 连接与副歌
        if chorus_adj:
            prompt += f" {connector_eng} a {chorus_adj} {chorus_genre} chorus."
        else:
            prompt += f" {connector_eng} a {chorus_genre} chorus."
            
        # Part D: 增加一点融合的 "Glue" (胶水词)
        prompt += " The production creates a unique fusion of styles."

        return (prompt,)
