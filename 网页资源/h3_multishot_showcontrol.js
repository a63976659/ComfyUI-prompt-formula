// 新增：网页资源/h3_multishot_showcontrol.js
// H3音画多镜头公式节点：镜头组件数量跟随"镜头数量"变化（隐藏多余镜头的组件）
import { app } from "../../scripts/app.js";

// 查找指定名称的widget
const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

// 切换widget的禁用状态（禁用即隐藏）
function toggleWidget(node, widget, show = false) {
    if (!widget) return;
    widget.disabled = !show;
}

// 每个镜头包含的组件字段
const SHOT_WIDGET_SUFFIXES = ["开始时间", "结束时间", "景别", "描述", "运镜方式", "台词", "声音设计"];

// H3音画多镜头处理函数
function h3MultiShotHandler(node) {
    if (node.comfyClass !== "H3音画多镜头公式") return;

    // 获取镜头数量widget
    const shotCountWidget = findWidgetByName(node, "镜头数量");
    if (!shotCountWidget) return;

    const shotCount = parseInt(shotCountWidget.value) || 3;

    // 镜头1始终显示（最少1个镜头），镜头2~5按镜头数量显示/隐藏
    for (let i = 1; i <= 5; i++) {
        const show = i <= shotCount;
        for (const suffix of SHOT_WIDGET_SUFFIXES) {
            toggleWidget(node, findWidgetByName(node, `镜头${i}${suffix}`), show);
        }
    }
}

// 为指定widget添加值监听
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

            // 值变化时重新处理widget状态
            handler(node);
        }
    });
}

app.registerExtension({
    name: "h3.multishot.showcontrol",
    nodeCreated(node) {
        if (node.comfyClass === "H3音画多镜头公式") {
            // 初始处理
            h3MultiShotHandler(node);

            // 为镜头数量widget添加监听，数量变化时更新显隐
            const shotCountWidget = findWidgetByName(node, "镜头数量");
            if (shotCountWidget) {
                addWidgetValueListener(node, shotCountWidget, h3MultiShotHandler);
            }
        }
    }
});
