import { app } from "../../scripts/app.js";

// 辅助：查找组件
const findWidget = (node, name) => node.widgets.find((w) => w.name === name);

// 辅助：数值修正（16的倍数，且至少为16）
const snap16 = (val) => Math.max(16, Math.floor(val / 16) * 16);

// 辅助：绘制平滑圆角矩形
function drawRoundRect(ctx, x, y, w, h, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + w - radius, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + radius);
    ctx.lineTo(x + w, y + h - radius);
    ctx.quadraticCurveTo(x + w, y + h, x + w - radius, y + h);
    ctx.lineTo(x + radius, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fill();
}

app.registerExtension({
    name: "ComfyUI.CropNode.Draggable",
    async nodeCreated(node) {
        if (node.comfyClass !== "图像裁剪节点") return;

        // 默认让节点创建时就宽一些，给右侧九宫格和左侧尺子留够空间
        if (!node.properties || !node.properties.hasExpanded) {
            node.size[0] = node.size[0] + 200; 
            node.properties = node.properties || {};
            node.properties.hasExpanded = true;
        }

        // 缓存数据
        node.imgCache = null;
        node.imgUrl = "";
        node.dragState = null;
        node.lastScale = 1.0; 
        node.hoveredGrid = null; 
        node.customBase = { w: 512, h: 512 }; 
        
        // --- 核心尺寸设定 (完美对称居中) ---
        const paddingLeft = 30;   // 左侧：尺子 30px
        const paddingRight = 25;  // 右侧：对称留白 25px (让图片水平居中)
        const paddingTop = 25;    // 顶部：尺子 25px
        const paddingBottom = 15; // 底部：留白 15px (让图片垂直居中)

        // --- 接管节点的原生拉伸事件 (onResize) ---
        const origOnResize = node.onResize;
        node.onResize = function(size) {
            if (origOnResize) origOnResize.apply(this, arguments);
            if (this.imgCache) {
                // 利用引擎原生 API，获取组件真实占用高度
                const widgetBottomY = this.computeSize([size[0], 0])[1];
                const topMargin = widgetBottomY + paddingTop;
                
                const drawW = size[0] - paddingLeft - paddingRight;
                const scale = drawW / this.imgCache.width;
                const drawH = Math.floor(this.imgCache.height * scale);
                
                const btnH = 28, gap = 4, padding = 8;
                const gridTotalH = btnH * 3 + gap * 2 + padding * 2;
                const minH = topMargin + gridTotalH + 30; 
                
                const neededHeight = Math.max(minH, topMargin + drawH + paddingBottom);
                size[1] = neededHeight; 
            }
        };

        // --- 0. 定义居中与9宫格对齐计算方法 ---
        function centerCrop(iw, ih, cw, ch) {
            const xW = findWidget(node, "裁剪X");
            const yW = findWidget(node, "裁剪Y");
            if (xW && yW) {
                xW.value = Math.floor((iw - cw) / 2);
                yW.value = Math.floor((ih - ch) / 2);
            }
        }

        node.alignCrop = function(type) {
            if (!this.imgCache) return;
            const img = this.imgCache;
            const iw = img.width;
            const ih = img.height;
            const widthW = findWidget(this, "裁剪宽度");
            const heightW = findWidget(this, "裁剪高度");
            const xW = findWidget(this, "裁剪X");
            const yW = findWidget(this, "裁剪Y");

            if (!widthW || !heightW || !xW || !yW) return;

            const cw = widthW.value;
            const ch = heightW.value;

            const maxX = Math.max(0, iw - cw);
            const maxY = Math.max(0, ih - ch);
            const cX = Math.floor((iw - cw) / 2);
            const cY = Math.floor((ih - ch) / 2);

            switch(type) {
                case "左上": xW.value = 0; yW.value = 0; break;
                case "中上": xW.value = cX; yW.value = 0; break;
                case "右上": xW.value = maxX; yW.value = 0; break;
                case "左中": xW.value = 0; yW.value = cY; break;
                case "居中": xW.value = cX; yW.value = cY; break;
                case "右中": xW.value = maxX; yW.value = cY; break;
                case "左下": xW.value = 0; yW.value = maxY; break;
                case "中下": xW.value = cX; yW.value = maxY; break;
                case "右下": xW.value = maxX; yW.value = maxY; break;
            }
            this.setDirtyCanvas(true, true);
        };

        // --- 1. 重写绘制方法 ---
        node.onDrawBackground = function(ctx) {
            if (!this.imgCache) return;

            ctx.save();
            const img = this.imgCache;
            
            // 获取组件真实占用高度，计算图片起始Y
            const widgetBottomY = this.computeSize([this.size[0], 0])[1];
            const topMargin = widgetBottomY + paddingTop;
            this.layoutTopMargin = topMargin;

            // 计算绘图可用宽度和缩放比
            const drawW = this.size[0] - paddingLeft - paddingRight;
            const scale = drawW / img.width;
            this.renderScale = scale;
            const drawH = Math.floor(img.height * scale);

            // 9宫格 UI 尺寸与位置
            const btnW = 32;
            const btnH = 28;
            const gap = 4;
            const uiPadding = 8;
            const gridTotalW = btnW * 3 + gap * 2 + uiPadding * 2;
            const gridTotalH = btnH * 3 + gap * 2 + uiPadding * 2;
            
            // UI 面板与图片右边缘对齐 (减去 paddingRight)
            const gridStartX = this.size[0] - gridTotalW - paddingRight - 5;
            const gridStartY = topMargin + 10;
            
            this.gridRect = { x: gridStartX, y: gridStartY, w: gridTotalW, h: gridTotalH, btnW, btnH, gap, uiPadding };

            // 高度锁定校验
            const minH = topMargin + gridTotalH + 30; 
            const neededHeight = Math.max(minH, topMargin + drawH + paddingBottom);
            if (Math.round(this.size[1]) !== neededHeight) {
                this.size[1] = neededHeight;
            }

            // --- A. 绘制动态刻度尺 (Professional Ruler) ---
            ctx.fillStyle = "rgba(10, 10, 10, 0.3)"; // 尺子底板微透明黑
            ctx.fillRect(paddingLeft, topMargin - paddingTop, drawW, paddingTop); // 顶部
            ctx.fillRect(0, topMargin, paddingLeft, drawH); // 左侧

            // 计算合理的动态刻度跨度 (防止数字互相重叠)
            let step = 100;
            const minPxGap = 40; // 最小显示间隔像素
            if (100 * scale < minPxGap) {
                if (200 * scale >= minPxGap) step = 200;
                else if (500 * scale >= minPxGap) step = 500;
                else if (1000 * scale >= minPxGap) step = 1000;
                else if (2000 * scale >= minPxGap) step = 2000;
                else step = 5000;
            }

            ctx.beginPath();
            ctx.strokeStyle = "#666666";
            ctx.lineWidth = 1;

            // X轴刻度 (顶部)
            ctx.textAlign = "center";
            ctx.textBaseline = "bottom";
            ctx.font = "10px Arial";
            ctx.fillStyle = "#aaaaaa";
            
            // 描边主轴线
            ctx.moveTo(paddingLeft, topMargin); ctx.lineTo(paddingLeft + drawW, topMargin);
            ctx.moveTo(paddingLeft, topMargin); ctx.lineTo(paddingLeft, topMargin + drawH);
            ctx.stroke();

            ctx.beginPath();
            for (let i = 0; i <= img.width; i += step / 2) {
                const isMajor = (i % step === 0);
                const tickX = paddingLeft + (i * scale);
                const tickLen = isMajor ? 6 : 3;
                
                ctx.moveTo(tickX, topMargin);
                ctx.lineTo(tickX, topMargin - tickLen);
                
                if (isMajor) {
                    ctx.fillText(i.toString(), tickX, topMargin - 8);
                }
            }
            
            // Y轴刻度 (左侧)
            ctx.textAlign = "right";
            ctx.textBaseline = "middle";
            for (let i = 0; i <= img.height; i += step / 2) {
                const isMajor = (i % step === 0);
                const tickY = topMargin + (i * scale);
                const tickLen = isMajor ? 6 : 3;
                
                ctx.moveTo(paddingLeft, tickY);
                ctx.lineTo(paddingLeft - tickLen, tickY);
                
                if (isMajor && tickY > topMargin + 10) { // 避免左上角 0 和 0 重叠
                    ctx.fillText(i.toString(), paddingLeft - 8, tickY);
                }
            }
            ctx.stroke();

            // --- B. 绘制底图 ---
            ctx.drawImage(img, paddingLeft, topMargin, drawW, drawH);

            // --- C. 绘制半透明圆角悬浮面板 ---
            ctx.fillStyle = "rgba(20, 20, 20, 0.75)";
            drawRoundRect(ctx, gridStartX, gridStartY, gridTotalW, gridTotalH, 10);

            const actions = [
                ["左上", "中上", "右上"],
                ["左中", "居中", "右中"],
                ["左下", "中下", "右下"]
            ];
            const arrows = [
                ["\u2196", "\u2191", "\u2197"],
                ["\u2190", "居中", "\u2192"],
                ["\u2199", "\u2193", "\u2198"]
            ];
            
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            
            for (let row = 0; row < 3; row++) {
                for (let col = 0; col < 3; col++) {
                    const bx = gridStartX + uiPadding + col * (btnW + gap);
                    const by = gridStartY + uiPadding + row * (btnH + gap);
                    
                    const isHovered = (this.hoveredGrid && this.hoveredGrid.row === row && this.hoveredGrid.col === col);
                    
                    ctx.fillStyle = isHovered ? "rgba(255, 255, 255, 0.25)" : "rgba(60, 60, 60, 0.5)"; 
                    drawRoundRect(ctx, bx, by, btnW, btnH, 6);
                    
                    ctx.fillStyle = isHovered ? "#ffffff" : "#cccccc";
                    if (row === 1 && col === 1) {
                        ctx.font = "12px Arial";
                        ctx.fillText("居中", bx + btnW/2, by + btnH/2);
                    } else {
                        ctx.font = "bold 16px Arial";
                        ctx.fillText(arrows[row][col], bx + btnW/2, by + btnH/2 + 1);
                    }
                }
            }

            const widthW = findWidget(this, "裁剪宽度");
            const heightW = findWidget(this, "裁剪高度");
            const xW = findWidget(this, "裁剪X");
            const yW = findWidget(this, "裁剪Y");
            
            if (!widthW || !heightW || !xW || !yW) {
                ctx.restore();
                return;
            }

            // --- D. 计算红框视觉坐标 ---
            const cropW = widthW.value * scale;
            const cropH = heightW.value * scale;
            const cropX = paddingLeft + (xW.value * scale); 
            const cropY = topMargin + (yW.value * scale);

            this.cropRect = { x: cropX, y: cropY, w: cropW, h: cropH };

            // --- E. 绘制遮罩 (完美控制在边框内) ---
            ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
            if (cropY > topMargin) ctx.fillRect(paddingLeft, topMargin, drawW, cropY - topMargin);
            const imgBottom = topMargin + drawH;
            if (cropY + cropH < imgBottom) ctx.fillRect(paddingLeft, cropY + cropH, drawW, imgBottom - (cropY + cropH));
            if (cropX > paddingLeft) ctx.fillRect(paddingLeft, cropY, cropX - paddingLeft, cropH);
            if (cropX + cropW < paddingLeft + drawW) ctx.fillRect(cropX + cropW, cropY, (paddingLeft + drawW) - (cropX + cropW), cropH);

            // --- F. 绘制红框 ---
            ctx.strokeStyle = "#ff0000";
            ctx.lineWidth = 2;
            ctx.strokeRect(cropX, cropY, cropW, cropH);

            // --- G. 文字信息 ---
            ctx.fillStyle = "white";
            ctx.font = "12px Arial";
            const text = `${Math.round(widthW.value)} x ${Math.round(heightW.value)}`;
            ctx.fillText(text, cropX + 5, cropY + 15);
            
            ctx.restore();
        };

        // --- 2. 鼠标交互 ---
        node.onMouseDown = function(e, localPos) {
            const [mx, my] = localPos;

            if (this.gridRect) {
                const { x, y, uiPadding, btnW, btnH, gap } = this.gridRect;
                for (let r = 0; r < 3; r++) {
                    for (let c = 0; c < 3; c++) {
                        const bx = x + uiPadding + c * (btnW + gap);
                        const by = y + uiPadding + r * (btnH + gap);
                        if (mx >= bx && mx <= bx + btnW && my >= by && my <= by + btnH) {
                            const actions = [
                                ["左上", "中上", "右上"],
                                ["左中", "居中", "右中"],
                                ["左下", "中下", "右下"]
                            ];
                            this.alignCrop(actions[r][c]);
                            return true; 
                        }
                    }
                }
            }

            if (!this.cropRect) return false;
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
            const [mx, my] = localPos;
            
            let newHover = null;
            if (this.gridRect) {
                const { x, y, uiPadding, btnW, btnH, gap } = this.gridRect;
                for (let r = 0; r < 3; r++) {
                    for (let c = 0; c < 3; c++) {
                        const bx = x + uiPadding + c * (btnW + gap);
                        const by = y + uiPadding + r * (btnH + gap);
                        if (mx >= bx && mx <= bx + btnW && my >= by && my <= by + btnH) {
                            newHover = { row: r, col: c };
                        }
                    }
                }
            }
            const hoverChanged = (!this.hoveredGrid && newHover) || 
                                 (this.hoveredGrid && !newHover) ||
                                 (this.hoveredGrid && newHover && (this.hoveredGrid.row !== newHover.row || this.hoveredGrid.col !== newHover.col));
            if (hoverChanged) {
                this.hoveredGrid = newHover;
                this.setDirtyCanvas(true, false);
            }

            if (!this.dragState) return;
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
            const imgMaxW = Math.floor(img.width / 16) * 16;
            const imgMaxH = Math.floor(img.height / 16) * 16;

            if (!isCustom) {
                const ratios = { "1:1": 1, "2:3": 2/3, "3:2": 3/2, "3:4": 3/4, "4:3": 4/3, "9:16": 9/16, "16:9": 16/9 };
                const r = ratios[presetW.value] || 1;
                let baseW, baseH;
                if (img.width / img.height > r) {
                    baseH = img.height; baseW = baseH * r;
                } else {
                    baseW = img.width; baseH = baseW / r;
                }
                let effectiveScale = scaleVal;
                const minScaleW = 16 / baseW;
                const minScaleH = 16 / baseH;
                if (effectiveScale < minScaleW) effectiveScale = minScaleW;
                if (effectiveScale < minScaleH) effectiveScale = minScaleH;
                targetW = snap16(baseW * effectiveScale);
                targetH = snap16(baseH * effectiveScale);
                node.customBase = { w: baseW, h: baseH };
            } else {
                if (scaleChanged) {
                    const minScaleForW = 16 / node.customBase.w;
                    const minScaleForH = 16 / node.customBase.h;
                    const limitScale = Math.max(minScaleForW, minScaleForH);
                    let effectiveScale = Math.max(scaleVal, limitScale);
                    targetW = Math.min(snap16(node.customBase.w * effectiveScale), imgMaxW);
                    targetH = Math.min(snap16(node.customBase.h * effectiveScale), imgMaxH);
                } else {
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

            if (widthW.value !== targetW || heightW.value !== targetH) {
                const oldW = widthW.value;
                const oldH = heightW.value;
                widthW.value = targetW;
                heightW.value = targetH;
                if (oldW > 0 && oldH > 0) {
                    const oldCenterX = xW.value + oldW / 2;
                    const oldCenterY = yW.value + oldH / 2;
                    xW.value = Math.floor(oldCenterX - targetW / 2);
                    yW.value = Math.floor(oldCenterY - targetH / 2);
                }
            }
            node.lastScale = scaleVal;
            const maxSafeX = Math.max(0, img.width - widthW.value);
            const maxSafeY = Math.max(0, img.height - heightW.value);
            xW.value = Math.max(0, Math.min(xW.value, maxSafeX));
            yW.value = Math.max(0, Math.min(yW.value, maxSafeY));

            node.setDirtyCanvas(true, true);
        };

        node.widgets.forEach(w => {
            const oldCallback = w.callback;
            w.callback = (...args) => {
                if (oldCallback) oldCallback.apply(w, args);
                refresh();
            };
        });

        setTimeout(refresh, 200);
    }
});