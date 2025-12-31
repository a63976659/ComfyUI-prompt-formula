// 新增：网页资源/wan26_multishot_showcontrol.js
import { app } from "../../scripts/app.js";

// 查找指定名称的widget
const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

// 根据时间格式调整视频总时长滑块的最大值和步长
function adjustDurationSlider(node) {
    if (node.comfyClass === "Wan26多镜头") {
        const timeFormatWidget = findWidgetByName(node, "时间格式");
        const durationWidget = findWidgetByName(node, "视频总时长");
        
        if (timeFormatWidget && durationWidget) {
            const timeFormat = timeFormatWidget.value;
            
            if (timeFormat === "秒") {
                // 秒格式：最大值15，步长1.0（与Wan25运镜时长滑块一致）
                durationWidget.options = durationWidget.options || {};
                durationWidget.options.min = 1.0;
                durationWidget.options.max = 15.0;
                durationWidget.options.step = 1.0;
                durationWidget.options.display = "slider";
                
                // 确保当前值在有效范围内
                if (durationWidget.value > 15.0) {
                    durationWidget.value = 15.0;
                }
            } else {
                // 帧格式：最大值900，步长1.0
                durationWidget.options = durationWidget.options || {};
                durationWidget.options.min = 1.0;
                durationWidget.options.max = 900.0;
                durationWidget.options.step = 1.0;
                durationWidget.options.display = "slider";
            }
            
            // 触发widget更新
            if (node.canvas) {
                node.canvas.nodeChanged(node);
            }
        }
    }
}

// Wan26多镜头处理函数
function wan26MultiShotHandler(node) {
    if (node.comfyClass === "Wan26多镜头") {
        // 调整视频总时长滑块
        adjustDurationSlider(node);
        
        // 获取镜头数量widget
        const shotCountWidget = findWidgetByName(node, "镜头数量");
        if (!shotCountWidget) return;
        
        const shotCount = shotCountWidget.value;
        
        // 获取智能多镜开关
        const smartMultiShotWidget = findWidgetByName(node, "启用智能多镜");
        const isSmartMode = smartMultiShotWidget ? smartMultiShotWidget.value : false;
        
        // 获取所有镜头相关widget
        const shot4StartWidget = findWidgetByName(node, "镜头4开始时间");
        const shot4EndWidget = findWidgetByName(node, "镜头4结束时间");
        const shot4DescWidget = findWidgetByName(node, "镜头4描述");
        const shot4CameraWidget = findWidgetByName(node, "镜头4运镜方式");
        
        const shot5StartWidget = findWidgetByName(node, "镜头5开始时间");
        const shot5EndWidget = findWidgetByName(node, "镜头5结束时间");
        const shot5DescWidget = findWidgetByName(node, "镜头5描述");
        const shot5CameraWidget = findWidgetByName(node, "镜头5运镜方式");
        
        // 获取其他相关widget
        const transitionWidget = findWidgetByName(node, "转场效果");
        const timeFormatWidget = findWidgetByName(node, "时间格式");
        
        // 如果是智能模式，隐藏所有镜头详细参数
        if (isSmartMode) {
            // 隐藏镜头4参数
            toggleWidget(node, shot4StartWidget, false);
            toggleWidget(node, shot4EndWidget, false);
            toggleWidget(node, shot4DescWidget, false);
            toggleWidget(node, shot4CameraWidget, false);
            
            // 隐藏镜头5参数
            toggleWidget(node, shot5StartWidget, false);
            toggleWidget(node, shot5EndWidget, false);
            toggleWidget(node, shot5DescWidget, false);
            toggleWidget(node, shot5CameraWidget, false);
            
            // 隐藏其他相关参数
            toggleWidget(node, transitionWidget, false);
            toggleWidget(node, timeFormatWidget, false);
            toggleWidget(node, shotCountWidget, false);
        } else {
            // 非智能模式下，根据镜头数量显示
            // 显示镜头数量控制
            toggleWidget(node, shotCountWidget, true);
            toggleWidget(node, transitionWidget, true);
            toggleWidget(node, timeFormatWidget, true);
            
            // 控制镜头4的显示
            if (shotCount >= 4) {
                toggleWidget(node, shot4StartWidget, true);
                toggleWidget(node, shot4EndWidget, true);
                toggleWidget(node, shot4DescWidget, true);
                toggleWidget(node, shot4CameraWidget, true);
            } else {
                toggleWidget(node, shot4StartWidget, false);
                toggleWidget(node, shot4EndWidget, false);
                toggleWidget(node, shot4DescWidget, false);
                toggleWidget(node, shot4CameraWidget, false);
            }
            
            // 控制镜头5的显示
            if (shotCount >= 5) {
                toggleWidget(node, shot5StartWidget, true);
                toggleWidget(node, shot5EndWidget, true);
                toggleWidget(node, shot5DescWidget, true);
                toggleWidget(node, shot5CameraWidget, true);
            } else {
                toggleWidget(node, shot5StartWidget, false);
                toggleWidget(node, shot5EndWidget, false);
                toggleWidget(node, shot5DescWidget, false);
                toggleWidget(node, shot5CameraWidget, false);
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
    name: "wan26.multishot.showcontrol",
    nodeCreated(node) {
        if (node.comfyClass === "Wan26多镜头") {
            // 初始处理
            wan26MultiShotHandler(node);
            
            // 为关键widget添加监听
            const shotCountWidget = findWidgetByName(node, "镜头数量");
            const smartMultiShotWidget = findWidgetByName(node, "启用智能多镜");
            const timeFormatWidget = findWidgetByName(node, "时间格式");
            
            if (shotCountWidget) {
                addWidgetValueListener(node, shotCountWidget, wan26MultiShotHandler);
            }
            
            if (smartMultiShotWidget) {
                addWidgetValueListener(node, smartMultiShotWidget, wan26MultiShotHandler);
            }
            
            if (timeFormatWidget) {
                addWidgetValueListener(node, timeFormatWidget, wan26MultiShotHandler);
            }
        }
    }
});