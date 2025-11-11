# ComfyUI-提示公式

comfyui使用的提示词便捷输入节点

<img width="4958" height="2452" alt="图像提示词公式使用示例" src="https://github.com/user-attachments/assets/5883d566-10c8-40a9-b628-f72c08bae277" />

提示词预设文本可以直接在`提示词预设文件夹`中进行添加、编辑、删除
<img width="1380" height="528" alt="预设文本png" src="https://github.com/user-attachments/assets/39b9396c-27e3-43c3-92c8-30d00578af42" />

## 更新说明
20250814
1. 增加提示词预设文件格式json支持
2. 优化读取机制，减少算力占用
3. 支持输入内容为空，选择项为无时，不输出内容
4. 将原来的 "Template" 文件夹改为`提示词预设文件夹`，更方便中国宝宝找到文件夹进行编辑
5. 节点名称优化、选择项内容增加
## 20250816
1. 增加提示词保存为预设节点，支持格式txt和json
2. 增加千问图像多种类型提示词公式节点
<img width="2709" height="1496" alt="预设文本" src="https://github.com/user-attachments/assets/acf84548-7f34-4def-a028-8d5072f341fd" />
<img width="3840" height="1854" alt="千问提示词节点效果" src="https://github.com/user-attachments/assets/df576479-2f1d-417d-8d7a-c856152de5c6" />

## 20250819
1. 视频提示词公式节点，运镜效果提升
2. 增加情绪、运动、光源、风格更多可选项
<img width="3528" height="1337" alt="视频提示词公式，运镜效果提升" src="https://github.com/user-attachments/assets/23ac5a8f-3c34-4c90-a93d-05143d032b08" />

## 20250826
1. 视频提示词公式节点，去除权重参数，增加眼型、天气更多可选项，可选项内容丰富，优化输出内容
 <img width="2649" height="1680" alt="Wan视频提示词生成" src="https://github.com/user-attachments/assets/747b9537-a762-4139-9e1e-f1a431a02607" />

2. 增加工作流模版，在模版中可以查看使用示例
<img width="3422" height="1284" alt="Wan视频提示词生成模版" src="https://github.com/user-attachments/assets/ee5bc83b-990f-4b50-b3eb-e46556ff6278" />


https://github.com/user-attachments/assets/645b8ce7-7ed1-4660-9c1e-89c5713c0081



## 20250923
1. 新增随机人像节点，随机时需要前面连一个随机种子生成器，否则只在改变参数时执行随机
2. 新增热门的图像变动态视频提示词示例（需配合Wan图生视频工作流），还有类似于纳米香蕉模型的图像变手办提示词示例
   
 ## 20251002
1. 更新海报生成节点，增加输入项，让海报包含更多信息
   
<img width="544" height="960" alt="ComfyUI_05842_" src="https://github.com/user-attachments/assets/203abcfa-0e09-48a4-9d23-1b8feeff88a7" />


2. 更新千问图像节点，使用默认参考内容，生成仙女图像，如下图
   
![ComfyUI_05744_](https://github.com/user-attachments/assets/b3970029-4550-43b5-bb07-a84c2940aef0)

## 20251104
1. 修复"提示词预设"节点读取文件时名称混乱。感谢网友 luckyu445 的建议。
2. 新增工具节点 “合并多组提示词”有20个可输入项，分隔符多种可以选择（逗号，句号，斜杠，换行）。
<img width="982" height="490" alt="合并多组字符串" src="https://github.com/user-attachments/assets/52d713cb-746b-45e2-b0b6-57a55f3e419b" />

3. 新增工具节点 “字符串输入反转”与“图像输入反转”作用是交换输入.
<img width="570" height="520" alt="字符串反转" src="https://github.com/user-attachments/assets/0b101b43-c93e-4f7d-bc32-ebaeb695c07c" />
<img width="620" height="716" alt="图像反转" src="https://github.com/user-attachments/assets/a66e7db9-dace-4a6f-ac63-c0603b872357" />

## 20251110
1. 新增千问单图编辑提示词公式节点，多个节点功能各不相同。
 <img width="1500" height="822" alt="千问单图编辑示例工作流" src="https://github.com/user-attachments/assets/9135c7f0-82ea-4837-b2cd-bbc044ba9e1d" />
2. 工作流模版中加入示例，可参考示例工作流使用。

## 20251111
1. 新增提取视频结束帧节点，使用方法：输入视频图像序列，输出最后一帧图像。
2. 优化千问编辑预设内容，输出更加合理。
3. 新增判断并输出预览图像节点，使用方法：第一个端口连接提示词输入（字符串都可以），目标文本输入触发词，输出加载的预览图像。
4. 新增批量判断并输出同名图像节点核心功能。效果类似判断并输出预览图像节点。

批量判断并输出同名图像节点介绍：
1. 智能文件名匹配
2. 后缀忽略：不检查目标文本是否带有图像文件后缀
3. 灵活匹配：支持多种分隔符的匹配模式
4. 基础名称提取：自动从目标文本中提取文件名基础部分
5. 动态图像查找
6. 目录搜索：在指定目录中递归查找匹配的图像文件
7. 多格式支持：支持jpg、png、bmp、tiff、webp等常见格式
8. 实时反馈：提供详细的查找和加载状态。

！！！功能还不完善，使用可能会报错。


## 安装说明
1. 确保已安装ComfyUI
2. 将此仓库克隆到ComfyUI的`custom_nodes`目录下：
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/a63976659/ComfyUI-prompt-formula.git
```

## 使用方法
1. 在右键添加节点中，您可以在"📃提示词公式"类别下找到所有工具节点,点击名称即可将节点加入到工作区
2. 在节点库（快捷键n）在"📃提示词公式"类别下找到所有工具节点,将需要的节点拖入工作区使用
3. 支持提示词历史记录10条，超过自动清理时间最远的记录，不用担心缓存文件过多。
4. 支持将历史记录保存为预设，在历史记录和预设管理节点，为预设命名，并连接任意节点执行一次，点击快捷键r刷新后在提示词预设节点中即可找到
5. 手动在`提示词预设文件夹`中进行添加、编辑、删除预设，点击快捷键r刷新后，即可看到改变后的预设文件
6. 默认预设文件使用txt格式
节点使用介绍视频：https://www.bilibili.com/video/BV1nveMzcES4/
7. 千问编辑节点配合千问编辑工作流使用。
千问编辑效果参考以下视频：https://www.bilibili.com/video/BV1C21wBZEsf/

## 插件作者
- BiliBili:猪的飞行梦
- 企鹅群202018000
- 觉得插件还不错，支持一下作者
![微信图片_2025-08-26_170541_386](https://github.com/user-attachments/assets/b6ae0001-a39f-41b4-af9d-fbefe9d30cd0)


Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
