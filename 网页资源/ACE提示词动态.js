import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ACE.Prompt.Presets",
    async nodeCreated(node, app) {
        if (node.comfyClass === "ACE提示词预设") {
            const genreWidget = node.widgets.find(w => w.name === "主要流派");
            
            // 1. 定义需要自动管理的组件名称列表
            //    注意：不包含"歌曲主题"和"额外风格关键词"，以免误删用户输入的通用提示词
            const STYLE_WIDGETS = [
                "融合流派A", "融合流派B",
                "情感氛围1", "情感氛围2",
                "人声特色1", "人声特色2",
                "乐器重点1", "乐器重点2",
                "节奏速度"
            ];
            
            const SEGMENT_PREFIXES = [
                "前奏", "尾奏",
                "段落1", "段落2", "段落3", "段落4", "段落5", 
                "段落6", "段落7", "段落8", "段落9"
            ];

            // 构建完整的重置目标集合
            const AUTO_RESET_TARGETS = new Set(STYLE_WIDGETS);
            SEGMENT_PREFIXES.forEach(prefix => {
                AUTO_RESET_TARGETS.add(`${prefix}_类型`);
                AUTO_RESET_TARGETS.add(`${prefix}_歌词`);
                
                // 处理描述字段命名的不一致 (前奏/尾奏用 _描述，中间段落用 _风格描述)
                if (prefix === "前奏" || prefix === "尾奏") {
                    AUTO_RESET_TARGETS.add(`${prefix}_描述`);
                } else {
                    AUTO_RESET_TARGETS.add(`${prefix}_风格描述`);
                }
            });

            if (genreWidget) {
                const originalCallback = genreWidget.callback;
                
                genreWidget.callback = function(value) {
                    if (originalCallback) {
                        originalCallback.apply(this, arguments);
                    }
                    
                    const presets = {
                        "标准完整版 (Standard Full)": {
                            "融合流派A": "无",
                            "情感氛围1": "浪漫/温馨 (Romantic/Warm)",
                            "人声特色1": "女声-清亮 (Female-Clear)",
                            "乐器重点1": "钢琴叙事 (Piano Ballad)",
                            "节奏速度": "中速/律动 (Mid-tempo/Groovy)",
                            "前奏_类型": "Intro - 纯音乐", "前奏_描述": "钢琴独奏 (Piano Solo)",
                            "段落1_类型": "主歌 (Verse)", "段落1_风格描述": "抒情主歌 (Melodic Verse)",
                            "段落2_类型": "导歌 (Pre-Chorus)", "段落2_风格描述": "柔和导歌 (Melodic R&B)",
                            "段落3_类型": "副歌 (Chorus)", "段落3_风格描述": "洗脑副歌 (Anthemic Vocal)",
                            "段落4_类型": "主歌 (Verse)", "段落4_风格描述": "抒情主歌 (Melodic Verse)",
                            "段落5_类型": "导歌 (Pre-Chorus)", "段落5_风格描述": "柔和导歌 (Melodic R&B)",
                            "段落6_类型": "堆叠 (Build-up)", "段落6_风格描述": "情绪堆叠 (Atmospheric Build-up)",
                            "段落7_类型": "副歌 (Chorus)", "段落7_风格描述": "洗脑副歌 (Anthemic Vocal)",
                            "段落8_类型": "副歌 (Chorus)", "段落8_风格描述": "洗脑副歌 (Anthemic Vocal)",
                            "段落9_类型": "桥段 (Bridge)", "段落9_风格描述": "吉他独奏 (Guitar Solo)",
                            "尾奏_类型": "Outro - 淡出", "尾奏_描述": "钢琴渐弱 (Piano fade out)"
                        },
                        "C-Pop (华语流行)": {
                            "融合流派A": "无", "情感氛围1": "浪漫/温馨 (Romantic/Warm)", "人声特色1": "女声-清亮 (Female-Clear)", "乐器重点1": "钢琴叙事 (Piano Ballad)", "节奏速度": "中速/律动 (Mid-tempo/Groovy)",
                            "前奏_类型": "Intro - 纯音乐", "前奏_描述": "钢琴独奏 (Piano Solo)",
                            "段落1_类型": "主歌 (Verse)", "段落1_风格描述": "抒情主歌 (Melodic Verse)",
                            "段落2_类型": "导歌 (Pre-Chorus)", "段落2_风格描述": "柔和导歌 (Melodic R&B)",
                            "段落3_类型": "副歌 (Chorus)", "段落3_风格描述": "流行爆发 (Pop Explosion)",
                            "段落4_类型": "主歌 (Verse)", "段落4_风格描述": "抒情主歌 (Melodic Verse)",
                            "段落6_类型": "堆叠 (Build-up)", "段落6_风格描述": "情绪堆叠 (Atmospheric Build-up)",
                            "段落7_类型": "副歌 (Chorus)", "段落7_风格描述": "洗脑副歌 (Anthemic Vocal)",
                            "尾奏_类型": "Outro - 淡出", "尾奏_描述": "钢琴渐弱 (Piano fade out)"
                        },
                        "K-Pop (韩国流行)": {
                            "融合流派A": "嘻哈/说唱 (Hip-Hop/Rap)", "情感氛围1": "高能/科技感 (High-Energy/Tech)", "人声特色1": "男女对唱 (Duet)", "乐器重点1": "合成器主导 (Synth-driven)", "节奏速度": "快速/疾驰 (Fast-Paced)",
                            "前奏_类型": "Intro - 故障音效", "前奏_描述": "故障前奏 (Glitchy Error Sounds)",
                            "段落1_类型": "说唱 (Rap Verse)", "段落1_风格描述": "说唱主歌 (Rap Verse)",
                            "段落3_类型": "副歌 (Chorus)", "段落3_风格描述": "洗脑副歌 (Anthemic Vocal)",
                            "段落4_类型": "说唱 (Rap Verse)", "段落4_风格描述": "快嘴说唱 (Fast Flow Rap)",
                            "段落5_类型": "导歌 (Pre-Chorus)", "段落5_风格描述": "柔和导歌 (Melodic R&B)",
                            "段落6_类型": "堆叠 (Build-up)", "段落6_风格描述": "情绪堆叠 (Atmospheric Build-up)",
                            "段落7_类型": "跌落 (Drop)", "段落7_风格描述": "电子跌落 (Future Bass Drop)", 
                            "尾奏_类型": "Outro - 骤停", "尾奏_描述": "故障淡出 (Glitch fade)"
                        },
                        "J-Pop (日本流行)": {
                            "融合流派A": "摇滚 (Rock)", "情感氛围1": "欢快/高能量 (Upbeat/High Energy)", "人声特色1": "女声-可爱/元气 (Female-Clear)", "乐器重点1": "钢琴叙事 (Piano Ballad)", "节奏速度": "快速/疾驰 (Fast-Paced)",
                            "段落1_类型": "主歌 (Verse)", "段落1_风格描述": "诗意主歌 (Poetic Verse)",
                            "段落3_类型": "副歌 (Chorus)", "段落3_风格描述": "流行爆发 (Pop Explosion)",
                            "段落7_类型": "桥段 (Bridge)", "段落7_风格描述": "吉他独奏 (Guitar Solo)", 
                        },
                        "流行 (Pop)": {
                            "情感氛围1": "欢快/高能量 (Upbeat/High Energy)", "乐器重点1": "合成器主导 (Synth-driven)",
                            "段落1_类型": "主歌 (Verse)", "段落1_风格描述": "抒情主歌 (Melodic Verse)",
                            "段落3_类型": "副歌 (Chorus)", "段落3_风格描述": "洗脑副歌 (Anthemic Vocal)"
                        },
                        "未来贝斯 (Future Bass)": {
                            "融合流派A": "赛博朋克 (Cyberpunk)", "情感氛围1": "高能/科技感 (High-Energy/Tech)", "人声特色1": "自动调音/电音 (Auto-tuned)", "乐器重点1": "超锯齿波合成器 (Heavy Supersaws)", "节奏速度": "切分音 (Syncopated)",
                            "前奏_类型": "Intro - 故障音效", "前奏_描述": "故障前奏 (Glitchy Error Sounds)",
                            "段落1_类型": "堆叠 (Build-up)", "段落1_风格描述": "情绪堆叠 (Atmospheric Build-up)",
                            "段落2_类型": "跌落 (Drop)", "段落2_风格描述": "电子跌落 (Future Bass Drop)",
                            "段落3_类型": "主歌 (Verse)", "段落3_风格描述": "故障切片 (Vocal Chop)",
                            "段落4_类型": "堆叠 (Build-up)", "段落4_风格描述": "情绪堆叠 (Atmospheric Build-up)",
                            "段落5_类型": "跌落 (Drop)", "段落5_风格描述": "重低音跌落 (Heavy Synth Drop)", "尾奏_类型": "Outro - 骤停"
                        },
                        "赛博朋克 (Cyberpunk)": {
                            "融合流派A": "电子舞曲 (EDM)", "情感氛围1": "紧张/故障感 (Tense/Glitchy)", "人声特色1": "机械/机器人 (Robotic)", "乐器重点1": "故障音效 (Glitch Sounds)",
                            "前奏_类型": "Intro - 故障音效", "前奏_描述": "环境音效 (Ambient Sci-fi)",
                            "段落1_类型": "说唱 (Rap Verse)", "段落1_风格描述": "冷酷念白 (Spoken Word)",
                            "段落2_类型": "跌落 (Drop)", "段落2_风格描述": "重低音跌落 (Heavy Synth Drop)"
                        },
                        "电子舞曲 (EDM)": {
                            "情感氛围1": "欢快/高能量 (Upbeat/High Energy)", "乐器重点1": "强力鼓点 (Heavy Drums)",
                            "段落3_类型": "跌落 (Drop)", "段落3_风格描述": "电子跌落 (Future Bass Drop)"
                        },
                        "故障艺术 (Glitch Hop)": {
                            "融合流派A": "嘻哈/说唱 (Hip-Hop/Rap)", "乐器重点1": "故障音效 (Glitch Sounds)", "节奏速度": "切分音 (Syncopated)",
                            "前奏_类型": "Intro - 故障音效", "前奏_描述": "故障前奏 (Glitchy Error Sounds)",
                            "段落1_类型": "说唱 (Rap Verse)", "段落1_风格描述": "快嘴说唱 (Fast Flow Rap)"
                        },
                        "陷阱音乐 (Trap)": {
                            "情感氛围1": "黑暗/深沉 (Dark/Deep)", "乐器重点1": "808贝斯 (808 Bass)", "节奏速度": "中速/律动 (Mid-tempo/Groovy)",
                            "前奏_类型": "Intro - 纯音乐", "前奏_描述": "器乐独奏 (Instrumental Solo)",
                            "段落1_类型": "说唱 (Rap Verse)", "段落1_风格描述": "陷阱说唱 (Aggressive Trap Rap)",
                            "段落2_类型": "副歌 (Chorus)", "段落2_风格描述": "洗脑副歌 (Anthemic Vocal)",
                            "段落3_类型": "说唱 (Rap Verse)", "段落3_风格描述": "陷阱说唱 (Aggressive Trap Rap)", "尾奏_类型": "Outro - 骤停"
                        },
                        "嘻哈/说唱 (Hip-Hop/Rap)": {
                            "情感氛围1": "愤怒/侵略性 (Angry/Aggressive)", "人声特色1": "说唱-快嘴 (Rap-Fast Flow)", "乐器重点1": "强力鼓点 (Heavy Drums)",
                            "段落1_类型": "说唱 (Rap Verse)", "段落1_风格描述": "快嘴说唱 (Fast Flow Rap)",
                            "段落4_类型": "说唱 (Rap Verse)", "段落4_风格描述": "快嘴说唱 (Fast Flow Rap)"
                        },
                        "摇滚 (Rock)": {
                            "融合流派A": "金属 (Metal)", "情感氛围1": "愤怒/侵略性 (Angry/Aggressive)", "人声特色1": "男声-力量 (Male-Forceful)", "乐器重点1": "吉他失真 (Distorted Guitar)",
                            "段落1_类型": "主歌 (Verse)", "段落1_风格描述": "摇滚主歌 (Rock Verse)",
                            "段落3_类型": "副歌 (Chorus)", "段落3_风格描述": "流行爆发 (Pop Explosion)",
                            "段落7_类型": "桥段 (Bridge)", "段落7_风格描述": "吉他独奏 (Guitar Solo)"
                        },
                        "金属 (Metal)": {
                            "情感氛围1": "黑暗/深沉 (Dark/Deep)", "乐器重点1": "吉他失真 (Distorted Guitar)",
                            "段落1_类型": "主歌 (Verse)", "段落1_风格描述": "摇滚主歌 (Rock Verse)",
                            "段落3_类型": "跌落 (Drop)", "段落3_风格描述": "重低音跌落 (Heavy Synth Drop)"
                        },
                        "中国风/古风 (Chinese Traditional)": {
                            "情感氛围1": "梦幻/空灵 (Dreamy/Ethereal)", "人声特色1": "女声-空灵 (Female-Ethereal)", "乐器重点1": "中国乐器-古筝/琵琶", "节奏速度": "慢速 (Slow)",
                            "前奏_类型": "Intro - 纯音乐", "前奏_描述": "器乐独奏 (Instrumental Solo)",
                            "段落1_类型": "主歌 (Verse)", "段落1_风格描述": "诗意主歌 (Poetic Verse)",
                            "段落2_类型": "副歌 (Chorus)", "段落2_风格描述": "宏大副歌 (Grand Chorus)",
                            "段落3_类型": "桥段 (Bridge)", "段落3_风格描述": "器乐独奏 (Instrumental Solo)",
                            "尾奏_类型": "Outro - 淡出", "尾奏_描述": "器乐独奏 (Instrumental Solo)"
                        },
                        "电影配乐 (Cinematic)": {
                            "融合流派A": "歌剧 (Opera)", "情感氛围1": "史诗/胜利 (Epic/Triumphant)", "人声特色1": "合唱团 (Choir)", "乐器重点1": "管弦乐团 (Orchestra)",
                            "段落1_类型": "堆叠 (Build-up)", "段落1_风格描述": "情绪堆叠 (Atmospheric Build-up)",
                            "段落2_类型": "副歌 (Chorus)", "段落2_风格描述": "宏大副歌 (Grand Chorus)", "尾奏_类型": "Outro - 淡出"
                        },
                        "爵士 (Jazz)": {
                            "融合流派A": "R&B (节奏蓝调)", "情感氛围1": "轻松/慵懒 (Chill/Laid-back)", "乐器重点1": "萨克斯风 (Saxophone)", "节奏速度": "切分音 (Syncopated)",
                            "前奏_类型": "Intro - 纯音乐", "前奏_描述": "器乐独奏 (Instrumental Solo)",
                            "段落7_类型": "桥段 (Bridge)", "段落7_风格描述": "器乐独奏 (Instrumental Solo)"
                        },
                        "R&B (节奏蓝调)": {
                            "融合流派A": "灵魂乐 (Soul)", "情感氛围1": "浪漫/温馨 (Romantic/Warm)", "人声特色1": "女声-精致 (Female-Polished)",
                            "段落1_类型": "导歌 (Pre-Chorus)", "段落1_风格描述": "柔和导歌 (Melodic R&B)",
                            "段落3_类型": "副歌 (Chorus)", "段落3_风格描述": "洗脑副歌 (Anthemic Vocal)"
                        },
                        "民谣 (Folk)": {
                            "情感氛围1": "轻松/慵懒 (Chill/Laid-back)", "乐器重点1": "原声吉他 (Acoustic Guitar)", "节奏速度": "慢速 (Slow)",
                            "段落1_类型": "主歌 (Verse)", "段落1_风格描述": "诗意主歌 (Poetic Verse)"
                        },
                         "歌剧 (Opera)": {
                            "情感氛围1": "史诗/胜利 (Epic/Triumphant)", "人声特色1": "合唱团 (Choir)", "乐器重点1": "管弦乐团 (Orchestra)",
                            "段落3_类型": "副歌 (Chorus)", "段落3_风格描述": "宏大副歌 (Grand Chorus)"
                        }
                    };

                    const preset = presets[value];
                    if (preset) {
                        // 遍历所有受控组件
                        for (const widgetName of AUTO_RESET_TARGETS) {
                            const targetWidget = node.widgets.find(w => w.name === widgetName);
                            if (!targetWidget) continue;

                            let targetValue = "无"; // 默认下拉框设为“无”

                            // 判断预设中是否存在该配置
                            if (preset.hasOwnProperty(widgetName)) {
                                targetValue = preset[widgetName];
                            } else {
                                // 如果预设未提及，且组件是文本输入框，则设为空字符串
                                if (targetWidget.type === "STRING" || targetWidget.type === "customtext") {
                                    targetValue = ""; 
                                }
                            }

                            // 仅当数值确实需要改变时才更新，避免不必要的重绘
                            if (targetWidget.value !== targetValue) {
                                targetWidget.value = targetValue;
                                if (targetWidget.callback) {
                                    targetWidget.callback(targetValue);
                                }
                            }
                        }

                        node.setDirtyCanvas(true, true);
                    }
                };
            }
        }
    }
});