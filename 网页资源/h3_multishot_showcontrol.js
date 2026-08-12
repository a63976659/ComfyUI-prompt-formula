// 新增：网页资源/h3_multishot_showcontrol.js
// H3音画多镜头公式节点：镜头组件数量跟随"镜头数量"变化（隐藏多余镜头的组件）
import { app } from "../../scripts/app.js";

// 查找指定名称的widget
const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

// 切换widget的显隐状态（真隐藏并同步缩放节点高度，参考智能体对话预设.js的组件隐藏实现）
function toggleWidget(node, widget, show = false) {
    if (!widget) return;

    // 只在第一次备份最原始的属性，便于恢复
    if (widget._h3BackedUp === undefined) {
        widget._h3OrigType = widget.type;
        widget._h3OrigComputeSize = widget.hasOwnProperty('computeSize') ? widget.computeSize : undefined;
        widget._h3BackedUp = true;
    }

    if (show) {
        widget.type = widget._h3OrigType;
        if (widget._h3OrigComputeSize !== undefined) widget.computeSize = widget._h3OrigComputeSize;
        else delete widget.computeSize;

        if (widget.inputEl) widget.inputEl.style.display = "";
        if (widget.element) widget.element.style.display = "";
    } else {
        widget.type = "hidden";
        // 返回 [0, -4] 可以完美抵消 ComfyUI 默认增加的 4px 渲染缝隙
        widget.computeSize = () => [0, -4];

        if (widget.inputEl) widget.inputEl.style.display = "none";
        if (widget.element) widget.element.style.display = "none";
    }
}

// 每个镜头包含的组件字段
const SHOT_WIDGET_SUFFIXES = ["开始时间", "结束时间", "景别", "描述", "运镜方式", "台词", "声音设计"];

// 镜头上限（与Python端 H3音画多镜头公式.最大镜头数 保持一致）
const MAX_SHOTS = 50;

// 缓存组件索引（节点创建后组件列表固定，避免每次显隐都遍历查找，组件多时拖动更流畅）
function getWidgetIndex(node) {
    if (!node._h3WidgetIndex) {
        node._h3WidgetIndex = new Map();
        if (node.widgets) {
            for (const w of node.widgets) {
                node._h3WidgetIndex.set(w.name, w);
            }
        }
    }
    return node._h3WidgetIndex;
}

// H3音画多镜头处理函数
function h3MultiShotHandler(node) {
    if (node.comfyClass !== "H3音画多镜头公式") return;

    const widgetIndex = getWidgetIndex(node);

    // 获取镜头数量widget
    const shotCountWidget = widgetIndex.get("镜头数量");
    if (!shotCountWidget) return;

    const shotCount = parseInt(shotCountWidget.value) || 3;

    // 按镜头数量显隐各镜头的组件（镜头1始终显示，最少1个镜头）
    for (let i = 1; i <= MAX_SHOTS; i++) {
        const show = i <= shotCount;
        for (const suffix of SHOT_WIDGET_SUFFIXES) {
            toggleWidget(node, widgetIndex.get(`镜头${i}${suffix}`), show);
        }
    }

    // 显隐变化后重新计算节点尺寸，让节点高度跟随可见镜头数量自动缩放（保留当前宽度，尺寸无变化时跳过重排）
    if (node.computeSize) {
        const size = node.computeSize();
        if (node.size && node.size[0] > size[0]) {
            size[0] = node.size[0];
        }
        if (!node.size || node.size[0] !== size[0] || node.size[1] !== size[1]) {
            node.setSize(size);
        }
    }
    node.setDirtyCanvas(true, true);
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
