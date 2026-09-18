// 新增：网页资源/h3_bottom_padding.js
// MiniMax H3 系列节点底部预留留白（参考 imagecrop.js 的 paddingBottom 底部留白方案），
// 避免组件紧贴节点下边缘。
import { app } from "../../scripts/app.js";

// 需要底部留白的 H3 节点（与 __init__.py 注册的类名一致）
const H3_CLASSES = [
    "H3文生视频公式",
    "H3首尾帧公式",
    "H3图生视频公式",
    "H3全能参考公式",
    "H3音画多镜头公式",
    "H3视频编辑公式"
];

// 底部预留高度（像素，与 imagecrop.js 的 paddingBottom=15 保持一致）
const BOTTOM_PADDING = 15;

// 组件默认高度兜底
const DEFAULT_WIDGET_HEIGHT = 24;

// 布局稳定等待时间：新版布局引擎由 Vue 响应式异步触发，
// 尺寸/显隐变化后需等待布局完成才能测量组件实际底边
const SETTLE_DELAY = 150;

// 布局重试上限（组件 y 尚未写入时延迟重测）
const MAX_RETRY = 10;

// 测量可见组件实际布局的底边（相对节点顶部的像素值）。
// 新版布局引擎写入 widget.y，旧版写入 last_y，两者都兼容。
// 返回 { bottom, ready }：有可见组件尚未完成布局时 ready=false
function getWidgetsBottom(node) {
    if (!node.widgets || !node.widgets.length) return { bottom: 0, ready: false };
    let bottom = 0;
    let ready = true;
    let hasVisible = false;
    for (const w of node.widgets) {
        if (w.type === "hidden" || w.hidden) continue;
        hasVisible = true;
        const wy = (typeof w.y === "number" && w.y > 0) ? w.y
            : (typeof w.last_y === "number" && w.last_y > 0 ? w.last_y : null);
        if (wy === null) {
            ready = false;
            continue;
        }
        const h = w.computedHeight ?? (typeof w.computeSize === "function" && node.size
            ? w.computeSize(node.size[0])[1]
            : DEFAULT_WIDGET_HEIGHT);
        bottom = Math.max(bottom, wy + h);
    }
    return { bottom, ready: ready && hasVisible };
}

// 测量并补齐底部留白：节点高度不足"组件底边 + 留白"时撑高（保留当前宽度）
function measureAndPad(node, retry = 0) {
    if (!node.graph || !node.widgets || !node.widgets.length || !node.size) return;
    const { bottom, ready } = getWidgetsBottom(node);
    if (!ready) {
        // 布局尚未完成，稍后重测
        if (retry < MAX_RETRY) {
            node._h3PadTimer = setTimeout(() => measureAndPad(node, retry + 1), SETTLE_DELAY);
        }
        return;
    }
    const 目标高度 = bottom + BOTTOM_PADDING;
    if (node.size[1] < 目标高度) {
        // 标记防止 setSize 触发 onResize 守卫后重复调度
        node._h3PaddingResize = true;
        node.setSize([node.size[0], 目标高度]);
        node._h3PaddingResize = false;
        node.setDirtyCanvas(true, true);
    }
}

// 防抖调度：任何尺寸/显隐变化后等待布局稳定再测量补齐
function schedulePadding(node) {
    clearTimeout(node._h3PadTimer);
    node._h3PadTimer = setTimeout(() => measureAndPad(node), SETTLE_DELAY);
}

// 暴露给显隐控制扩展（h3_multishot/h3_reference_showcontrol）直接调用：
// 扩展注册顺序不保证 onResize 守卫先于显隐 handler 安装，直接串联调用最可靠
window.__h3EnsureBottomPadding = schedulePadding;

app.registerExtension({
    name: "ComfyUI-prompt-formula.H3.BottomPadding",
    nodeCreated(node) {
        if (!H3_CLASSES.includes(node.comfyClass)) return;
        // 避免重复包装（多个扩展钩子或节点重建场景）
        if (node._h3BottomPaddingApplied) return;
        node._h3BottomPaddingApplied = true;

        // 新版布局引擎会把节点内的剩余空间全部分配给可变高度组件（STRING文本框），
        // 直接撑高节点只会让文本框变高、留白被吸收。
        // 这里给可变组件的高度分布设置"冻结上限"：首次布局不限高（取得自然高度），
        // 之后每次布局以上次实际分配的高度为上限，多出的节点高度即成为真实底部留白
        for (const w of node.widgets || []) {
            if (typeof w.computeLayoutSize === "function" && !w._h3LayoutCapped) {
                const 原布局尺寸 = w.computeLayoutSize.bind(w);
                w.computeLayoutSize = function (目标节点) {
                    const 结果 = 原布局尺寸(目标节点) || {};
                    const 最小高度 = 结果.minHeight ?? DEFAULT_WIDGET_HEIGHT;
                    // computedHeight 为上一次布局实际分配的高度；首次布局前尚未赋值，不限高
                    if (typeof w.computedHeight === "number" && w.computedHeight > 最小高度) {
                        return { ...结果, minHeight: 最小高度, maxHeight: w.computedHeight };
                    }
                    return 结果;
                };
                w._h3LayoutCapped = true;
            }
        }

        // onResize 守卫：setSize 会触发 onResize，显隐控制扩展缩放节点、
        // 用户手动调整尺寸时都会走到这里，调度布局稳定后的留白补齐
        const origOnResize = node.onResize;
        node.onResize = function () {
            if (origOnResize) origOnResize.apply(this, arguments);
            if (this._h3PaddingResize) return;
            schedulePadding(this);
        };

        // 新创建节点 / 旧工作流加载（configure 会用保存的旧尺寸覆盖）后调度补齐
        schedulePadding(node);
        const origConfigure = node.onConfigure;
        node.onConfigure = function () {
            if (origConfigure) origConfigure.apply(this, arguments);
            schedulePadding(this);
        };
    }
});
