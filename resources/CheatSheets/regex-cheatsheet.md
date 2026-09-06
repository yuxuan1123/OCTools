---
Title: 正则表达式 速查表
Description: 编程所需的所有正则表达式命令
Created: 2022-10-27
---

<a id="table-of-contents"></a>
## 目录

- [面向开发者的正则表达式 (RegEx) 速查表](#regular-expressions-regex-cheatsheet-for-developers)
  - [正则表达式简介](#regular-expressions-introduction)
  - [锚点](#anchors)
  - [量词](#quantifiers)
  - [分组与范围](#groups-and-ranges)
  - [转义序列](#escape-sequences)
  - [常见元字符](#common-meta-characters)
  - [特殊字符](#special-characters)
  - [断言](#assertions)
  - [字符串替换](#string-replacement)
  - [模式修饰符](#pattern-modifiers)

<a id="regular-expressions-regex-cheatsheet-for-developers"></a>
# Regular Expressions (RegEx) CheatSheet for Developers

<a id="regular-expressions-introduction"></a>
## Regular Expressions Introduction

> 正则表达式（也称为有理表达式）是指定文本中搜索模式的字符序列。此类模式常用于字符串搜索算法中，对字符串执行"查找"和"查找并替换"操作，或用于校验输入。

**[🔼Back to Top](#table-of-contents)**

<a id="anchors"></a>
## Anchors

| Operators     |                       Description                       |
|:-------------:|:-------------------------------------------------------:|
|      `^`      | 字符串开头，或多行模式中的行首 |
|      `\A`     |                     字符串开头                     |
|      `$`      |   字符串结尾，或多行模式中的行尾   |
|      `\Z`     |                      字符串结尾                      |
|      `\b`     |                      单词边界                      |
|      `\B`     |                    非单词边界                    |
|      `\<`     |                      单词开头                      |
|      `\>`     |                       单词结尾                       |

**[🔼Back to Top](#table-of-contents)**

<a id="quantifiers"></a>
## Quanti­fiers

| Operators | Occurrence    | Example   | Description   |
|:---------:|:-------------:|:---------:|:-------------:|
| `?`       |   **0 或 1**  | **{3,5}** | **3、4 或 5** |
|   `*`     | **0 或更多** |  **{3}**  | **恰好 3** |
| `+`       | **1 或更多** |  **{3,}** | **3 或更多** |

在量词后添加 `?` 可使其变为非贪婪。

**[🔼Back to Top](#table-of-contents)**

<a id="groups-and-ranges"></a>
## Groups and Ranges

|  Operator  |             Description            |
|:----------:|:----------------------------------:|
| `.`        | 除换行符 (\n) 外的任意字符 |
| `(a\|b)`   | a 或 b                             |
| `(...)`    | 分组                              |
| `(?:...)`  | 被动（非捕获）分组      |
| `[abc]`    | 范围（a 或 b 或 c）                |
| `[^abc]`   | 非（a 或 b 或 c）                  |
| `[a-q]`    | 从 a 到 q 的小写字母      |
| `[A-Q]`    | 从 A 到 Q 的大写字母      |
| `[0-7]`    | 从 0 到 7 的数字                  |
| `\x`       | 分组/子模式编号 "x"        |

范围包含两端。

**[🔼Back to Top](#table-of-contents)**

<a id="escape-sequences"></a>
## Escape Sequences

|   Operator   |         Description         |
|:----------:  |:---------------------------:|
| `\`          | 转义其后的字符  |
| `\Q`         | 开始字面量序列      |
| `\E`         | 结束字面量序列        |

> `Escaping` 是一种将正则中具有特殊含义的字符按字面量处理，而非作为特殊字符的方式。

**[🔼Back to Top](#table-of-contents)**

<a id="common-meta-characters"></a>
## Common Meta-characters

| `^` | `[` | `.`  | `$`  |
|-----|-----|------|------|
| `{` | `*` | `(`  | `\`  |
| `+` | `)` | `\|` | `?`  |
| `<` | `>` |      |      |

转义字符通常为 `\`

**[🔼Back to Top](#table-of-contents)**

<a id="special-characters"></a>
## Special Characters

|  Operator  |     Description     |
|:----------:|:-------------------:|
| `\n`       | 换行符            |
| `\r`       | 回车符     |
| `\t`       | 制表符                 |
| `\v`       | 垂直制表符        |
| `\f`       | 换页符        |
| `\xxx`     | 八进制字符 xxx |
| `\xhh`     | 十六进制字符 hh    |

**[🔼Back to Top](#table-of-contents)**

<a id="assertions"></a>
## Assertions

|  Operator                    |        Description       |
|:----------------------------:|:------------------------:|
| `?=`                         | 正向先行断言      |
| `?!`                         | 负向先行断言       |
| `?<=`                        | 正向后行断言     |
| `?!=` <br /> or <br /> `?<!` | 负向后行断言      |
| `?>`                         | 一次性子表达式  |
| `?()`                        | 条件 [若 则]      |
| `?()\|`                      | 条件 [若 则 否则] |
| `?#`                         | 注释                  |

**[🔼Back to Top](#table-of-contents)**

<a id="string-replacement"></a>
## String Replacement

| Operator       |           Description          |
|:--------------:|:------------------------------:|
|    `$n`        |      第 n 个非被动分组     |
|    `$2`        |   /^(abc(xyz))$ 中的 "xyz"       |
|    `$1`        | /^(?:abc)(xyz)$/ 中的 "xyz"      |
|    `` $` ``    |      匹配字符串之前的内容     |
|    `$'`        |      匹配字符串之后的内容      |
|    `$+`        |       最后匹配到的字符串      |
|    `$&`        |      整个匹配到的字符串     |

某些正则实现使用 `\` 而非 `$`。

**[🔼Back to Top](#table-of-contents)**

<a id="pattern-modifiers"></a>
## Pattern Modifiers

| Operator   |                Description               |
|:----------:|:----------------------------------------:|
|     `g`    |               全局匹配               |
|    `i *`   |            不区分大小写              |
|    `m *`   |              多行              |
|    `s *`   |        将字符串视为单行       |
|    `x *`   | 允许模式中的注释和空白 |
|    `e *`   |           求值替换           |
|    `U *`   |             非贪婪模式             |

> `*` --> ___PCRE 修饰符___

**[🔼Back to Top](#table-of-contents)**
