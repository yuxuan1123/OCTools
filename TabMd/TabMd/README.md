# TabMd

一个零依赖的单页 Markdown 管理器：自动列出同级 `md/` 目录下的所有 `.md` 文件，**点击文件弹出新窗口编辑**，保存后直接写回磁盘。

界面遵循 `config/ui_config.json` 主题规范：**清爽现代蓝（浅灰蓝页面底 + 白色卡片 + 靛蓝主色）**，所有视觉参数集中声明、页面只按名字取用。

## 文件结构

```
TabMd/
├── TabMd.html              # 列表页 + 编辑页 + Markdown 渲染器（单文件）
├── server.py               # 零依赖本地服务：扫描 md/ 目录、读写文件、静态托管
├── config/
│   └── ui_config.json      # 唯一主题源：颜色 / 字号 / 圆角 / 内边距 / 控件高度 / 图标尺寸
└── md/                     # 你的 Markdown 都放这里
    ├── 欢迎使用.md
    ├── 语法速查.md
    └── manifest.json       # 纯静态部署时的文件清单（可选，由服务生成）
```

## 启动

```bash
cd TabMd
python3 server.py            # 打开 http://localhost:8848
python3 server.py 9000       # 换端口
python3 server.py 8848 --no-open   # 不自动开浏览器
```

只需要 Python 3，不用装任何包。

## 主题规范

**唯一主题源是 `config/ui_config.json`，不允许在页面里另建主题或硬编码样式。**

| 分组 | 关键参数 |
| --- | --- |
| `colors` | `bg` `#eef2f7`、`card` `#ffffff`、`primary` `#4f46e5`（靛蓝）、`text` `#1f2937`、`border` `#dfe5ee` |
| `fonts` | `family` / `fallback_family` / `mono_family` / `body` / `card_title` / `page_title` / 字重 / 行高 |
| `sizes` | `radius_card` 12、`border_w` 1、`control_height` 34、`nav_indicator_w` 3、`icon_size` 16 |
| `sidebar.button.alignment` | 侧栏条目文字对齐 |

落地方式：

1. `CONFIG` 单例按名字取用（`color()` / `size()` / `font()` / `raw()` / `section()`）；
2. `buildStyleSheet()` 把全部参数拼成 CSS 变量（对应 QSS 的拼接过程），注入 `<style id="theme-qss">`；
3. 页面 CSS 只允许写 `var(--c-*)` / `var(--s-*)` / `var(--f-*)`，**不得出现任何色值与硬编码尺寸**。

规范要点：卡片统一 12px 圆角 + 细边框；控件统一高度与圆角；左侧文件列表激活态带主色指示条；留白与层级靠统一间距参数控制。

> `file://` 直接打开时无法 fetch JSON，页面会启用一份与 JSON 完全同步的内嵌副本兜底（同一套主题，不是第二套主题）。用 `server.py` 启动时始终以 JSON 为准。

## 三种运行模式

页面按 **本地服务 → 静态 manifest → 手动选目录** 顺序自动探测，右上角徽章显示当前模式。

| 模式 | 条件 | 读 | 写 |
| --- | --- | --- | --- |
| 本地服务 | 运行 `server.py` | ✅ | ✅ 写回磁盘 |
| 静态 | `md/manifest.json` 存在 | ✅ | ⚠️ 只能下载 |
| 本地文件夹 | 点「选择文件夹」授权 md 目录 | ✅ | ✅ Chrome/Edge |

纯静态部署（如 nginx）先生成清单：

```bash
curl "http://localhost:8848/api/manifest?write=1"
```

## 操作说明

**列表页**

- 单击文件行 → 右侧快速预览
- 双击文件行 / 点「打开」→ **弹出新窗口编辑**
- 「+ 新建」→ 在 `md/` 下创建文件并立即打开
- 支持文件名搜索、刷新、删除

**编辑窗口**

- 顶部三个 Tab：**分屏 / 编辑 / 预览**
- `Ctrl / ⌘ + S` 保存，未保存时状态位与标题栏圆点提示
- `Ctrl / ⌘ + B` 加粗、`Ctrl / ⌘ + I` 斜体、`Tab` 缩进
- 顶部文件名可直接改名
- 保存后通过 `BroadcastChannel` 通知列表页自动刷新

## HTTP 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/files` | 扫描 `md/`，返回 `[{name,size,mtime,title}]` |
| GET | `/api/file?name=x.md` | 读取文件文本 |
| PUT/POST | `/api/file?name=x.md` | 写入（body 为全文） |
| DELETE | `/api/file?name=x.md` | 删除 |
| GET | `/api/manifest?write=1` | 生成 `md/manifest.json` |

文件名经过 `basename` + `.md` 后缀校验，不会穿越出 `md/` 目录。

## 说明

- Markdown 渲染为页面内置实现（标题、列表、引用、表格、代码块、行内样式、图片链接），不引外部 CDN，完全离线可用；渲染前做 HTML 转义。
- 浏览器安全策略不允许 `file://` 页面读取目录，想获得「自动扫描 + 保存回写」的完整体验，请用 `server.py` 启动。
