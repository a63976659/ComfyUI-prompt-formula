import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ComfyUI.ImageMaskPreviewNodeUI",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "图像遮罩预览节点") {
            return;
        }

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

            // 1. 隐藏自带的 image 字符串输入框
            const imageWidget = this.widgets.find((w) => w.name === "image");
            if (imageWidget) {
                imageWidget.type = "hidden";
                imageWidget.computeSize = () => [0, -4]; 
            }

            // 2. 劫持右键菜单（为了在右键打开时也能清空旧图缓存）
            const getExtraMenuOptions = this.getExtraMenuOptions;
            this.getExtraMenuOptions = function (canvas, options) {
                if (getExtraMenuOptions) {
                    getExtraMenuOptions.apply(this, arguments);
                }
                
                // 完全还原你原版的匹配方式
                let maskOption = options.find((o) => o && o.content && (
                    o.content === "Open in MaskEditor" || 
                    o.content.includes("MaskEditor") || 
                    o.content.includes("遮罩编辑器") || 
                    o.content === "在遮罩编辑器中打开"
                ));

                if (maskOption && !maskOption._cache_hijacked) {
                    const originalCallback = maskOption.callback;
                    maskOption.callback = function() {
                        // 🌟 障眼法：清空隐藏的旧图路径
                        if (imageWidget) { imageWidget.value = ""; }
                        if (originalCallback) { return originalCallback.apply(this, arguments); }
                    };
                    maskOption._cache_hijacked = true;
                }
            };

            // 3. 完全还原你最初的面板按钮点击逻辑！
            this.addWidget("button", "🎨 编辑遮罩", "edit_mask", () => {
                if (!this.imgs || this.imgs.length === 0) {
                    alert("⚠️ 请先连接图像并【运行一次】工作流。\n需要节点上显示出图像后，才能进行遮罩手绘！");
                    return;
                }

                // 🌟 唯一加入的救命代码：点击按钮前，先把底层旧缓存抹除
                if (imageWidget) {
                    imageWidget.value = "";
                }

                let options = [];
                if (this.getExtraMenuOptions) {
                    this.getExtraMenuOptions(app.canvas, options);
                    
                    // 还原你原版代码的精确匹配！
                    let maskOption = options.find((o) => o && o.content && (
                        o.content === "Open in MaskEditor" || 
                        o.content.includes("MaskEditor") || 
                        o.content.includes("遮罩编辑器") || 
                        o.content === "在遮罩编辑器中打开"
                    ));
                    
                    if (maskOption && maskOption.callback) {
                        maskOption.callback(); // 还原你原版的调用方式！
                        return;
                    }
                }
                alert("未找到遮罩编辑器功能，请尝试在图像上【右键 -> 在遮罩编辑器中打开】。");
            });

            return r;
        };
    },
});