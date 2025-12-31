// 新增：网页资源/wan26_showcontrol.js
import { app } from "../../scripts/app.js";

// 查找指定名称的widget
const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

// Wan26图生视频处理函数
function wan26Handler(node) {
    if (node.comfyClass === "Wan26图生视频") {
        // 获取运镜方式widget
        const cameraMovementWidget = findWidgetByName(node, "运镜方式");
        
        // 获取相关widget
        const cameraTargetWidget = findWidgetByName(node, "镜头目标");
        const cameraSpeedWidget = findWidgetByName(node, "运镜速度");
        const cameraDurationWidget = findWidgetByName(node, "运镜时长");
        
        // 获取动态效果widget
        const characterEffectWidget = findWidgetByName(node, "人物动态效果");
        const characterIntensityWidget = findWidgetByName(node, "人物效果强度");
        const environmentEffectWidget = findWidgetByName(node, "环境动态效果");
        const environmentIntensityWidget = findWidgetByName(node, "环境效果强度");
        
        // 根据运镜方式控制相关widget
        if (cameraMovementWidget) {
            const cameraValue = cameraMovementWidget.value;
            
            if (cameraValue === "无") {
                // 禁用所有运镜相关widget
                toggleWidget(node, cameraTargetWidget, false);
                toggleWidget(node, cameraSpeedWidget, false);
                toggleWidget(node, cameraDurationWidget, false);
            } else {
                // 启用所有运镜相关widget
                toggleWidget(node, cameraTargetWidget, true);
                toggleWidget(node, cameraSpeedWidget, true);
                toggleWidget(node, cameraDurationWidget, true);
            }
        }
    }
}

// 切换widget的禁用状态
function toggleWidget(node, widget, show = false) {
    if (!widget) return;
    widget.disabled = !show;
}

// 为指定widget添加值监听
function addWidgetValueListener(node, widget, handler) {
    if (!widget) return;
    
    let widgetValue = widget.value;
    
    Object.defineProperty(widget, 'value', {
        get() {
            return widgetValue;
        },
        set(newVal) {
            widgetValue = newVal;
            handler(node);
        }
    });
}

app.registerExtension({
    name: "wan26.showcontrol",
    nodeCreated(node) {
        if (node.comfyClass === "Wan26图生视频") {
            // 初始处理
            wan26Handler(node);
            
            // 为运镜方式widget添加监听
            const cameraMovementWidget = findWidgetByName(node, "运镜方式");
            if (cameraMovementWidget) {
                addWidgetValueListener(node, cameraMovementWidget, wan26Handler);
            }
            
            // 监听所有widget变化
            for (const w of node.widgets || []) {
                addWidgetValueListener(node, w, wan26Handler);
            }
        }
    }
});