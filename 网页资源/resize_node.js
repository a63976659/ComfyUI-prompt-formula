import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ComfyUI.ResizeImageMaskNode",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "智能缩放图像及遮罩") {
            return;
        }

        console.log("%c >>> RESIZE NODE V9.0 (Multiplier Rename) <<< ", "background: #9900cc; color: white");

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

            this.all_widgets_repo = [...this.widgets];
            let lastMode = null;
            
            // 宽度记忆变量
            this.user_width = this.size[0]; 

            // 监听手动调整大小事件
            const origOnResize = this.onResize;
            this.onResize = function(size) {
                if (origOnResize) origOnResize.apply(this, arguments);
                this.user_width = Math.max(size[0], 280);
            };

            // 高度映射表
            const HEIGHT_MAP = {
                "指定尺寸 (Dimensions)": 200,
                "按系数 (Scale By)": 140,
                "指定长边 (Longer Side)": 140,
                "指定短边 (Shorter Side)": 140,
                "指定宽度 (Width)": 140,
                "指定高度 (Height)": 140,
                "指定像素 (Megapixels)": 140,
                "匹配图像 (Match Size)": 160,
                "乘数调整 (To Multiple)": 160  // 【已更名】
            };

            this.updateLayout = function () {
                const modeWidget = this.widgets.find((w) => w.name === "调整类型");
                if (!modeWidget) return;
                const mode = modeWidget.value;

                if (mode === lastMode && !this.force_update) return;
                lastMode = mode;
                this.force_update = false;

                // --- 确定白名单 ---
                const modeWidgets = {
                    "指定尺寸 (Dimensions)": ["宽度", "高度", "裁剪方式"],
                    "按系数 (Scale By)": ["缩放系数"],
                    "指定长边 (Longer Side)": ["指定长度"],
                    "指定短边 (Shorter Side)": ["指定长度"],
                    "指定宽度 (Width)": ["宽度"],
                    "指定高度 (Height)": ["高度"],
                    "指定像素 (Megapixels)": ["百万像素"],
                    "匹配图像 (Match Size)": ["裁剪方式"],
                    "乘数调整 (To Multiple)": ["放大"] // 【已更名】
                };
                const alwaysShow = ["调整类型", "插值方法"];
                const targetWidgetNames = [...alwaysShow, ...(modeWidgets[mode] || [])];

                // --- 重构组件列表 ---
                const newWidgetsList = [];
                for (const w of this.all_widgets_repo) {
                    if (targetWidgetNames.includes(w.name.trim())) {
                        if (w.type === "HIDDEN") {
                             if (["调整类型", "插值方法", "裁剪方式"].some(k => w.name.includes(k))) w.type = "COMBO";
                             else if (["宽度", "高度", "指定长度", "放大"].some(k => w.name.includes(k))) w.type = "INT";
                             else w.type = "FLOAT";
                             w.computeSize = null;
                        }
                        newWidgetsList.push(w);
                    }
                }
                this.widgets = newWidgetsList;

                // --- 端口处理 ---
                const isMatchMode = mode === "匹配图像 (Match Size)";
                const requiredInputs = isMatchMode ? 2 : 1;
                const currentInputs = this.inputs ? this.inputs.length : 0;
                
                if (currentInputs !== requiredInputs) {
                    if (isMatchMode && currentInputs < 2) {
                        this.addInput("参考图像", "*");
                    } else if (!isMatchMode && currentInputs > 1) {
                        this.removeInput(1);
                    }
                }
                if (this.inputs && this.inputs[0]) this.inputs[0].name = "图像或遮罩";

                // --- 强制应用尺寸 ---
                const fixedHeight = HEIGHT_MAP[mode] || 200;
                const targetWidth = Math.max(this.user_width || 280, this.size[0], 280);
                
                this.setSize([targetWidth, fixedHeight]);
                
                app.graph.setDirtyCanvas(true, true);
            };

            const modeWidget = this.widgets.find((w) => w.name === "调整类型");
            if (modeWidget) {
                const cb = modeWidget.callback;
                modeWidget.callback = (...args) => {
                    this.force_update = true;
                    this.updateLayout();
                    if (cb) cb.apply(modeWidget, args);
                };
            }

            // 立即初始化
            this.force_update = true;
            this.updateLayout();
            
            setTimeout(() => {
                this.force_update = true;
                this.updateLayout();
            }, 16);

            return r;
        };

        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            if (onConfigure) onConfigure.apply(this, arguments);
            if(this.size && this.size[0]) {
                this.user_width = this.size[0];
            }
            if (this.updateLayout) {
                this.force_update = true;
                this.updateLayout();
            }
        };
    },
});