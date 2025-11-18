// preset_preview.js
import { app } from "../../scripts/app.js";

// 扩展提示词预设节点，添加自定义预览功能
app.registerExtension({
    name: "PromptPreset.Preview",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "提示词预设") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // 创建自定义预览容器
                this.previewContainer = document.createElement('div');
                this.previewContainer.className = 'prompt-preset-preview';
                this.previewContainer.style.cssText = `
                    margin-top: 10px;
                    padding: 8px;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background: #f8f9fa;
                    font-size: 12px;
                    max-height: 200px;
                    overflow-y: auto;
                `;
                
                // 将预览容器添加到节点内容之后
                this.addDOMWidget('preset_preview', 'div', this.previewContainer, {
                    getValue: () => '',
                    setValue: () => {}
                });
                
                // 监听选择变化
                const originalOnConfigure = this.onConfigure;
                this.onConfigure = function () {
                    if (originalOnConfigure) {
                        originalOnConfigure.apply(this, arguments);
                    }
                    this.updatePreview();
                };
                
                return result;
            };
            
            // 添加更新预览的方法
            nodeType.prototype.updatePreview = function () {
                if (!this.previewContainer) return;
                
                const widget = this.widgets?.find(w => w.name === "预设名称");
                if (!widget) return;
                
                try {
                    const previewMetadata = JSON.parse(widget.options.preview_metadata || '{}');
                    const selectedValue = widget.value;
                    const presetInfo = previewMetadata[selectedValue];
                    
                    if (presetInfo && presetInfo.content) {
                        // 显示文本内容预览
                        this.previewContainer.innerHTML = `
                            <div style="margin-bottom: 8px; font-weight: bold; color: #333;">
                                📄 ${selectedValue}
                            </div>
                            <div style="color: #666; line-height: 1.4; white-space: pre-wrap;">
                                ${this.escapeHtml(presetInfo.content)}
                            </div>
                        `;
                    } else {
                        this.previewContainer.innerHTML = `
                            <div style="color: #999; text-align: center; padding: 20px;">
                                选择预设以查看内容...
                            </div>
                        `;
                    }
                } catch (error) {
                    console.error('更新预设预览失败:', error);
                    this.previewContainer.innerHTML = `
                        <div style="color: #d32f2f; text-align: center; padding: 20px;">
                            预览加载失败
                        </div>
                    `;
                }
            };
            
            // HTML转义工具函数
            nodeType.prototype.escapeHtml = function (text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            };
        }
    },
});