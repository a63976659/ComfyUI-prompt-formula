import { app } from "../../../scripts/app.js";
import { $el } from "../../../scripts/ui.js";
import { api } from "../../../scripts/api.js";

let presetCache = null;

async function getPresetData() {
    if (presetCache) return presetCache;
    try {
        const resp = await api.fetchApi("/preset_preview/list");
        presetCache = await resp.json();
        return presetCache;
    } catch (e) {
        console.error("获取预设数据失败:", e);
        return {};
    }
}

app.registerExtension({
    name: "ComfyUI-prompt-formula.AgentDialogPreset",
    
    async init() {
        $el("style", {
            textContent: `
                .preset-content-preview {
                    background: var(--comfy-input-bg);
                    border: 1px solid var(--border-color);
                    border-radius: 4px;
                    padding: 8px;
                    margin: 8px auto;
                    font-size: 11px;
                    line-height: 1.3;
                    color: var(--input-text);
                    overflow: auto;
                    word-wrap: break-word;
                    white-space: pre-wrap;
                    font-family: monospace;
                    min-height: 40px;
                    display: flex;
                    align-items: flex-start;
                    box-sizing: border-box;
                    width: calc(100% - 16px);
                }
                .preset-content-empty { color: var(--descrip-text); font-style: italic; opacity: 0.7; justify-content: center; align-items: center; }
                .preset-content-loaded { justify-content: flex-start; align-items: flex-start; }
                .preset-content-preview::-webkit-scrollbar { width: 6px; }
                .preset-content-preview::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); border-radius: 3px; }
                .preset-content-preview::-webkit-scrollbar-thumb { background: var(--descrip-text); border-radius: 3px; }

                .agent-save-row {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    background: var(--comfy-input-bg);
                    border: 1px solid var(--border-color);
                    border-radius: 4px;
                    padding: 6px 12px;
                    margin: 8px auto;
                    width: calc(100% - 16px);
                    box-sizing: border-box;
                    color: var(--input-text);
                    font-family: sans-serif;
                    font-size: 12px;
                }
                .agent-switch { position: relative; display: inline-block; width: 36px; height: 20px; }
                .agent-switch input { opacity: 0; width: 0; height: 0; }
                .agent-slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #555; transition: .3s; border-radius: 20px; }
                .agent-slider:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background-color: white; transition: .3s; border-radius: 50%; }
                .agent-switch input:checked + .agent-slider { background-color: #4CAF50; }
                .agent-switch input:checked + .agent-slider:before { transform: translateX(16px); }

                /* 纯 CSS 手动输入框样式 */
                .agent-manual-input-container {
                    display: flex;
                    flex-direction: column;
                    width: calc(100% - 16px);
                    margin: 4px auto;
                }
                .agent-manual-label {
                    font-size: 11px;
                    color: var(--descrip-text, #aaa);
                    margin-bottom: 4px;
                    margin-left: 2px;
                    font-weight: 600;
                }
                .agent-manual-input {
                    background-color: var(--comfy-input-bg);
                    color: var(--input-text);
                    border: 1px solid var(--border-color);
                    border-radius: 4px;
                    padding: 6px 8px;
                    font-size: 12px;
                    outline: none;
                    width: 100%;
                    box-sizing: border-box;
                    height: 28px;
                    transition: border-color 0.2s;
                }
                .agent-manual-input:focus { border-color: #888; }
            `,
            parent: document.head
        });
        await getPresetData();
    },

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "智能体对话预设") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) {
                    try { onNodeCreated.apply(this, arguments); } 
                    catch(e) { console.error(e); }
                }
                
                const node = this;
                const getW = (name) => node.widgets && node.widgets.find(w => w.name === name);

                // ==========================================
                // 1. 创建 UI 组件矩阵
                // ==========================================
                
                // 1.1 预设预览框 DOM
                node.previewSub = $el("div", { className: "preset-content-preview preset-content-empty", textContent: "请选择主体描述预设..." });
                node.previewSys = $el("div", { className: "preset-content-preview preset-content-empty", textContent: "请选择系统指令预设..." });
                
                node.widgetPreviewSub = node.addDOMWidget("custom_dom_prev_sub", "preview", node.previewSub, { getValue: () => "", setValue: () => {} });
                node.widgetPreviewSys = node.addDOMWidget("custom_dom_prev_sys", "preview", node.previewSys, { getValue: () => "", setValue: () => {} });

                // 1.2 手动输入框工厂函数 (纯 CSS 版)
                const createManualInput = (labelText, nativeName) => {
                    const wrap = $el("div", { className: "agent-manual-input-container" });
                    const lbl = $el("div", { className: "agent-manual-label", textContent: labelText });
                    const inp = $el("input", { type: "text", className: "agent-manual-input", placeholder: "点击输入..." });
                    wrap.appendChild(lbl);
                    wrap.appendChild(inp);
                    
                    const nativeW = getW(nativeName);
                    if (nativeW) inp.value = nativeW.value; 
                    
                    // 监听输入，实时同步给后端的幽灵组件
                    inp.addEventListener("input", e => {
                        const nw = getW(nativeName);
                        if (nw) nw.value = e.target.value;
                    });
                    
                    // 彻底解决拖拽、复制粘贴的焦点拦截问题
                    inp.addEventListener("pointerdown", e => e.stopPropagation());
                    inp.addEventListener("keydown", e => e.stopPropagation());
                    
                    const widgetName = "custom_dom_man_" + nativeName;
                    const widget = node.addDOMWidget(widgetName, "preview", wrap, { getValue: () => "", setValue: () => {} });
                    return { wrap, inp, widget };
                };

                node.manSub = createManualInput("✍️ 主体描述", "手动_主体描述");
                node.manSys = createManualInput("✍️ 系统指令", "手动_系统指令");

                // 1.3 CSS 现代开关组件
                const nativeSave = getW("保存为预设");
                node.saveCheckbox = $el("input", { type: "checkbox", checked: nativeSave ? nativeSave.value : false });
                
                node.saveCheckbox.addEventListener("change", e => {
                    const ns = getW("保存为预设");
                    if (ns) ns.value = e.target.checked;
                });
                
                node.saveRow = $el("div", { className: "agent-save-row" }, [
                    $el("span", { textContent: "💾 开启保存预设" }),
                    $el("label", { className: "agent-switch" }, [node.saveCheckbox, $el("span", { className: "agent-slider" })])
                ]);
                node.widgetSave = node.addDOMWidget("custom_dom_save", "preview", node.saveRow, { getValue: () => "", setValue: () => {} });

                // ==========================================
                // 2. 绝对排版机制 (彻底杜绝混乱重叠)
                // ==========================================
                // 按我们想要的终极视觉顺序定义数组
                const layoutOrder = [
                    "模式",
                    "预设_主体描述",
                    "custom_dom_prev_sub",
                    "预设_系统指令",
                    "custom_dom_prev_sys",
                    "手动_主体描述", // 原生组件(稍后会幽灵化)
                    "手动_系统指令", // 原生组件
                    "保存为预设",    // 原生组件
                    "custom_dom_man_手动_主体描述",
                    "custom_dom_man_手动_系统指令",
                    "custom_dom_save"
                ];
                
                const newWidgets = [];
                // 先放入不属于上面的核心组件 (如果有的话)
                node.widgets.forEach(w => {
                    if (!layoutOrder.includes(w.name)) newWidgets.push(w);
                });
                // 严格按照我们定义的顺序插入组件
                layoutOrder.forEach(name => {
                    const w = node.widgets.find(x => x.name === name);
                    if (w) newWidgets.push(w);
                });
                node.widgets = newWidgets;

                // ==========================================
                // 3. 数据预览更新逻辑
                // ==========================================
                const updatePreviews = async () => {
                    const data = await getPresetData();
                    const setContent = (el, val, folder) => {
                        if (val && val !== "无") {
                            const key = folder + "/" + val.replace(/\.txt$/i, '');
                            const content = data[key]?.完整内容;
                            if (content) {
                                el.textContent = content;
                                el.className = "preset-content-preview preset-content-loaded";
                            } else {
                                el.textContent = "内容为空";
                                el.className = "preset-content-preview preset-content-empty";
                            }
                        } else {
                            el.textContent = "请选择预设...";
                            el.className = "preset-content-preview preset-content-empty";
                        }
                    };

                    if (getW("预设_主体描述")) setContent(node.previewSub, getW("预设_主体描述").value, "主体描述");
                    if (getW("预设_系统指令")) setContent(node.previewSys, getW("预设_系统指令").value, "系统指令");

                    if (node.previewSub.style.display !== "none") {
                        node.widgetPreviewSub.computeSize = () => [0, node.previewSub.offsetHeight + 16];
                        node.widgetPreviewSys.computeSize = () => [0, node.previewSys.offsetHeight + 16];
                    }
                    node.setDirtyCanvas(true, true);
                };

                ["预设_主体描述", "预设_系统指令"].forEach(name => {
                    const w = getW(name);
                    if (w) {
                        const origCb = w.callback;
                        w.callback = function() {
                            if (origCb) origCb.apply(this, arguments);
                            updatePreviews();
                        };
                    }
                });

                // ==========================================
                // 4. 终极幽灵化 & 显隐控制引擎
                // ==========================================
                node.toggleVisibility = () => {
                    const modeW = getW("模式");
                    if (!modeW) return;
                    const isPreset = modeW.value === "使用预设";

                    // 万能遮蔽法：只要是被点名隐藏的，一律打入冷宫！
                    const toggleCanvasW = (name, show) => {
                        const w = getW(name);
                        if (!w) return;
                        
                        // 只在第一次备份它最原始健康的属性
                        if (w._backedUp === undefined) {
                            w._origType = w.type;
                            w._origComputeSize = w.hasOwnProperty('computeSize') ? w.computeSize : undefined;
                            w._origDraw = w.hasOwnProperty('draw') ? w.draw : undefined;
                            w._origMouse = w.hasOwnProperty('mouse') ? w.mouse : undefined;
                            w._backedUp = true;
                        }

                        if (show) {
                            w.type = w._origType;
                            if (w._origComputeSize !== undefined) w.computeSize = w._origComputeSize; else delete w.computeSize;
                            if (w._origDraw !== undefined) w.draw = w._origDraw; else delete w.draw;
                            if (w._origMouse !== undefined) w.mouse = w._origMouse; else delete w.mouse;
                            
                            if (w.inputEl) w.inputEl.style.display = "";
                            if (w.element) w.element.style.display = "";
                        } else {
                            w.type = "hidden";
                            // 返回 [0, -4] 可以完美抵消 ComfyUI 默认增加的 4px 渲染缝隙
                            w.computeSize = () => [0, -4];
                            w.draw = () => {};
                            w.mouse = () => false;
                            
                            if (w.inputEl) w.inputEl.style.display = "none";
                            if (w.element) w.element.style.display = "none";
                        }
                    };

                    // 原生的手动输入框和保存开关，不论何种模式，永久幽灵化！
                    toggleCanvasW("手动_主体描述", false);
                    toggleCanvasW("手动_系统指令", false);
                    toggleCanvasW("保存为预设", false);

                    // 预设模式下的原生下拉框
                    toggleCanvasW("预设_主体描述", isPreset);
                    toggleCanvasW("预设_系统指令", isPreset);

                    // 控制 CSS UI 界面
                    if (isPreset) {
                        // 显示预设预览
                        node.previewSub.style.display = "flex";
                        node.previewSys.style.display = "flex";
                        updatePreviews();
                        
                        // 隐藏我们自己写的手动 DOM
                        node.manSub.wrap.style.display = "none";
                        node.manSys.wrap.style.display = "none";
                        node.saveRow.style.display = "none";
                        
                        node.manSub.widget.computeSize = () => [0, -4];
                        node.manSys.widget.computeSize = () => [0, -4];
                        node.widgetSave.computeSize = () => [0, -4];
                    } else {
                        // 隐藏预设预览
                        node.previewSub.style.display = "none";
                        node.previewSys.style.display = "none";
                        node.widgetPreviewSub.computeSize = () => [0, -4];
                        node.widgetPreviewSys.computeSize = () => [0, -4];
                        
                        // 显示手动 DOM 和保存按钮
                        node.manSub.wrap.style.display = "flex";
                        node.manSys.wrap.style.display = "flex";
                        node.saveRow.style.display = "flex";
                        
                        // CSS 元素占据的高度
                        node.manSub.widget.computeSize = () => [0, 40]; 
                        node.manSys.widget.computeSize = () => [0, 40];
                        node.widgetSave.computeSize = () => [0, 40]; 
                    }

                    // 刷新自适应尺寸
                    requestAnimationFrame(() => {
                        if (node.computeSize) {
                            const size = node.computeSize();
                            size[0] = Math.max(340, size[0]);
                            node.setSize(size);
                            node.setDirtyCanvas(true, true);
                        }
                    });
                };

                const modeW = getW("模式");
                if (modeW) {
                    const origCb = modeW.callback;
                    modeW.callback = function() {
                        if (origCb) origCb.apply(this, arguments);
                        node.toggleVisibility();
                    }.bind(this);
                }

                // 首次挂载初始化
                setTimeout(() => {
                    if (node.toggleVisibility) node.toggleVisibility();
                    if (getW("模式")?.value === "使用预设") updatePreviews();
                }, 100);
            };
            
            // 跟随节点拉伸自适应
            const onResize = nodeType.prototype.onResize;
            nodeType.prototype.onResize = function(size) {
                if (onResize) onResize.apply(this, arguments);
                const node = this;
                if (node.widgetPreviewSub && node.previewSub && node.previewSub.style.display !== "none") {
                     node.widgetPreviewSub.computeSize = () => [0, node.previewSub.offsetHeight + 16];
                }
                if (node.widgetPreviewSys && node.previewSys && node.previewSys.style.display !== "none") {
                     node.widgetPreviewSys.computeSize = () => [0, node.previewSys.offsetHeight + 16];
                }
            };
            
            // 读取已保存的工作流数据
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function() {
                if (onConfigure) onConfigure.apply(this, arguments);
                const node = this;
                try {
                    const nSave = node.widgets && node.widgets.find(w => w.name === "保存为预设");
                    if (nSave && node.saveCheckbox) node.saveCheckbox.checked = nSave.value;
                    
                    const nSub = node.widgets && node.widgets.find(w => w.name === "手动_主体描述");
                    if (nSub && node.manSub) node.manSub.inp.value = nSub.value;
                    
                    const nSys = node.widgets && node.widgets.find(w => w.name === "手动_系统指令");
                    if (nSys && node.manSys) node.manSys.inp.value = nSys.value;
                    
                    setTimeout(() => {
                        if (node.toggleVisibility) node.toggleVisibility();
                    }, 100);
                } catch(e) { console.error(e); }
            }
        }
    }
});