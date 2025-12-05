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

// 视频首尾帧转场处理函数（原节点）
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
        const foregroundOcclusionWidget = findWidgetByName(node, "前景遮挡物");
        const unfoldMethodWidget = findWidgetByName(node, "展开方式");
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
        toggleWidget(node, foregroundOcclusionWidget, false);
        toggleWidget(node, unfoldMethodWidget, false);
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
                
                // 检查遮挡物类型是否为"前景物体遮挡"
                if (occlusionTypeWidget && occlusionTypeWidget.value === "前景物体遮挡") {
                    toggleWidget(node, foregroundOcclusionWidget, true);
                }
                break;
                
            case "多重转场组合":
                toggleWidget(node, motionSubtypeWidget, true);
                toggleWidget(node, motionDirectionWidget, true);
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
                
            case "画卷展开式转场":
                toggleWidget(node, unfoldMethodWidget, true);
                toggleWidget(node, foregroundOcclusionWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                break;
                
            case "无":
                // 不需要任何额外参数
                break;
        }
    }
}

// 视频首尾帧转场-增强版处理函数
function enhancedVideoTransitionHandler(node) {
    if (node.comfyClass === "视频首尾帧转场-增强版") {
        // 获取主要转场方式widget
        const mainTransitionWidget = findWidgetByName(node, "主要转场方式");
        if (!mainTransitionWidget) return;

        // 获取所有需要动态控制的widget
        const motionSubtypeWidget = findWidgetByName(node, "运动子类型");
        const motionDirectionWidget = findWidgetByName(node, "运动方向");
        const morphSubtypeWidget = findWidgetByName(node, "变形子类型");
        const occlusionTypeWidget = findWidgetByName(node, "遮挡物类型");
        const foregroundOcclusionWidget = findWidgetByName(node, "前景遮挡物");
        const unfoldMethodWidget = findWidgetByName(node, "展开方式");
        const characterChangeTypeWidget = findWidgetByName(node, "人物变化类型");
        const transitionRhythmWidget = findWidgetByName(node, "转场节奏");
        const visualConsistencyWidget = findWidgetByName(node, "视觉连贯性");
        const cameraMovementWidget = findWidgetByName(node, "运镜方式");
        const characterEffectWidget = findWidgetByName(node, "人物动态效果");
        const characterIntensityWidget = findWidgetByName(node, "人物效果强度");
        const environmentEffectWidget = findWidgetByName(node, "环境动态效果");
        const environmentIntensityWidget = findWidgetByName(node, "环境效果强度");

        // 根据主要转场方式动态控制其他widget
        const mainTransition = mainTransitionWidget.value;
        
        // 默认禁用所有可选widget
        toggleWidget(node, motionSubtypeWidget, false);
        toggleWidget(node, motionDirectionWidget, false);
        toggleWidget(node, morphSubtypeWidget, false);
        toggleWidget(node, occlusionTypeWidget, false);
        toggleWidget(node, foregroundOcclusionWidget, false);
        toggleWidget(node, unfoldMethodWidget, false);
        toggleWidget(node, characterChangeTypeWidget, false);
        toggleWidget(node, transitionRhythmWidget, false);
        toggleWidget(node, visualConsistencyWidget, false);
        toggleWidget(node, cameraMovementWidget, false);
        toggleWidget(node, characterEffectWidget, false);
        toggleWidget(node, characterIntensityWidget, false);
        toggleWidget(node, environmentEffectWidget, false);
        toggleWidget(node, environmentIntensityWidget, false);

        // 根据选择的转场方式启用相关widget
        switch (mainTransition) {
            case "运镜提示词转场":
                toggleWidget(node, motionSubtypeWidget, true);
                toggleWidget(node, motionDirectionWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                break;
                
            case "运动匹配转场":
                toggleWidget(node, motionSubtypeWidget, true);
                toggleWidget(node, motionDirectionWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                toggleWidget(node, cameraMovementWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                break;
                
            case "形态变形转场":
                toggleWidget(node, morphSubtypeWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                toggleWidget(node, cameraMovementWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                break;
                
            case "遮挡物转场":
                toggleWidget(node, occlusionTypeWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                toggleWidget(node, cameraMovementWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                
                // 检查遮挡物类型是否为"前景物体遮挡"
                if (occlusionTypeWidget && occlusionTypeWidget.value === "前景物体遮挡") {
                    toggleWidget(node, foregroundOcclusionWidget, true);
                }
                break;
                
            case "多重转场组合":
                toggleWidget(node, motionSubtypeWidget, true);
                toggleWidget(node, motionDirectionWidget, true);
                toggleWidget(node, morphSubtypeWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                toggleWidget(node, cameraMovementWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                break;
                
            case "主体变形转场":
            case "画面渐变转场":
            case "主体遮挡转场":
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                toggleWidget(node, cameraMovementWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                break;
                
            case "人物到人物变化":
                toggleWidget(node, characterChangeTypeWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                toggleWidget(node, cameraMovementWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                break;
                
            case "交叉溶解转场":
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                toggleWidget(node, cameraMovementWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                break;
                
            case "画卷展开式转场":
                toggleWidget(node, unfoldMethodWidget, true);
                toggleWidget(node, foregroundOcclusionWidget, true);
                toggleWidget(node, transitionRhythmWidget, true);
                toggleWidget(node, visualConsistencyWidget, true);
                toggleWidget(node, cameraMovementWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                break;
                
            case "无":
                // 不需要转场参数，但允许使用动态效果
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
                break;
                
            default:
                // 对于其他转场方式，启用运镜方式widget和动态效果widget
                toggleWidget(node, cameraMovementWidget, true);
                toggleWidget(node, characterEffectWidget, true);
                toggleWidget(node, environmentEffectWidget, true);
        }
        
        // 根据人物动态效果的值控制人物效果强度widget
        if (characterEffectWidget) {
            if (!characterEffectWidget.disabled) {
                const characterEffectValue = characterEffectWidget.value;
                if (characterEffectValue === "无") {
                    toggleWidget(node, characterIntensityWidget, false);
                } else {
                    toggleWidget(node, characterIntensityWidget, true);
                }
            } else {
                toggleWidget(node, characterIntensityWidget, false);
            }
        }
        
        // 根据环境动态效果的值控制环境效果强度widget
        if (environmentEffectWidget) {
            if (!environmentEffectWidget.disabled) {
                const environmentEffectValue = environmentEffectWidget.value;
                if (environmentEffectValue === "无") {
                    toggleWidget(node, environmentIntensityWidget, false);
                } else {
                    toggleWidget(node, environmentIntensityWidget, true);
                }
            } else {
                toggleWidget(node, environmentIntensityWidget, false);
            }
        }
    }
}

// 视频动效提示词处理函数
function videoEffectsHandler(node) {
    if (node.comfyClass === "视频动效提示词") {
        // 获取人物动态效果widget
        const characterEffectWidget = findWidgetByName(node, "人物动态效果");
        // 获取动态目标对象widget
        const targetObjectWidget = findWidgetByName(node, "动态目标对象");
        
        // 初始处理
        if (characterEffectWidget && targetObjectWidget) {
            const characterEffectValue = characterEffectWidget.value;
            
            // 如果人物动态效果为"无"，则禁用动态目标对象
            if (characterEffectValue === "无") {
                toggleWidget(node, targetObjectWidget, false);
            } else {
                // 否则启用动态目标对象
                toggleWidget(node, targetObjectWidget, true);
            }
        }
    }
}

// 辅助函数：为指定widget添加值监听
function addWidgetValueListener(node, widget, handler) {
    if (!widget) return;
    
    let widgetValue = widget.value;
    
    // 存储原始描述符
    let originalDescriptor = Object.getOwnPropertyDescriptor(widget, 'value') || 
        Object.getOwnPropertyDescriptor(Object.getPrototypeOf(widget), 'value');
    if (!originalDescriptor) {
        originalDescriptor = Object.getOwnPropertyDescriptor(widget.constructor.prototype, 'value');
    }
    
    Object.defineProperty(widget, 'value', {
        get() {
            let valueToReturn = originalDescriptor && originalDescriptor.get
                ? originalDescriptor.get.call(widget)
                : widgetValue;
            return valueToReturn;
        },
        set(newVal) {
            if (originalDescriptor && originalDescriptor.set) {
                originalDescriptor.set.call(widget, newVal);
            } else { 
                widgetValue = newVal;
            }
            
            // 值变化时调用处理函数
            handler(node);
        }
    });
}

app.registerExtension({
    name: "video-transition.showcontrol",
    nodeCreated(node) {
        if (node.comfyClass === "视频首尾帧转场") {
            // 原节点处理
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
        else if (node.comfyClass === "视频首尾帧转场-增强版") {
            // 增强版节点处理
            enhancedVideoTransitionHandler(node);
            
            // 找到需要特殊监听的widget
            const characterEffectWidget = findWidgetByName(node, "人物动态效果");
            const environmentEffectWidget = findWidgetByName(node, "环境动态效果");
            const mainTransitionWidget = findWidgetByName(node, "主要转场方式");
            const occlusionTypeWidget = findWidgetByName(node, "遮挡物类型");
            
            // 为主转场方式widget添加监听
            if (mainTransitionWidget) {
                addWidgetValueListener(node, mainTransitionWidget, enhancedVideoTransitionHandler);
            }
            
            // 为遮挡物类型widget添加监听（用于控制前景遮挡物组件）
            if (occlusionTypeWidget) {
                addWidgetValueListener(node, occlusionTypeWidget, enhancedVideoTransitionHandler);
            }
            
            // 为人物动态效果widget添加监听
            if (characterEffectWidget) {
                addWidgetValueListener(node, characterEffectWidget, enhancedVideoTransitionHandler);
            }
            
            // 为环境动态效果widget添加监听
            if (environmentEffectWidget) {
                addWidgetValueListener(node, environmentEffectWidget, enhancedVideoTransitionHandler);
            }
            
            // 为其他相关widget也添加监听
            const relevantWidgetNames = [
                "运动子类型", "运动方向", "变形子类型",
                "人物变化类型", "转场节奏", "视觉连贯性", 
                "运镜方式", "展开方式"  // 新增展开方式widget监听
            ];
            
            for (const widgetName of relevantWidgetNames) {
                const widget = findWidgetByName(node, widgetName);
                if (widget) {
                    addWidgetValueListener(node, widget, enhancedVideoTransitionHandler);
                }
            }
        }
        else if (node.comfyClass === "视频动效提示词") {
            // 视频动效提示词节点处理
            videoEffectsHandler(node);
            
            // 找到需要监听的widget
            const characterEffectWidget = findWidgetByName(node, "人物动态效果");
            const targetObjectWidget = findWidgetByName(node, "动态目标对象");
            
            // 为人物的动态效果widget添加监听
            if (characterEffectWidget) {
                addWidgetValueListener(node, characterEffectWidget, videoEffectsHandler);
            }
            
            // 为其他可能影响目标对象的widget也添加监听
            // 例如：环境动态效果、镜头特效、物理效果
            const otherEffectWidgets = [
                "环境动态效果",
                "镜头特效", 
                "物理效果"
            ];
            
            for (const widgetName of otherEffectWidgets) {
                const widget = findWidgetByName(node, widgetName);
                if (widget) {
                    addWidgetValueListener(node, widget, videoEffectsHandler);
                }
            }
        }
    }
});