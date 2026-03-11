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

            // 预设坐标极值与中心点
            const maxX = Math.max(0, iw - cw);
            const maxY = Math.max(0, ih - ch);
            const cX = Math.floor((iw - cw) / 2);
            const cY = Math.floor((ih - ch) / 2);

            switch(type) {
                case "左上": xW.value = 0; yW.value = 0; break;
                case "中上": xW.value = cX; yW.value = 0; break;
                case "右上": xW.value = maxX; yW.value = 0; break;
                case "左中": xW.value = 0; yW.value = cY; break;
                case "点击居中": xW.value = cX; yW.value = cY; break;
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

            ctx.save(); // 保护上下文，防止 Win10 缩放堆叠
            const img = this.imgCache;
            
            const headerHeight = 30;
            const widgetHeight = 32;
            const visibleWidgets = this.widgets ? this.widgets.length : 7;
            
            // --- 新增：9宫格 UI 尺寸与坐标计算 ---
            const btnW = 54;
            const btnH = 46;
            const gap = 4;
            const gridTotalW = btnW * 3 + gap * 2;
            const gridTotalH = btnH * 3 + gap * 2;
            
            const gridStartY = headerHeight + (visibleWidgets * widgetHeight) - 10;
            const gridStartX = (this.size[0] - gridTotalW) / 2;
            
            // 缓存给鼠标点击事件用
            this.gridRect = { x: gridStartX, y: gridStartY, w: gridTotalW, h: gridTotalH, btnW, btnH, gap };
            
            const topMargin = Math.floor(gridStartY + gridTotalH + 15);
            this.layoutTopMargin = topMargin;

            // 计算缩放
            const scale = this.size[0] / img.width;
            this.renderScale = scale;
            const drawH = Math.floor(img.height * scale);

            // --- 核心优化：稳定性高度自适应 ---
            const minH = Math.floor(gridStartY + gridTotalH + 60); 
            const neededHeight = Math.max(minH, topMargin + drawH + 20);
            
            if (Math.abs(this.size[1] - neededHeight) > 10) {
                this.size[1] = neededHeight;
            }

            // --- A. 绘制9宫格交互区 ---
            // 浅灰底板
            ctx.fillStyle = "#e0e0e0"; 
            ctx.fillRect(gridStartX - gap, gridStartY - gap, gridTotalW + gap*2, gridTotalH + gap*2);
            
            const labels = [
                ["左上", "中上", "右上"],
                ["左中", "点击居中", "右中"],
                ["左下", "中下", "右下"]
            ];
            const arrows = [
                ["\u2196", "\u2191", "\u2197"],
                ["\u2190", "", "\u2192"],
                ["\u2199", "\u2193", "\u2198"]
            ];
            
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            
            for (let row = 0; row < 3; row++) {
                for (let col = 0; col < 3; col++) {
                    const bx = gridStartX + col * (btnW + gap);
                    const by = gridStartY + row * (btnH + gap);
                    
                    // 按钮深色底
                    ctx.fillStyle = "#161616"; 
                    ctx.fillRect(bx, by, btnW, btnH);
                    
                    // 背景方向指示箭头
                    if (arrows[row][col]) {
                        ctx.fillStyle = "rgba(255, 255, 255, 0.08)";
                        ctx.font = "bold 34px Arial";
                        ctx.fillText(arrows[row][col], bx + btnW/2, by + btnH/2 + 2);
                    }
                    
                    // 按钮文字
                    ctx.font = "14px Arial";
                    ctx.fillStyle = "#ff6a5c"; // 匹配参考图的橙红
                    if (labels[row][col] === "点击居中") {
                        // 居中文字换行处理
                        ctx.fillText("点击", bx + btnW/2, by + btnH/2 - 8);
                        ctx.fillText("居中", bx + btnW/2, by + btnH/2 + 8);
                    } else {
                        ctx.fillText(labels[row][col], bx + btnW/2, by + btnH/2);
                    }
                }
            }

            // --- B. 绘制原图 ---
            ctx.drawImage(img, 0, topMargin, this.size[0], drawH);

            const widthW = findWidget(this, "裁剪宽度");
            const heightW = findWidget(this, "裁剪高度");
            const xW = findWidget(this, "裁剪X");
            const yW = findWidget(this, "裁剪Y");
            
            if (!widthW || !heightW || !xW || !yW) {
                ctx.restore();
                return;
            }

            // --- C. 计算红框视觉坐标 ---
            const cropW = widthW.value * scale;
            const cropH = heightW.value * scale;
            const cropX = xW.value * scale; 
            const cropY = topMargin + (yW.value * scale);

            this.cropRect = { x: cropX, y: cropY, w: cropW, h: cropH };

            // --- D. 绘制遮罩 ---
            ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
            if (cropY > topMargin) ctx.fillRect(0, topMargin, this.size[0], cropY - topMargin);
            const imgBottom = topMargin + drawH;
            if (cropY + cropH < imgBottom) ctx.fillRect(0, cropY + cropH, this.size[0], imgBottom - (cropY + cropH));
            if (cropX > 0) ctx.fillRect(0, cropY, cropX, cropH);
            if (cropX + cropW < this.size[0]) ctx.fillRect(cropX + cropW, cropY, this.size[0] - (cropX + cropW), cropH);

            // --- E. 绘制红框 ---
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

            // --- 新增：9宫格点击检测 ---
            if (this.gridRect) {
                const { x, y, w, h, btnW, btnH, gap } = this.gridRect;
                if (mx >= x && mx <= x + w && my >= y && my <= y + h) {
                    const col = Math.floor((mx - x) / (btnW + gap));
                    const row = Math.floor((my - y) / (btnH + gap));
                    const bx = x + col * (btnW + gap);
                    const by = y + row * (btnH + gap);
                    // 确保精准点击在按钮内（排除间隙）
                    if (mx >= bx && mx <= bx + btnW && my >= by && my <= by + btnH) {
                        const actions = [
                            ["左上", "中上", "右上"],
                            ["左中", "点击居中", "右中"],
                            ["左下", "中下", "右下"]
                        ];
                        if (actions[row] && actions[row][col]) {
                            this.alignCrop(actions[row][col]);
                            return true; // 拦截事件，防止触发画布拖动
                        }
                    }
                }
            }

            // 原有：红框拖拽检测
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

        // 绑定刷新事件到所有组件
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