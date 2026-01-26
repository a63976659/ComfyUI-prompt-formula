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
        node.dragState = null; // 存储拖拽状态

        // --- 1. 重写绘制方法 (增加 X/Y 坐标支持) ---
        node.onDrawBackground = function(ctx) {
            if (!this.imgCache) return;

            const img = this.imgCache;
            
            // 计算布局偏移 (标题栏 + 组件高度)
            // 动态计算头部高度，避免写死
            // 标题栏 ~30px，每个组件 ~32px
            const headerHeight = 30;
            const widgetHeight = 32;
            // 获取当前可见的组件数量，预留一点缓冲
            const visibleWidgets = this.widgets ? this.widgets.length : 6;
            const topMargin = headerHeight + (visibleWidgets * widgetHeight) + 10;
            this.layoutTopMargin = topMargin; // 存下来供鼠标事件使用

            // 计算缩放
            const scale = this.size[0] / img.width;
            this.renderScale = scale; // 存下来供鼠标事件使用
            const drawH = img.height * scale;

            // 自动调整节点高度
            const neededHeight = topMargin + drawH + 20;
            if (Math.abs(this.size[1] - neededHeight) > 5) {
                this.setSize([this.size[0], neededHeight]);
            }

            // A. 绘制原图
            ctx.drawImage(img, 0, topMargin, this.size[0], drawH);

            // 获取参数
            const widthW = findWidget(this, "裁剪宽度");
            const heightW = findWidget(this, "裁剪高度");
            const xW = findWidget(this, "裁剪X");
            const yW = findWidget(this, "裁剪Y");
            
            if (!widthW || !heightW || !xW || !yW) return;

            // B. 计算红框的视觉坐标
            // 注意：这里不再居中计算，而是直接读取 X/Y 组件的值
            const cropW = widthW.value * scale;
            const cropH = heightW.value * scale;
            const cropX = xW.value * scale; 
            const cropY = topMargin + (yW.value * scale);

            // 保存当前的红框区域，用于 hit test (点击检测)
            this.cropRect = { x: cropX, y: cropY, w: cropW, h: cropH };

            // C. 绘制遮罩 (四矩形法)
            ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
            
            // 上
            if (cropY > topMargin) 
                ctx.fillRect(0, topMargin, this.size[0], cropY - topMargin);
            // 下
            const imgBottom = topMargin + drawH;
            if (cropY + cropH < imgBottom) 
                ctx.fillRect(0, cropY + cropH, this.size[0], imgBottom - (cropY + cropH));
            // 左
            if (cropX > 0) 
                ctx.fillRect(0, cropY, cropX, cropH);
            // 右
            if (cropX + cropW < this.size[0]) 
                ctx.fillRect(cropX + cropW, cropY, this.size[0] - (cropX + cropW), cropH);

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

            // F. 绘制文字
            ctx.fillStyle = "white";
            ctx.font = "12px Arial";
            const text = `${Math.round(widthW.value)} x ${Math.round(heightW.value)}`;
            ctx.fillText(text, cropX + 5, cropY + 15);
        };

        // --- 2. 鼠标交互逻辑 (拖拽) ---
        
        // 鼠标按下
        node.onMouseDown = function(e, localPos) {
            if (!this.cropRect) return false;
            
            const [mx, my] = localPos;
            const { x, y, w, h } = this.cropRect;

            // 检测是否点击在红框内
            if (mx >= x && mx <= x + w && my >= y && my <= y + h) {
                const xW = findWidget(this, "裁剪X");
                const yW = findWidget(this, "裁剪Y");
                
                // 记录拖拽初始状态
                this.dragState = {
                    startX: mx,
                    startY: my,
                    initialValX: xW.value,
                    initialValY: yW.value
                };
                
                // 捕获输入，防止拖动节点本身
                this.captureInput(true); 
                return true; // 消费事件
            }
            
            return false; // 未击中红框，允许拖动节点
        };

        // 鼠标移动
        node.onMouseMove = function(e, localPos) {
            if (!this.dragState) return;
            
            const [mx, my] = localPos;
            const deltaX = mx - this.dragState.startX;
            const deltaY = my - this.dragState.startY;

            // 将屏幕像素偏移转换为图像像素偏移
            const imgDeltaX = deltaX / this.renderScale;
            const imgDeltaY = deltaY / this.renderScale;

            const xW = findWidget(this, "裁剪X");
            const yW = findWidget(this, "裁剪Y");
            const widthW = findWidget(this, "裁剪宽度");
            const heightW = findWidget(this, "裁剪高度");

            if(xW && yW && this.imgCache) {
                // 计算新坐标
                let newX = this.dragState.initialValX + imgDeltaX;
                let newY = this.dragState.initialValY + imgDeltaY;

                // 边界限制 (不让红框跑出图片)
                const maxX = this.imgCache.width - widthW.value;
                const maxY = this.imgCache.height - heightW.value;

                newX = Math.max(0, Math.min(newX, maxX));
                newY = Math.max(0, Math.min(newY, maxY));

                // 更新组件值 (取整)
                xW.value = Math.round(newX);
                yW.value = Math.round(newY);

                // 强制重绘
                this.setDirtyCanvas(true, true);
            }
        };

        // 鼠标松开
        node.onMouseUp = function(e, localPos) {
            if (this.dragState) {
                this.dragState = null;
                this.captureInput(false);
                // 触发一次回调以确保后端能感知到变化（如果有连接其他逻辑）
                const xW = findWidget(this, "裁剪X");
                if (xW && xW.callback) xW.callback(xW.value);
            }
        };

        // --- 3. 刷新与逻辑控制 ---
        const refresh = async () => {
            const fileW = findWidget(node, "图像文件");
            const presetW = findWidget(node, "预设");
            const widthW = findWidget(node, "裁剪宽度");
            const heightW = findWidget(node, "裁剪高度");
            const xW = findWidget(node, "裁剪X");
            const yW = findWidget(node, "裁剪Y");

            if (!fileW || !fileW.value) return;

            // 图像加载
            if (node.imgUrl !== fileW.value) {
                const img = new Image();
                img.src = `/view?filename=${encodeURIComponent(fileW.value)}&type=input`;
                await new Promise((r) => { img.onload = r; img.onerror = r; });
                node.imgCache = img;
                node.imgUrl = fileW.value;
                
                // 图片加载时，重置最大值
                if (img.width) {
                    const maxW = Math.floor(img.width / 16) * 16;
                    const maxH = Math.floor(img.height / 16) * 16;
                    widthW.options.max = maxW; widthW.max = maxW;
                    heightW.options.max = maxH; heightW.max = maxH;
                    xW.options.max = img.width; xW.max = img.width;
                    yW.options.max = img.height; yW.max = img.height;
                    
                    // 新图加载，默认居中
                    centerCrop(img.width, img.height, widthW.value, heightW.value);
                }
            }

            const img = node.imgCache;
            if (!img) return;

            // 预设逻辑
            const isCustom = presetW.value === "自定义";
            [widthW, heightW].forEach(w => { w.disabled = !isCustom; });

            // 辅助函数：居中
            function centerCrop(iw, ih, cw, ch) {
                xW.value = Math.floor((iw - cw) / 2);
                yW.value = Math.floor((ih - ch) / 2);
            }

            // 如果切换了预设，计算尺寸并自动居中
            // 我们通过检查是否是 "刚刚切换预设" 来决定是否重置位置
            // 这里简化逻辑：只要是非自定义模式，强制尺寸匹配比例，并执行一次居中
            if (!isCustom) {
                const ratios = { "1:1": 1, "2:3": 2/3, "3:2": 3/2, "3:4": 3/4, "4:3": 4/3, "9:16": 9/16, "16:9": 16/9 };
                const r = ratios[presetW.value] || 1;
                
                let targetW, targetH;
                if (img.width / img.height > r) {
                    targetH = snap16(img.height);
                    targetW = snap16(targetH * r);
                } else {
                    targetW = snap16(img.width);
                    targetH = snap16(targetW / r);
                }

                // 只有当尺寸发生变化时，才重新居中，避免用户在预设模式下拖动后被强制复位
                // 但预设模式下通常不调整大小，所以这里的逻辑是：
                // 如果当前值不等于目标值，说明刚切过来 -> 更新并居中
                if (widthW.value !== targetW || heightW.value !== targetH) {
                    widthW.value = targetW;
                    heightW.value = targetH;
                    centerCrop(img.width, img.height, targetW, targetH);
                }
            } else {
                // 自定义模式：限制数值
                widthW.value = Math.min(snap16(widthW.value), Math.floor(img.width/16)*16);
                heightW.value = Math.min(snap16(heightW.value), Math.floor(img.height/16)*16);
                
                // 限制X/Y不越界
                xW.value = Math.max(0, Math.min(xW.value, img.width - widthW.value));
                yW.value = Math.max(0, Math.min(yW.value, img.height - heightW.value));
            }

            node.setDirtyCanvas(true, true);
        };

        // 监听
        node.widgets.forEach(w => {
            const oldCallback = w.callback;
            w.callback = (...args) => {
                if (oldCallback) oldCallback.apply(w, args);
                refresh();
            };
        });

        setTimeout(refresh, 100);
    }
});