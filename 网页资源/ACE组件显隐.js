import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ACE.Prompt.Visibility",
    async nodeCreated(node, app) {
        // 修改点：只针对“ACE提示词预设”启用显隐逻辑
        if (node.comfyClass === "ACE提示词预设") {
            
            const DEFAULT_WIDTH = 500;

            // =========================================================
            // 1. 初始化
            // =========================================================
            setTimeout(() => {
                const h = node.size ? node.size[1] : 300;
                node.setSize([Math.max(node.size[0], DEFAULT_WIDTH), h]);
                node.updateWidgetStates();
            }, 100);

            // =========================================================
            // 2. 核心逻辑：禁用变灰控制
            // =========================================================
            node.updateWidgetStates = function() {
                const widgets = node.widgets || [];
                
                const findVal = (name) => {
                    const w = widgets.find(x => x.name === name);
                    return w ? w.value : "无";
                };
                
                const mainGenre = findVal("主要流派");
                const mixMode = findVal("融合流派A");

                // --- B. 构建"启用"白名单 ---
                const activeNames = new Set([
                    "主要流派", "融合流派A", "歌曲主题", 
                    "情感氛围1", "人声特色1", "乐器重点1", "节奏速度", "额外风格关键词"
                ]);

                // 【关键修改】如果主流派是"无"或"标准完整版"，则启用所有混合选项（自由模式）
                const isFreeMode = (mainGenre === "无" || mainGenre === "标准完整版 (Standard Full)");

                if (isFreeMode || (mixMode && mixMode !== "无")) {
                    activeNames.add("融合流派B");
                    activeNames.add("情感氛围2");
                    activeNames.add("人声特色2");
                    activeNames.add("乐器重点2");
                }

                // 动态段落组件
                const sections = [
                    { prefix: "前奏", type: "前奏_类型" },
                    { prefix: "段落1", type: "段落1_类型" },
                    { prefix: "段落2", type: "段落2_类型" },
                    { prefix: "段落3", type: "段落3_类型" },
                    { prefix: "段落4", type: "段落4_类型" },
                    { prefix: "段落5", type: "段落5_类型" },
                    { prefix: "段落6", type: "段落6_类型" },
                    { prefix: "段落7", type: "段落7_类型" },
                    { prefix: "段落8", type: "段落8_类型" },
                    { prefix: "段落9", type: "段落9_类型" },
                    { prefix: "尾奏", type: "尾奏_类型" }
                ];

                sections.forEach(sec => {
                    // 类型选择器永远启用
                    activeNames.add(sec.type);
                    
                    // 【关键修改】自由模式下，或者当前段落类型不为"无"时，启用详情
                    const currentTypeVal = findVal(sec.type);
                    if (isFreeMode || (currentTypeVal && currentTypeVal !== "无")) {
                        activeNames.add(`${sec.prefix}_风格描述`);
                        activeNames.add(`${sec.prefix}_描述`);
                        activeNames.add(`${sec.prefix}_歌词`);
                    }
                });

                // --- C. 应用状态 ---
                let changed = false;
                
                for (const w of widgets) {
                    const shouldEnable = activeNames.has(w.name);
                    
                    // 1. LiteGraph 禁用状态
                    if (w.disabled !== !shouldEnable) {
                        w.disabled = !shouldEnable;
                        changed = true;
                    }

                    // 2. DOM 视觉反馈
                    if (w.element) {
                        if (shouldEnable) {
                            w.element.disabled = false;
                            w.element.style.opacity = "1.0";
                            w.element.style.pointerEvents = "auto";
                            w.element.style.filter = "none";
                            // 恢复多行文本框高度
                            if (w.options && w.options.multiline) {
                                w.element.style.height = "auto"; 
                                w.element.style.minHeight = "60px";
                            }
                        } else {
                            w.element.disabled = true;
                            w.element.style.opacity = "0.4"; 
                            w.element.style.pointerEvents = "none"; 
                            w.element.style.filter = "grayscale(100%)"; 
                            // 折叠高度
                            if (w.options && w.options.multiline) {
                                w.element.style.height = "24px"; 
                                w.element.style.minHeight = "24px";
                            }
                        }
                    }
                }

                if (changed) {
                    node.setDirtyCanvas(true, true);
                }
            };

            // =========================================================
            // 3. 绑定回调
            // =========================================================
            // 增加监控 "主要流派"
            const triggerWidgets = [
                "主要流派", "融合流派A", 
                "前奏_类型", "尾奏_类型",
                "段落1_类型", "段落2_类型", "段落3_类型", 
                "段落4_类型", "段落5_类型", "段落6_类型", 
                "段落7_类型", "段落8_类型", "段落9_类型"
            ];

            setTimeout(() => {
                if (!node.widgets) return;

                triggerWidgets.forEach(name => {
                    const widget = node.widgets.find(w => w.name === name);
                    if (widget) {
                        const originalCallback = widget.callback;
                        widget.callback = function(value) {
                            if (originalCallback) {
                                originalCallback.apply(this, arguments);
                            }
                            node.updateWidgetStates();
                        };
                    }
                });
            }, 200);

            const onConfigure = node.onConfigure;
            node.onConfigure = function() {
                if (onConfigure) onConfigure.apply(this, arguments);
                setTimeout(() => {
                    node.updateWidgetStates();
                }, 100);
            };
        }
    }
});