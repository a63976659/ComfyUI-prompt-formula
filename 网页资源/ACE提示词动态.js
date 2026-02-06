import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ACE.Prompt.Dynamic",
    async nodeCreated(node, app) {
        if (node.comfyClass === "ACE提示词公式") {
            const genreWidget = node.widgets.find(w => w.name === "主要流派");
            
            if (genreWidget) {
                const callback = genreWidget.callback;
                genreWidget.callback = function(value) {
                    if (callback) {
                        callback.apply(this, arguments);
                    }
                    
                    // 定义流派对应的智能全曲预设
                    const presets = {
                        "C-Pop (华语流行)": {
                            "情感氛围": "浪漫/温馨 (Romantic/Warm)",
                            "人声特色": "女声-清亮 (Female-Clear)",
                            "乐器重点": "钢琴叙事 (Piano Ballad)",
                            // Verse (主歌) 统一风格
                            "段落1_风格描述": "抒情主歌 (Melodic Verse)",
                            "段落4_风格描述": "抒情主歌 (Melodic Verse)",
                            // Pre-Chorus (导歌) 统一风格
                            "段落2_风格描述": "柔和导歌 (Soft Pre-Chorus)",
                            "段落5_风格描述": "渐强导歌 (Building Pre-Chorus)",
                            // Chorus (副歌) 统一风格
                            "段落3_风格描述": "流行爆发 (Pop Explosion)",
                            "段落6_风格描述": "流行爆发 (Pop Explosion)",
                            "段落8_风格描述": "情感高潮 (Emotional Climax)",
                            // Bridge (桥段)
                            "段落7_风格描述": "安静桥段 (Quiet Bridge)"
                        },
                        "K-Pop (韩国流行)": {
                            "情感氛围": "欢快/高能量 (Upbeat/High Energy)",
                            "人声特色": "男女对唱 (Duet)",
                            "乐器重点": "合成器主导 (Synth-driven)",
                            "段落1_风格描述": "说唱主歌 (Rap Verse)",
                            "段落4_风格描述": "说唱主歌 (Rap Verse)",
                            "段落2_风格描述": "柔和导歌 (Soft Pre-Chorus)",
                            "段落5_风格描述": "渐强导歌 (Building Pre-Chorus)",
                            "段落3_风格描述": "洗脑副歌 (Catchy Hook)",
                            "段落6_风格描述": "洗脑副歌 (Catchy Hook)",
                            "段落8_风格描述": "洗脑副歌 (Catchy Hook)",
                            "段落7_风格描述": "器乐独奏 (Instrumental Solo)"
                        },
                        "摇滚 (Rock)": {
                            "情感氛围": "侵略性/愤怒 (Aggressive/Angry)",
                            "人声特色": "男声-沙哑 (Male-Raspy)",
                            "乐器重点": "吉他失真 (Distorted Guitar)",
                            "段落1_风格描述": "摇滚主歌 (Rock Verse)",
                            "段落4_风格描述": "摇滚主歌 (Rock Verse)",
                            "段落2_风格描述": "渐强导歌 (Building Pre-Chorus)",
                            "段落5_风格描述": "渐强导歌 (Building Pre-Chorus)",
                            "段落3_风格描述": "强力副歌 (Power Chorus)",
                            "段落6_风格描述": "强力副歌 (Power Chorus)",
                            "段落8_风格描述": "强力副歌 (Power Chorus)",
                            "段落7_风格描述": "吉他独奏 (Guitar Solo)"
                        },
                        "嘻哈/说唱 (Hip-Hop/Rap)": {
                            "情感氛围": "黑暗/紧张 (Dark/Tense)",
                            "人声特色": "说唱-快嘴 (Rap-Fast)",
                            "乐器重点": "808贝斯 (808 Bass)",
                            "段落1_风格描述": "陷阱说唱 (Trap Rap)",
                            "段落4_风格描述": "陷阱说唱 (Trap Rap)",
                            "段落2_风格描述": "抒情主歌 (Melodic Verse)",
                            "段落5_风格描述": "抒情主歌 (Melodic Verse)",
                            "段落3_风格描述": "旋律说唱 (Melodic Rap)",
                            "段落6_风格描述": "旋律说唱 (Melodic Rap)",
                            "段落8_风格描述": "旋律说唱 (Melodic Rap)",
                            "段落7_风格描述": "器乐独奏 (Instrumental Solo)"
                        },
                        "中国风/古风 (Chinese Traditional)": {
                            "情感氛围": "梦幻/空灵 (Dreamy/Ethereal)",
                            "人声特色": "女声-空灵 (Female-Ethereal)",
                            "乐器重点": "中国乐器-古筝/琵琶 (Guzheng/Pipa)",
                            "段落1_风格描述": "诗意主歌 (Poetic Verse)",
                            "段落4_风格描述": "诗意主歌 (Poetic Verse)",
                            "段落2_风格描述": "柔和导歌 (Soft Pre-Chorus)",
                            "段落5_风格描述": "柔和导歌 (Soft Pre-Chorus)",
                            "段落3_风格描述": "宏大副歌 (Grand Chorus)",
                            "段落6_风格描述": "宏大副歌 (Grand Chorus)",
                            "段落8_风格描述": "宏大副歌 (Grand Chorus)",
                            "段落7_风格描述": "器乐独奏 (Instrumental Solo)"
                        }
                    };

                    const preset = presets[value];
                    if (preset) {
                        for (const [key, val] of Object.entries(preset)) {
                            const targetWidget = node.widgets.find(w => w.name === key);
                            if (targetWidget) {
                                targetWidget.value = val;
                            }
                        }
                        node.setDirtyCanvas(true, true);
                    }
                };
            }
        }
    }
});