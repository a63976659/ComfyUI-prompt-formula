# ACE提示词公式.py
from 工具函数 import clean_text

# =============================================================================
# 常量定义
# =============================================================================

GENRE_MAPPING = {
    "C-Pop (华语流行)": "Mandopop",
    "K-Pop (韩国流行)": "K-Pop",
    "J-Pop (日本流行)": "J-Pop",
    "流行 (Pop)": "Pop",
    "摇滚 (Rock)": "Rock",
    "嘻哈/说唱 (Hip-Hop/Rap)": "Hip-Hop",
    "R&B (节奏蓝调)": "R&B",
    "电子舞曲 (EDM)": "EDM",
    "爵士 (Jazz)": "Jazz",
    "中国风/古风 (Chinese Traditional)": "Chinese Traditional style",
    "民谣 (Folk)": "Folk",
    "电影配乐 (Cinematic)": "Cinematic Score"
}

MOOD_MAPPING = {
    "浪漫/温馨 (Romantic/Warm)": "romantic, warm, intimate",
    "欢快/高能量 (Upbeat/High Energy)": "high-energy, upbeat",
    "悲伤/忧郁 (Sad/Melancholic)": "sad, melancholic, emotional",
    "史诗/宏大 (Epic/Grand)": "epic, grand, orchestral",
    "轻松/慵懒 (Chill/Laid-back)": "chill, laid-back, relaxing",
    "梦幻/空灵 (Dreamy/Ethereal)": "dreamy, ethereal, atmospheric",
    "侵略性/愤怒 (Aggressive/Angry)": "aggressive, angry, forceful"
}

INSTRUMENT_MAPPING = {
    "钢琴叙事 (Piano Ballad)": "melodic piano accompaniment",
    "合成器主导 (Synth-driven)": "synth-driven, lush synthesizers",
    "吉他失真 (Distorted Guitar)": "heavily distorted guitars, chugging riffs",
    "原声吉他 (Acoustic Guitar)": "fingerstyle acoustic guitar",
    "管弦乐团 (Orchestra)": "full orchestral arrangement, strings section",
    "强力鼓点 (Heavy Drums)": "powerful driving drum beat, thumping bass",
    "808贝斯 (808 Bass)": "deep 808 bass, rattling sub-bass",
    "中国乐器-古筝/琵琶 (Guzheng/Pipa)": "traditional Chinese instruments, Pipa and Guzheng"
}

VOCAL_MAPPING = {
    "女声-清亮 (Female-Clear)": "bright, clear female vocals",
    "女声-空灵 (Female-Ethereal)": "breathy, ethereal female vocals",
    "女声-力量 (Female-Power)": "powerful, belting female vocals",
    "男声-深沉 (Male-Deep)": "deep, resonant male vocals",
    "男声-沙哑 (Male-Raspy)": "slightly raspy, gritty male vocals",
    "男女对唱 (Duet)": "male and female duet, harmonizing",
    "说唱-快嘴 (Rap-Fast)": "rapid-fire rapping, intricate flow"
}

RHYTHM_MAPPING = {
    "中速 (Mid-tempo)": "mid-tempo, groovy",
    "慢速 (Slow)": "slow tempo, ballad style",
    "快速 (Fast)": "fast tempo, driving rhythm",
    "四四拍/舞曲 (4-on-the-floor)": "relentless four-on-the-floor beat"
}

# 段落具体风格选项 (用于下拉菜单)
SECTION_STYLES = [
    "抒情主歌 (Melodic Verse)", 
    "说唱主歌 (Rap Verse)", 
    "摇滚主歌 (Rock Verse)", 
    "柔和导歌 (Soft Pre-Chorus)", 
    "渐强导歌 (Building Pre-Chorus)",
    "流行爆发 (Pop Explosion)", 
    "洗脑副歌 (Catchy Hook)", 
    "强力副歌 (Power Chorus)", 
    "情感高潮 (Emotional Climax)",
    "器乐独奏 (Instrumental Solo)", 
    "吉他独奏 (Guitar Solo)",
    "安静桥段 (Quiet Bridge)",
    "诗意主歌 (Poetic Verse)",
    "陷阱说唱 (Trap Rap)",
    "宏大副歌 (Grand Chorus)"
]

