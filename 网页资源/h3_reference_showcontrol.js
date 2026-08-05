// 新增：网页资源/h3_reference_showcontrol.js
// H3全能参考公式节点：素材组件数量跟随"图片数量/视频数量/音频数量"变化（隐藏多余素材槽位的组件）
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

// H3全能参考处理函数
function h3ReferenceHandler(node) {
    if (node.comfyClass !== "H3全能参考公式") return;

    const imageCountWidget = findWidgetByName(node, "图片数量");
    const videoCountWidget = findWidgetByName(node, "视频数量");
    const audioCountWidget = findWidgetByName(node, "音频数量");
    if (!imageCountWidget || !videoCountWidget || !audioCountWidget) return;

    const imageCount = parseInt(imageCountWidget.value) || 0;
    const videoCount = parseInt(videoCountWidget.value) || 0;
    const audioCount = parseInt(audioCountWidget.value) || 0;

    // 按数量滑块显隐素材槽位（每个槽位含"用途"+"描述"两个组件）
    for (let i = 1; i <= 9; i++) {
        const show = i <= imageCount;
        toggleWidget(node, findWidgetByName(node, `参考图${i}用途`), show);
        toggleWidget(node, findWidgetByName(node, `参考图${i}描述`), show);
    }
    for (let i = 1; i <= 3; i++) {
        const show = i <= videoCount;
        toggleWidget(node, findWidgetByName(node, `参考视频${i}用途`), show);
        toggleWidget(node, findWidgetByName(node, `参考视频${i}描述`), show);
    }
    for (let i = 1; i <= 3; i++) {
        const show = i <= audioCount;
        toggleWidget(node, findWidgetByName(node, `参考音频${i}用途`), show);
        toggleWidget(node, findWidgetByName(node, `参考音频${i}描述`), show);
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
    name: "h3.reference.showcontrol",
    nodeCreated(node) {
        if (node.comfyClass === "H3全能参考公式") {
            // 初始处理
            h3ReferenceHandler(node);

            // 为三个数量widget添加监听，数量变化时更新显隐
            for (const countName of ["图片数量", "视频数量", "音频数量"]) {
                const countWidget = findWidgetByName(node, countName);
                if (countWidget) {
                    addWidgetValueListener(node, countWidget, h3ReferenceHandler);
                }
            }
        }
    }
});
