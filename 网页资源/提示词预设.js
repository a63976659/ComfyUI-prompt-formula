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
                    margin: 5px auto;
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
                    width: calc(100% - 16px); /* 左右各留8px边距 */
                    max-width: calc(100% - 16px);
                }
                
                .preset-content-empty {
                    color: var(--descrip-text);
                    font-style: italic;
                    opacity: 0.7;
                    justify-content: center;
                    align-items: center;
                }
                
                .preset-content-loaded {
                    justify-content: flex-start;
                    align-items: flex-start;
                }
                
                /* 节点样式优化 */
                .node[data-type="提示词预设"] {
                    min-width: 300px !important;
                    min-height: 180px !important;
                    resize: both;
                    overflow: hidden;
                }
                
                /* 隐藏默认的resize手柄 */
                .node[data-type="提示词预设"]::-webkit-resizer {
                    display: none;
                }
                
                /* 自定义节点调整大小的视觉反馈 */
                .node[data-type="提示词预设"]:active {
                    border: 1px dashed var(--border-color);
                }
                
                /* 预览框滚动条样式 */
                .preset-content-preview::-webkit-scrollbar {
                    width: 6px;
                }
                
                .preset-content-preview::-webkit-scrollbar-track {
                    background: rgba(0,0,0,0.1);
                    border-radius: 3px;
                }
                
                .preset-content-preview::-webkit-scrollbar-thumb {
                    background: var(--descrip-text);
                    border-radius: 3px;
                }
            `,
            parent: document.head
        });
        
        await 获取预设数据();
    },
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "提示词预设") {
            const 原节点添加 = nodeType.prototype.onAdded;
            const 原序列化 = nodeType.prototype.serialize;
            const 原配置 = nodeType.prototype.configure;
            const 原调整大小 = nodeType.prototype.onResize;
            
            nodeType.prototype.onAdded = function() {
                原节点添加?.apply(this, arguments);
                
                // 找到预设文件选择部件
                const 预设部件 = this.widgets.find(w => w.name === "预设文件");
                if (!预设部件) return;
                
                // 从节点数据获取保存的节点尺寸
                const 保存的宽度 = this._nodeWidth || 300;
                const 保存的高度 = this._nodeHeight || 200;
                
                // 设置节点初始大小
                this.setSize([保存的宽度, 保存的高度]);
                
                // 创建内容预览容器（自动适应节点大小）
                this.预览容器 = $el("div", {
                    className: "preset-content-preview preset-content-empty",
                    textContent: "请选择预设文件...",
                    style: { 
                        display: "block",
                        height: "auto" // 高度自动适应内容
                    }
                });
                
                // 将预览容器添加到节点
                this.addDOMWidget("preset_preview", "preset_preview", this.预览容器, {
                    getValue: () => "",
                    setValue: () => {}
                });
                
                // 重写调整大小方法
                this.onResize = function(size) {
                    原调整大小?.apply(this, arguments);
                    
                    // 保存节点尺寸
                    this._nodeWidth = size[0];
                    this._nodeHeight = size[1];
                    
                    // 自动调整预览框高度
                    this.自动调整预览框高度();
                };
                
                // 自动调整预览框高度的方法
                this.自动调整预览框高度 = function() {
                    if (!this.预览容器) return;
                    
                    // 计算可用高度：节点高度 - 标题栏 - 下拉框 - 边距
                    const 标题高度 = 30;
                    const 下拉框高度 = 30;
                    const 边距 = 20;
                    const 可用高度 = this.size[1] - 标题高度 - 下拉框高度 - 边距;
                    
                    // 设置预览框高度，但不小于最小高度
                    const 预览框高度 = Math.max(40, 可用高度);
                    this.预览容器.style.height = `${预览框高度}px`;
                    
                    // 标记画布需要重绘
                    this.setDirtyCanvas(true, true);
                };
                
                // 初始调整预览框高度
                setTimeout(() => {
                    this.自动调整预览框高度();
                }, 100);
                
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
                        } else {
                            this.预览容器.textContent = "预设文件内容为空";
                            this.预览容器.className = "preset-content-preview preset-content-empty";
                        }
                    } else {
                        this.title = "提示词预设";
                        this.预览容器.textContent = "请选择预设文件...";
                        this.预览容器.className = "preset-content-preview preset-content-empty";
                    }
                    
                    // 重新调整预览框高度以适应新内容
                    this.自动调整预览框高度();
                    
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
            
            // 重写序列化方法以保存节点尺寸
            nodeType.prototype.serialize = function() {
                const 数据 = 原序列化 ? 原序列化.apply(this, arguments) : {};
                
                // 保存节点尺寸
                if (this._nodeWidth && this._nodeHeight) {
                    数据._nodeWidth = this._nodeWidth;
                    数据._nodeHeight = this._nodeHeight;
                }
                
                return 数据;
            };
            
            // 重写配置方法以恢复节点尺寸
            nodeType.prototype.configure = function(配置) {
                原配置?.apply(this, arguments);
                
                // 恢复节点尺寸
                if (配置._nodeWidth && 配置._nodeHeight) {
                    this._nodeWidth = 配置._nodeWidth;
                    this._nodeHeight = 配置._nodeHeight;
                }
            };
            
            // 监听节点尺寸变化
            const 原绘制前景 = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function(ctx) {
                原绘制前景?.apply(this, arguments);
                
                // 检查节点尺寸是否变化，如果变化则调整预览框
                if (this.预览容器 && (this._lastWidth !== this.size[0] || this._lastHeight !== this.size[1])) {
                    this._lastWidth = this.size[0];
                    this._lastHeight = this.size[1];
                    this.自动调整预览框高度();
                }
            };
        }
    }
});