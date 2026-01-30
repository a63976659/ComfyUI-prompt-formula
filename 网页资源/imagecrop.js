import { app } from "../../scripts/app.js";

// 辅助：查找组件
const findWidget = (node, name) => node.widgets.find((w) => w.name === name);

// 辅助：数值修正（16的倍数，且至少为16）
const snap16 = (val) => Math.max(16, Math.floor(val / 16) * 16);

app.registerExtension({
    name: "ComfyUI.CropNode.Draggable",
    async nodeCreated(node) {
        if (node.comfyClass !== "图像裁剪节点") return;

        // 缓存数据
        node.imgCache = null;
        node.imgUrl = "";
        node.dragState = null;
        node.lastScale = 1.0; 
        
        // 记录自定义模式下的基准尺寸
        node.customBase = { w: 512, h: 512 }; 

        // --- 0. 添加“点击居中”按钮 ---
        node.addWidget("button", "点击居中", null, () => {
            if (!node.imgCache) return;
            const widthW = findWidget(node, "裁剪宽度");
            const heightW = findWidget(node, "裁剪高度");
            centerCrop(node.imgCache.width, node.imgCache.height, widthW.value, heightW.value);
            node.setDirtyCanvas(true, true);
        });
        
        function centerCrop(iw, ih, cw, ch) {
            const xW = findWidget(node, "裁剪X");
            const yW = findWidget(node, "裁剪Y");
            if (xW && yW) {
                xW.value = Math.floor((iw - cw) / 2);
                yW.value = Math.floor((ih - ch) / 2);
            }
        }

        // --- 1. 重写绘制方法 ---
        node.onDrawBackground = function(ctx) {
            if (!this.imgCache) return;

            const img = this.imgCache;
            
            // 布局计算
            const headerHeight = 30;
            const widgetHeight = 32;
            const visibleWidgets = this.widgets ? this.widgets.length : 8;
            const topMargin = headerHeight + (visibleWidgets * widgetHeight) + 10;
            this.layoutTopMargin = topMargin;

            // 计算缩放
            const scale = this.size[0] / img.width;
            this.renderScale = scale;
            const drawH = img.height * scale;

            // 自动调整节点高度
            const neededHeight = topMargin + drawH + 20;
            if (Math.abs(this.size[1] - neededHeight) > 5) {
                this.setSize([this.size[0], neededHeight]);
            }

            // A. 绘制原图
            ctx.drawImage(img, 0, topMargin, this.size[0], drawH);

            const widthW = findWidget(this, "裁剪宽度");
            const heightW = findWidget(this, "裁剪高度");
            const xW = findWidget(this, "裁剪X");
            const yW = findWidget(this, "裁剪Y");
            
            if (!widthW || !heightW || !xW || !yW) return;

            // B. 计算红框视觉坐标
            const cropW = widthW.value * scale;
            const cropH = heightW.value * scale;
            const cropX = xW.value * scale; 
            const cropY = topMargin + (yW.value * scale);

            this.cropRect = { x: cropX, y: cropY, w: cropW, h: cropH };

            // C. 绘制遮罩
            ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
            if (cropY > topMargin) ctx.fillRect(0, topMargin, this.size[0], cropY - topMargin);
            const imgBottom = topMargin + drawH;
            if (cropY + cropH < imgBottom) ctx.fillRect(0, cropY + cropH, this.size[0], imgBottom - (cropY + cropH));
            if (cropX > 0) ctx.fillRect(0, cropY, cropX, cropH);
            if (cropX + cropW < this.size[0]) ctx.fillRect(cropX + cropW, cropY, this.size[0] - (cropX + cropW), cropH);

            // D. 绘制红框
            ctx.strokeStyle = "#ff0000";
            ctx.lineWidth = 2;
            ctx.strokeRect(cropX, cropY, cropW, cropH);

            // E. 绘制辅助线
            ctx.strokeStyle = "rgba(255, 255, 255, 0.5)";
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(cropX, cropY + cropH / 3); ctx.lineTo(cropX + cropW, cropY + cropH / 3);
            ctx.moveTo(cropX, cropY + cropH * 2 / 3); ctx.lineTo(cropX + cropW, cropY + cropH * 2 / 3);
            ctx.moveTo(cropX + cropW / 3, cropY); ctx.lineTo(cropX + cropW / 3, cropY + cropH);
            ctx.moveTo(cropX + cropW * 2 / 3, cropY); ctx.lineTo(cropX + cropW * 2 / 3, cropY + cropH);
            ctx.stroke();

            // F. 文字信息
            ctx.fillStyle = "white";
            ctx.font = "12px Arial";
            const text = `${Math.round(widthW.value)} x ${Math.round(heightW.value)}`;
            ctx.fillText(text, cropX + 5, cropY + 15);
        };

        // --- 2. 鼠标交互 ---
        node.onMouseDown = function(e, localPos) {
            if (!this.cropRect) return false;
            const [mx, my] = localPos;
            const { x, y, w, h } = this.cropRect;

            if (mx >= x && mx <= x + w && my >= y && my <= y + h) {
                const xW = findWidget(this, "裁剪X");
                const yW = findWidget(this, "裁剪Y");
                this.dragState = {
                    startX: mx, startY: my,
                    initialValX: xW.value, initialValY: yW.value
                };
                this.captureInput(true); 
                return true;
            }
            return false;
        };

        node.onMouseMove = function(e, localPos) {
            if (!this.dragState) return;
            const [mx, my] = localPos;
            const deltaX = (mx - this.dragState.startX) / this.renderScale;
            const deltaY = (my - this.dragState.startY) / this.renderScale;

            const xW = findWidget(this, "裁剪X");
            const yW = findWidget(this, "裁剪Y");
            const widthW = findWidget(this, "裁剪宽度");
            const heightW = findWidget(this, "裁剪高度");

            if(xW && yW && this.imgCache) {
                let newX = this.dragState.initialValX + deltaX;
                let newY = this.dragState.initialValY + deltaY;

                const maxX = this.imgCache.width - widthW.value;
                const maxY = this.imgCache.height - heightW.value;

                newX = Math.max(0, Math.min(newX, maxX));
                newY = Math.max(0, Math.min(newY, maxY));

                xW.value = Math.round(newX);
                yW.value = Math.round(newY);
                this.setDirtyCanvas(true, true);
            }
        };

        node.onMouseUp = function(e, localPos) {
            if (this.dragState) {
                this.dragState = null;
                this.captureInput(false);
                const xW = findWidget(this, "裁剪X");
                if (xW && xW.callback) xW.callback(xW.value);
            }
        };

        // --- 3. 核心逻辑：刷新与计算 ---
        const refresh = async () => {
            const fileW = findWidget(node, "图像文件");
            const presetW = findWidget(node, "预设");
            const widthW = findWidget(node, "裁剪宽度");
            const heightW = findWidget(node, "裁剪高度");
            const xW = findWidget(node, "裁剪X");
            const yW = findWidget(node, "裁剪Y");
            const scaleW = findWidget(node, "缩放比例");

            if (!fileW || !fileW.value) return;

            // A. 图像加载
            if (node.imgUrl !== fileW.value) {
                const img = new Image();
                img.src = `/view?filename=${encodeURIComponent(fileW.value)}&type=input`;
                await new Promise((r) => { img.onload = r; img.onerror = r; });
                node.imgCache = img;
                node.imgUrl = fileW.value;
                
                if (img.width) {
                    const maxW = Math.floor(img.width / 16) * 16;
                    const maxH = Math.floor(img.height / 16) * 16;
                    widthW.options.max = maxW; widthW.max = maxW;
                    heightW.options.max = maxH; heightW.max = maxH;
                    xW.options.max = img.width; xW.max = img.width;
                    yW.options.max = img.height; yW.max = img.height;
                    
                    node.customBase = { w: img.width, h: img.height };
                    centerCrop(img.width, img.height, widthW.value, heightW.value);
                }
            }

            const img = node.imgCache;
            if (!img) return;

            const isCustom = presetW.value === "自定义";
            const scaleVal = scaleW ? scaleW.value : 1.0;
            const scaleChanged = (Math.abs(scaleVal - node.lastScale) > 0.001);

            widthW.disabled = !isCustom;
            heightW.disabled = !isCustom;

            let targetW = widthW.value;
            let targetH = heightW.value;

            // 获取图像物理最大限制
            const imgMaxW = Math.floor(img.width / 16) * 16;
            const imgMaxH = Math.floor(img.height / 16) * 16;

            // B. 计算目标宽高
            if (!isCustom) {
                // --- 预设模式 ---
                const ratios = { "1:1": 1, "2:3": 2/3, "3:2": 3/2, "3:4": 3/4, "4:3": 4/3, "9:16": 9/16, "16:9": 16/9 };
                const r = ratios[presetW.value] || 1;
                
                let baseW, baseH;
                if (img.width / img.height > r) {
                    baseH = img.height;
                    baseW = baseH * r;
                } else {
                    baseW = img.width;
                    baseH = baseW / r;
                }
                
                // 预设模式也应用“防比例破坏”逻辑
                let effectiveScale = scaleVal;
                const minScaleW = 16 / baseW;
                const minScaleH = 16 / baseH;
                if (effectiveScale < minScaleW) effectiveScale = minScaleW;
                if (effectiveScale < minScaleH) effectiveScale = minScaleH;
                
                targetW = snap16(baseW * effectiveScale);
                targetH = snap16(baseH * effectiveScale);
                
                node.customBase = { w: baseW, h: baseH };

            } else {
                // --- 自定义模式 ---
                if (scaleChanged) {
                    // 用户动了缩放滑块
                    let calcW = node.customBase.w * scaleVal;
                    let calcH = node.customBase.h * scaleVal;

                    // 1. 检查是否存在“触底”风险，保护比例
                    // 如果计算出的值小于16，说明该比例会让这一边崩坏。
                    // 我们需要算出“能维持16px的最小比例”是多少。
                    const minScaleForW = 16 / node.customBase.w;
                    const minScaleForH = 16 / node.customBase.h;
                    
                    // 取限制最严格的那个（即较大的Scale值）
                    // 比如 W只需0.1倍就触底，H需要0.5倍就触底，那我们在0.5倍时就得停下
                    const limitScale = Math.max(minScaleForW, minScaleForH);

                    // 如果用户请求的比例比极限还小，我们强制使用极限比例
                    let effectiveScale = scaleVal;
                    if (scaleVal < limitScale) {
                        effectiveScale = limitScale;
                    }

                    // 2. 重新计算（使用安全的比例）
                    calcW = node.customBase.w * effectiveScale;
                    calcH = node.customBase.h * effectiveScale;

                    // 3. 结果修正（Snap16 和 图片最大限制）
                    targetW = Math.min(snap16(calcW), imgMaxW);
                    targetH = Math.min(snap16(calcH), imgMaxH);

                } else {
                    // 用户动了宽高滑块：反算 Base
                    targetW = Math.min(widthW.value, imgMaxW);
                    targetH = Math.min(heightW.value, imgMaxH);
                    
                    const expectedW = snap16(node.customBase.w * scaleVal);
                    const expectedH = snap16(node.customBase.h * scaleVal);
                    
                    if (Math.abs(targetW - expectedW) > 16 || Math.abs(targetH - expectedH) > 16) {
                        node.customBase.w = targetW / scaleVal;
                        node.customBase.h = targetH / scaleVal;
                    }
                }
            }

            // C. 应用宽高变更 + 中心缩放修正
            if (widthW.value !== targetW || heightW.value !== targetH) {
                const oldW = widthW.value;
                const oldH = heightW.value;
                
                widthW.value = targetW;
                heightW.value = targetH;

                // Center Scaling
                if (oldW > 0 && oldH > 0) {
                    const oldCenterX = xW.value + oldW / 2;
                    const oldCenterY = yW.value + oldH / 2;
                    
                    let newX = oldCenterX - targetW / 2;
                    let newY = oldCenterY - targetH / 2;
                    
                    xW.value = Math.floor(newX);
                    yW.value = Math.floor(newY);
                }
            }
            
            node.lastScale = scaleVal;

            // D. 强制边界检查
            if (widthW.value > imgMaxW) widthW.value = imgMaxW;
            if (heightW.value > imgMaxH) heightW.value = imgMaxH;

            const maxSafeX = Math.max(0, img.width - widthW.value);
            const maxSafeY = Math.max(0, img.height - heightW.value);

            if (xW.value > maxSafeX) xW.value = maxSafeX;
            if (xW.value < 0) xW.value = 0;
            if (yW.value > maxSafeY) yW.value = maxSafeY;
            if (yW.value < 0) yW.value = 0;

            node.setDirtyCanvas(true, true);
        };

        // 监听
        node.widgets.forEach(w => {
            if (w.name === "点击居中") return;
            const oldCallback = w.callback;
            w.callback = (...args) => {
                if (oldCallback) oldCallback.apply(w, args);
                refresh();
            };
        });

        setTimeout(refresh, 100);
    }
});