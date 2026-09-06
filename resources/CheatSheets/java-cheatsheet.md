---
title: Java 速查表
description: 这里给出最常用的 Java 概念。
created: 2022-10-21
---

<a id="table-of-contents"></a>
## Table of Contents

- [Java 开发者速查表](#java-cheatsheet-for-developers)
	- [数据类型](#data-types)
	- [数据转换](#data-conversion)
		- [字符串转数字](#string-to-number)
		- [任意类型转字符串](#any-type-to-string)
		- [数值转换](#numeric-conversions)
	- [运算符](#operators)
	- [语句](#statements)
		- [If 语句](#if-statement)
		- [While 循环](#while-loop)
		- [Do-While 循环](#do-while-loop)
		- [For 循环](#for-loop)
		- [For Each 循环](#for-each-loop)
		- [Switch 语句](#switch-statement)
		- [异常处理](#exception-handling)
	- [字符串方法](#string-methods)
	- [数学库方法](#math-library-methods)
	- [变量类型](#types-of-variables)
	- [Java 正则表达式](#java-regex)
		- [Matcher 类](#matcher-class)
	- [Java 中的继承](#inheritance-in-java)
		- [单继承：](#single-inheritance)
		- [多层继承：](#multi-level-inheritance)
		- [分层继承](#hierarchical-inheritance)
		- [混合继承：](#hybrid-inheritance)
	- [注意](#note)
	- [Java 中的封装](#encapsulation-in-java)
		- [Java 包](#java-packages)
	- [Java 中的抽象](#abstraction-in-java)
		- [抽象类](#abstract-class)
		- [接口](#interface)
	- [Java 中的多态](#polymorphism-in-java)
		- [方法重载](#method-overloading)
		- [方法重写](#method-overriding)
	- [集合](#collections)

<a id="java-cheatsheet-for-developers"></a>
# Java CheatSheet for Developers

<a id="data-types"></a>
## Data Types
| 数据类型 | 大小 |
|--|--|
| boolean | 1 bit |
| char | 2 byte |
| int | 4 byte |
| short | 2 byte| 
|long |8 byte |
|float|4 byte|
|double|8 byte |

**[🔼Back to Top](#table-of-contents)**

<a id="data-conversion"></a>
## Data Conversion

<a id="string-to-number"></a>
### String to Number

```java
    int i = Intege­r.p­ars­eInt(_str_);  
	double d = Double.pa­rse­Double(_str_);
```

**[🔼Back to Top](#table-of-contents)**

<a id="any-type-to-string"></a>
### Any Type to String

```java
	String s = String.va­lueOf(_value_);  

```

**[🔼Back to Top](#table-of-contents)**

<a id="numeric-conversions"></a>
### Numeric Conversions

```java
	int i = (int) _numeric expression_; 

```

**[🔼Back to Top](#table-of-contents)**

<a id="operators"></a>
## Operators

| 运算符类别 | 运算符 |
|--|--|
| 算术运算符 |+, -, /, *, %  |
|关系运算符|<, >, <=, >=,==, !=|
|逻辑运算符|&&, \|\||
|赋值运算符|=, +=, −=, ×=, ÷=, %=, &=, ^=, \|=, <<=, >>=, >>>=|
|自增和自减运算符|++ , - -|
|条件运算符|?, :|
|位运算符|^, &, \||
|特殊运算符|. (dot operator to access methods of class)|

**[🔼Back to Top](#table-of-contents)**

<a id="statements"></a>
## Statements

<a id="if-statement"></a>
### If Statement

```java
if ( _expression_ ) {  
­ _statements_  
} else if ( _expression_ ) {  
­ _statements_  
} else {  
­ _statements_  
}  
```

**[🔼Back to Top](#table-of-contents)**

<a id="while-loop"></a>
### While Loop 

```java
while ( _expression_ ) {  
­ _statements_  
}  
```

**[🔼Back to Top](#table-of-contents)**

<a id="do-while-loop"></a>
### Do-While Loop 

```java
do {  
­ _statements_  
} while ( _expression_ ); 
```

**[🔼Back to Top](#table-of-contents)**

<a id="for-loop"></a>
### For Loop

```java
for ( int i = 0; i < _max_; ++i) {  
­ _statements_  
}  
```

**[🔼Back to Top](#table-of-contents)**

<a id="for-each-loop"></a>
### For Each Loop

```java
for ( _var_ : _collection_ ) {  
­ _statements_  
} 
```

**[🔼Back to Top](#table-of-contents)**

<a id="switch-statement"></a>
### Switch Statement

```java
switch ( _expression_ ) {  
­ case _value_:  
­ ­ ­ _statements_  
­ ­ ­ ­break;  
­ case _value2_:  
­ ­ ­ _statements_  
­ ­ ­ ­break;  
­ ­def­ault:  
­ ­ ­ _statements_  
} 
```

**[🔼Back to Top](#table-of-contents)**

<a id="exception-handling"></a>
### Exception Handling

```java
try {  
­ ­sta­tem­ents;  
} catch (_Except­ionType_  _e1_) {  
­ ­sta­tem­ents;  
} catch (Exception _e2_) {  
­ ­cat­ch-all statem­ents;  
} finally {  
­ ­sta­tem­ents;  
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="string-methods"></a>
## String Methods

| 命令 |说明  |
|--|--|
|length | 字符串的长度 |
|charAt(_i_) |提取第 _i_ 个字符  |
|subst­ring(_start_, _end_) |提取从 _start_ 到 _end_-1 的子串  |
|toUpp­erC­ase() |返回 _s_ 的全大写副本  |
|toLow­erC­ase() |返回 _s_ 的小写副本  |
|indexOf(_x_) |_x_ 首次出现的位置  |
|replace(_old_, _new_)|查找并替换  |
|split(_regex_) |将字符串拆分为标记  |
|trim()  |去除首尾空白  |
|equals(_s2_)  |若 s 等于 s2 则返回 true  |
|equalsIgnoreCase(_s2_) | 忽略大小写，若 s 等于 s2 则返回 true |
|compareTo(_s2_)  | 相等返回 0 / s>s2 返回正 / s<s2 返回负 |
|concat(_s2_) | 将 s2 追加到 s 的末尾 |
|contains(_s2_) | 检查 s 是否包含字符序列 s2 |
|replace(_s2_) | 查找指定的字符串 s2，并返回替换指定值后的新字符串 |
|toCharArray() | 将字符串转换为新的字符数组 |

**[🔼Back to Top](#table-of-contents)**

<a id="math-library-methods"></a>
## Math Library Methods

|命令|说明|
|--|--|
|abs(_x_)|x 的绝对值|
|max(a, b| a 和 b 中的最大值|
|min(a, b)| a 和 b 中的最小值|
|E| _e（常数）的值_|
|sin(theta)| theta 的正弦值|
|cos(theta| theta 的余弦值|
|tan(theta)| theta 的正切值|
|round(_x_)| 返回 x 四舍五入为最接近的整数|

**[🔼Back to Top](#table-of-contents)**

<a id="types-of-variables"></a>
## Types of Variables

|变量类型|作用域|生命周期|
|--|--|--|
|实例变量|在整个类中（静态方法除外）|直到对象在内存中存在期间|
|类变量|在整个类中|直到程序结束|
|局部变量|在声明它的代码块内|直到控制离开声明它的代码块| 

**[🔼Back to Top](#table-of-contents)**

<a id="java-regex"></a>
## Java Regex 

<a id="matcher-class"></a>
### Matcher Class

|方法|说明|
|--|--|
|matches()|测试正则表达式是否匹配模式|
|find()|查找下一个匹配模式的表达式|
|find(int a)| 从起始序号 _a_ 开始查找下一个匹配的表达式|
|group()|返回匹配的子序列 |
|start()|返回匹配子序列的起始索引|
|end()|返回匹配子序列的结束索引|

**[🔼Back to Top](#table-of-contents)**

<a id="inheritance-in-java"></a>
## Inheritance in Java

> 继承 —— 这是子/派生/子类所拥有的特性，使其能够从父/基/超类继承属性（properties）和函数功能或数据成员方法。

___Java 支持 4 种继承方式：___

1.	单继承
2.	多层继承
3.	分层继承
4.	混合继承 

**[🔼Back to Top](#table-of-contents)**

<a id="single-inheritance"></a>
### Single Inheritance: 

> 顾名思义，只有一个类属于这种继承方式。父类只派生出一个子类。

___语法：___

```java
Class A{
  //your parent class code
}
Class B extends A {
   //your child class code
} 
```

**[🔼Back to Top](#table-of-contents)**

<a id="multi-level-inheritance"></a>
### Multi-Level Inheritance:

> 在多层继承中，一个类有多个父类，但处于不同的继承层级。

___语法：___

```java
Class A{
  //your parent class code
}
Class B extends A {
   //your code
}
Class C extends B {
    //your code 
} 
```

**[🔼Back to Top](#table-of-contents)**

<a id="hierarchical-inheritance"></a>
### Hierarchical Inheritance

> 在分层继承中，一个父类可以拥有一个或多个子/派/派生类。

___语法：___

```java
Class A{
  //your parent class code
}
Class B extends A {
   //your child class code
}
Class C extends A {
    //your child class code 
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="hybrid-inheritance"></a>
### Hybrid Inheritance:

> 混合继承是在同一个程序中组合了多种继承方式。

**[🔼Back to Top](#table-of-contents)**

<a id="note"></a>
## NOTE

> Java 不支持多重继承，因为这会导致菱形问题（diamond problem）。<br /> 我们可以通过抽象（Abstraction）的概念在 Java 中实现多重继承。

**[🔼Back to Top](#table-of-contents)**

<a id="encapsulation-in-java"></a>
## Encapsulation in Java

> 封装 —— 是将数据成员（变量）和函数（方法）作为一个整体单元包裹在一起。它也被称为**数据隐藏**，因为类的变量对其他类隐藏，只能通过该类的方法访问。

Java 中的封装可以通过包来实现

**[🔼Back to Top](#table-of-contents)**

<a id="java-packages"></a>
### Java Packages

> Java 包是一组相似类型的类、接口和子包。它提供访问保护并防止命名冲突。

```java
package mypack;
public class Demo{
	public static void main(String args[]){
		­ _statements_  
	}
}
```
**编译：** javac -d . Demo.java
**运行：** java mypack.Demo
**从另一个包访问包：** import package.* 或 import package.className.*

**[🔼Back to Top](#table-of-contents)**

<a id="abstraction-in-java"></a>
## Abstraction in Java

> 抽象是隐藏实现细节、只向用户展示功能的过程。

___Java 中可以通过 2 种方式实现抽象___

1.	抽象类
2.	接口

**[🔼Back to Top](#table-of-contents)**

<a id="abstract-class"></a>
### Abstract class

> 使用 abstract 关键字声明的类，无法被实例化，必须由其他类继承以实现其方法。它可以同时包含抽象方法和非抽象方法。

```java
    abstract class A{  
      abstract void demo();  
    }  
	//Abstract class extended by other class to implement its methods
	class B extends A{
		void demo(){
			_statements_  
		}
	}
```
**[🔼Back to Top](#table-of-contents)**

<a id="interface"></a>
### Interface 

> 接口是类的蓝图，包含公共抽象方法和公共静态最终常量。它无法被实例化。接口可由其他接口扩展，并由类实现。

```java
interface Printable{
	void print(); //empty method body
}
class Demo implements Printable{
	public void print(){
		_statements_
	}
}
```
**[🔼Back to Top](#table-of-contents)**

<a id="polymorphism-in-java"></a>
## Polymorphism in Java

> 多态是指我们可以通过不同方式执行同一动作的概念。它分为两种：编译时多态（方法重载）和运行时多态（方法重写）。

**[🔼Back to Top](#table-of-contents)**

<a id="method-overloading"></a>
### Method overloading

> 这是编译时多态。如果一个类拥有多个同名但参数不同的方法，则称为方法重载。参数可以在参数个数或参数数据类型上有所不同。

```java
class Demo{
	int add(int a, int b){return a+b;}
	double add(double a, double b, double c){return a+b+c;}
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="method-overriding"></a>
### Method overriding

> 这是运行时多态。如果子类提供了父类中声明方法的具体实现，则称为方法重写。

```java
class Vehicle{
	void run(){System.out.println("Vehicle is running")};
}
class Car{
	void run(){System.out.println("Car is running")};
}
```

**[🔼Back to Top](#table-of-contents)**

<a id="collections"></a>
## Collections

|集合|说明|
|-----|-----|
|Set| Set 是不包含重复值的元素集合。Set 由 HashSet、LinkedHashSet、TreeSet 等实现|
|List| List 是有序的元素集合，可以包含重复值。List 分为 ArrayList、LinkedList、Vector|
|Queue| 先进先出（FIFO）方式，实例化 Queue 接口时可以选择 LinkedList 或 PriorityQueue。|
|Stack| 后进先出（LIFO）方式，stack 是 vector 的子类，用于执行不同的操作。|
|Deque| Deque（双端队列）用于在 Queue 的两端（头部和尾部）添加或移除元素|
|Map| Map 包含没有重复键的键值对。Map 由 HashMap、TreeMap 等实现。|

**[🔼Back to Top](#table-of-contents)**