# =============================================================================
# 节点类
# =============================================================================
class ACE提示词公式:
    DESCRIPTION = """此节点专为 ACE-Step 1.5 模型设计，针对华语流行音乐优化。
    
【结构说明】
本节点预设了 10 个段落 (Intro -> Outro)，这是生成一首标准 3-4 分钟完整流行歌曲的标准结构。
如果您只需要生成短曲，可将不需要的段落类型选择为“无”。

【使用提示】
- 前端脚本会根据“主要流派”自动调整建议的组件选项。
- 歌词框内已预置了参考歌词，可直接运行测试。"""

    @classmethod
    def INPUT_TYPES(cls):
        # 预定义的段落类型列表 (增加"无"选项以允许用户缩短歌曲)
        types_intro = ["Intro - 纯音乐", "Intro - 带人声", "无"]
        types_verse = ["主歌 (Verse)", "无"]
        types_pre = ["导歌 (Pre-Chorus)", "无"]
        types_chorus = ["副歌 (Chorus)", "无"]
        types_bridge = ["桥段 (Bridge)", "无"]
        types_outro = ["Outro - 淡出", "Outro - 骤停", "无"]

        return {
            "required": {
                "主要流派": (list(GENRE_MAPPING.keys()), {"default": "C-Pop (华语流行)"}),
            },
            "optional": {
                # --- 系统指令 (System Instruction) ---
                "情感氛围": (list(MOOD_MAPPING.keys()), {"default": "浪漫/温馨 (Romantic/Warm)"}),
                "人声特色": (list(VOCAL_MAPPING.keys()), {"default": "女声-清亮 (Female-Clear)"}),
                "乐器重点": (list(INSTRUMENT_MAPPING.keys()), {"default": "钢琴叙事 (Piano Ballad)"}),
                "节奏速度": (list(RHYTHM_MAPPING.keys()), {"default": "中速 (Mid-tempo)"}),
                "额外风格关键词": ("STRING", {"multiline": False, "default": "", "placeholder": "额外补充..."}),
                
                # --- 歌词与结构 (Lyrics & Structure) ---
                
                # 1. Intro (前奏)
                "前奏_类型": (types_intro, {"default": "Intro - 纯音乐"}),
                "前奏_描述": (["钢琴独奏", "环境音效", "合成器渐入", "吉他扫弦"], {"default": "钢琴独奏"}),

                # 2. Verse 1 (主歌 1)
                "段落1_类型": (types_verse, {"default": "主歌 (Verse)"}),
                "段落1_风格描述": (SECTION_STYLES, {"default": "抒情主歌 (Melodic Verse)"}),
                "段落1_歌词": ("STRING", {"multiline": True, "default": "窗外的雨还在下\n滴答滴答敲打着窗纱\n想起那天你转身的刹那\n我的世界仿佛崩塌"}),

                # 3. Pre-Chorus 1 (导歌 1)
                "段落2_类型": (types_pre, {"default": "导歌 (Pre-Chorus)"}),
                "段落2_风格描述": (SECTION_STYLES, {"default": "柔和导歌 (Soft Pre-Chorus)"}),
                "段落2_歌词": ("STRING", {"multiline": True, "default": "回忆像风沙\n迷了眼睛 乱了步伐\n如果在某个路口再遇\n还来得及说出那句话吗"}),

                # 4. Chorus 1 (副歌 1)
                "段落3_类型": (types_chorus, {"default": "副歌 (Chorus)"}),
                "段落3_风格描述": (SECTION_STYLES, {"default": "流行爆发 (Pop Explosion)"}),
                "段落3_歌词": ("STRING", {"multiline": True, "default": "我们的爱 像断线的风筝\n飞向了 遥远的天空\n如果你能听见 这首歌\n是否会懂 我此刻的心痛"}),
                
                # 5. Verse 2 (主歌 2)
                "段落4_类型": (types_verse, {"default": "主歌 (Verse)"}),
                "段落4_风格描述": (SECTION_STYLES, {"default": "抒情主歌 (Melodic Verse)"}),
                "段落4_歌词": ("STRING", {"multiline": True, "default": "咖啡店的角落\n只有我 守着承诺\n看着人来人往的过客\n寻找着 熟悉的轮廓"}),

                # 6. Pre-Chorus 2 (导歌 2)
                "段落5_类型": (types_pre, {"default": "导歌 (Pre-Chorus)"}),
                "段落5_风格描述": (SECTION_STYLES, {"default": "渐强导歌 (Building Pre-Chorus)"}),
                "段落5_歌词": ("STRING", {"multiline": True, "default": "时间在说话\n抚平伤疤 却留牵挂\n如果命运能重新解答\n结局是否会不一样啊"}),

                # 7. Chorus 2 (副歌 2)
                "段落6_类型": (types_chorus, {"default": "副歌 (Chorus)"}),
                "段落6_风格描述": (SECTION_STYLES, {"default": "流行爆发 (Pop Explosion)"}),
                "段落6_歌词": ("STRING", {"multiline": True, "default": "我们的爱 像断线的风筝\n飞向了 遥远的天空\n如果你能听见 这首歌\n是否会懂 我此刻的心痛"}),

                # 8. Bridge (桥段)
                "段落7_类型": (types_bridge, {"default": "桥段 (Bridge)"}),
                "段落7_风格描述": (SECTION_STYLES, {"default": "安静桥段 (Quiet Bridge)"}),
                "段落7_歌词": ("STRING", {"multiline": True, "default": "也许有一天\n我们会擦肩而过\n只要你过得快乐\n我也就 值得"}),

                # 9. Chorus 3 (副歌 3 - 高潮)
                "段落8_类型": (types_chorus, {"default": "副歌 (Chorus)"}),
                "段落8_风格描述": (SECTION_STYLES, {"default": "情感高潮 (Emotional Climax)"}),
                "段落8_歌词": ("STRING", {"multiline": True, "default": "我们的爱 曾是那么生动\n如今只剩 回忆在翻涌\n最后一句 珍重\n是我给你 最后的温柔"}),

                # 10. Outro (尾奏)
                "尾奏_类型": (types_outro, {"default": "Outro - 淡出"}),
                "尾奏_描述": (["钢琴渐弱", "弦乐余音", "人声哼唱", "雨声淡出"], {"default": "钢琴渐弱"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("系统指令(Caption)", "歌词提示词(Lyrics)")
    FUNCTION = "generate_ace_prompt"
    CATEGORY = "📕提示词公式/ACE音乐"

    def generate_ace_prompt(self, 主要流派, 情感氛围, 人声特色, 乐器重点, 节奏速度, 额外风格关键词,
                          前奏_类型, 前奏_描述,
                          段落1_类型, 段落1_风格描述, 段落1_歌词,
                          段落2_类型, 段落2_风格描述, 段落2_歌词,
                          段落3_类型, 段落3_风格描述, 段落3_歌词,
                          段落4_类型, 段落4_风格描述, 段落4_歌词,
                          段落5_类型, 段落5_风格描述, 段落5_歌词,
                          段落6_类型, 段落6_风格描述, 段落6_歌词,
                          段落7_类型, 段落7_风格描述, 段落7_歌词,
                          段落8_类型, 段落8_风格描述, 段落8_歌词,
                          尾奏_类型, 尾奏_描述):
        
        # 1. 构建系统指令 (Caption)
        genre_en = GENRE_MAPPING.get(主要流派, "")
        mood_en = MOOD_MAPPING.get(情感氛围, "")
        vocal_en = VOCAL_MAPPING.get(人声特色, "")
        inst_en = INSTRUMENT_MAPPING.get(乐器重点, "")
        rhythm_en = RHYTHM_MAPPING.get(节奏速度, "")
        extra_en = clean_text(额外风格关键词)
        
        caption_parts = []
        base_desc = f"A {mood_en} {genre_en} track" if mood_en else f"A {genre_en} track"
        caption_parts.append(base_desc)
        
        if inst_en or rhythm_en:
            inst_part = f"featuring {inst_en}" if inst_en else ""
            rhythm_part = f"driven by a {rhythm_en}" if rhythm_en else ""
            if inst_part and rhythm_part: caption_parts.append(f"{inst_part} and {rhythm_part}")
            elif inst_part: caption_parts.append(inst_part)
            elif rhythm_part: caption_parts.append(f"built on a {rhythm_en}")
            
        if vocal_en: caption_parts.append(f"delivered with {vocal_en}")
        if extra_en: caption_parts.append(extra_en)
        
        system_prompt = ". ".join([p for p in caption_parts if p]) + "."
        
        # 2. 构建歌词与结构 (Lyrics)
        lyrics_blocks = []
        
        # 辅助处理函数：提取英文描述
        def get_desc_en(text):
            if not text: return ""
            # 从 "中文 (English)" 中提取 English
            if "(" in text and ")" in text:
                return text.split("(")[1].split(")")[0]
            return clean_text(text)

        def process_section(sec_type_raw, sec_desc_raw, sec_lyrics=None):
            if not sec_type_raw or sec_type_raw == "无": return None
            
            # 提取Tag
            if "Intro" in sec_type_raw: tag = "Intro"
            elif "Outro" in sec_type_raw: tag = "Outro"
            elif "(" in sec_type_raw: tag = sec_type_raw.split("(")[1].split(")")[0]
            else: tag = sec_type_raw

            # 提取Style Description
            desc_en = get_desc_en(sec_desc_raw)
            
            full_tag = f"[{tag} - {desc_en}]" if desc_en else f"[{tag}]"
            
            block = f"{full_tag}"
            if sec_lyrics and clean_text(sec_lyrics):
                block += f"\n{clean_text(sec_lyrics)}"
            
            return block

        # 处理10个段落
        sections = [
            (前奏_类型, 前奏_描述, None),
            (段落1_类型, 段落1_风格描述, 段落1_歌词),
            (段落2_类型, 段落2_风格描述, 段落2_歌词),
            (段落3_类型, 段落3_风格描述, 段落3_歌词),
            (段落4_类型, 段落4_风格描述, 段落4_歌词),
            (段落5_类型, 段落5_风格描述, 段落5_歌词),
            (段落6_类型, 段落6_风格描述, 段落6_歌词),
            (段落7_类型, 段落7_风格描述, 段落7_歌词),
            (段落8_类型, 段落8_风格描述, 段落8_歌词),
            (尾奏_类型, 尾奏_描述, None)
        ]

        for s_type, s_desc, s_lyric in sections:
            block = process_section(s_type, s_desc, s_lyric)
            if block: lyrics_blocks.append(block)
        
        lyrics_prompt = "\n\n".join(lyrics_blocks)
        
        return (system_prompt, lyrics_prompt)

# =============================================================================
# 节点 2: ACE-Step 1.5 高级流派融合 (额外设计)
# =============================================================================
class ACE高级流派融合:
    DESCRIPTION = """此节点专注于生成复杂的【系统指令 (Caption)】，模拟 ACE-Step 1.5 模型擅长的 "流派融合 (Genre-hopping)" 能力。
    
使用场景：
当您希望生成一首风格多变、结构复杂的歌曲时使用（例如：主歌是说唱，副歌突然转变为流行乐）。

使用方法：
1. 【整体流派】：定义歌曲的基底风格。
2. 【分段风格定义】：分别指定主歌(Verse)、导歌(Pre-Chorus)和副歌(Chorus)的独立风格。
3. 【人声描述】：描述人声如何在不同风格间切换。

连接建议：
此节点的输出可作为 "额外风格关键词" 连接到【ACE提示词公式】节点，从而生成包含复杂指令的完整提示词。"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "整体流派": (list(GENRE_MAPPING.keys()), {"default": "K-Pop (韩国流行)"}),
            },
            "optional": {
                "主歌风格(Verse)": (list(GENRE_MAPPING.keys()), {"default": "嘻哈/说唱 (Hip-Hop/Rap)"}),
                "主歌形容词": ("STRING", {"default": "hard-hitting, rapid-fire", "placeholder": "形容主歌的词..."}),
                
                "导歌风格(Pre-Chorus)": (list(GENRE_MAPPING.keys()), {"default": "R&B (节奏蓝调)"}),
                "导歌形容词": ("STRING", {"default": "softer, breathy vocals", "placeholder": "形容导歌的词..."}),
                
                "副歌风格(Chorus)": (list(GENRE_MAPPING.keys()), {"default": "流行 (Pop)"}),
                "副歌形容词": ("STRING", {"default": "explosive, synth-driven, ear worm hook", "placeholder": "形容副歌的词..."}),
                
                "人声描述": ("STRING", {"default": "shifts seamlessly between rapping and singing", "placeholder": "整体人声描述"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("复杂系统指令(Caption)",)
    FUNCTION = "generate_complex_caption"
    CATEGORY = "📕提示词公式/ACE音乐"

    def generate_complex_caption(self, 整体流派, 主歌风格="无", 主歌形容词="", 
                               导歌风格="无", 导歌形容词="", 
                               副歌风格="无", 副歌形容词="", 
                               人声描述=""):
        
        main_genre = GENRE_MAPPING.get(整体流派, "")
        verse_genre = GENRE_MAPPING.get(主歌风格, "")
        pre_genre = GENRE_MAPPING.get(导歌风格, "")
        chorus_genre = GENRE_MAPPING.get(副歌风格, "")
        
        parts = [f"A slick, maximalist {main_genre} track that genre-hops with precision and style"]
        
        structure_desc = []
        
        # 描述主歌
        if verse_genre != "无":
            desc = clean_text(主歌形容词)
            v_str = f"a {desc} {verse_genre} verse" if desc else f"a {verse_genre} verse"
            structure_desc.append(v_str)
            
        # 描述导歌
        if pre_genre != "无":
            desc = clean_text(导歌形容词)
            p_str = f"a {desc} {pre_genre} pre-chorus" if desc else f"a {pre_genre} pre-chorus"
            structure_desc.append(p_str)
            
        # 描述副歌
        if chorus_genre != "无":
            desc = clean_text(副歌形容词)
            c_str = f"an {desc} {chorus_genre} chorus" if desc else f"an {chorus_genre} chorus"
            structure_desc.append(c_str)
            
        if structure_desc:
            transition_text = "The production shifts seamlessly between sections—" + ", ".join(structure_desc)
            parts.append(transition_text)
            
        if clean_text(人声描述):
            parts.append(f"featuring vocals that {clean_text(人声描述)}")
            
        return (". ".join(parts) + ".",)