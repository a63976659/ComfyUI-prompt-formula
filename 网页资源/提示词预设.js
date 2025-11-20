// 提示词预设.js
import { app } from "../../../scripts/app.js";
import { $el } from "../../../scripts/ui.js";
import { api } from "../../../scripts/api.js";

// 预设数据缓存
let 预设数据缓存 = null;

// 获取预设数据
async function 获取预设数据() {
    if (预设数据缓存) return 预设数据缓存;
    
    try {
        const 响应 = await api.fetchApi("/preset_preview/list");
        预设数据缓存 = await 响应.json();
        return 预设数据缓存;
    } catch (错误) {
        console.error("获取预设数据失败:", 错误);
        return {};
    }
}

app.registerExtension({
    name: "提示词预设插件",
    
    async init() {
        // 添加样式
        $el("style", {
            textContent: `
                .preset-content-preview {
                    background: var(--comfy-input-bg);
                    border: 1px solid var(--border-color);
                    border-radius: 4px;
                    padding: 8px;
                    margin: 5px 8px;
                    font-size: 11px;
                    line-height: 1.3;
                    color: var(--input-text);
                    max-height: 200px;
                    overflow-y: auto;
                    word-wrap: break-word;
                    white-space: pre-wrap;
                    font-family: monospace;
                    min-height: 60px;
                    display: flex;
                    align-items: center;
                }
                
                .preset-content-empty {
                    color: var(--descrip-text);
                    font-style: italic;
                    opacity: 0.7;
                    justify-content: center;
                }
                
                .preset-content-loaded {
                    justify-content: flex-start;
                    align-items: flex-start;
                }
                
                .node[data-type="提示词预设"] {
                    min-width: 320px !important;
                    min-height: 180px !important;
                }
            `,
            parent: document.head
        });
        
        await 获取预设数据();
    },
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "提示词预设") {
            const 原节点添加 = nodeType.prototype.onAdded;
            
            nodeType.prototype.onAdded = function() {
                原节点添加?.apply(this, arguments);
                
                // 找到预设文件选择部件
                const 预设部件 = this.widgets.find(w => w.name === "预设文件");
                if (!预设部件) return;
                
                // 创建内容预览容器
                this.预览容器 = $el("div", {
                    className: "preset-content-preview preset-content-empty",
                    textContent: "请选择预设文件...",
                    style: { display: "block" }
                });
                
                // 将预览容器添加到节点
                this.addDOMWidget("preset_preview", "preset_preview", this.预览容器, {
                    getValue: () => "",
                    setValue: () => {}
                });
                
                // 调整节点大小
                this.setSize([320, 200]);
                
                // 当选择变化时更新预览内容
                const 原回调 = 预设部件.callback;
                预设部件.callback = async () => {
                    const 结果 = 原回调?.apply(this, arguments) ?? 预设部件.value;
                    
                    // 更新节点标题
                    if (预设部件.value && 预设部件.value !== "无") {
                        this.title = `提示词预设 - ${预设部件.value}`;
                        
                        // 更新预览内容
                        const 预设数据 = await 获取预设数据();
                        const 当前预设数据 = 预设数据[预设部件.value];
                        
                        if (当前预设数据?.完整内容) {
                            this.预览容器.textContent = 当前预设数据.完整内容;
                            this.预览容器.className = "preset-content-preview preset-content-loaded";
                            
                            // 根据内容长度调整节点高度
                            const 行数 = 当前预设数据.完整内容.split('\n').length;
                            const 基础高度 = 120;
                            const 额外高度 = Math.min(行数 * 15, 200);
                            this.setSize([320, 基础高度 + 额外高度]);
                        } else {
                            this.预览容器.textContent = "预设文件内容为空";
                            this.预览容器.className = "preset-content-preview preset-content-empty";
                            this.setSize([320, 150]);
                        }
                    } else {
                        this.title = "提示词预设";
                        this.预览容器.textContent = "请选择预设文件...";
                        this.预览容器.className = "preset-content-preview preset-content-empty";
                        this.setSize([320, 150]);
                    }
                    
                    this.setDirtyCanvas(true, true);
                    return 结果;
                };
                
                // 初始设置
                if (预设部件.value && 预设部件.value !== "无") {
                    this.title = `提示词预设 - ${预设部件.value}`;
                    setTimeout(() => {
                        预设部件.callback();
                    }, 100);
                }
            };
        }
    }
});