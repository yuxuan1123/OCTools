---
title: NumPy 速查表
description: 这里列出了最常用的 NumPy 命令。
created: 2022-10-23
---

<a id="table-of-contents"></a>
## 目录

- [NumPy 面向开发者速查表](#numpy-cheatsheet-for-developers)
  - [简介——什么是 NumPy？](#introduction-what-is-numpy)
  - [关键与导入](#key-and-imports)
  - [NumPy 中的数据类型](#data-types-in-numpy)
  - [保存与加载数据](#save-and-load-data)
    - [文本/CSV 文件：](#textcsv-files)
    - [属性：](#properties)
  - [操作](#operations)
  - [数组数学运算](#array-mathematics)
  - [函数](#functions)

<a id="numpy-cheatsheet-for-developers"></a>
# NumPy 面向开发者速查表

<a id="introduction-what-is-numpy"></a>
## 简介——什么是 NumPy？

> 一个由**多维数组对象**组成的库，以及用于处理这些数组的一系列例程。

**[🔼返回顶部](#table-of-contents)**

<a id="key-and-imports"></a>
## 关键与导入

> 我们在速查表中使用以下简写：

|Command | Description|
|----------|-------------|
|`np`|导入 numpy 库|
|`np.array` |  NumPy 中的数组对象|
|`np.array.shape`|数组的形状即每个维度中的元素数量。|
|`np.array.reshape`|重塑是指改变数组的形状（例如从 1-D 到 2-D）|
|`np.zeros(3)` | 长度为 3 的全零一维数组|
|`np.zeros((2,3))` | 全零二维数组|
|`np.zeros((3,2,4))` | 全零三维数组|
|`np.full((3,4),2)`| 值全为 2 的 3x4 数组|
|`np.random.rand(3,5)` | 0 到 1 之间的 3x5 随机浮点数数组 |
|`np.ones((3,4))` | 值全为 1 的 3x4 数组|
|`np.eye(4)` | 对角线为 1 的 4x4 数组|

**[🔼返回顶部](#table-of-contents)**

<a id="data-types-in-numpy"></a>
## NumPy 中的数据类型

> NumPy 有一些额外的数据类型，使用单个字符来指代数据类型，例如 i 表示整数，u 表示无符号整数等。

> 以下是 NumPy 中所有数据类型及其表示字符的列表。

|Command | Description|
|-------------|----------|
|`i`| 整数|
|`b `| 布尔值|
|`u`| 无符号整数|
|`f`| 浮点数|
|`c `| 复数浮点|
|`m` | 时间间隔|
|`M` | 日期时间|
|`O`| 对象|
|`S` | 字符串|
|`U `| Unicode 字符串|
|`V`| 其他类型的固定内存块（void）|

**[🔼返回顶部](#table-of-contents)**

<a id="save-and-load-data"></a>
## 保存与加载数据

<a id="textcsv-files"></a>
### 文本/CSV 文件：

|Command | Description|
|-------------|----------|
|`np.loadtxt('New_file.txt')` | 从文本文件|
|`np.genfromtxt('New_file.csv',delimiter=',') `| 从 CSV 文件|
|`np.savetxt('New_file.txt',arr,delimiter=' ') `| 写入文本文件|
|`np.savetxt('New_file.csv',arr,delimiter=',') `| 写入 CSV 文件|

**[🔼返回顶部](#table-of-contents)**

<a id="properties"></a>
### 属性：

|Command | Description|
|-------------|----------|
|`array.size` | 返回数组中的元素数量|
|`array.shape` | 返回数组的维度（行，列）|
|`array.dtype` | 返回数组中元素的类型|

**[🔼返回顶部](#table-of-contents)**

<a id="operations"></a>
## 操作

|Keywords | Description|Action|
|-------------|----------|:-------:|
|`np.copy(array)` | 将数组复制到新的内存数组。|复制|
|`view(dtype)` | 以 dtype 类型创建数组元素的视图|复制|
|`array.sort()` | 对数组排序|排序|
| `array.sort(axis=0)` | 对数组的特定轴排序|排序|
| `array.reshape(2,3)` | 将数组重塑为 2 行 3 列，且不改变数据。|排序|
|`np.append(array,values)`| 将值追加到数组末尾|添加|
|`np.insert(array,4,values)` | 在索引 4 之前将值插入数组|添加|
|`np.delete(array,2,axis=0)` | 删除数组索引 2 处的行|删除|
|`np.delete(array,3,axis=1)` | 删除数组索引 3 处的列|删除|
|`np.concatenate((array1,array2),axis=0)` | 将 array2 作为行追加到 array1 末尾|合并|
| `np.concatenate((array1,array2),axis=1)` | 将 array2 作为列追加到 array1 末尾|合并|
|`np.split(array,3)` | 将数组分割为 3 个子|数组|分割|
|`a[0]=5` | 将索引 0 处的数组元素赋值为 5|索引|
| `a[2,3]=1` | 将索引 [2][3] 处的数组元素赋值为 1|索引|
| `a[2]`| 返回数组 a 中索引 2 的元素。|子集|
|`a[3,5]` | 返回索引 [3][5] 处的二维数组元素|子集|
|`a[0:4]` | 返回索引 0,1,2,3 处的元素|切片|
|`a[0:4,3]`| 返回第 0,1,2,3 行第 3 列的元素|切片|
|`a[:2]`| 返回索引 0,1 处的元素|切片|
|`a[:,1]` | 返回所有行中索引 1 处的元素|切片|

**[🔼返回顶部](#table-of-contents)**

<a id="array-mathematics"></a>
## 数组数学运算

|Operation type | Syntax|Action|
|-------------|----------|:------:|
| 加法| np.add(a,b)|算术运算|
| 减法| np.subtract(a,b)|算术运算|
| 乘法| np.multiply(a,b)|算术运算|
| 除法| np.divide(a,b)|算术运算|
| 幂运算| np.exp(a)|算术运算|
| 平方根| np.sqrt(b)|算术运算|
| 逐元素| a==b|比较|
| 数组级| np.array_equal(a,b)|比较|

**[🔼返回顶部](#table-of-contents)**

<a id="functions"></a>
## 函数

|Operation Type | Syntax|
|-------------|----------|
|数组级求和| a.sum()|
| 数组级最小值| a.min()|
| 数组行最大值| a.max(axis=0)|
| 平均值| a.mean()|
| 中位数| a.median()|

**[🔼返回顶部](#table-of-contents)**
