# KiCAD JLCPCB Tools (SZLCSC Edition)

本插件是 [Bouni's kicad-jlcpcb-tools](https://github.com/bouni/kicad-jlcpcb-tools) 的国内优化分支，专为国内用户打造。

## 🌟 核心改进与特性
* **纯在线 API 搜索**：彻底移除了原版必须下载高达 2GB+ 离线 SQLite 数据库的限制。直接调取立创商城（szlcsc.com）的在线 API，获取最精准、实时的元件信息。

* **全新过滤界面**：
    * 简化了过滤规则，移除了一些的过滤条件。
    * 独有的 **封装 (Package)** 智能下拉框，自动提取当前搜索结果中的可用封装。
    * 支持 **库存 (Stock)** 阶梯阈值筛选（`All`, `>0`, `>10`, `>100`, `>1000`）。
    * 独立的 `Basic`（基础库）和 `Extended`（扩展库）排他性选择逻辑。

* **全景元件详情**：
    * 直接在插件内预览元器件图片。
    * 一键在浏览器打开立创商城专属的国内产品详情页（`item.szlcsc.com/...`）。
    
* **UI 本地化优化**：
    * 所有美金 `$` 符号修正为人民币 `¥` 价格显示。
    * 大部分按钮都进行了汉化，并添加了中文提示。
    * 增加了 load more 按钮，避免一次性加载过多元件耗时太长，以及网站的反爬虫机制。

![alt text](https://raw.githubusercontent.com/harry10086/kicad-jlcpcb-tools/main/images/new.png)

**注意：**
    除了搜索，适配元件，生成 gerber 文件，bom，cpl，其他功能我暂时没用到，所以没有详细测试，如果有问题请提交 issue，谢谢。
**提醒： 搜索适配元件时，尽量使用基础库，扩展库的元件在贴片时每种都要收 20 元的换料费。**

## 📦 安装说明
### 方法一：从文件安装
1. 进入本仓库的 [Releases](https://github.com/harry10086/kicad-jlcpcb-tools/releases) 页面。
2. 下载最新版本的 `KiCAD-PCM-*.*.*.zip` 安装包（**请勿解压**）。
3. 打开 KiCad，进入主界面的 **插件和内容管理器 (Plugin and Content Manager)**。
4. 在下方选择 **从文件安装 (Install from File...)** 并在弹窗中选择刚才下载到的 `.zip` 压缩包。
5. 安装完成后，在需要时从 PCB Editor 的上方工具栏点击 JLCPCB 图标即可启动插件。

### 方法二：通过 PCM 安装
1. 打开 KiCad，进入主界面的 **插件和内容管理器 (Plugin and Content Manager)**。
2. 在 **插件 (Plugins)** 标签页中，点击 **添加插件仓库 (Add Plugin Repository...)**。
3. 在弹出的对话框中，输入插件仓库URL：`https://raw.githubusercontent.com/harry10086/kicad-jlcpcb-tools/main/repository.json`
4. 点击 **添加 (Add)**，然后返回插件列表。
5. 找到 `KiCAD JLCPCB Tools (SZLCSC Edition)`，点击 **安装 (Install)** 按钮。
6. 安装完成后，在需要时从 PCB Editor 的上方工具栏点击 `JLCPCB` 图标即可启动插件。

## 🔧 使用方法
1. 在 PCB 编辑器内点击启动 `KiCAD JLCPCB Tools`。
2. 如果此前未曾配置过，可以在弹出界面的 Settings 内确认 "在线搜索 SZLCSC" 功能已经打开。
3. （可选）选中任意需要分配元件的 footprint，点击右侧的放大镜图标打开元件搜索器（Part Selector）。
4. 在左上角的关键字（Keywords）文本框内输入关键型号，例如：`10k 0603`，然后敲击回车或点击 `Search` 按钮获取结果。
5. 你可以使用底部的下拉框与勾选框筛选需要的元件；点击 `Load More` 可以增量加载更多立创商城的元件数据。
6. 选中元件并关闭窗口后，其 LCSC 编号就会录入进你的 KiCad 工程。
7. 在工程完成后，可以用主界面的工具一键生成专属的 BOM、CPL 甚至 Gerber 制造文件。

## 版本更新
* `v3.8.9`：分配立创编号后，元件属性里添加的 LCSC Params 字段会默认不显示，改在 F.Fab 层。
* `v3.7.8`：将绝大部分按钮进行了汉化，并添加了中文提示（AI 自动翻译）。界面默认大小进行了调整，按钮全部显示。
* `v3.7.7`：将离线数据库改为默认立创商城在线搜索，元件信息都关联到立创商城，并且将搜索结果筛选规则进行了简化。

## 🤝 致谢
感谢原作者 [Bouni](https://github.com/bouni/kicad-jlcpcb-tools) 创造了杰出的工程环境，本分支保留其出色的插件脚手架以及一键生产制造文件的等功能模块，在此基础上针对元件搜索与选型体验进行了系统性重构。

## 📜 许可证
基于 MIT / WTFPL（继承自原作者）许可。
