---
title: JavaScript 速查表
description: 这里列出了最常用的 JavaScript 概念。
created: 2022-10-21
---

<a id="table-of-contents"></a>

## 目录

- [面向开发者的 JavaScript 速查表](#javascript-cheatsheet-for-developers)
  - [JavaScript 基础](#javascript-basics)
    - [HTML 页面中的 JavaScript 代码](#javascript-code-in-the-html-page)
    - [注释](#comments)
    - [变量](#variables)
    - [数组](#arrays)
    - [数组方法](#array-methods)
      - [Array.Prototype.Push()](#arrayprototypepush)
      - [Array.Prototype.Pop()](#arrayprototypepop)
      - [Array.Prototype.Shift()](#arrayprototypeshift)
      - [Array.Prototype.Unshift()](#arrayprototypeunshift)
      - [Array.Prototype.Slice()](#arrayprototypeslice)
      - [Array.Prototype.Splice()](#arrayprototypesplice)
      - [Array.Prototype.Concat()](#arrayprototypeconcat)
      - [Array.Prototype.IndexOf()](#arrayprototypeindexof)
      - [Array.Prototype.LastIndexOf()](#arrayprototypelastindexof)
      - [Array.Prototype.Join()](#arrayprototypejoin)
      - [Array.Prototype.Reverse()](#arrayprototypereverse)
      - [Array.Prototype.Sort()](#arrayprototypesort)
      - [Array.Prototype.ForEach()](#arrayprototypeforeach)
      - [Array.Prototype.Map()](#arrayprototypemap)
      - [Array.Prototype.Filter()](#arrayprototypefilter)
      - [Array.Prototype.Reduce()](#arrayprototypereduce)
      - [Array.Prototype.ReduceRight()](#arrayprototypereduceright)
      - [Array.Prototype.Every()](#arrayprototypeevery)
      - [Array.Prototype.Some()](#arrayprototypesome)
      - [Array.Prototype.Find()](#arrayprototypefind)
      - [Array.Prototype.FindIndex()](#arrayprototypefindindex)
      - [Array.Prototype.Fill()](#arrayprototypefill)
      - [Array.Prototype.CopyWithin()](#arrayprototypecopywithin)
      - [Array.Prototype.Includes()](#arrayprototypeincludes)
      - [Array.Prototype.Flat()](#arrayprototypeflat)
      - [Array.Prototype.FlatMap()](#arrayprototypeflatmap)
      - [Array.Prototype.Keys()](#arrayprototypekeys)
      - [Array.Prototype.Values()](#arrayprototypevalues)
      - [Array.Prototype.Entries()](#arrayprototypeentries)
      - [Array.Prototype.at()](#arrayprototypeat)
    - [函数](#functions)
    - [循环](#loops)
      - [For](#for)
      - [While](#while)
      - [Do While](#do-while)
      - [Break](#break)
    - [字符串](#strings)
    - [字符串方法](#string-methods)
  - [数字与数学](#numbers-and-math)
    - [数字属性](#number-properties)
    - [处理日期](#dealing-with-dates)
      - [设置日期](#setting-dates)
      - [获取日期和时间值](#pulling-date-and-time-values)
      - [设置日期的部分](#setting-part-of-a-date)
      - [格式化日期对象](#format-date-object)
  - [DOM（文档对象模型）](#dom-document-object-modulation)
    - [元素方法](#element-methods)
  - [事件](#events)
    - [鼠标](#mouse)
    - [键盘](#keyboard)
    - [框架](#frame)
    - [表单](#form)
  - [错误](#errors)

<a id="javascript-cheatsheet-for-developers"></a>

# 面向开发者的 JavaScript 速查表

<a id="javascript-basics"></a>

## JavaScript 基础

<a id="javascript-code-in-the-html-page"></a>

### HTML 页面中的 JavaScript 代码

``` JavaScript
<script type="text/javascript">
    // JS code goes here
</script>
```

**[🔼Back to Top](#table-of-contents)**

<a id="comments"></a>

### 注释

``` JavaScript
// Single line comments

/* Multi-line comments */ 
```

**[🔼Back to Top](#table-of-contents)**

<a id="variables"></a>

### 变量

| 变量 | 描述 |
| :----:    | :--- |
| `var`     | 最常见的变量。可以重新赋值，但只能在函数内部访问，用 var 定义的变量在执行代码时会提升到顶部。 |
| `const`   | 不能重新赋值，并且在代码中出现之前无法访问。 |
| `let`     | 类似于 const，但 let 变量可以重新赋值，不能重复声明。 |

**[🔼Back to Top](#table-of-contents)**

<a id="arrays"></a>

### 数组

``` JavaScript
// Example
var names= ["Raj", "Ram", "Sham"];
```

**[🔼Back to Top](#table-of-contents)**

<a id="array-methods"></a>

### 数组方法

| 方法             | 描述                                                                  |
| :-------------: | :---------------------------------------------------------------------- |
| `push()`        | 向数组末尾添加一个元素                                                |
| `pop()`         | 移除数组的最后一个元素                                                |
| `shift()`       | 移除数组的第一个元素                                                  |
| `unshift()`     | 向数组开头添加一个元素                                                |
| `slice()`       | 选取数组的一部分并返回新数组                                          |
| `splice()`      | 向数组中添加/移除元素                                                 |
| `concat()`      | 连接两个或多个数组，并返回连接后数组的副本                            |
| `indexOf()`     | 在数组中搜索某个元素并返回其位置                                      |
| `lastIndexOf()` | 从末尾开始在数组中搜索某个元素，并返回其位置                          |
| `join()`        | 将数组中的所有元素连接成一个字符串                                    |
| `reverse()`     | 反转数组中元素的顺序                                                  |
| `sort()`        | 对数组元素进行排序                                                    |
| `forEach()`     | 为数组的每个元素调用一个函数                                          |
| `map()`         | 通过为每个数组元素调用函数的结果创建一个新数组                        |
| `filter()`      | 创建一个新数组，包含数组中通过测试的每个元素                          |
| `reduce()`      | 将数组的值缩减为单个值（从左到右）                                    |
| `reduceRight()` | 将数组的值缩减为单个值（从右到左）                                    |
| `every()`       | 检查是否所有数组值都通过测试                                          |
| `some()`        | 检查是否部分数组值通过测试                                            |
| `find()`        | 返回通过测试的第一个数组元素的值                                      |
| `findIndex()`   | 返回通过测试的第一个数组元素的索引                                    |
| `fill()`        | 用静态值填充数组中的元素                                              |
| `copyWithin()`  | 在数组内部复制数组元素                                                |
| `includes()`    | 检查数组是否包含指定元素                                              |
| `flat()`        | 创建一个新数组，将子数组元素连接到其中                                |
| `flatMap()`     | 先使用映射函数映射每个元素，然后将结果扁平化为一个新数组              |
| `keys()`        | 返回带有数组键的 Array Iterator 对象                                  |
| `values()`      | 返回带有数组值的 Array Iterator 对象                                  |
| `entries()`     | 返回带有键值对的 Array Iterator 对象                                  |
| `at()`          | 返回数组中指定索引处的元素                                            |

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypepush"></a>

#### Array.Prototype.Push()

``` JavaScript
// Syntax
array.push(element1, element2, ..., elementN);
// Example
var names= ["Raj", "Ram", "Sham"];
names.push("Ramesh");
// Output
["Raj", "Ram", "Sham", "Ramesh"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypepop"></a>

#### Array.Prototype.Pop()

``` JavaScript
// Syntax
array.pop();
// Example
var names= ["Raj", "Ram", "Sham"];
names.pop();
// Output
["Raj", "Ram"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeshift"></a>

#### Array.Prototype.Shift()

``` JavaScript
// Syntax
array.shift();
// Example
var names= ["Raj", "Ram", "Sham"];
names.shift();
// Output
["Ram", "Sham"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeunshift"></a>

#### Array.Prototype.Unshift()

``` JavaScript
// Syntax
array.unshift(element1, element2, ..., elementN);
// Example
var names= ["Raj", "Ram", "Sham"];
names.unshift("Ramesh");
// Output
["Ramesh", "Raj", "Ram", "Sham"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeslice"></a>

#### Array.Prototype.Slice()

``` JavaScript
// Syntax
array.slice();
array.slice(start);
array.slice(start, end);
// Example
var names= ["Raj", "Ram", "Sham"];
names.slice(1, 2);
// Output
["Ram"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypesplice"></a>

#### Array.Prototype.Splice()

``` JavaScript
// Syntax
array.splice(start)
array.splice(start, deleteCount)
array.splice(start, deleteCount, item1)
array.splice(start, deleteCount, item1, item2, itemN)
// Example
var names= ["Raj", "Ram", "Sham"];
names.splice(1, 2);
// Output
["Ram", "Sham"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeconcat"></a>

#### Array.Prototype.Concat()

``` JavaScript
// Syntax
array.concat(array1, array2, ..., arrayN);
// Example
var names= ["Raj", "Ram", "Sham"];
var names2= ["Ramesh", "Rajesh", "Rakesh"];
names.concat(names2);
// Output
["Raj", "Ram", "Sham", "Ramesh", "Rajesh", "Rakesh"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeindexof"></a>

#### Array.Prototype.IndexOf()

``` JavaScript
// Syntax
array.indexOf(searchElement);
// Example
var names= ["Raj", "Ram", "Sham"];
names.indexOf("Ram");
// Output
1
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypelastindexof"></a>

#### Array.Prototype.LastIndexOf()

``` JavaScript
// Syntax
array.lastIndexOf(searchElement);
// Example
var names= ["Raj", "Ram", "Sham", "Ram"];
names.lastIndexOf("Ram");
// Output
3
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypejoin"></a>

#### Array.Prototype.Join()

``` JavaScript
// Syntax
array.join(separator);
// Example
var names= ["Raj", "Ram", "Sham"];
names.join(" ");
// Output
Raj Ram Sham
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypereverse"></a>

#### Array.Prototype.Reverse()

``` JavaScript
// Syntax
array.reverse();
// Example
var names= ["Raj", "Ram", "Sham"];
names.reverse();
// Output
["Sham", "Ram", "Raj"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypesort"></a>

#### Array.Prototype.Sort()

``` JavaScript
// Syntax
array.sort();
array.sort(compareFunction);
// Example
var names= ["Raj", "Ram", "Sham"];
names.sort();
// Output
["Ram", "Raj", "Sham"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeforeach"></a>

#### Array.Prototype.ForEach()

``` JavaScript
// Syntax
array.forEach(function(currentValue, index, arr), thisValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.forEach(function(name) {
    console.log(name);
});
// Output
Raj
Ram
Sham
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypemap"></a>

#### Array.Prototype.Map()

``` JavaScript
// Syntax
array.map(function(currentValue, index, arr), thisValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.map(function(name) {
    return name + " Singh";
});
// Output
["Raj Singh", "Ram Singh", "Sham Singh"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypefilter"></a>

#### Array.Prototype.Filter()

``` JavaScript
// Syntax
array.filter(function(currentValue, index, arr), thisValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.filter(function(name) {
    return name.length > 3;
});
// Output
["Raj", "Sham"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypereduce"></a>

#### Array.Prototype.Reduce()

``` JavaScript
// Syntax
array.reduce(function(total, currentValue, currentIndex, arr), initialValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.reduce(function(total, name) {
    return total + name;
}, "");
// Output
RajRamSham

// Example
var numbers= [1, 2, 3];
numbers.reduce(function(total, number) {
    return total * number;
}, 1);
// Output
6
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypereduceright"></a>

#### Array.Prototype.ReduceRight()

``` JavaScript
// Syntax
array.reduceRight(function(total, currentValue, currentIndex, arr), initialValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.reduceRight(function(total, name) {
    return total + name;
}, "");
// Output
ShamRamRaj
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeevery"></a>

#### Array.Prototype.Every()

``` JavaScript
// Syntax
array.every(function(currentValue, index, arr), thisValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.every(function(name) {
    return name.length > 3;
});
// Output
false
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypesome"></a>

#### Array.Prototype.Some()

``` JavaScript
// Syntax
array.some(function(currentValue, index, arr), thisValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.some(function(name) {
    return name.length > 3;
});
// Output
true
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypefind"></a>

#### Array.Prototype.Find()

``` JavaScript
// Syntax
array.find(function(currentValue, index, arr), thisValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.find(function(name) {
    return name.length > 3;
});
// Output
Raj
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypefindindex"></a>

#### Array.Prototype.FindIndex()

``` JavaScript
// Syntax
array.findIndex(function(currentValue, index, arr), thisValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.findIndex(function(name) {
    return name.length > 3;
});
// Output
0
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypefill"></a>

#### Array.Prototype.Fill()

``` JavaScript
// Syntax
array.fill(value, start, end)
// Example
var names= ["Raj", "Ram", "Sham"];
names.fill("Ramesh");
// Output
["Ramesh", "Ramesh", "Ramesh"]

// Example
var names= ["Raj", "Ram", "Sham"];
names.fill("Ramesh", 1, 2);
// Output
["Raj", "Ramesh", "Sham"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypecopywithin"></a>

#### Array.Prototype.CopyWithin()

``` JavaScript
// Syntax
array.copyWithin(target, start, end)
// Example
var names= ["Raj", "Ram", "Sham"];
names.copyWithin(1, 0);
// Output
["Raj", "Raj", "Ram"]

// Example
var names= ["Raj", "Ram", "Sham"];
names.copyWithin(1, 0, 2);
// Output
["Raj", "Raj", "Sham"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeincludes"></a>

#### Array.Prototype.Includes()

``` JavaScript
// Syntax
array.includes(searchElement, fromIndex)
// Example
var names= ["Raj", "Ram", "Sham"];
names.includes("Ram");
// Output
true

// Example
var names= ["Raj", "Ram", "Sham"];
names.includes("Ram", 1);
// Output
false
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeflat"></a>

#### Array.Prototype.Flat()

``` JavaScript
// Syntax
array.flat(depth)
// Example
var names= ["Raj", ["Ram", "Sham"]];
names.flat();
// Output
["Raj", "Ram", "Sham"]

// Example
var names= ["Raj", ["Ram", ["Sham"]]];
names.flat(1);
// Output
["Raj", "Ram", ["Sham"]]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeflatmap"></a>

#### Array.Prototype.FlatMap()

``` JavaScript
// Syntax
array.flatMap(function(currentValue, index, arr), thisValue)
// Example
var names= ["Raj", "Ram", "Sham"];
names.flatMap(function(name) {
    return name + " Singh";
});
// Output
["Raj Singh", "Ram Singh", "Sham Singh"]
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypekeys"></a>

#### Array.Prototype.Keys()

``` JavaScript
// Syntax
array.keys()
// Example
var names= ["Raj", "Ram", "Sham"];
var iterator = names.keys();
iterator.next();
// Output
{value: 0, done: false}
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypevalues"></a>

#### Array.Prototype.Values()

``` JavaScript
// Syntax
array.values()
// Example
var names= ["Raj", "Ram", "Sham"];
var iterator = names.values();
iterator.next();
// Output
{value: "Raj", done: false}
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeentries"></a>

#### Array.Prototype.Entries()

``` JavaScript
// Syntax
array.entries()
// Example
var names= ["Raj", "Ram", "Sham"];
var iterator = names.entries();
iterator.next();
// Output
{value: Array(2), done: false}
```

**[🔼Back to Top](#table-of-contents)**

<a id="arrayprototypeat"></a>

#### Array.Prototype.at()

``` JavaScript
// Syntax
array.at(index)
// Example
var names= ["Raj", "Ram", "Sham"];
names.at(1);
// Output
Ram
```

**[🔼Back to Top](#table-of-contents)**

<a id="functions"></a>

### 函数 

``` JavaScript
function name(parameter1, parameter2, parameter3) {
    // what the function does
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="loops"></a>

### 循环

``` JavaScript
for (Initialization; Condition; Increment/Decrement) {
    // what to do during the loop
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="for"></a>

#### For

> Javascript 中最常见的创建循环的方式

**[🔼Back to Top](#table-of-contents)**

<a id="while"></a>

#### While

> 设置循环执行的条件

**[🔼Back to Top](#table-of-contents)**

<a id="do-while"></a>

#### Do While

> 类似于 while 循环，但至少执行一次，并在末尾进行检查以判断是否满足再次执行的条件

**[🔼Back to Top](#table-of-contents)**

<a id="break"></a>

#### Break

> 用于在特定条件下停止并退出循环；continue 用于在满足特定条件时跳过循环的部分内容

**[🔼Back to Top](#table-of-contents)**

<a id="strings"></a>

### 字符串

``` JavaScript
var event = "Hacktoberfest 2022";
```

**[🔼Back to Top](#table-of-contents)**

<a id="string-methods"></a>

### 字符串方法

| 方法              | 描述                                                                              |
| :--------------: | :--------------------------------------------------------------------------------------- |
| `charAt()`       | 返回字符串中指定位置的字符                                                            |
| `charCodeAt()`   | 给出该位置字符的 unicode 编码                                                          |
| `concat()`       | 将两段或多段字符串连接（拼接）成一段                                                  |
| `fromCharCode()` | 返回由指定的 UTF-16 代码单元序列创建的字符串                                          |
| `indexOf()`      | 提供指定文本在字符串中首次出现的位置                                                  |
| `lastIndexOf()`  | 与 indexOf() 相同，但搜索方向相反，返回最后一次出现的位置                            |
| `match()`        | 检索字符串与搜索模式的匹配项                                                          |
| `replace()`      | 查找并替换字符串中的特定文本                                                          |
| `search()`       | 执行搜索以匹配文本并返回其位置                                                        |
| `slice()`        | 提取字符串的一部分并将其作为新字符串返回                                              |
| `split()`        | 在指定位置将字符串对象拆分为字符串数组                                                |
| `substr()`       | 类似于 slice()，但根据指定的字符数提取子字符串                                       |
| `substring()`    | 也类似于 slice()，但不能接受负的索引                                                 |
| `toLowerCase()`  | 将字符串转换为小写                                                                  |
| `toUpperCase()`  | 将字符串转换为大写                                                                  |
| `valueOf()`      | 返回字符串对象的原始值（没有属性或方法）                                              |

**[🔼Back to Top](#table-of-contents)**

<a id="numbers-and-math"></a>

## 数字与数学

<a id="number-properties"></a>

### 数字属性

| 方法              | 描述                                                 |
| :-----------------: | :---------------------------------------------------------- |
| `MAX_VALUE`         | JavaScript 中可表示的最大数值            |
| `MIN_VALUE`         | JavaScript 中可表示的最小正数             |
| `NaN`               | “非数字”（Not-a-Number）值                         |
| `NEGATIVE_INFINITY` | 负无穷大值                                                    |
| `POSITIVE_INFINITY` | 正无穷大值                                                    |

**[🔼Back to Top](#table-of-contents)**

<a id="dealing-with-dates"></a>

### 处理日期

> `Contents need to be added in this section.`  

**[🔼Back to Top](#table-of-contents)**

<a id="setting-dates"></a>

#### 设置日期

| 方法                            | 描述                                                                                                                                                          |
| :-------------------------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Date()`                          | 使用当前日期和时间创建一个新的日期对象                                                                                                             |
| `Date(2022, 5, 21, 3, 23, 10, 0)` | 创建自定义日期对象。这些数字分别代表年、月、日、时、分、秒、毫秒。除了年和月，其余都可以省略。 |
| `Date("2017-06-23")`              | 以字符串形式声明日期                                                                                                                                         |

**[🔼Back to Top](#table-of-contents)**

<a id="pulling-date-and-time-values"></a>

#### 获取日期和时间值

| 函数                | 描述                                                                                                                                  |
| :-----------------: | :------------------------------------------------------------------------------------------------------------------------------------------- |
| `getDate()`         | 获取月份中的日期，以数字表示（1-31）                                                                                                  |
| `getDay()`          | 星期几，以数字表示（0-6）                                                                                                                |
| `getFullYear()`     | 四位数字表示的年份（yyyy）                                                                                                           |
| `getHours()`        | 获取小时（0-23）                                                                                                                          |
| `getMilliseconds()` | 毫秒（0-999）                                                                                                                      |
| `getMinutes()`      | 获取分钟（0-59）                                                                                                                        |
| `getMonth()`        | 月份，以数字表示（0-11）                                                                                                                     |
| `getSeconds()`      | 获取秒（0-59）                                                                                                                        |
| `getTime()`         | 获取自 1970 年 1 月 1 日以来的毫秒数                                                                                                   |
| `getUTCDate()`      | 根据世界时，指定日期中的日（日期）（day、month、fullyear、hours、minutes 等同样可用） |

**[🔼Back to Top](#table-of-contents)**

<a id="setting-part-of-a-date"></a>

#### 设置日期的部分

| 方法              | 描述                                                                                                                               |
| :-----------------: | :---------------------------------------------------------------------------------------------------------------------------------------- |
| `setDate()`         | 设置日，以数字表示（1-31）                                                                                                            |
| `setFullYear()`     | 设置年份（可选月份和日）                                                                                                  |
| `setHours()`        | 设置小时（0-23）                                                                                                                       |
| `setMilliseconds()` | 设置毫秒（0-999）                                                                                                                  |
| `setMinutes()`      | 设置分钟（0-59）                                                                                                                   |
| `setMonth()`        | 设置月份（0-11）                                                                                                                      |
| `setSeconds()`      | 设置秒（0-59）                                                                                                                   |
| `setTime()`         | 设置时间（自 1970 年 1 月 1 日以来的毫秒数）                                                                                         |
| `setUTCDate()`      | 根据世界时设置指定日期的月份中的日（day、month、fullyear、hours、minutes 等同样可用） |

**[🔼Back to Top](#table-of-contents)**

<a id="format-date-object"></a>

#### 格式化日期对象

| 方法                 | 描述                                                                                                                      |
| :--------------------: | :------------------------------------------------------------------------------------------------------------------------------- |
| `toLocaleDateString()` | 返回字符串，以用户代理时区中指定日期的日期部分的语言敏感表示 |

**[🔼Back to Top](#table-of-contents)**

<a id="dom-document-object-modulation"></a>

## DOM（文档对象模型）

<a id="element-methods"></a>

### 元素方法

| 方法                     | 描述                                                                                                         |
| :------------------------: | :------------------------------------------------------------------------------------------------------------------ |
| `getAttribute()`           | 返回元素节点的指定属性值                                                            |
| `getAttributeNS()`         | 返回具有指定命名空间和名称的属性的字符串值                                         |
| `getAttributeNode()`       | 获取指定的属性节点                                                                                   |
| `getAttributeNodeNS()`     | 返回具有给定命名空间和名称的属性的属性节点                                      |
| `getElementsByTagName()`   | 提供具有指定标签名的所有子元素的集合                                             |
| `getElementsByTagNameNS()` | 返回属于给定命名空间、具有特定标签名的元素的实时 HTMLCollection                  |
| `hasAttribute()`           | 如果元素具有任何属性，则返回 true，否则返回 false                                                      |
| `hasAttributeNS()`         | 提供真/假值，指示给定命名空间中的当前元素是否具有指定属性 |
| `removeAttribute()`        | 从元素中移除指定属性                                                                       |
| `removeAttributeNS()`      | 从元素中移除特定命名空间内的指定属性                                          |
| `removeAttributeNode()`    | 移除指定的属性节点并返回被移除的节点                                                  |
| `setAttribute()`           | 将指定属性设置或更改指定的值                                                        |
| `setAttributeNS()`         | 添加新属性或更改具有给定命名空间和名称的属性的值                         |
| `setAttributeNode()`       | 设置或更改指定的属性节点                                                                        |
| `setAttributeNodeNS()`     | 向元素添加新的带命名空间的属性节点                                                                 |

**[🔼Back to Top](#table-of-contents)**

<a id="events"></a>

## 事件

<a id="mouse"></a>

### 鼠标

| 方法          | 描述                                                           |
| :-------------: | :-------------------------------------------------------------------- |
| `onclick`       | 用户单击元素时触发                   |
| `oncontextmenu` | 用户右键单击元素以打开上下文菜单                |
| `ondblclick`    | 用户双击元素                                  |
| `onmousedown`   | 用户在元素上按下鼠标按钮                           |
| `onmouseenter`  | 指针移动到元素上                                     |
| `onmouseleave`  | 指针移出元素                                       |
| `onmousemove`   | 指针在元素上方时正在移动                     |
| `onmouseover`   | 当指针移动到元素或其某个子元素上时      |
| `onmouseout`    | 用户将鼠标指针移出元素或其某个子元素                 |
| `onmouseup`     | 用户在元素上方释放鼠标按钮                |

**[🔼Back to Top](#table-of-contents)**

<a id="keyboard"></a>

### 键盘

| 方法       | 描述                               |
| :----------: | :---------------------------------------- |
| `onkeydown`  | 用户按下按键时      |
| `onkeypress` | 用户刚开始按下按键时 |
| `onkeyup`    | 用户释放按键时                   |

**[🔼Back to Top](#table-of-contents)**

<a id="frame"></a>

### 框架

| 方法           | 描述                                                                          |
| :--------------: | :----------------------------------------------------------------------------------- |
| `onabort`        | 媒体加载被中止                                                    |
| `onbeforeunload` | 文档即将卸载之前触发                             |
| `onerror`        | 加载外部文件时发生错误                                       |
| `onhashchange`   | URL 的锚点部分发生更改时触发；onload 对象已加载时               |
| `onpagehide`     | 用户导航离开网页                                               |
| `onpageshow`     | 用户导航到网页时                                                 |
| `onresize`       | 文档视图被调整大小时                                                         |
| `onscroll`       | 元素的滚动条正在被滚动                                             |
| `onunload`       | 页面卸载时触发                                                |

**[🔼Back to Top](#table-of-contents)**

<a id="form"></a>

### 表单

| 方法       | 描述                                 |
| :----------: | :------------------------------------------ |
| `onblur`     | 元素失去焦点时                 |
| `onchange`   | 表单元素的内容发生变化时       |
| `onfocus`    | 元素获得焦点时                       |
| `onfocusin`  | 元素即将获得焦点时       |
| `onfocusout` | 元素即将失去焦点时          |
| `oninput`    | 用户在元素上输入时                    |
| `oninvalid`  | 元素无效时                       |
| `onreset`    | 表单被重置时                             |
| `onsearch`   | 用户在搜索字段中输入内容时 |

**[🔼Back to Top](#table-of-contents)**

<a id="errors"></a>

## 错误

| 错误处理   | 描述                                                            |
| :--------------: | :--------------------------------------------------------------------- |
| `try`            | 让你定义一个代码块来测试错误                     |
| `catch`          | 设置一个代码块，在发生错误时执行                  |
| `throw`          | 创建自定义错误消息，以取代标准 JavaScript 错误 |
| `finally`        | 让你在 try 和 catch 之后，无论结果如何都执行代码   |

**[🔼Back to Top](#table-of-contents)**
