---
title: HTML 速查表
description: 这里列出了最常用的 HTML 标签。
created: 2022-10-20
---

<a id="table-of-contents"></a>

## 目录

- [HTML 开发者速查表](#html-cheatsheet-for-developers)
  - [HTML 基础标签](#basic-tags-of-html)
  - [用于构建文档的标签](#tags-to-structure-document)
  - [语义化元素](#semantic-elements)
  - [格式化](#formatting)
  - [链接](#links)
  - [图像](#images)
  - [列表](#lists)
  - [表单](#forms)
  - [重要属性](#important-attributes)
  - [输入类型](#input-Types)
  - [表格](#tables)
  - [图形](#graphics)
  - [媒体](#media)

<a id="html-cheatsheet-for-developers"></a>

# HTML 开发者速查表

<a id="basic-tags-of-html"></a>

## HTML 基础标签

> 标签类似于关键字，用于定义 Web 浏览器将如何格式化和显示内容。

| Command                | Description                                                                                                                               |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `<html>...</html>`     | 可被视为页面中所有其他标签的父标签。                                                               |
| `<head>...</head>`     | 用于指定网页的元数据。包括网页名称、依赖项（JS 和 CSS 脚本）、字体使用等。 |
| `<body>...</body>`     | 网页所有内容的容器。                                                                                            |
| `<base/>`              | 用于指定站点的基础 URL，此标签可使站点内部链接更简洁。                                  |
| `<meta/>`              | 可用于注明页面的作者、关键字、原始发布日期等。                                                     |
| `<link/>`              | 用于链接网页外部的脚本。通常用于引入样式表。                                    |
| `<style>...</style>`   | style 标签可用作外部样式表的替代方案，或对其加以补充。包含网页的外观信息。   |
| `<script>...</script>` | 用于添加代码片段（通常为 JavaScript）以使网页具有动态性。也可仅用于链接外部脚本。       |

**[🔼Back to Top](#table-of-contents)**

<a id="tags-to-structure-document"></a>

## 用于构建文档的标签

| Command                        | Description                                                                                                                    |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `<h1..h6> … </h1..h6>`         | 六种不同级别的标题写法。`<h1>` 标签字体最大，而 `<h6>` 字体最小。            |
| `<div>...</div>`               | 网页内容通常被划分为区块，由 div 标签指定。                                                  |
| `<span>...</span>`             | 此标签注入内联元素，如图像、图标、表情符号，而不会破坏页面的格式/样式。            |
| `<p>...</p>`                   | 纯文本放置在该标签内。                                                                                           |
| `<br>`                         | 网页的换行符。用于在需要另起一行时使用。                                                         |
| `<hr/>`                        | 除了切换到下一行外，此标签还会绘制一条水平线以标示该部分的结束。             |
| `<strike>...</strike>`         | 另一个旧标签，用于在文本中间绘制一条线，使其看起来不重要或不再有用。 |
| `<cite>...</cite>`             | 用于引用引文作者的标签。                                                                                              |
| `<blockquote> … </blockquote>` | 引用内容通常放入此标签。与 `<cite>` 标签配合使用。                                                         |
| `<q> … </q>`                   | 类似于上面的标签，但用于较短的引用。                                                                              |
| `<abbr> … </abbr>`             | 表示缩写及其完整形式。                                                                                              |
| `<address> … </address>`       | 用于指定作者联系方式的标签。                                                                                   |
| `<dfn> … </dfn>`               | 专门用于定义的标签。                                                                                                 |
| `<code> … </code>`             | 用于在段落内显示代码片段。                                                                      |
| `<bdo dir="rtl/ltr"> … </bdo>` | 覆盖文本当前的书写方向，使其中文本以不同方向呈现。                    |

**[🔼Back to Top](#table-of-contents)**

<a id="semantic-elements"></a>

## 语义化元素

> 语义化元素向浏览器和开发者清晰地描述了其含义。

| Command                          | Description                                                                                 |
| -------------------------------- | ------------------------------------------------------------------------------------------- |
| `<article> ... </article>`       | 定义独立、自包含的内容                                                 |
| `<aside> ... </aside>`           | 定义页面内容之外的补充内容                                                 |
| `<details> ... </details>`       | 定义用户可以查看或隐藏的附加细节                                   |
| `<figcaption> ... </figcaption>` | 为 `<figure>` 元素定义标题。                                         |
| `<figure> ... </figure>`         | 指定自包含内容，如插图、图表、照片、代码清单等。 |
| `<footer> ... </footer>`         | 为文档或节定义页脚                                                  |
| `<header> ... </header>`         | 为文档或节指定页眉                                                |
| `<main> ... </main>`             | 指定文档的主要内容                                                    |
| `<nav> ... </nav>`               | 定义导航链接                                                                    |
| `<section> ... </section>`       | 定义文档中的一个节                                                             |
| `<summary> ... </summary>`       | 为 `<details>` 元素定义可见标题                                         |
| `<time> ... </time>`             | 定义日期/时间                                                                         |
| `<pre> ... </pre>`               | 保留空格和换行符                                                         |

**[🔼Back to Top](#table-of-contents)**

<a id="formatting"></a>

## 格式化

> 格式化元素用于显示特殊类型的文本：

| Command                  | Description                                          |
| ------------------------ | ---------------------------------------------------- |
| `<b> ... </b>`           | 定义粗体文本                                    |
| `<em> ... </em>`         | 定义强调文本                              |
| `<i> ... </i>`           | 定义不同语气或语调的文本部分 |
| `<small> ... </small>`   | 定义更小的文本                                 |
| `<strong> ... </strong>` | 定义重要文本                               |
| `<sub> ... </sub>`       | 定义下标文本                             |
| `<sup> ... </sup>`       | 定义上标文本                           |
| `<ins> ... </ins>`       | 定义插入的文本                                |
| `<del> ... </del>`       | 定义删除的文本                                 |
| `<mark> ... </mark>`     | 定义标记/高亮文本                      |

**[🔼Back to Top](#table-of-contents)**

<a id="links"></a>

## 链接

> 链接允许用户在页面间点击浏览。

| Command                         | Description                                                                                                                    |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `<a href=””> … </a>`            | 锚点标签。主要用于包含超链接。                                                                           |
| `<a href=”mailto:”> … </a>`     | 专门用于发送电子邮件的标签。                                                                                               |
| `<a href=”tel:###-###”> … </a>` | 用于注明联系电话号码的锚点标签。由于号码可点击，这对移动用户尤为有用。 |
| `<a name=”name”> … </a>`        | 此标签可用于快速导航到网页的不同部分。                                                   |
| `<a href=”#name”> … </a>`       | 上面标签的变体，仅用于导航到网页的 div 区块。                                  |

**[🔼Back to Top](#table-of-contents)**

<a id="images"></a>

## 图像

> 图像可以改善网页的设计和外观。

| Command                  | Description                                                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `<img />`                | 在网页中显示图像的标签。                                                                                        |
| `src=”url”`              | 图像所在位置的 URL 或路径，位于驱动器或网络上。                                                        |
| `alt=”text”`             | 此处写入的文本在用户将鼠标悬停在图像上时显示。可用于提供图像的额外详情。 |
| `height=””`              | 以像素或百分比指定图像高度。                                                                               |
| `width=””`               | 以像素或百分比指定图像宽度。                                                                                |
| `align=””`               | 图像的相对对齐方式。会随网页中其他元素的变化而改变。                                 |
| `border=””`              | 指定图像的边框粗细。如果未指定，默认为 0。                                                      |
| `<map> … </map>`         | 表示可交互（可点击）的图像。                                                                                      |
| `<map name=””> … </map>` | 图像与地图之间关联的地图名称。                                                                      |
| `<area />`               | 指定图像映射区域。                                                                                                      |
| `shape=””`               | 区域的形状。                                                                                                             |
| `coords=””`              | coords 属性指定图像映射中某个区域的坐标。                                                     |

**[🔼Back to Top](#table-of-contents)**

<a id="lists"></a>

## 列表

> 列表允许 Web 开发者将一组相关项归入列表。

| Command        | Description                                                 |
| -------------- | ----------------------------------------------------------- |
| `<ol> … </ol>` | 有序或编号列表项的标签。                  |
| `<ul> … </ul>` | 与上述标签相反，用于无序列表项。 |
| `<li> … </li>` | 作为列表一部分的单个项。                          |
| `<dl> … </dl>` | 带定义的项列表的标签。                     |
| `<dt> … </dt>` | 与正文内容内联的单个术语定义。   |
| `<dd> … </dd>` | 所定义术语的描述。                       |

**[🔼Back to Top](#table-of-contents)**

<a id="forms"></a>

## 表单

> 表单用于收集用户输入。用户输入通常会被发送到服务器进行处理。

| Command            | Description                                                                      |
| ------------------ | -------------------------------------------------------------------------------- |
| `<form> … </form>` | HTML 表单的父标签。                                                 |
| `action=”url”`     | 此处列出的 URL 是用户填写表单后提交表单数据的位置。 |
| `method=”POST”`        | 它指定将使用哪种 HTTP 方法（POST 或 GET）提交表单。   |
| `accept-charset`   | 它指定用于表单提交的字符编码。                   |
| `autocomplete`        | 它指定表单是否应开启或关闭自动完成。   |
| `enctype`        | 它指定在将表单数据提交到服务器时如何对其进行编码（仅适用于 method="post"）   |
| `name`        | 它指定表单的名称。   |
| `novalidate`        | 它指定提交表单时不应进行验证   |
| `target`        | 它指定提交表单后显示所收到响应的位置  |

| Form Elements           | Description                                                                      |
| ------------------ | -------------------------------------------------------------------------------- |
| `<input>` | 用于接收用户输入，根据 'type' 属性的不同可呈现不同形式。       |
| `<label>`     | 它为多个表单元素定义标签。 |
| `<select>`        | 该元素定义下拉列表  |
| `<textarea>`   | 该元素定义多行输入字段（文本区域）                   |
| `<button>`        | 该元素定义可点击按钮   |

**示例：**

```html
<form method="POST" action="/page">
  <label for="name">Page Name</label>
  <input id="name" type="text" name="page_name" />
  <input type="submit" value="Create" />
</form>
```

**[🔼Back to Top](#table-of-contents)**

<a id="input-Types"></a>

## 输入类型

| Field Type | HTML Code  Notes |
| :---: |----- |
| 纯文本 | `<input type="text">` | 可以省略 type 属性 |
| 密码字段 | `<input type="password">`  | 显示圆点而非字符 |
| 文本区域 | `<textarea></textarea>` |  更可定制的纯文本区域 |
| 复选框 | `<input type="checkbox">` | 可切换开或关 |
| 单选按钮 | `<input type="radio">`  | 可与其他输入分组 |
| 下拉列表 | `<select><option>` | [点击此处了解更多信息](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select) |
| 文件选择器 | `<input type="file">`  | 弹出“打开文件”对话框 |
| 隐藏字段 | `<input type="hidden">`   | 什么都没有！ |
| 提交按钮 | `<input type="submit">`  | 激活表单提交 <br/>(一个 `POST` 请求或 <br/>Javascript 操作) |

**[🔼Back to Top](#table-of-contents)**

<a id="important-attributes"></a>

### 重要属性

**输入标签属性：**

|keyword|description|
|--------|---------|
| `type` | 正在输入的数据的类型（影响浏览器用于显示该元素的“控件”）。|
| `name` | 用于在 HTTP 请求中描述此数据的键。|
| `id` | 其他 HTML 元素、JavaScript 和 CSS 用于在浏览器中访问此元素的唯一标识符。|
| `value` | 分配给元素的默认数据。|
| `placeholder` | 不是默认值，而是 HTML5 新增的有用功能，作为输入的数据“提示”。|
| `disabled` | 一个布尔属性，指示该“控件”不可用于交互。|

**单选按钮或复选框属性：**

|keyword|description|
|--------|---------|
| `checked` | 一个布尔值，指示控件是否默认被选中（否则为 false）。|
| `name` | 此元素所连接的组。对于单选按钮，每个组（或名称）只能选中一个元素。|
| `value` | 如果选中此元素，则为特定组（多元素控件）返回的数据或值。|

**[🔼Back to Top](#table-of-contents)**

## 输入控件

| Command                                       | Description                                                                      |
| -------------------------------------------   | -------------------------------------------------------------------------------- |
| `<input type="email" name=" ">`               | 设置用于输入电子邮件地址的单行文本框。                                  |
| `<input type="url" name=" ">`                 | 设置用于输入 URL 的单行文本框。                                             |
| `<input type="number" name=" ">`              | 设置用于输入数字的单行文本框。                                         |
| `<input type="range" name=" ">`               | 设置用于输入范围数字的单行文本框。                                 |
| `<input type="date" name=" ">`                | 设置带有日历、显示日期的单行文本框。                   |
| `<input type="month" name=" ">`               | 设置带有日历、显示月份的单行文本框。                  |
| `<input type="time" name=" ">`                | 设置带有日历、显示时间的单行文本框。                   |
| `<input type="search" name=" ">`              | 设置用于搜索的单行文本框。                                      |
| `<input type="color" name=" ">`               | 设置用于选取颜色的单行文本框。                                 |

**[🔼Back to Top](#table-of-contents)**

<a id="tables"></a>

## 表格

> 表格允许 Web 开发者将数据排列为行和列。

| Command                    | Description                                                        |
| -------------------------- | ------------------------------------------------------------------ |
| `<table> … </table>`       | 在网页中标记一个表格。                                        |
| `<caption> … </caption>`   | 表格的描述放置在此标签内。                |
| `<thead> … </thead>`       | 指定与表格特定列相关的信息。 |
| `<tbody> … </tbody>`       | 表格的主体，保存数据的地方。                       |
| `<tfoot> … </tfoot>`       | 确定表格的页脚。                                |
| `<tr> … </tr>`             | 表示表格中的单行。                                   |
| `<th> … </th>`             | 表格列的标题值。                        |
| `<td> … </td>`             | 表格的单个单元格。包含实际的值/数据。          |
| `<colgroup> … </colgroup>` | 用于将列组合在一起。                                |
| `<col>`                    | 表示表格中的一列。                                   |

**[🔼Back to Top](#table-of-contents)**

<a id="graphics"></a>

## 图形

| Command                    | Description                                           |
| -------------------------- | ----------------------------------------------------- |
| `<canvas> … </canvas>`     | 用于在网页上使用 javascript 绘制图形。 |
| `<svg> … </svg>`           | 用于定义 XML 格式的矢量图形。  |

**[🔼Back to Top](#table-of-contents)**

<a id="media"></a>

## 媒体

| Command                    | Description                                      |
| -------------------------- | ------------------------------------------------ |
| `<video> … </video>`       | 用于在网页上显示视频。              |
| `<audio> … </audio>`       | 用于在网页上播放音频文件。        |
| `<object>`       | 它在 HTML 文档中定义嵌入对象。 |
| `<iframe>`       | 它有助于直接播放来自 youtube 的视频。                       |

**[🔼Back to Top](#table-of-contents)**
