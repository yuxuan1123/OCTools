---
title: Kotlin 速查表
description: 你可以在掌握之中随时获取 Kotlin 最重要的元素。
created: 2022-10-18
---

<a id="table-of-contents"></a>
## Table of Contents

- [Git 开发者速查表](#git-cheatsheet-for-developers)
  - [关于 Kotlin](#about-kotlin)
  - [基础](#basics)
    - [`Print Syntax`](#print-syntax)
    - [`声明函数`](#declaring-function)
    - [`单表达式函数`](#single-expression-function)
    - [`声明变量`](#declaring-variables)
    - [`可空类型变量`](#variables-with-nullable-types)
  - [控制结构](#control-structures)
  - [类](#classes)
    - [`主构造函数`](#primary-constructor)
    - [`继承`](#inheritance)
    - [`带访问器的属性`](#properties-with-assessors)
    - [`数据类`](#data-classes)
  - [集合字面量](#collection-literals)
  - [集合处理](#collection-processing)
    - [`students`](#students)
    - [`集合处理中最重要的函数`](#most-important-functions-for-collection-processing)
    - [`可变与不可变集合处理函数`](#mutable-vs-immutable-collection-processing-functions)
  - [扩展函数 -> Object](#extension-functions---object)
  - [函数](#functions)
    - [`函数类型`](#function-types)
    - [`函数字面量`](#function-literals)
    - [`扩展函数`](#extension-functions)
  - [委托](#delegates)
  - [可见性修饰符](#visibility-modifiers)
  - [型变修饰符](#variance-modifiers)

<a id="git-cheatsheet-for-developers"></a>
# Git CheatSheet for Developers

<a id="about-kotlin"></a>
## About Kotlin

> Kotlin 最初为 JVM（Java 虚拟机）和 Android 创建，是一种通用的、免费的、开源的、静态类型的“务实”编程语言，融合了面向对象和函数式编程能力。互操作性、安全性、清晰度和工具支持是其主要关注点。

**[🔼Back to Top](#table-of-contents)**

<a id="basics"></a>
## Basics

1. [打印语法](#print-syntax)
2. [声明函数](#declaring-function)
3. [单表达式函数](#single-expression-function)
4. [声明变量](#declaring-variables)
5. [可空类型变量](#variables-with-nullable-types)

**[🔼Back to Top](#table-of-contents)**

<a id="print-syntax"></a>
### `Print Syntax`

```bash
fun main(args: Array<String>) {
 println("Hello, World")
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="declaring-function"></a>
### `Declaring function`

```bash
fun sum(a: Int, b: Int): Int {
 return a + b
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="single-expression-function"></a>
### `Single-expression function`

```bash
fun sum(a: Int, b: Int) = a + b
```

**[🔼Back to Top](#table-of-contents)**

<a id="declaring-variables"></a>
### `Declaring variables`

```bash
val name = ”Marcin” ## Can't be changed
var age = 5 ## Can be changed
age++
```

**[🔼Back to Top](#table-of-contents)**

<a id="variables-with-nullable-types"></a>
### `Variables with nullable types`

```bash
var name: String? = null
val length: Int
length = name?.length ?: 0
## length, or 0 if name is null
length = name?.length ?: return
## length, or return when name is null
length = name?.length ?: throw Error()
## length, or throw error when name is null
```

**[🔼Back to Top](#table-of-contents)**

<a id="control-structures"></a>
## Control Structures

- **If 作为表达式**

```bash
fun bigger(a: Int, b: Int) = if (a > b) a else b
```

- **For 循环**

```bash
val list = listOf("A", "B", "C")
for (element in list) {
 println(element)
}
```

- **When 表达式**

```bash
fun numberTypeName(x: Number) = when(x) {
 0 -> "Zero" ## Equality check
 in 1..4 -> "Four or less" ## Range check
 5, 6, 7 -> "Five to seven" ## Multiple values
 is Byte -> "Byte" ## Type check
 else -> "Some number"
```

- **带谓词的 When 表达式**

```bash
fun signAsString(x: Int)= when {
 x < 0 -> "Negative"
 x == 0 -> "Zero"
 else -> "Positive"
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="classes"></a>
## Classes

1. [主构造函数](#primary-constructor)
2. [继承](#inheritance)
3. [带访问器的属性](#properties-with-assessors)
4. [数据类](#data-classes)

**[🔼Back to Top](#table-of-contents)**

<a id="primary-constructor"></a>
### `Primary constructor`

```bash
val declares a read-only property, var a mutable one
class Person(val name: String, var age: Int)
## name is read-only, age is mutable
```

**[🔼Back to Top](#table-of-contents)**

<a id="inheritance"></a>
### `Inheritance`

```bash
open class Person(val name: String) {
 open fun hello() = "Hello, I am $name"
 ## Final by default so we need open
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="properties-with-assessors"></a>
### `Properties with assessors`

```bash
class Person(var name: String, var surname: String) {
 var fullName: String
 get() = "$name $surname"
 set(value) {
 val (first, rest) = value.split(" ", limit = 2)
 name = first
 surname = rest
 }
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="data-classes"></a>
### `Data classes`

```bash
data class Person(val name: String, var age: Int)
val mike = Person("Mike", 23)
Modifier data adds:

 1. toString that displays all primary constructor
properties
print(mike.toString()) ## Person(name=Mike, age=23)

 2. equals that compares all primary constructor
properties
print(mike == Person("Mike", 23)) ## True
print(mike == Person("Mike", 21)) ## False

 3. hashCode that is based on all primary
constructor properties
val hash = mike.hashCode()
print(hash == Person("Mike", 23).hashCode()) ## True
print(hash == Person("Mike", 21).hashCode()) ## False

 4. component1, component2 etc. that allows
deconstruction
val (name, age) = mike
print("$name $age") ## Mike 23

 5. copy that returns copy of object with concrete
properties changed
val jake = mike.copy(name = "Jake")
```

**[🔼Back to Top](#table-of-contents)**

<a id="collection-literals"></a>
## Collection Literals

```bash
listOf(1,2,3,4) ## List<Int>

mutableListOf(1,2,3,4) ## MutableList<Int>

setOf("A", "B", "C") ## Set<String>

mutableSetOf("A", "B", "C") ## MutableSet<String>

arrayOf('a', 'b', 'c') ## Array<Char>

mapOf(1 to "A", 2 to "B") ## Map<Int, String>

mutableMapOf(1 to "A", 2 to "B") ## MutableMap<Int, String>

sequenceOf(4,3,2,1) ## Sequence<Int>

1 to "A" ## Pair<Int, String>

List(4) { it * 2 } ## List<Int>

generateSequence(4) { it + 2 } ## Sequence<Int>
```

**[🔼Back to Top](#table-of-contents)**

<a id="collection-processing"></a>
## Collection Processing

<a id="students"></a>
### `students`

- **.filter { it.passing && it.averageGrade > 4.0 }** <br>
  *// 仅包含通过的学生*

- **.sortedByDescending { it.averageGrade }** <br>
  *// 从成绩最高的开始*

- **.take(10)** <br>*// 取前 10 个*
  
- **.sortedWith(compareBy({ it.surname }, { it.name }))** <br>
 *// 先按姓氏排序，再按名字排序*

- **.generateSequence(0) { it + 1 }**<br>
// 从 0 开始的后续数字无限序列

- **.filter { it % 2 == 0 }**<br> *// 仅保留偶数*
 
- **.map { it * 3 }**<br> *// 每个元素乘 3*
 
- **.take(100)**<br> *// 取前 100 个*

- **.average()** <br>*// 计算平均值*

**[🔼Back to Top](#table-of-contents)**

<a id="most-important-functions-for-collection-processing"></a>
### `Most important functions for collection processing`

**val l = listOf(1,2,3,4)**

- **filter - 仅返回满足谓词的元素**<br>
 ``l.filter { it % 2 == 0 }`` <br>// [2, 4]

- **map - 返回转换后的元素**<br>
 ``l.map { it * 2 }`` <br>// [2, 4, 6, 8]

- **flatMap - 返回由转换结果产生的元素** <br>
``l.flatMap { listOf(it, it + 10) }`` <br>// [1, 11, 2, 12, 3, 13, 4, 14]

- **fold/reduce - 累加元素**<br>
``l.fold(0.0) { acc, i -> acc + i }`` // 10.0 <br>
``l.reduce { acc, i -> acc * i }`` // 48

- **forEach/onEach - 对每个元素执行操作**<br>
``l.forEach { print(it) }`` <br> // Prints 1234, returns Unit<br>
``l.onEach { print(it) }``<br> // Prints 1234, returns [1, 2, 3, 4]

- **partition - 拆分为一对列表**<br>
``val (even, odd) = l.partition { it % 2 == 0 }``<br>
print(even) // [2, 4]<br>
print(odd) // [1, 3]<br>

- **min/max/minBy/maxBy**<br>
``l.min()`` // 1, possible because we can compare Int<br>
``l.minBy { -it }`` // 4<br>
``l.max()`` // 4, possible because we can compare Int<br>
``l.maxBy { -it }`` // 1

- **first/firstBy**<br>
``l.first()`` // 1<br>
``l.first { it % 2 == 0 }`` // 2 (first even number)

- **count - 统计满足谓词的元素个数**<br>
``l.count { it % 2 == 0 }`` // 2

- **sorted/sortedBy - 返回排序后的集合**<br>
``listOf(2,3,1,4).sorted()`` // [1, 2, 3, 4]<br>
``l.sortedBy { it % 2 }`` // [2, 4, 1, 3]

- **groupBy - 按 key 对集合中的元素分组**<br>
``l.groupBy { it % 2 }`` <br>// Map: {1=[1, 3], 0=[2, 4]}

- **distinct/distinctBy - 仅返回唯一元素**<br>
``listOf(1,1,2,2).distinct()``  // [1, 2]

**[🔼Back to Top](#table-of-contents)**

<a id="mutable-vs-immutable-collection-processing-functions"></a>
### `Mutable vs immutable collection processing functions`

```bash
val list = mutableListOf(3,4,2,1)
val sortedResult = list.sorted() ## Returns sorted
println(sortedResult) ## [1, 2, 3, 4]
println(list) ## [3, 4, 2, 1]
val sortResult = list.sort() ## Sorts mutable collection
println(sortResult) ## kotlin.Unit
println(list) ## [1, 2, 3, 4]
```

**[🔼Back to Top](#table-of-contents)**

<a id="extension-functions---object"></a>
## Extension Functions -> Object

| 对接收者的引用 | 接收者 | Lambda 结果 |
| ----------- | ----------- | ----------- |
| it | also | let |
| has | apply | run/with |

```bash
val dialog = Dialog().apply {
 title = "Dialog title"
 onClick { print("Clicked") }
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="functions"></a>
## Functions

1. [函数类型](#function-types)
2. [函数字面量](#function-literals)
3. [扩展函数](#extension-functions)

**[🔼Back to Top](#table-of-contents)**

<a id="function-types"></a>
### `Function types`

```bash
()->Unit - takes no arguments and returns nothing (Unit).
(Int, Int)->Int - takes two arguments of type Int
and returns Int.
(()->Unit)->Int - takes another function
and returns Int.
(Int)->()->Unit - takes argument of type Int
and returns function.
```

**[🔼Back to Top](#table-of-contents)**

<a id="function-literals"></a>
### `Function literals`

```bash
val add: (Int, Int) -> Int = { i, j -> i + j }
## Simple lambda expression
val printAndDouble: (Int) -> Int = {
 println(it)
 ## When single parameter, we can reference it using `it`
 it * 2 ## In lambda, last expression is returned
}
## Anonymous function alternative
val printAndDoubleFun: (Int) -> Int = fun(i: Int): Int {
 println(i) ## Single argument can’t be referenced by `it`
 return i * 2 ## Needs return like any function
}
val i = printAndDouble(10) ## 10
print(i) ## 20
```

**[🔼Back to Top](#table-of-contents)**

<a id="extension-functions"></a>
### `Extension functions`

```bash
fun Int.isEven() = this % 2 == 0
print(2.isEven()) ## true
fun List<Int>.average() = 1.0 * sum() / size
print(listOf(1, 2, 3, 4).average()) ## 2
```

**[🔼Back to Top](#table-of-contents)**
   
<a id="delegates"></a>
## Delegates

```bash
Lazy - calculates value before first usage

val i by lazy { print("init "); 10 }
print(i) ## Prints: init 10
print(i) ## Prints: 10


notNull - returns last setted value, or throws error

if no value has been set
observable/vetoable - calls function every time
value changes. In vetoable function also decides

if new value should be set.
var name by observable("Unset") { p, old, new ->
 println("${p.name} changed $old -> $new")
}
name = "Marcin"
## Prints: name changed Unset -> Marcin


Map/MutableMap - finds value on map by property
name

val map = mapOf("a" to 10)
val a by map
print(a) ## Prints: 10
```

**[🔼Back to Top](#table-of-contents)**

<a id="visibility-modifiers"></a>
## Visibility Modifiers

|修饰符|类成员|顶层|
| ----------- | ----------- | ----------- |
| Public (default) | 任何地方可见 | 任何地方可见 |
|Private  | 仅在同一类中可见| 在同一文件中可见 |
| Protected |仅在同一类及其子类中可见  | 不允许 |
| Internal |  类可访问时在同一模块中可见  | 在同一模块中可见 |

**[🔼Back to Top](#table-of-contents)**

<a id="variance-modifiers"></a>
## Variance Modifiers

```bash
              Invariance           Covariance          Contravariance
             class Box<T>       class Box <out T>     class box <in T>
[Number]     [Box<Number>]        [Box<Numbers>]        [Box<Number>]
   ⬆              X                    |                      |
   |              X                    |                      |
   |              X                    ↓                      ↓
 [Int]        [Box<Int>]          [Box<Int>]            [Box<Int>]
```

**[🔼Back to Top](#table-of-contents)**
