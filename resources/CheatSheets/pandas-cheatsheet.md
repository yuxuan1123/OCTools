---
title: Pandas 速查表
description: 这里列出了最常用的 pandas 命令。
created: 2022-10-24
---

<a id="table-of-contents"></a>
## 目录

- [面向开发者的 Pandas 速查表](#pandas-cheatsheet-for-developers)
  - [简介——什么是 Pandas？](#introduction-what-is-pandas)
  - [关键符号与导入](#key-and-imports)
  - [导入数据](#importing-data)
  - [导出数据](#exporting-data)
  - [创建测试对象](#create-test-objects)
  - [查看/检查数据](#viewinginspecting-data)
  - [选择数据](#selection)
  - [数据清洗](#data-cleaning)
  - [筛选、排序与分组](#filter-sort-and-groupby)
  - [连接/合并](#joincombine)
  - [统计](#statistics)
  - [使用 DataFrame 进行数据可视化](#data-visualization-with-dataframe)
    - [术语与定义](#terminology-and-definitions)
    - [绘图类型](#type-of-plots)


<a id="pandas-cheatsheet-for-developers"></a>
# 面向开发者的 Pandas 速查表

<a id="introduction-what-is-pandas"></a>
## 简介——什么是 Pandas？

> Pandas 可以被视为 **数据科学** 中 **最重要的 Python** 包。它提供了大量函数，让数据处理变得更加轻松。其 **快速、灵活且富有表现力的数据结构** 旨在使真实世界的数据分析成为可能。
> Pandas 速查表是一份快速指南，涵盖了使用 Python 处理数据所需掌握的 Pandas 基础。如果你想开启基于 Pandas 的数据科学之旅，可以将其作为便捷参考，轻松处理数据。

本速查表将引导你了解 Pandas 库的基础内容，从数据结构到 I/O、选择、排序与排名等。

**[🔼Back to Top](#table-of-contents)**

<a id="key-and-imports"></a>
## 关键符号与导入

> 我们在速查表中使用以下简写：

|Command | description|
|----------|-------------|
|`pd`|导入 pandas 库| 
|`df` | 指代任意 Pandas DataFrame 对象。|
|`s` | 指代任意 Pandas Series 对象。|

> 你可以使用以下导入语句开始：

**[🔼Back to Top](#table-of-contents)**

<a id="importing-data"></a>
## 导入数据

|Command | description|
|---------|-------------|
|`pd.read_csv(filename)` | 从 CSV 文件读取数据。|
|`pd.read_table(filename)` | 从带分隔符的文本文件读取数据。|
|`pd.read_excel(filename)` | 从 Excel 文件读取数据。|
|`pd.read_sql(query,connection _object)`| 从 SQL 表/数据库读取数据。|
|`pd.read_json(json _string)` | 从 JSON 格式的字符串、URL 或文件读取数据。|
|`pd.read_html(url)` | 解析 HTML 格式的 URL、字符串或文件，并将表格提取为 DataFrame 列表。|
|`pd.read_clipboard()` | 获取剪贴板内容并传递给 read_table() 函数。|
|`pd.DataFrame(dict)` | 从字典创建，键作为列名，值作为列表形式的数据。|

**[🔼Back to Top](#table-of-contents)**

<a id="exporting-data"></a>
## 导出数据

|Command | description|
|-------------|----------|
|`df.to_csv(filename)`| 写入 CSV 文件。|
|`df.to_excel(filename)`| 写入 Excel 文件。|
|`df.to_sql(table_name, connection_object)`| 写入 SQL 表。|
|`df.to_json(filename)` | 以 JSON 格式写入文件。|

**[🔼Back to Top](#table-of-contents)**

<a id="create-test-objects"></a>
## 创建测试对象

> 它对于测试代码片段很有用。

|Command | description|
|-------------|----------|
|`pd.DataFrame(np.random.rand(7,18))`| 指代 18 列、7 行的随机浮点数。|
|`pd.Series(my_list)`| 从可迭代对象 my_list 创建一个 Series。|
|`df.index= pd.date_range('1940/1/20', periods=df.shape[0])`|添加日期索引。|

**[🔼Back to Top](#table-of-contents)**

<a id="viewinginspecting-data"></a>
## 查看/检查数据

|Command | description|
|-------------|----------|
|`df.head(n)`| 返回 DataFrame 的前 n 行，默认返回前 5 行。|
|`df.tail(n)` | 返回 DataFrame 的后 n 行，默认返回后 5 行。|
|`df.shape` | 返回行数和列数。|
|`df.info()`| 返回索引、数据类型和内存信息。|
|`s.value_counts(dropna=False)`| 查看唯一值及其计数。|
|`df.apply(pd.Series.value_counts)`| 指代所有列的唯一值及其计数。|

**[🔼Back to Top](#table-of-contents)**

<a id="selection"></a>
## 选择数据

|Command | description|
|-------------|----------|
|`df[col1]` | 返回标签为 col 的列（以 Series 形式）。|
|`df[[col1, col2]]`| 以新 DataFrame 形式返回多列。|
|`s.iloc[0]` | 按位置选择。|
|`s.loc['index_one']` | 按索引选择。|
|`df.iloc[0,:]`| 返回第一行。|
|`df.iloc[0,0]` | 返回第一列的第一个元素。|

**[🔼Back to Top](#table-of-contents)**

<a id="data-cleaning"></a>
## 数据清洗

|Command | description|
|-------------|----------|
|`df.columns` = ['a','b','c'] | 重命名列。|
|`pd.isnull()` | 检查空值并返回布尔数组。|
|`pd.notnull()` | 与 pd.isnull() 相反。|
|`df.dropna()`|删除所有包含空值的行。|
|`df.dropna(axis= 1)`| 删除所有包含空值的列。|
|`df.dropna(axis=1,thresh=n)`| 删除非空值少于 n 的所有行。|
|`df.fillna(x)`| 用 x 替换所有空值。|
|`s.fillna(s.mean())`| 用均值替换所有空值（均值可替换为统计模块中几乎任意函数）。|
|`s.astype(float)`| 将 Series 的数据类型转换为 float。|
|`s.replace(1, 'one')`| 将所有等于 1 的值替换为 'one'。|
|`s.replace([1,3],[ 'one', 'three'])`|将所有 1 替换为 'one'，所有 3 替换为 'three'。|
|`df.rename(columns=lambda x: x+1)`|批量重命名列。|
|`df.rename(columns={'old_name': 'new_ name'})`| 进行选择性重命名。|
|`df.set_index('column_one')`| 用于更改索引。|
|`df.rename(index=lambda x: x+1)`| 批量重命名索引。|

**[🔼Back to Top](#table-of-contents)**

<a id="filter-sort-and-groupby"></a>
## 筛选、排序与分组

|Command | description|
|-------------|----------|
|`df[df[col] > 0.5]` | 返回 col 列大于 0.5 的行|
|`df[(df[col] > 0.5) & (df[col] < 0.7)]`| 返回 0.7 > col > 0.5 的行|
|`df.sort_values(col1)` | 按 col1 升序排序。|
|`df.sort_values(col2,ascending=False)` | 按 col2 降序排序。|
|`df.sort_values([col1,col2],ascending=[True,False])` | 按 col1 升序、col2 降序排序。|
|`df.groupby(col1)`| 返回按单列值分组的 groupby 对象。|
|`df.groupby([col1,col2])`| 返回按多列值分组的 groupby 对象。|
|`df.groupby(col1)[col2])` | 返回按 col1 分组后 col2 的均值。|
|`df.pivot_table(index=col1,values=[col2,col3],aggfunc=mean)` | 创建透视表，按 col1 分组并计算 col2、col3 的均值。|
|`df.groupby(col1).agg(np.mean`)` | 为每个唯一的 col1 分组计算所有列的平均值。|
|`df.apply(np.mean)` | 其任务是在每列上应用函数 np.mean()。|
|`nf.apply(np.max,axis=1)`|其任务是在每行上应用函数 np.max()。|

**[🔼Back to Top](#table-of-contents)**

<a id="joincombine"></a>
## 连接/合并

|Command | description|
|-------------|----------|
|`df1.append(df2)`| 其任务是将 df1 的行添加到 df2 末尾（列应完全相同）。|
|`pd.concat([df1, df2], axis=1)`| 其任务是将 df1 的列添加到 df2 末尾（行应完全相同）。|
|`df1.join(df2,on=col1,how='inner')`| 以 SQL 风格将 df1 的列与 df2 的列连接，其中 col 行的值相同；'how' 可为 'left'、'right'、'outer'、'inner'。|

**[🔼Back to Top](#table-of-contents)**

<a id="statistics"></a>
## 统计

> 统计函数可应用于 Series，如下所示：

|Command | description|
|-------------|----------|
|`df.describe()`| 返回数值列的汇总统计信息。|
|`df.mean()` | 返回所有列的均值。|
|`df.corr()` | 返回 DataFrame 中各列之间的相关性。|
|`df.count()`| 返回每个 DataFrame 列中所有非空值的计数。|
|`df.max()`| 返回每列的最大值。|
|`df.min()`| 返回每列的最小值。|
|`df.median()`| 返回每列的中位数。|
|`df.std()`| 返回每列的标准差。|

**[🔼Back to Top](#table-of-contents)**

<a id="data-visualization-with-dataframe"></a>
## 使用 DataFrame 进行数据可视化

<a id="terminology-and-definitions"></a>
### 术语与定义

|data| DataFrame|
|--------|------|
|`x`| 标签或位置，默认 None|
|`y` | 标签、位置或标签列表、位置列表，默认 None，允许一列对另一列绘图|
|`ax `| matplotlib 轴对象，默认 None|
|`subplots`| 布尔值，默认 False，为每列创建独立的子图|
|`sharex `| 布尔值，默认 True（若 ax 为 None），否则为 False。注意，同时传入 ax 和 sharex=True 会更改图中所有轴的 x 轴标签！|
|`sharey`| 布尔值，默认 False。当 subplots=True 时，共享 y 轴并将部分 y 轴标签设为不可见|
|`layout`|元组（可选），子图布局的（行，列）|
|`figsize`| 以英寸为单位的元组（宽度，高度）|
|`use_index `| 布尔值，默认 True。使用索引作为 x 轴的刻度|
|`title `| 字符串或列表。绘图使用的标题。若传入字符串，在图顶部打印该字符串；若传入列表且 subplots 为 True，在对应子图上方打印列表中的每一项。|
|`grid `| 布尔值，默认 None（matlab 风格默认值）。坐标轴网格线|
|`legend`| False/True/’reverse’。在轴子图上放置图例|
|`style `| 列表或字典。每列的 Matplotlib 线型|
|`logx `| 布尔值，默认 False。在 x 轴使用对数缩放|
|`logy `| 布尔值，默认 False。在 y 轴使用对数缩放|
|`loglog `| 布尔值，默认 False。在 x 和 y 轴均使用对数缩放|
|`xticks `| 序列。用于 xticks 的值|
|`yticks `| 序列。用于 yticks 的值|
|`xlim `| 2 元组/列表|
|`ylim `| 2 元组/列表|
|`rot `| 整数，默认 None。刻度的旋转角度（垂直图为 xticks，水平图为 yticks）|
|`fontsize `| 整数，默认 None。xticks 和 yticks 的字体大小|
|`colormap `| 字符串或 matplotlib 颜色映射对象，默认 None。从中选择颜色的颜色映射。若为字符串，则按该名称从 matplotlib 加载颜色映射。|
|`colorbar `| 布尔值，可选。若为 True，绘制颜色条（仅与 ‘scatter’ 和 ‘hexbin’ 图相关）|
|`position `| 浮点数。为条形图布局指定相对对齐方式。从 0（左/底侧）到 1（右/顶侧）。默认 0.5（居中）|
|`table `| 布尔值、Series 或 DataFrame，默认 False。若为 True，使用 DataFrame 中的数据绘制表格，数据将被转置以符合 matplotlib 的默认布局。若传入 Series 或 DataFrame，则使用传入的数据绘制表格。|
|`yerr `| DataFrame、Series、类数组、字典和字符串。详见带误差条的绘图。|
|`xerr `| 与 yerr 类型相同。|
|`stacked `| 布尔值，在线图和条形图中默认 False，在面积图中默认 True。若为 True，创建堆叠图。|
|`sort_columns `| 布尔值，默认 False。对列名排序以确定绘图顺序|
|`secondary_y `| 布尔值或序列，默认 False。是否绘制在副 y 轴上。若为列表/元组，则指定在副 y 轴上绘制的列|
|`mark_right `| 布尔值，默认 True。使用 secondary_y 轴时，自动在图例的列标签后加上“(right)”标记|
|`kwds`|  关键字参数。传递给 matplotlib 绘图方法的选项|
|`axes`|  matplotlib.axes.Axes 或它们的 numpy.ndarray|

**[🔼Back to Top](#table-of-contents)**

<a id="type-of-plots"></a>
### 绘图类型

`注意：这是数据可视化的一部分`

|类型 | 说明|
|-----|-----|
|`‘line’ `| 折线图（默认）|
|`‘bar’ `| 垂直条形图|
|`‘barh’ `| 水平条形图|
|`‘hist’ `| 直方图|
|`‘box’ `| 箱线图|
|`‘kde’ `| 核密度估计图|
|`‘density’ `| 与 ‘kde’ 相同|
|`‘area’`| 面积图|
|`‘pie’ `| 饼图|
|`‘scatter’ `| 散点图|
|`‘hexbin’ `| 六边形分箱图|

**[🔼Back to Top](#table-of-contents)**
