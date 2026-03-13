import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Comfy.ToolsNode.MergePrompts",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 这里的名称必须对应 Python 中 NODE_CLASS_MAPPINGS 的 Key
        if (nodeData.name === "合并多组提示词") {
            
            // --- 核心逻辑函数 ---
            const updateNodeInputs = function(node) {
                // 获取当前最后一个有连线的输入索引 (0-based)
                let lastLinkIndex = -1;
                
                // node.inputs 可能在初始化瞬间为空，做个保护
                if (!node.inputs) return;

                for (let i = 0; i < node.inputs.length; i++) {
                    if (node.inputs[i].link !== null) {
                        lastLinkIndex = i;
                    }
                }

                // 计算目标显示的输入数量
                // 规则：显示到 "最后一个连接 + 1个空位"
                // 基础至少显示 2 个
                let targetCount = lastLinkIndex + 2;
                if (targetCount < 2) targetCount = 2;
                if (targetCount > 50) targetCount = 50;

                const currentCount = node.inputs.length;

                let hasChanged = false;

                // 情况A: 需要增加输入槽
                if (currentCount < targetCount) {
                    for (let i = currentCount; i < targetCount; i++) {
                        // 必须使用与 Python 端一致的名称 "提示词X"
                        // i是索引(0开始)，所以名称是 i+1
                        const inputName = `提示词${i + 1}`;
                        node.addInput(inputName, "STRING");
                    }
                    hasChanged = true;
                }
                
                // 情况B: 需要移除多余的空闲输入槽
                else if (currentCount > targetCount) {
                    // 从末尾开始删除
                    for (let i = currentCount; i > targetCount; i--) {
                        node.removeInput(i - 1);
                    }
                    hasChanged = true;
                }

                // 【关键修改】如果输入数量发生了改变，强制重新计算并设置节点尺寸
                if (hasChanged) {
                    // computeSize() 会根据当前的输入/输出端口数量计算所需的最小尺寸
                    const newSize = node.computeSize();
                    // 应用新的尺寸，使节点高度适应内容
                    node.setSize(newSize);
                    
                    // 触发重绘
                    node.setDirtyCanvas(true, true);
                }
            };

            // --- 监听1: 节点创建时 ---
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // 节点刚生成时，Python传来了50个输入，我们立刻执行清理，变成默认的2个
                // 这时上面的 setSize 逻辑会生效，把节点高度缩回来
                updateNodeInputs(this);
                
                return r;
            };

            // --- 监听2: 连接发生变化时 ---
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info, slotObj) {
                const r = onConnectionsChange ? onConnectionsChange.apply(this, arguments) : undefined;
                
                // 只有当是输入端口(type 1)发生变化时才处理
                // 使用 setTimeout 确保 LiteGraph 内部状态更新完毕后再执行我们的逻辑
                if (type === 1) {
                    setTimeout(() => {
                        updateNodeInputs(this);
                    }, 20);
                }
                
                return r;
            };
        }
    }
});