// 网页资源/showcontrol_video_transition.js
import { app } from "../../scripts/app.js";

// 查找指定名称的widget
const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

// 切换widget的禁用状态
function toggleWidget(node, widget, show = false, suffix = "") {
    if (!widget) return;
    widget.disabled = !show;
    widget.linkedWidgets?.forEach(w => toggleWidget(node, w, ":" + widget.name, show));
}

// 视频首尾帧转场处理函数
function videoTransitionHandler(node) {
    if (node.comfyClass === "视频首尾帧转场") {
        // 获取主要转场方式widget
        const mainTransitionWidget = findWidgetByName(node, "主要转场方式");
        if (!mainTransitionWidget) return;

        // 获取所有需要动态控制的widget
        const motionSubtypeWidget = findWidgetByName(node, "运动子类型");
        const motionDirectionWidget = findWidgetByName(node, "运动方向");
        const morphSubtypeWidget = findWidgetByName(node, "变形子类型");
        const occlusionTypeWidget = findWidgetByName(node, "遮挡物类型");
        const characterChangeTypeWidget = findWidgetByName(node, "人物变化类型");
        const transitionRhythmWidget = findWidgetByName(node, "转场节奏");
        const visualConsistencyWidget = findWidgetByName(node, "视觉连贯性");

        // 根据主要转场方式动态控制其他widget
        const mainTransition = mainTransitionWidget.value;
        
        // 默认禁用所有可选widget
        toggleWidget(node, motionSubtypeWidget, false);
        toggleWidget(node, motionDirectionWidget, false);
        toggleWidget(node, morphSubtypeWidget, false);
        toggleWidget(node, occlusionTypeWidget, false);
        toggleWidget(node, characterChangeTypeWidget, false);
        toggleWidget(node, transitionRhythmWidget, false);
        toggleWidget(node, visualConsistencyWidget, false);

        // 根据选择的转场方式启用相关widget
        switch (mainTransition) {
            case "运镜提示词转场":
                toggleWidget(node, motionSubtypeWidget, true);
                toggleWidget(node, motionDirectionWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                break;
                
            case "运动匹配转场":
                toggleWidget(node, motionSubtypeWidget, true);
                toggleWidget(node, motionDirectionWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                break;
                
            case "形态变形转场":
                toggleWidget(node, morphSubtypeWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                break;
                
            case "遮挡物转场":
                toggleWidget(node, occlusionTypeWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                break;
                
            case "多重转场组合":
                toggleWidget(node, motionSubtypeWidget, true);
                toggleWidget(node, morphSubtypeWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                break;
                
            case "主体变形转场":
            case "画面渐变转场":
            case "主体遮挡转场":
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                break;
                
            case "人物到人物变化":
                toggleWidget(node, characterChangeTypeWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                break;
                
            case "交叉溶解转场":
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                break;
                
            case "无":
                // 不需要任何额外参数
                break;
        }
    }
}

app.registerExtension({
    name: "video-transition.showcontrol",
    nodeCreated(node) {
        if (node.comfyClass !== "视频首尾帧转场") {
            return;
        }

        // 初始处理
        videoTransitionHandler(node);
        
        // 为所有widget添加值监听
        for (const w of node.widgets || []) {
            let widgetValue = w.value;

            // 存储原始描述符
            let originalDescriptor = Object.getOwnPropertyDescriptor(w, 'value') || 
                Object.getOwnPropertyDescriptor(Object.getPrototypeOf(w), 'value');
            if (!originalDescriptor) {
                originalDescriptor = Object.getOwnPropertyDescriptor(w.constructor.prototype, 'value');
            }

            Object.defineProperty(w, 'value', {
                get() {
                    let valueToReturn = originalDescriptor && originalDescriptor.get
                        ? originalDescriptor.get.call(w)
                        : widgetValue;
                    return valueToReturn;
                },
                set(newVal) {
                    if (originalDescriptor && originalDescriptor.set) {
                        originalDescriptor.set.call(w, newVal);
                    } else { 
                        widgetValue = newVal;
                    }

                    // 值变化时重新处理widget状态
                    videoTransitionHandler(node);
                }
            });
        }
    }
});