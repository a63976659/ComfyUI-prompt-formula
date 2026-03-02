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

            // 1. 隐藏自带的 image 字符串输入框 (用于静默接收编辑器回传的遮罩缓存)
            const imageWidget = this.widgets.find((w) => w.name === "image");
            if (imageWidget) {
                imageWidget.type = "hidden";
                imageWidget.computeSize = () => [0, -4]; 
            }

            // 2. 添加【编辑遮罩】按钮
            this.addWidget("button", "🎨 编辑遮罩", "edit_mask", () => {
                if (!this.imgs || this.imgs.length === 0) {
                    alert("⚠️ 请先连接图像并【运行一次】工作流。\n需要节点上显示出图像后，才能进行遮罩手绘！");
                    return;
                }

                let options = [];
                if (this.getExtraMenuOptions) {
                    this.getExtraMenuOptions(app.canvas, options);
                    
                    // 兼容汉化插件和原版的菜单名
                    let maskOption = options.find((o) => o && o.content && (
                        o.content === "Open in MaskEditor" || 
                        o.content.includes("MaskEditor") || 
                        o.content.includes("遮罩编辑器") || 
                        o.content === "在遮罩编辑器中打开"
                    ));
                    
                    if (maskOption && maskOption.callback) {
                        maskOption.callback(); 
                        return;
                    }
                }
                alert("未找到遮罩编辑器功能，请尝试在图像上【右键 -> 在遮罩编辑器中打开】。");
            });

            return r;
        };
    },
});