---
title: CSS 速查表
description: 这里列出了最常用的 css 属性和特性。
created: 2022-10-20
---

<a id="table-of-contents"></a>

## 目录

- [面向开发者的 CSS 速查表](#css-cheatsheet-for-developers)
  - [CSS 属性](#css-properties)
  - [CSS 选择器](#css-selectors)
  - [CSS 伪类](#css-pseudo-classes)
  - [CSS 属性选择器](#css-attribute-selectors)

<a id="css-cheatsheet-for-developers"></a>

# 面向开发者的 CSS 速查表

<a id="css-properties"></a>

## CSS 属性

*语法*：**`property-name : value;`**

**所有属性通用的部分取值**：`inherit / initial / revert / revert-layer / unset`

| 属性名 | 描述 | 取值（以 / 分隔） |
| ------------- | ----------- | ----------------------- |
| `align-content` | 当交叉轴存在多余空间时，对齐弹性容器内各行 | `flex-start / flex-end / center / space-between / space-around / space-evenly / stretch / start / end / baseline / first baseline / last baseline / safe center / unsafe center` |
| `align-items` | 以与 justify-content 相同的方式对齐当前行的弹性项 | `flex-start / flex-end / center / baseline / stretch` |
| `align-self` | 以与 justify-content 相同的方式对齐当前行的弹性项 | `auto / flex-start / flex-end / center / baseline / stretch` |
| `all` | 设置所有属性 | `initial / inherit / unset` |
| `animation` | 所有 animation-* 属性的简写属性 | 语法：`animation-name animation-duration animation-timing-function animation-delay animation-iteration-count animation-direction animation-fill-mode animation-play-state` |
| `animation-delay` | 定义动画何时开始 | `time / %` |
| `animation-direction` | 定义动画在交替循环时是否反向播放 | `normal / reverse / alternate / alternate-reverse` |
| `animation-duration` | 定义动画完成一个周期所需的时间 | `time / %` |
| `animation-fill-mode` | 定义动画未播放时（已结束或存在延迟时）目标元素的样式 | `none / forwards / backwards / both` |
| `animation-iteration-count` | 定义动画应播放的次数 | `number / infinite` |
| `animation-name` | 为 @keyframes 动画指定名称 | `none / keyframes-name` |
| `animation-play-state` | 定义动画是运行还是暂停 | `running / paused` |
| `animation-timing-function` | 定义动画的速度曲线 | `ease / linear / ease-in / ease-out / ease-in-out / cubic-bezier(n,n,n,n)` |
| `backface-visibility` | 定义元素背面朝向用户时是否可见 | `visible / hidden` |
| `background` | 所有 background-* 属性的简写属性 | 语法 `background-color background-image background-position background-size background-repeat background-origin background-clip background-attachment background-blend-mode` |
| `background-attachment` | 设置背景图像随页面其余部分滚动还是固定 | `scroll / fixed / local` |
| `background-blend-mode` | 指定每个背景层（颜色/图像）的混合模式 | `normal / multiply / screen / overlay / darken / lighten / color-dodge / saturation / color / luminosity` |
| `background-clip` | 指定背景（颜色或图像）在元素内延伸的范围 | `border-box / padding-box / content-box` |
| `background-color` | 设置元素的背景颜色 | `color` |
| `background-image` | 为元素设置一个或多张背景图像 | `url(image-path) / none` |
| `background-origin` | 指定背景图像的起启位置 | `padding-box / border-box / content-box` |
| `background-position` | 设置背景图像的起始位置 | `top left / top center / top right / center left / center center / center right / bottom left / bottom center / bottom right / x-axis y-axis / x-axis / y-axis` |
| `background-repeat` | 背景图像的重复方式 | `repeat / repeat-x / repeaty / no-repeat ` |
| `background-size` | 背景图像尺寸 | `length / percentage / auto / cover / contain` |
| `border` | 在一行内设置所有边框属性 | 语法：`top right bottom left` / `top-bottom left-right` / `all-at-once` |
| `border-bottom`| 在一行内设置底边框属性 | 语法：`width style color` |
| `border-bottom-color`| 底部颜色 | `color (RGB, HEX, name) / transparent` |
| `border-bottom-left-radius` | 边框左下角圆角 | `length / percentage` |
| `border-bottom-right-radius` | 边框右下角圆角 | `length / percentage` |
| `border-bottom-style` | 底部边框样式 | `none / hidden / dotted / dashed / solid / double / groove / ridge / inset / outset` |
| `border-bottom-width` | 底部边框宽度 | `length / percentage` |
| `border-collapse` | 合并表格单元格之间的边框 | `collapse / separate` |
| `border-color` | 在一行内设置所有边框颜色属性 | 语法：`top right bottom left` / `top-bottom left-right` / `all-at-once` |
| `border-image` | border-image-* 的简写属性 | 语法：`source slice width outset repeat` |
| `border-image-outset` | 边框图像的外部边距 | `length / number` |
| `border-image-repeat` | 边框图像的重复方式 | `stretch / repeat / round` |
| `border-image-slice` | 切片边框图像 | `number / percentage` |
| `border-image-source` | 边框图像的来源 | `url (path to image) / none` |
| `border-image-width` | 边框图像的宽度 | `length / percentage / number` |
| `border-left` | 在一行内设置左边框属性 | 语法：`width style color` |
| `border-left-color` | 左边框的颜色 | `color (RGB, HEX, name) / transparent` |
| `border-left-style` | 左边框的样式 | `none / hidden / dotted / dashed / solid / double / groove / ridge / inset / outset` |
| `border-left-width` | 左边框的宽度 | `length / percentage` |
| `border-radius` | 在一行内设置所有边框圆角属性 | 语法：`top-left top-right bottom-right bottom-left` / `top-bottom left-right` / `all-at-once` |
| `border-right` | 在一行内设置右边框属性 | 语法：`width style color` |
| `border-right-color` | 右边框的颜色 | `color (RGB, HEX, name) / transparent` |
| `border-right-style` | 右边框的样式 | `none / hidden / dotted / dashed / solid / double / groove / ridge / inset / outset` |
| `border-right-width` | 右边框的宽度 | `length / percentage` |
| `border-spacing` | 单元格之间的间距 | `length / percentage` |
| `border-style` | 在一行内设置所有边框样式属性 | 语法：`top right bottom left` / `top-bottom left-right` / `all-at-once` |
| `border-top` | 在一行内设置顶边框属性 | 语法：`width style color` |
| `border-top-color` | 顶边框的颜色 | `color (RGB, HEX, name) / transparent` |
| `border-top-left-radius` | 边框左上角圆角 | `length / percentage` |
| `border-top-right-radius` | 边框右上角圆角 | `length / percentage` |
| `border-top-style` | 顶边框的样式 | `none / hidden / dotted / dashed / solid / double / groove / ridge / inset / outset` |
| `border-top-width` | 顶边框的宽度 | `length / percentage` |
| `border-width` | 在一行内设置所有边框宽度属性 | 语法：`top right bottom left` / `top-bottom left-right` / `all-at-once` |
| `bottom` | 距离元素底部的距离 | `length / percentage / auto` |
| `box-shadow` | 为盒子添加阴影 | 语法：`h-offset v-offset blur spread color inset` |
| `box-sizing` | 定义如何计算元素的宽度和高度 | `content-box / border-box` |
| `caption-side` | 表格标题的位置 | `top / bottom` |
| `caret-color` | 插入符（光标）的颜色 | `color (RGB, HEX, name) / auto` |
| `clear` | 指定元素哪一侧不允许出现浮动元素 | `none / left / right / both` |
| `clip` | 裁剪区域 | `rect (top right bottom left) / auto` |
| `color` | 文本颜色 | `color (RGB, HEX, name) / transparent` |
| `column-count` | 列数 | `number / auto` |
| `column-fill` | 如何填充列 | `balance / auto` |
| `column-gap` | 列之间的间距 | `length / percentage` |
| `column-rule` | 在一行内设置所有列分隔线属性 | 语法：`width style color` |
| `column-rule-color` | 列分隔线的颜色 | `color (RGB, HEX, name) / transparent` |
| `column-rule-style` | 列分隔线的样式 | `none / hidden / dotted / dashed / solid / double / groove / ridge / inset / outset` |
| `column-rule-width` | 列分隔线的宽度 | `length / percentage` |
| `column-span` | 元素应跨越多少列 | `none / all` |
| `column-width` | 列的宽度 | `length / percentage` |
| `columns` | 在一行内设置所有列属性 | 语法：`column-width column-count` |
| `content` | 与 ::before 和 ::after 伪元素一起使用，以插入生成的内容 | `string / url (path to image) / none` |
| `counter-increment` | 增加或减少一个或多个 CSS 计数器的值 | `counter-name value` |
| `counter-reset` | 重置一个或多个 CSS 计数器 | `counter-name value` |
| `cursor` | 指定悬停在元素上时显示的鼠标光标 | `auto / default / none / context-menu / help / pointer / progress / wait / cell / crosshair / text / vertical-text / alias / copy / move / no-drop / not-allowed / e-resize / n-resize / ne-resize / nw-resize / s-resize / se-resize / sw-resize / w-resize / ew-resize / ns-resize / nesw-resize / nwse-resize / col-resize / row-resize / all-scroll / zoom-in / zoom-out / grab / grabbing` |
| `direction` | 指定文本方向/书写方向 | `ltr / rtl` |
| `display` | 指定某个 HTML 元素应如何显示 | `none / inline / block / inline-block / list-item / run-in / compact / marker / table / inline-table / table-row-group / table-header-group / table-footer-group / table-row / table-column-group / table-column / table-cell / table-caption / ruby / ruby-base / ruby-text / ruby-base-container / ruby-text-container / contents / flow / flow-root / table / flex / inline-flex / grid / inline-grid / ruby-base-group / ruby-text-group` |
| `empty-cells` | 指定是否在空表格单元格上显示边框和背景 | `show / hide` |
| `filter` | 在元素显示前对其应用效果（例如模糊或颜色偏移） | `none / url (path to SVG filter) / blur (length) / brightness (percentage) / contrast (percentage) / drop-shadow (h-offset v-offset blur spread color) / grayscale (percentage) / hue-rotate (angle) / invert (percentage) / opacity (percentage) / saturate (percentage) / sepia (percentage)` |
| `flex` | 在一行内设置所有弹性属性 | 语法：`flex-grow flex-shrink flex-basis` |
| `flex-basis` | 指定弹性项的初始长度 | `length / auto` |
| `flex-direction` | 指定弹性项的方向 | `row / row-reverse / column / column-reverse` |
| `flex-flow` | 在一行内设置所有弹性流属性 | 语法：`flex-direction flex-wrap` |
| `flex-grow` | 指定项相对于其余项的增长比例 | `number` |
| `flex-shrink` | 指定项相对于其余项的收缩比例 | `number` |
| `flex-wrap` | 指定弹性项是否应换行 | `nowrap / wrap / wrap-reverse` |
| `float` | 指定盒子是否浮动 | `left / right / none` |
| `font` | 在一行内设置所有字体属性 | 语法：`font-style font-variant font-weight font-size/line-height font-family` |
| `font-family` | 指定文本的字体族 | `font-name / generic-family` |
| `font-feature-settings` | 控制 OpenType 字体中的高级排版特性 | `normal / string` |
| `font-kerning` | 控制字距信息的使用 | `auto / normal / none` |
| `font-language-override` | 控制字体中特定语言字形（glyph）的使用 | `normal / string` |
| `font-size` | 指定文本的字体大小 | `length / percentage / xx-small / x-small / small / medium / large / x-large / xx-large / smaller / larger` |
| `font-size-adjust` | 在字体回退发生时保持文本的可读性 | `none / number` |
| `font-stretch` | 从字体族中选择正常的、压缩的或扩展的字形 | `normal / ultra-condensed / extra-condensed / condensed / semi-condensed / semi-expanded / expanded / extra-expanded / ultra-expanded` |
| `font-style` | 指定文本的字体样式 | `normal / italic / oblique` |
| `font-synthesis` | 控制浏览器可以合成哪些缺失的字体（粗体或斜体） | `none / weight / style / weight style` |
| `font-variant` | 指定文本是否以小写大写字母（small-caps）字体显示 | `normal / small-caps / all-small-caps / petite-caps / all-petite-caps / unicase / titling-caps` |
| `font-variant-alternates` | 控制在 @font-feature-values 中定义的替代名称关联备用字形的使用 | `normal / string` |
| `font-variant-caps` | 控制大写字母备用字形的使用 | `normal / small-caps / all-small-caps / petite-caps / all-petite-caps / unicase / titling-caps` |
| `font-variant-east-asian` | 控制东亚文字备用字形的使用 | `normal / string` |
| `font-variant-ligatures` | 控制所应用元素文本内容中使用的连字和上下文形式 | `normal / none / string` |
| `font-variant-numeric` | 控制数字、分数和序数标记备用字形的使用 | `normal / ordinal / slashed-zero / lining-nums / oldstyle-nums / proportional-nums / tabular-nums / diagonal-fractions / stacked-fractions` |
| `font-variant-position` | 控制相对于字体基线以上标或下标形式定位的较小尺寸备用字形 | `normal / sub / super` |
| `font-weight` | 指定字体的粗细 | `normal / bold / bolder / lighter / 100 / 200 / 300 / 400 / 500 / 600 / 700 / 800 / 900` |
| `grid` | 在一行内设置所有网格属性 | 语法：`grid-template-rows grid-template-columns grid-template-areas grid-auto-rows grid-auto-columns grid-auto-flow grid-column-gap grid-row-gap` |
| `grid-area` | 为网格项指定名称 | `grid-row-start / grid-column-start / grid-row-end / grid-column-end` |
| `grid-auto-columns` | 指定隐式创建的列轨道的大小 | `length / percentage / auto` |
| `grid-auto-flow` | 指定自动放置的项如何插入网格 | `row / column / row dense / column dense` |
| `grid-auto-rows` | 指定隐式创建的行轨道的大小 | `length / percentage / auto` |
| `grid-column` | 通过引用特定网格线，指定网格项在网格列中的大小和位置 | `grid-column-start / grid-column-end` |
| `grid-column-end` | 指定网格项的结束位置 | `grid-column-line` |
| `grid-column-gap` | 指定列之间的间距大小 | `length / percentage` |
| `grid-column-start` | 指定网格项的起始位置 | `grid-column-line` |
| `grid-gap` | 设置行和列之间的间距 | 语法：`grid-row-gap grid-column-gap` |
| `grid-row` | 通过引用特定网格线，指定网格项在网格行中的大小和位置 | `grid-row-start / grid-row-end` |
| `grid-row-end` | 指定网格项的结束位置 | `grid-row-line` |
| `grid-row-gap` | 指定行之间的间距大小 | `length / percentage` |
| `grid-row-start` | 指定网格项的起始位置 | `grid-row-line` |
| `grid-template` | 在一行内设置所有网格模板属性 | 语法：`grid-template-rows grid-template-columns grid-template-areas` |
| `grid-template-areas` | 使用命名网格项指定如何显示列和行 | `none / string` |
| `grid-template-columns` | 指定列的大小以及网格布局中的列数 | `none / track-list` |
| `grid-template-rows` | 指定网格布局中行的大小 | `none / track-list` |
| `height` | 设置元素的高度 | `length / percentage / auto` |
| `hyphens` | 指定如何拆分单词以改善段落排版 | `none / manual / auto` |
| `image-orientation` | 指定图像的方向 | `angle / from-image` |
| `image-rendering` | 提示浏览器在缩放图像时最应保留图像的哪些方面 | `auto / optimizeSpeed / optimizeQuality` |
| `image-resolution` | 指定栅格图像的预期分辨率 | `from-image / resolution` |
| `ime-mode` | 指定文本字段的输入法编辑器状态 | `auto / normal / active / inactive / disabled` |
| `initial-letter` | 指定首字母下沉、上浮和嵌入的样式 | `normal / number / length / percentage` |
| `initial-letter-align` | 指定首字母的对齐方式 | `auto / alphabetic / hanging / ideographic / mathematical` |
| `initial-letter-wrap` | 指定首字母是否可以换到下一行 | `normal / first / all` |
| `inline-size` | 根据 writing-mode 属性的值设置行内盒子的宽度或高度 | `length / percentage / auto` |
| `justify-content` | 当项未使用全部可用空间时，指定弹性容器内各项之间的对齐 | `flex-start / flex-end / center / space-between / space-around / space-evenly / start / end / left / right` |
| `justify-items` | 指定弹性容器内项的对齐 | `auto / normal / stretch / start / end / center / self-start / self-end / left / right / baseline / first baseline / last baseline / safe center / unsafe center` |
| `justify-self` | 指定弹性容器内所选的对齐项 | `auto / normal / stretch / start / end / center / self-start / self-end / left / right / baseline / first baseline / last baseline / safe center / unsafe center` |
| `left` | 指定已定位元素的左侧位置 | `length / percentage / auto` |
| `letter-spacing` | 增加或减少文本中字符之间的间距 | `normal / length` |
| `line-break` | 指定是否/如何换行 | `auto / loose / normal / strict / anywhere` |
| `line-height` | 指定行高 | `normal / number / length / percentage` |
| `list-style` | 在一个声明中设置列表的所有属性 | 语法：`list-style-type list-style-position list-style-image` |
| `list-style-image` | 指定作为列表项标记的图像 | `none / url` |
| `list-style-position` | 指定列表项标记（项目符号）的位置 | `inside / outside` |
| `list-style-type` | 指定列表项标记的类型 | `none / disc / circle / square / decimal / decimal-leading-zero / lower-roman / upper-roman / lower-greek / lower-latin / upper-latin / armenian / georgian / lower-alpha / upper-alpha / hebrew / cjk-ideographic / hiragana / hiragana-iroha / katakana / katakana-iroha` |
| `margin` | 在一个声明中设置所有外边距属性 | 语法：`margin-top margin-right margin-bottom margin-left` |
| `margin-block-end` | 设置元素底部的外边距 | `length / percentage / auto` |
| `margin-block-start` | 设置元素顶部的外边距 | `length / percentage / auto` |
| `margin-bottom` | 设置元素的下外边距 | `length / percentage / auto` |
| `margin-inline-end` | 设置元素右侧的外边距 | `length / percentage / auto` |
| `margin-inline-start` | 设置元素左侧的外边距 | `length / percentage / auto` |
| `margin-left` | 设置元素的左外边距 | `length / percentage / auto` |
| `margin-right` | 设置元素的右外边距 | `length / percentage / auto` |
| `margin-top` | 设置元素的上外边距 | `length / percentage / auto` |
| `max-height` | 设置元素的最大高度 | `length / percentage / none` |
| `max-inline-size` | 根据 writing-mode 属性的值设置行内盒子的最大宽度或高度 | `length / percentage / none` |
| `max-width` | 设置元素的最大宽度 | `length / percentage / none` |
| `min-block-size` | 根据 writing-mode 属性的值设置元素的最小高度或宽度 | `length / percentage` |
| `min-height` | 设置元素的最小高度 | `length / percentage` |
| `min-inline-size` | 根据 writing-mode 属性的值设置元素的最小宽度或高度 | `length / percentage` |
| `min-width` | 设置元素的最小宽度 | `length / percentage` |
| `mix-blend-mode` | 指定元素内容应如何与其直接父级背景混合 | `normal / multiply / screen / overlay / darken / lighten / color-dodge / saturation / color / luminosity` |
| `object-fit` | 指定被替换元素的内容应如何适配其使用的高度和宽度所建立的盒子 | `fill / contain / cover / none / scale-down` |
| `object-position` | 指定被替换元素在其盒子内的对齐 | `x-axis y-axis / x-axis / y-axis / center` |
| `offset` | 在一个声明中设置所有偏移属性 | 语法：`offset-path offset-distance offset-rotate offset-anchor` |
| `offset-anchor` | 指定元素偏移原点的位置 | `auto / x-axis y-axis / x-axis / y-axis / center` |
| `offset-distance` | 指定元素偏移原点与其偏移路径之间的距离 | `length / percentage / auto` |
| `offset-path` | 指定元素应遵循的路径 | `none / path() / <basic-shape> / <geometry-box>` |
| `offset-position` | 在一个声明中设置所有 offset-position 属性 | 语法：`offset-path offset-distance offset-rotate` |
| `offset-rotate` | 指定元素应沿偏移路径如何旋转 | `auto / angle / reverse` |
| `opacity` | 设置元素的透明度级别 | `number` |
| `order` | 指定弹性项相对于其余项的顺序 | `integer` |
| `orphans` | 指定在元素内发生分页时，页面底部必须保留的最小行数 | `integer` |
| `outline` | 在一个声明中设置所有轮廓属性 | 语法：`outline-width outline-style outline-color` |
| `outline-color` | 设置轮廓的颜色 | `color` |
| `outline-offset` | 偏移轮廓，并将其绘制在边框边缘之外 | `length` |
| `outline-style` | 设置轮廓的样式 | `none / hidden / dotted / dashed / solid / double / groove / ridge / inset / outset` |
| `outline-width` | 设置轮廓的宽度 | `thin / medium / thick / length` |
| `overflow` | 指定内容溢出元素盒子时发生的情况 | `visible / hidden / scroll / auto / overlay / clip` |
| `overflow-wrap` | 指定浏览器是否可在单词内换行以防止溢出（当字符串过长无法容纳其所在盒子时） | `normal / break-word / anywhere` |
| `overflow-x` | 指定内容溢出元素内容区域时，是否裁剪其左/右边缘 | `visible / hidden / scroll / auto / overlay / clip` |
| `overflow-y` | 指定内容溢出元素内容区域时，是否裁剪其上/下边缘 | `visible / hidden / scroll / auto / overlay / clip` |
| `padding` | 在一个声明中设置所有内边距属性 | 语法：`padding-top padding-right padding-bottom padding-left` |
| `padding-block-end` | 设置元素底部的填充 | `length / percentage` |
| `padding-block-start` | 设置元素顶部的填充 | `length / percentage` |
| `padding-bottom` | 设置元素的下内边距 | `length / percentage` |
| `padding-inline-end` | 设置元素右侧的填充 | `length / percentage` |
| `padding-inline-start` | 设置元素左侧的填充 | `length / percentage` |
| `padding-left` | 设置元素的左内边距 | `length / percentage` |
| `padding-right` | 设置元素的右内边距 | `length / percentage` |
| `padding-top` | 设置元素的上内边距 | `length / percentage` |
| `page-break-after` | 指定元素之后的分页行为 | `auto / always / avoid / left / right` |
| `page-break-before` | 指定元素之前的分页行为 | `auto / always / avoid / left / right` |
| `page-break-inside` | 指定元素内的分页行为 | `auto / avoid` |
| `perspective` | 为 3D 定位元素提供一些透视效果 | `none / length` |
| `perspective-origin` | 定义用户查看 3D 定位元素的位置 | `x-axis y-axis / x-axis / y-axis / center` |
| `place-content` | 在一个声明中设置 align-content 和 justify-content 属性 | 语法：`align-content justify-content` |
| `place-items` | 在一个声明中设置 align-items 和 justify-items 属性 | 语法：`align-items justify-items` |
| `place-self` | 在一个声明中设置 align-self 和 justify-self 属性 | 语法：`align-self justify-self` |
| `pointer-events` | 定义元素是否响应指针事件 | `auto / none / visiblePainted / visibleFill / visibleStroke / visible / painted / fill / stroke / all` |
| `position` | 指定元素使用的定位方法类型（static、relative、absolute 或 fixed） | `static / relative / absolute / fixed / sticky` |
| `quotes` | 指定引号的外观 | `none / string string string string` |
| `resize` | 指定元素是否可由用户调整大小 | `none / both / horizontal / vertical / block / inline` |
| `right` | 指定已定位元素的右侧位置 | `length / percentage / auto` |
| `row-gap` | 设置元素网格行之间的间距大小 | `length / percentage` |
| `scroll-behavior` | 指定是否平滑地动画滚动位置，而不是直接跳转 | `auto / smooth` |
| `tab-size` | 指定制表符的宽度 | `number / length` |
| `table-layout` | 指定用于布局表格单元格、行和列的算法 | `auto / fixed` |
| `text-align` | 指定文本的水平对齐 | `left / right / center / justify / justify-all / start / end / match-parent` |
| `text-align-last` | 指定块元素最后一行的对齐 | `auto / left / right / center / justify / start / end` |
| `text-combine-upright` | 指定如何将多个字符组合到单个字符的空间内 | `none / all / digits` |
| `text-decoration` | 在一个声明中设置所有 text-decoration 属性 | 语法：`text-decoration-line text-decoration-color text-decoration-style text-decoration-thickness` |
| `text-decoration-color` | 指定文本装饰的颜色 | `color` |
| `text-decoration-line` | 指定文本装饰中线的类型 | `none / underline / overline / line-through / blink` |
| `text-decoration-skip` | 指定应用任何文本装饰时跳过元素内容的哪些部分 | `none / objects / spaces / ink` |
| `text-decoration-style` | 指定文本装饰中线的样式 | `solid / double / dotted / dashed / wavy` |
| `text-decoration-thickness` | 指定文本装饰中线的粗细 | `auto / from-font / length` |
| `text-indent` | 指定文本块第一行的缩进 | `length / percentage` |
| `text-orientation` | 指定一行中文本的方向 | `mixed / upright / sideways / sideways-right / sideways-left / use-glyph-orientation` |
| `text-overflow` | 指定文本溢出包含元素时发生的情况 | `clip / ellipsis` |
| `text-rendering` | 精细控制用于渲染文本的算法 | `auto / optimizeSpeed / optimizeLegibility / geometricPrecision` |
| `text-shadow` | 为文本添加阴影 | `none / h-shadow v-shadow blur color` |
| `text-transform` | 控制文本的大小写 | `none / capitalize / uppercase / lowercase / full-width / full-size-kana` |
| `text-underline-offset` | 指定使用 text-decoration 属性设置的下划线的位置 | `auto / length` |
| `text-underline-position` | 指定使用 text-decoration 属性设置的下划线的位置 | `auto / under / left / right` |
| `top` | 指定已定位元素的顶部位置 | `length / percentage / auto` |
| `touch-action` | 指定特定区域是否以及如何由用户操作 | `auto / none / pan-x / pan-left / pan-right / pan-y / pan-up / pan-down / pinch-zoom` |
| `transform` | 对元素应用 2D 或 3D 变换 | `none / matrix() / matrix3d() / perspective() / rotate() / rotate3d() / rotateX() / rotateY() / rotateZ() / scale() / scale3d() / scaleX() / scaleY() / scaleZ() / skew() / skewX() / skewY() / translate() / translate3d() / translateX() / translateY() / translateZ()` |
| `transform-box` | 定义 transform-origin 属性适用的盒子 | `border-box / fill-box / view-box` |
| `transform-origin` | 允许你更改变换元素上的位置 | `x-axis y-axis z-axis / x-axis y-axis / x-axis / y-axis / z-axis / left / center / right / top / bottom` |
| `transform-style` | 指定嵌套元素在 3D 空间中如何渲染 | `flat / preserve-3d` |
| `transition` | 所有 transition-* 属性的简写属性 | 语法：`transition-property transition-duration transition-timing-function transition-delay` |
| `transition-delay` | 指定过渡效果何时开始 | `time` |
| `transition-duration` | 指定过渡效果完成所需的秒数或毫秒数 | `time` |
| `transition-property` | 指定过渡效果作用的 CSS 属性名称 | `none / all / property` |
| `transition-timing-function` | 指定过渡效果的速度曲线 | `ease / ease-in / ease-out / ease-in-out / linear / step-start / step-end / steps() / cubic-bezier()` |
| `unicode-bidi` | 与 direction 属性一起使用，设置或返回文本是否应被覆盖以支持同一文档中的多种语言 | `normal / embed / bidi-override` |
| `user-select` | 指定元素文本是否可被选择 | `auto / none / text / all / contain` |
| `vertical-align` | 设置元素的垂直对齐 | `baseline / sub / super / top / text-top / middle / bottom / text-bottom / length / percentage` |
| `visibility` | 指定元素是否可见 | `visible / hidden / collapse` |
| `white-space` | 指定如何处理元素内的空白 | `normal / pre / nowrap / pre-wrap / pre-line / break-spaces` |
| `width` | 设置元素的宽度 | `length / percentage / auto` |
| `will-change` | 指示在元素实际改变之前会发生什么改变 | `auto / contents / scroll-position / transform` |
| `word-break` | 指定到达行尾时单词应如何断行 | `normal / break-all / keep-all / break-word` |
| `word-spacing` | 增加或减少文本中单词之间的间距 | `normal / length` |
| `word-wrap` | 指定浏览器是否可在单词内换行以防止溢出（当字符串过长无法容纳其所在盒子时） | `normal / break-word` |
| `writing-mode` | 指定文本行是水平还是垂直排列，以及文本行和块的前进方向 | `horizontal-tb / vertical-rl / vertical-lr / sideways-rl / sideways-lr` |
| `z-index` | 指定元素的堆叠顺序 | `auto / number` |

**[🔼Back to Top](#table-of-contents)**

<a id="css-selectors"></a>

## CSS 选择器

| 命令             | 描述                                 |
| ---------------- | ----------------------------------- |
| `*`              | 所有元素                            |
| `div`            | 所有 'div' 标签                     |
| `div.p`          | 所有 'div' 和 'p' 段落              |
| `div p`          | div 内部的段落                     |
| `div > p`        | 'div' 中一级深度的 'p' 标签         |
| `div + p`        | div 之后紧邻的 p 标签               |
| `div ~ p`        | 前面带有 div 的 p 标签              |
| `.class-name`    | 所有带该类的元素                    |
| `#id-name`       | 带有 'id' 的元素                    |
| `div.class-name` | 带有特定类名的 div                  |
| `div#id-name`    | 带有特定 'id' 的 div               |
| `#id-name`       | 该 #id-name 内部的所有元素          |

**[🔼Back to Top](#table-of-contents)**

<a id="css-pseudo-classes"></a>

## CSS 伪类

| 命令                   | 描述                          |
| ------------------------- | ---------------------------- |
| `a:link`                  | 正常状态下的链接              |
| `a:active`                | 被点击状态下的链接            |
| `a:hover`                 | 鼠标悬停其上的链接            |
| `a:visited`               | 已访问的链接                  |
| `p::after{content:"yo"/}` | 在 p 之后添加内容             |
| `p::before`               | 在 p 之前添加内容             |
| `input:checked`           | 被选中的输入                  |
| `input:disabled`          | 被禁用的输入                  |
| `input:enabled`           | 已启用的输入                  |
| `input:focus`             | 获得焦点的输入                |
| `input:in-range`          | 值在范围内的输入              |
| `input:out-of-range`      | 值超出范围的输入              |
| `input:valid`             | 值有效的输入                  |
| `input:invalid`           | 值无效的输入                  |
| `input:optional`          | 没有 required 属性的输入      |
| `input:required`          | 带有 required 属性的输入      |
| `input:read-only`         | 带有 readonly 属性的输入      |
| `input:read-write`        | 没有 readonly 属性的输入      |
| `div:empty`               | 没有子元素的元素              |
| `p::first-letter`         | p 中的第一个字母              |
| `p::first-line`           | p 中的第一行                  |
| `p:first-of-type`         | 某类型的第一个                |
| `p:last-of-type`          | 某类型的最后一个              |
| `p:lang(en)`              | 带 en 语言属性的 p            |
| `:not(span)`              | 不是 span 的元素              |
| `p:first-child`           | 其父元素的第一个子元素        |
| `p:last-child`            | 其父元素的最后一个子元素      |
| `p:nth-child(2)`          | 其父元素的第二个子元素        |
| `p:nth-child(3n+1)`       | nth-child（an + b）公式       |
| `p:nth-last-child(2)`     | 从末尾数的第二个子元素        |
| `p:nth-of-type(2)`        | 其父元素的第二个 p            |
| `p:nth-last-of-type(2)`   | ……从末尾数                    |
| `p:only-of-type`          | 其父元素中唯一的一个          |
| `p:only-child`            | 其父元素的唯一子元素          |
| `:root`                   | 文档的根元素                  |
| `::selection`             | 用户选择的部分                |
| `:target`                 | 高亮当前活动的锚点            |

**[🔼Back to Top](#table-of-contents)**

<a id="css-attribute-selectors"></a>

## CSS 属性选择器

| 命令                | 描述                              |
| ---------------------- | -------------------------------- |
| `a[target]`            | 带有 target 属性的链接           |
| `a[target="_blank"]`   | 在新标签页打开的链接             |
| `[title~="chair"]`     | 包含某个单词的 title 元素        |
| `[class^="chair"]`     | 类名以 chair 开头的元素          |
| `[class="chair"]`      | 类名以 chair 单词开头的元素      |
| `[class*="chair"]`     | 类名包含 chair 的元素            |
| `[class$="chair"]`     | 类名以 chair 结尾的元素          |
| `input[type="button"]` | 指定类型的输入                  |

**[🔼Back to Top](#table-of-contents)**
