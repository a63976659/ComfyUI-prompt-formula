// 新增：网页资源/h3_reference_showcontrol.js
// H3全能参考公式节点：素材组件数量跟随"图片数量/视频数量/音频数量"变化（隐藏多余素材槽位的组件）
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
        widget.hidden = false;
        if (widget._h3OrigComputeSize !== undefined) widget.computeSize = widget._h3OrigComputeSize;
        else delete widget.computeSize;

        if (widget.inputEl) widget.inputEl.style.display = "";
        if (widget.element) widget.element.style.display = "";
    } else {
        widget.type = "hidden";
        // 新版前端的组件可见性判断读取 widget.hidden 标志（而非 type），
        // 不设置该标志会导致隐藏组件仍参与尺寸计算和命中检测，
        // 造成节点高度计算错乱、末尾组件无法点击
        widget.hidden = true;
        // 返回 [0, -4] 可以完美抵消 ComfyUI 默认增加的 4px 渲染缝隙（旧版前端兼容）
        widget.computeSize = () => [0, -4];

        if (widget.inputEl) widget.inputEl.style.display = "none";
        if (widget.element) widget.element.style.display = "none";
    }
}

// 缓存组件索引（节点创建后组件列表固定，避免每次显隐都遍历查找）
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

// H3全能参考处理函数
function h3ReferenceHandler(node) {
    if (node.comfyClass !== "H3全能参考公式") return;

    const widgetIndex = getWidgetIndex(node);

    const imageCountWidget = widgetIndex.get("图片数量");
    const videoCountWidget = widgetIndex.get("视频数量");
    const audioCountWidget = widgetIndex.get("音频数量");
    if (!imageCountWidget || !videoCountWidget || !audioCountWidget) return;

    const imageCount = parseInt(imageCountWidget.value) || 0;
    const videoCount = parseInt(videoCountWidget.value) || 0;
    const audioCount = parseInt(audioCountWidget.value) || 0;

    // 按数量滑块显隐素材槽位（每个槽位含"用途"+"描述"两个组件）
    for (let i = 1; i <= 9; i++) {
        const show = i <= imageCount;
        toggleWidget(node, widgetIndex.get(`参考图${i}用途`), show);
        toggleWidget(node, widgetIndex.get(`参考图${i}描述`), show);
    }
    for (let i = 1; i <= 3; i++) {
        const show = i <= videoCount;
        toggleWidget(node, widgetIndex.get(`参考视频${i}用途`), show);
        toggleWidget(node, widgetIndex.get(`参考视频${i}描述`), show);
    }
    for (let i = 1; i <= 3; i++) {
        const show = i <= audioCount;
        toggleWidget(node, widgetIndex.get(`参考音频${i}用途`), show);
        toggleWidget(node, widgetIndex.get(`参考音频${i}描述`), show);
    }

    // 显隐变化后重新计算节点尺寸，让节点高度跟随可见组件数量自动缩放（保留当前宽度，尺寸无变化时跳过重排）
    if (node.computeSize) {
        const size = node.computeSize();
        if (node.size && node.size[0] > size[0]) {
            size[0] = node.size[0];
        }
        if (!node.size || node.size[0] !== size[0] || node.size[1] !== size[1]) {
            node.setSize(size);
        }
    }
    // 串联调用底部留白补齐（h3_bottom_padding.js 提供）：
    // 等待布局稳定后按组件实际底边补齐底部留白
    if (window.__h3EnsureBottomPadding) window.__h3EnsureBottomPadding(node);
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
