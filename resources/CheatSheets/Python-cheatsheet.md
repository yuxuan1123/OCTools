---
title: Python 速查表
description: 这里给出了最常用的 Python 概念。
created: 2022-10-20
---

# Python 开发者速查表

<a id="content-outlines"></a>
<a id="table-of-contents"></a>
## 内容大纲

**&nbsp;&nbsp;&nbsp;** **1. 集合：** **&nbsp;** **[`List`](#list)**__,__ **[`Dictionary`](#dictionary)**__,__ **[`Set`](#set)**__,__ **[`Tuple`](#tuple)**__,__ **[`Range`](#range)**__,__ **[`Enumerate`](#enumerate)**__,__ **[`Iterator`](#iterator)**__,__ **[`Generator`](#generator)**__.__  
**&nbsp;&nbsp;&nbsp;** **2. 类型：** **&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**  **[`Type`](#type)**__,__ **[`String`](#string)**__,__ **[`Regular_Exp`](#regex)**__,__ **[`Format`](#format)**__,__ **[`Numbers`](#numbers-1)**__,__ **[`Combinatorics`](#combinatorics)**__,__ **[`Datetime`](#datetime)**__.__  
**&nbsp;&nbsp;&nbsp;** **3. 语法：** **&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**  **[`Args`](#arguments)**__,__ **[`Inline`](#inline)**__,__ **[`Import`](#imports)**__,__ **[`Decorator`](#decorator)**__,__ **[`Class`](#class)**__,__ **[`Duck_Types`](#duck-types)**__,__ **[`Enum`](#enum)**__,__ **[`Exception`](#exceptions)**__.__  
**&nbsp;&nbsp;&nbsp;** **4. 系统：** **&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**  **[`Exit`](#exit)**__,__ **[`Print`](#print)**__,__ **[`Input`](#input)**__,__ **[`Command_Line_Arguments`](#command-line-arguments)**__,__ **[`Open`](#open)**__,__ **[`Path`](#paths)**__,__ **[`OS_Commands`](#os-commands)**__.__  
**&nbsp;&nbsp;&nbsp;** **5. 数据：** **&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**  **[`JSON`](#json)**__,__ **[`Pickle`](#pickle)**__,__ **[`CSV`](#csv)**__,__ **[`SQLite`](#sqlite)**__,__ **[`Bytes`](#bytes)**__,__ **[`Struct`](#struct)**__,__ **[`Array`](#array)**__,__ **[`Memory_View`](#memory-view)**__,__ **[`Deque`](#deque)**__.__  
**&nbsp;&nbsp;&nbsp;** **6. 高级：** **&nbsp;&nbsp;&nbsp;**  **[`Threading`](#threading)**__,__ **[`Operator`](#operator)**__,__ **[`Introspection`](#introspection)**__,__ **[`Metaprograming`](#metaprogramming)**__,__ **[`Eval`](#eval)**__,__ **[`Coroutines`](#coroutines)**__.__  
**&nbsp;&nbsp;&nbsp;** **7. 库：** **&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**  **[`Progress_Bar`](#progress-bar)**__,__ **[`Plot`](#plot)**__,__ **[`Table`](#table)**__,__ **[`Curses`](#curses)**__,__ **[`Logging`](#logging)**__,__ **[`Scraping`](#scraping)**__,__ **[`Web`](#web)**__,__ **[`Profile`](#profiling)**__,__  
**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;** **[`NumPy`](#numpy)**__,__ **[`Image`](#image)**__,__ **[`Audio`](#audio)**__,__ **[`PyGames`](#pygame)**__,__ **[`Pandas`](#pandas)**__,__ **[`OpenCV`](#opencv)**__,__ **[`DataFrame`](#dataframe)**__.__


Main
----
```python
if __name__ == '__main__':     # Runs main() if file wasn't imported.
    main()
```

**[🔼Back to Top](#content-outlines)**

注释/取消注释所选代码的快捷键
----

| Editor       | Shortcut Block Comment	  | Shortcut Block Uncomment |
| :----------: | :----------------------: | :----------------------: | 
| Eclipse      |  `CTRL + /`	          |     `CTRL + /`           | 
| PyDev	       |  `CTRL + /`	          |     `CTRL + /`           | 
| PyCharm	   |  `CTRL + /`	          |     `CTRL + /`           | 
| Notepad++    |  `CTRL + K`	          |     `CTRL + SHIFT + K`   | 
| IDLE	       |  `ALT + 3`	              |     `ALT + 4`            | 

**[🔼Back to Top](#content-outlines)**

<a id="list"></a>
列表
----
```python
<list> = <list>[<slice>]       # Or: <list>[from_inclusive : to_exclusive : ±step]
```

```python
<list>.append(<el>)            # Or: <list> += [<el>] | adds a new element to the end of the list
<list>.extend(<collection>)    # Or: <list> += <collection> | adds all elements of a collection(list,tuples,etc) to the end of the list
```

```python
<list>.sort()                  # Sorts in ascending order.
<list>.reverse()               # Reverses the list in-place.
<list> = sorted(<collection>)  # Returns a new sorted list.
<iter> = reversed(<list>)      # Returns reversed iterator.
```

```python
sum_of_elements  = sum(<collection>)
elementwise_sum  = [sum(pair) for pair in zip(list_a, list_b)]
sorted_by_second = sorted(<collection>, key=lambda el: el[1])
sorted_by_both   = sorted(<collection>, key=lambda el: (el[1], el[0]))
flatter_list     = list(itertools.chain.from_iterable(<list>))
product_of_elems = functools.reduce(lambda out, el: out * el, <collection>)
list_of_chars    = list(<str>)
```
* **关于 sorted()、min() 和 max() 的详情，请参阅 [sortable](#sortable)。**
* **模块 [operator](#operator) 提供的 itemgetter() 和 mul() 函数，提供了与上述 [lambda](#lambda) 表达式相同的功能。**

```python
<list>.insert(<int>, <el>)     # Inserts item at index and moves the rest to the right.
<el>  = <list>.pop([<int>])    # Removes and returns item at index or from the end.
<int> = <list>.count(<el>)     # Returns number of occurrences. Also works on strings.
<int> = <list>.index(<el>)     # Returns index of the first occurrence or raises ValueError.
<list>.remove(<el>)            # Removes first occurrence of the item or raises ValueError.
<list>.clear()                 # Removes all items. Also works on dictionary and set.
```

**[🔼Back to Top](#content-outlines)**

<a id="dictionary"></a>
字典
----------
```python
<view> = <dict>.keys()                          # Coll. of keys that reflects changes.
<view> = <dict>.values()                        # Coll. of values that reflects changes.
<view> = <dict>.items()                         # Coll. of key-value tuples that reflects chgs.
```
```python
value  = <dict>.get(key, default=None)          # Returns default if key is missing.
value  = <dict>.setdefault(key, default=None)   # Returns and writes default if key is missing.
<dict> = collections.defaultdict(<type>)        # Returns a dict with default value of type.
<dict> = collections.defaultdict(lambda: 1)     # Returns a dict with default value 1.
```

```python
<dict> = dict(<collection>)                     # Creates a dict from coll. of key-value pairs.
<dict> = dict(zip(keys, values))                # Creates a dict from two collections.
<dict> = dict.fromkeys(keys [, value])          # Creates a dict from collection of keys.
```

```python
<dict>.update(<dict>)                           # Adds items. Replaces ones with matching keys.
value = <dict>.pop(key)                         # Removes item or raises KeyError.
{k for k, v in <dict>.items() if v == value}    # Returns set of keys that point to the value.
{k: v for k, v in <dict>.items() if k in keys}  # Returns a dictionary, filtered by keys.
```

### Counter
```python
>>> from collections import Counter
>>> colors = ['blue', 'blue', 'blue', 'red', 'red']
>>> counter = Counter(colors)
>>> counter['yellow'] += 1
Counter({'blue': 3, 'red': 2, 'yellow': 1})
>>> counter.most_common()[0]
('blue', 3)
```

**[🔼Back to Top](#content-outlines)**

<a id="set"></a>
集合
---
```python
<set> = set()                                   # `{}` returns a dictionary.
```

```python
<set>.add(<el>)                                 # Or: <set> |= {<el>}
<set>.update(<collection> [, ...])              # Or: <set> |= <set>
```

```python
<set>  = <set>.union(<coll.>)                   # Or: <set> | <set>
<set>  = <set>.intersection(<coll.>)            # Or: <set> & <set>
<set>  = <set>.difference(<coll.>)              # Or: <set> - <set>
<set>  = <set>.symmetric_difference(<coll.>)    # Or: <set> ^ <set>
<bool> = <set>.issubset(<coll.>)                # Or: <set> <= <set>
<bool> = <set>.issuperset(<coll.>)              # Or: <set> >= <set>
```

```python
<el> = <set>.pop()                              # Raises KeyError if empty.
<set>.remove(<el>)                              # Raises KeyError if missing.
<set>.discard(<el>)                             # Doesn't raise an error.
```

### Frozen Set
* **不可变且可哈希。**
* **这意味着它可以作为字典的键或集合中的元素使用。**
```python
<frozenset> = frozenset(<collection>)
```

**[🔼Back to Top](#content-outlines)**

<a id="tuple"></a>
元组
-----
**元组是一个不可变且可哈希的列表。**
```python
<tuple> = ()                                # Empty tuple.
<tuple> = (<el>,)                           # Or: <el>,
<tuple> = (<el_1>, <el_2> [, ...])          # Or: <el_1>, <el_2> [, ...]
```

### Named Tuple
**具有命名元素的元组子类。**

```python
>>> from collections import namedtuple
>>> Point = namedtuple('Point', 'x y')
>>> p = Point(1, y=2)
Point(x=1, y=2)
>>> p[0]
1
>>> p.x
1
>>> getattr(p, 'y')
2
```

**[🔼Back to Top](#content-outlines)**

<a id="range"></a>
范围
-----
**不可变且可哈希的整数序列。**
```python
<range> = range(stop)                       # range(to_exclusive)
<range> = range(start, stop)                # range(from_inclusive, to_exclusive)
<range> = range(start, stop, ±step)         # range(from_inclusive, to_exclusive, ±step_size)
```

```python
>>> [i for i in range(3)]
[0, 1, 2]
```

**[🔼Back to Top](#content-outlines)**

<a id="enumerate"></a>
枚举
---------
```python
for i, el in enumerate(<collection> [, i_start]):
    ...
```

**[🔼Back to Top](#content-outlines)**

<a id="iterator"></a>
迭代器
--------
```python
<iter> = iter(<collection>)                 # `iter(<iter>)` returns unmodified iterator.
<iter> = iter(<function>, to_exclusive)     # A sequence of return values until 'to_exclusive'.
<el>   = next(<iter> [, default])           # Raises StopIteration or returns 'default' on end.
<list> = list(<iter>)                       # Returns a list of iterator's remaining elements.
```

<a id="itertools"></a>
### Itertools
```python
import itertools as it
```

```python
<iter> = it.count(start=0, step=1)          # Returns updated value endlessly. Accepts floats.
<iter> = it.repeat(<el> [, times])          # Returns element endlessly or 'times' times.
<iter> = it.cycle(<collection>)             # Repeats the sequence endlessly.
```

```python
<iter> = it.chain(<coll>, <coll> [, ...])   # Empties collections in order (figuratively).
<iter> = it.chain.from_iterable(<coll>)     # Empties collections inside a collection in order.
```

```python
<iter> = it.islice(<coll>, to_exclusive)    # Only returns first 'to_exclusive' elements.
<iter> = it.islice(<coll>, from_inc, …)     # `to_exclusive, +step_size`. Indices can be None.
```

**[🔼Back to Top](#content-outlines)**

<a id="generator"></a>
生成器
---------
* **任何包含 yield 语句的函数都会返回一个生成器。**
* **生成器和迭代器可以互换使用。**

```python
def count(start, step):
    while True:
        yield start
        start += step
```

```python
>>> counter = count(10, 2)
>>> next(counter), next(counter), next(counter)
(10, 12, 14)
```

**[🔼Back to Top](#content-outlines)**

<a id="type"></a>
类型
----
* **一切皆对象。**
* **每个对象都有一个类型。**
* **类型与类是同义词。**

```python
<type> = type(<el>)                          # Or: <el>.__class__
<bool> = isinstance(<el>, <type>)            # Or: issubclass(type(<el>), <type>)
```

```python
>>> type('a'), 'a'.__class__, str
(<class 'str'>, <class 'str'>, <class 'str'>)
```

#### Some types do not have built-in names, so they must be imported:
```python
from types import FunctionType, MethodType, LambdaType, GeneratorType, ModuleType
```

### Abstract Base Classes
**每个抽象基类（ABC）都规定了一组虚拟子类。这些类随后会被 isinstance() 和 issubclass() 识别为 ABC 的子类，尽管它们实际上并不是。ABC 也可以手动决定某个特定类是否为它的虚拟子类，通常基于该类实现了哪些方法。例如，Iterable ABC 会查找 iter() 方法，而 Collection ABC 会查找 iter()、contains() 和 len()。**

```python
>>> from collections.abc import Iterable, Collection, Sequence
>>> isinstance([1, 2, 3], Iterable)
True
```

```text
+------------------+------------+------------+------------+
|                  |  Iterable  | Collection |  Sequence  |
+------------------+------------+------------+------------+
| list, range, str |    yes     |    yes     |    yes     |
| dict, set        |    yes     |    yes     |            |
| iter             |    yes     |            |            |
+------------------+------------+------------+------------+
```

```python
>>> from numbers import Number, Complex, Real, Rational, Integral
>>> isinstance(123, Number)
True
```

```text
+--------------------+----------+----------+----------+----------+----------+
|                    |  Number  |  Complex |   Real   | Rational | Integral |
+--------------------+----------+----------+----------+----------+----------+
| int                |   yes    |   yes    |   yes    |   yes    |   yes    |
| fractions.Fraction |   yes    |   yes    |   yes    |   yes    |          |
| float              |   yes    |   yes    |   yes    |          |          |
| complex            |   yes    |   yes    |          |          |          |
| decimal.Decimal    |   yes    |          |          |          |          |
+--------------------+----------+----------+----------+----------+----------+
```

**[🔼Back to Top](#content-outlines)**

<a id="string"></a>
字符串
------
```python
<str>  = <str>.strip()                       # Strips all whitespace characters from both ends.
<str>  = <str>.strip('<chars>')              # Strips all passed characters from both ends.
```

```python
<list> = <str>.split()                       # Splits on one or more whitespace characters.
<list> = <str>.split(sep=None, maxsplit=-1)  # Splits on 'sep' str at most 'maxsplit' times.
<list> = <str>.splitlines(keepends=False)    # On [\n\r\f\v\x1c-\x1e\x85\u2028\u2029] and \r\n.
<str>  = <str>.join(<coll_of_strings>)       # Joins elements using string as a separator.
```

```python
<bool> = <sub_str> in <str>                  # Checks if string contains a substring.
<bool> = <str>.startswith(<sub_str>)         # Pass tuple of strings for multiple options.
<bool> = <str>.endswith(<sub_str>)           # Pass tuple of strings for multiple options.
<int>  = <str>.find(<sub_str>)               # Returns start index of the first match or -1.
<int>  = <str>.index(<sub_str>)              # Same, but raises ValueError if missing.
```

```python
<str>  = <str>.replace(old, new [, count])   # Replaces 'old' with 'new' at most 'count' times.
<str>  = <str>.translate(<table>)            # Use `str.maketrans(<dict>)` to generate table.
```

```python
<str>  = chr(<int>)                          # Converts int to Unicode character.
<int>  = ord(<str>)                          # Converts Unicode character to int.
```
* **另有：`'lstrip()'`, `'rstrip()'` 和 `'rsplit()'`。**
* **另有：`'lower()'`, `'upper()'`, `'capitalize()'` 和 `'title()'`。**

### Property Methods
```text
+---------------+----------+----------+----------+----------+----------+
|               | [ !#$%…] | [a-zA-Z] |  [¼½¾]   |  [²³¹]   |  [0-9]   |
+---------------+----------+----------+----------+----------+----------+
| isprintable() |   yes    |   yes    |   yes    |   yes    |   yes    |
| isalnum()     |          |   yes    |   yes    |   yes    |   yes    |
| isnumeric()   |          |          |   yes    |   yes    |   yes    |
| isdigit()     |          |          |          |   yes    |   yes    |
| isdecimal()   |          |          |          |          |   yes    |
+---------------+----------+----------+----------+----------+----------+
```
* **另有：`'isspace()'` 检查 `'[ \t\n\r\f\v\x1c-\x1f\x85\u2000…]'`。**

**[🔼Back to Top](#content-outlines)**

<a id="regex"></a>
正则表达式
-----
```python
import re
<str>   = re.sub(<regex>, new, text, count=0)  # Substitutes all occurrences with 'new'.
<list>  = re.findall(<regex>, text)            # Returns all occurrences as strings.
<list>  = re.split(<regex>, text, maxsplit=0)  # Use brackets in regex to include the matches.
<Match> = re.search(<regex>, text)             # Searches for first occurrence of the pattern.
<Match> = re.match(<regex>, text)              # Searches only at the beginning of the text.
<iter>  = re.finditer(<regex>, text)           # Returns all occurrences as Match objects.
```

* **参数 'new' 可以是一个接受 Match 对象并返回字符串的函数。**
* **search() 和 match() 如果找不到匹配则返回 None。**
* **参数 `'flags=re.IGNORECASE'` 可与所有函数一起使用。**
* **参数 `'flags=re.MULTILINE'` 使 `'^'` 和 `'$'` 匹配每一行的开头/结尾。**
* **参数 `'flags=re.DOTALL'` 使点号也接受 `'\n'`。**
* **使用 `r'\1'` 或 `'\\1'` 表示反向引用（`'\1'` 会返回八进制码为 1 的字符）。**
* **在 `'*'` 和 `'+'` 后加 `'?''` 可使它们变为非贪婪匹配。**

### Match Object
```python
<str>   = <Match>.group()                      # Returns the whole match. Also group(0).
<str>   = <Match>.group(1)                     # Returns part in the first bracket.
<tuple> = <Match>.groups()                     # Returns all bracketed parts.
<int>   = <Match>.start()                      # Returns start index of the match.
<int>   = <Match>.end()                        # Returns exclusive end index of the match.
```

### Special Sequences
```python
'\d' == '[0-9]'                                # Matches decimal characters.
'\w' == '[a-zA-Z0-9_]'                         # Matches alphanumerics and underscore.
'\s' == '[ \t\n\r\f\v]'                        # Matches whitespaces.
```

* **默认情况下，会匹配所有字母表中的十进制字符、字母数字字符和空白字符，除非使用了 `'flags=re.ASCII'` 参数。**
* **如上所示，它会将所有特殊序列的匹配限制在最初的 128 个字符内，并阻止 `'\s'` 接受 `'[\x1c-\x1f]'`（即所谓的分隔符字符）。**
* **使用大写字母表示取反（与 ASCII 标志组合使用时，将匹配所有非 ASCII 字符）。**

**[🔼Back to Top](#content-outlines)**

<a id="format"></a>
格式化
------
```python
<str> = f'{<el_1>}, {<el_2>}'            # Curly brackets can also contain expressions. This is named "Fstring"
<str> = '{}, {}'.format(<el_1>, <el_2>)  # Or: '{0}, {a}'.format(<el_1>, a=<el_2>)
<str> = '%s, %s' % (<el_1>, <el_2>)      # Redundant and inferior C style formatting.
```

### Attributes
```python
>>> Person = collections.namedtuple('Person', 'name height')
>>> person = Person('Jean-Luc', 187)
>>> f'{person.height}'
'187'
>>> '{p.height}'.format(p=person)
'187'
```

### General Options
```python
{<el>:<10}                               # '<el>      '
{<el>:^10}                               # '   <el>   '
{<el>:>10}                               # '      <el>'
{<el>:.<10}                              # '<el>......'
{<el>:0}                                 # '<el>'
```
* **选项可动态生成：`f'{<el>:{<str/int>}[…]}'`。**
* **在冒号前加 `'!r'` 会通过调用其 [repr()](#class) 方法将对象转换为字符串。**

### Strings
```python
{'abcde':10}                             # 'abcde     '
{'abcde':10.3}                           # 'abc       '
{'abcde':.3}                             # 'abc'
{'abcde'!r:10}                           # "'abcde'   "
```

### Numbers
```python
{123456:10}                              # '    123456'
{123456:10,}                             # '   123,456'
{123456:10_}                             # '   123_456'
{123456:+10}                             # '   +123456'
{123456:=+10}                            # '+   123456'
{123456: }                               # ' 123456'
{-123456: }                              # '-123456'
```

### Floats
```python
{1.23456:10.3}                           # '      1.23'
{1.23456:10.3f}                          # '     1.235'
{1.23456:10.3e}                          # ' 1.235e+00'
{1.23456:10.3%}                          # '  123.456%'
```

#### Comparison of presentation types:
```text
+--------------+----------------+----------------+----------------+----------------+
|              |    {<float>}   |   {<float>:f}  |   {<float>:e}  |   {<float>:%}  |
+--------------+----------------+----------------+----------------+----------------+
|  0.000056789 |   '5.6789e-05' |    '0.000057'  | '5.678900e-05' |    '0.005679%' |
|  0.00056789  |   '0.00056789' |    '0.000568'  | '5.678900e-04' |    '0.056789%' |
|  0.0056789   |   '0.0056789'  |    '0.005679'  | '5.678900e-03' |    '0.567890%' |
|  0.056789    |   '0.056789'   |    '0.056789'  | '5.678900e-02' |    '5.678900%' |
|  0.56789     |   '0.56789'    |    '0.567890'  | '5.678900e-01' |   '56.789000%' |
|  5.6789      |   '5.6789'     |    '5.678900'  | '5.678900e+00' |  '567.890000%' |
| 56.789       |  '56.789'      |   '56.789000'  | '5.678900e+01' | '5678.900000%' |
+--------------+----------------+----------------+----------------+----------------+
```

```text
+--------------+----------------+----------------+----------------+----------------+
|              |  {<float>:.2}  |  {<float>:.2f} |  {<float>:.2e} |  {<float>:.2%} |
+--------------+----------------+----------------+----------------+----------------+
|  0.000056789 |    '5.7e-05'   |      '0.00'    |   '5.68e-05'   |      '0.01%'   |
|  0.00056789  |    '0.00057'   |      '0.00'    |   '5.68e-04'   |      '0.06%'   |
|  0.0056789   |    '0.0057'    |      '0.01'    |   '5.68e-03'   |      '0.57%'   |
|  0.056789    |    '0.057'     |      '0.06'    |   '5.68e-02'   |      '5.68%'   |
|  0.56789     |    '0.57'      |      '0.57'    |   '5.68e-01'   |     '56.79%'   |
|  5.6789      |    '5.7'       |      '5.68'    |   '5.68e+00'   |    '567.89%'   |
| 56.789       |    '5.7e+01'   |     '56.79'    |   '5.68e+01'   |   '5678.90%'   |
+--------------+----------------+----------------+----------------+----------------+
```
* **当既可以向上取整也可以向下取整时，会选择在最后一位得到偶数结果的那种。这使得 `'{6.5:.0f}'` 为 `'6'`，而 `'{7.5:.0f}'` 为 `'8'`。**
* **此规则仅影响可以用浮点数精确表示的数字（`.5`、`.25` 等）。**

### Ints
```python
{90:c}                                   # 'Z'
{90:b}                                   # '1011010'
{90:X}                                   # '5A'
```

**[🔼Back to Top](#content-outlines)**

<a id="numbers-1"></a>
数字
-------
```python
<int>      = int(<float/str/bool>)                # Or: math.floor(<float>)
<float>    = float(<int/str/bool>)                # Or: <real>e±<int>
<complex>  = complex(real=0, imag=0)              # Or: <real> ± <real>j
<Fraction> = fractions.Fraction(0, 1)             # Or: Fraction(numerator=0, denominator=1)
<Decimal>  = decimal.Decimal(<str/int>)           # Or: Decimal((sign, digits, exponent))
```
* **`'int(<str>)'` 和 `'float(<str>)'` 在遇到格式错误的字符串时会引发 ValueError。**
* **与大多数浮点数（其中 `'1.1 + 2.2 != 3.3'`）不同，Decimal 数字会被精确存储。**
* **浮点数可以用 `'math.isclose(<float>, <float>)'` 进行比较。**
* **Decimal 运算的精度通过 `'decimal.getcontext().prec = <int>'` 设置。**

### Basic Functions
```python
<num> = pow(<num>, <num>)                         # Or: <num> ** <num>
<num> = abs(<num>)                                # <float> = abs(<complex>)
<num> = round(<num> [, ±ndigits])                 # `round(126, -1) == 130`
```

### Math
```python
from math import e, pi, inf, nan, isinf, isnan    # `<el> == nan` is always False.
from math import sin, cos, tan, asin, acos, atan  # Also: degrees, radians.
from math import log, log10, log2                 # Log can accept base as second arg.
```

### Statistics
```python
from statistics import mean, median, variance     # Also: stdev, quantiles, groupby.
```

### Random
```python
from random import random, randint, choice        # Also shuffle, gauss, triangular, seed.
<float> = random()                                # A float inside [0, 1).
<int>   = randint(from_inc, to_inc)               # An int inside [from_inc, to_inc].
<el>    = choice(<sequence>)                      # Keeps the sequence intact.
```

### Bin, Hex
```python
<int> = ±0b<bin>                                  # Or: ±0x<hex>
<int> = int('±<bin>', 2)                          # Or: int('±<hex>', 16)
<int> = int('±0b<bin>', 0)                        # Or: int('±0x<hex>', 0)
<str> = bin(<int>)                                # Returns '[-]0b<bin>'.
```

### Bitwise Operators
```python
<int> = <int> & <int>                             # And (0b1100 & 0b1010 == 0b1000).
<int> = <int> | <int>                             # Or  (0b1100 | 0b1010 == 0b1110).
<int> = <int> ^ <int>                             # Xor (0b1100 ^ 0b1010 == 0b0110).
<int> = <int> << n_bits                           # Left shift. Use >> for right.
<int> = ~<int>                                    # Not. Also -<int> - 1.
```

**[🔼Back to Top](#content-outlines)**

<a id="combinatorics"></a>
组合数学
-------------
* **每个函数都返回一个迭代器。**
* **如果要打印迭代器，需要先将其传给 list() 函数！**

```python
import itertools as it
```

```python
>>> it.product([0, 1], repeat=3)
[(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
 (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
```

```python
>>> it.product('abc', 'abc')                      #   a  b  c
[('a', 'a'), ('a', 'b'), ('a', 'c'),              # a x  x  x
 ('b', 'a'), ('b', 'b'), ('b', 'c'),              # b x  x  x
 ('c', 'a'), ('c', 'b'), ('c', 'c')]              # c x  x  x
```

```python
>>> it.combinations('abc', 2)                     #   a  b  c
[('a', 'b'), ('a', 'c'),                          # a .  x  x
 ('b', 'c')]                                      # b .  .  x
```

```python
>>> it.combinations_with_replacement('abc', 2)    #   a  b  c
[('a', 'a'), ('a', 'b'), ('a', 'c'),              # a x  x  x
 ('b', 'b'), ('b', 'c'),                          # b .  x  x
 ('c', 'c')]                                      # c .  .  x
```

```python
>>> it.permutations('abc', 2)                     #   a  b  c
[('a', 'b'), ('a', 'c'),                          # a .  x  x
 ('b', 'a'), ('b', 'c'),                          # b x  .  x
 ('c', 'a'), ('c', 'b')]                          # c x  x  .
```

**[🔼Back to Top](#content-outlines)**

<a id="datetime"></a>
日期时间
--------
* **模块 'datetime' 提供 'date' `<D>`、'time' `<T>`、'datetime' `<DT>` 和 'timedelta' `<TD>` 类。它们都是不可变且可哈希的。**
* **时间和日期时间对象可以是 'aware' `<a>`（即已定义时区），也可以是 'naive' `<n>`（即未定义时区）。**
* **如果对象是 naive 的，则假定其处于系统的时区中。**

```python
from datetime import date, time, datetime, timedelta
from dateutil.tz import UTC, tzlocal, gettz, datetime_exists, resolve_imaginary
```

### Constructors
```python
<D>  = date(year, month, day)               # Only accepts valid dates from 1 to 9999 AD.
<T>  = time(hour=0, minute=0, second=0)     # Also: `microsecond=0, tzinfo=None, fold=0`.
<DT> = datetime(year, month, day, hour=0)   # Also: `minute=0, second=0, microsecond=0, …`.
<TD> = timedelta(weeks=0, days=0, hours=0)  # Also: `minutes=0, seconds=0, microsecond=0`.
```
* **使用 `'<D/DT>.weekday()'` 获取星期几（以整数表示，星期一为 0）。**
* **`'fold=1'` 表示时间回拨一小时时的第二次经过。**
* **Timedelta 会将参数归一化为 ±天、秒（< 86 400）和微秒（< 1M）。**

### Now
```python
<D/DTn>  = D/DT.today()                     # Current local date or naive datetime.
<DTn>    = DT.utcnow()                      # Naive datetime from current UTC time.
<DTa>    = DT.now(<tzinfo>)                 # Aware datetime from current tz time.
```
* **要提取时间，使用 `'<DTn>.time()'`, `'<DTa>.time()'` 或 `'<DTa>.timetz()'`。**

### Timezone
```python
<tzinfo> = UTC                              # UTC timezone. London without DST.
<tzinfo> = tzlocal()                        # Local timezone. Also gettz().
<tzinfo> = gettz('<Continent>/<City>')      # 'Continent/City_Name' timezone or None.
<DTa>    = <DT>.astimezone(<tzinfo>)        # Datetime, converted to the passed timezone.
<Ta/DTa> = <T/DT>.replace(tzinfo=<tzinfo>)  # Unconverted object with a new timezone.
```

<a id="encode"></a>
### Encode
```python
<D/T/DT> = D/T/DT.fromisoformat('<iso>')    # Object from ISO string. Raises ValueError.
<DT>     = DT.strptime(<str>, '<format>')   # Datetime from str, according to format.
<D/DTn>  = D/DT.fromordinal(<int>)          # D/DTn from days since the Gregorian NYE 1.
<DTn>    = DT.fromtimestamp(<real>)         # Local time DTn from seconds since the Epoch.
<DTa>    = DT.fromtimestamp(<real>, <tz.>)  # Aware datetime from seconds since the Epoch.
```
* **ISO 字符串有以下几种形式：`'YYYY-MM-DD'`、`'HH:MM:SS.mmmuuu[±HH:MM]'`，或两者用任意字符分隔。小时之后的所有部分都是可选的。**
* **Python 使用 Unix 纪元：`'1970-01-01 00:00 UTC'`、`'1970-01-01 01:00 CET'`……**

### Decode
```python
<str>    = <D/T/DT>.isoformat(sep='T')      # Also: `timespec='auto/hours/minutes/seconds/…'`.
<str>    = <D/T/DT>.strftime('<format>')    # Custom string representation.
<int>    = <D/DT>.toordinal()               # Days since Gregorian NYE 1, ignoring time and tz.
<float>  = <DTn>.timestamp()                # Seconds since the Epoch, from DTn in local tz.
<float>  = <DTa>.timestamp()                # Seconds since the Epoch, from aware datetime.
```

### Format
```python
>>> dt = datetime.strptime('2015-05-14 23:39:00.00 +2000', '%Y-%m-%d %H:%M:%S.%f %z')
>>> dt.strftime("%A, %dth of %B '%y, %I:%M%p %Z")
"Thursday, 14th of May '15, 11:39PM UTC+02:00"
```
* **`'%Z'` 只接受 `'UTC/GMT'` 和本地时区的代码。`'%z'` 也接受 `'±HH:MM'`。**
* **缩写星期和月份分别使用 `'%a'` 和 `'%b'`。**

### Arithmetics
```python
<D/DT>   = <D/DT>  ± <TD>                   # Returned datetime can fall into missing hour.
<TD>     = <D/DTn> - <D/DTn>                # Returns the difference, ignoring time jumps.
<TD>     = <DTa>   - <DTa>                  # Ignores time jumps if they share tzinfo object.
<TD>     = <TD>    * <real>                 # Also: <TD> = abs(<TD>) and <TD> = <TD> ±% <TD>.
<float>  = <TD>    / <TD>                   # How many weeks/years there are in TD. Also //.
```

**[🔼Back to Top](#content-outlines)**

<a id="arguments"></a>
参数
---------
### Inside Function Call
```python
func(<positional_args>)                           # func(0, 0)
func(<keyword_args>)                              # func(x=0, y=0)
func(<positional_args>, <keyword_args>)           # func(0, y=0)
```

### Inside Function Definition
```python
def func(<nondefault_args>): ...                  # def func(x, y): ...
def func(<default_args>): ...                     # def func(x=0, y=0): ...
def func(<nondefault_args>, <default_args>): ...  # def func(x, y=0): ...
```
* **默认值在函数首次在作用域中遇到时求值。**
* **对可变默认值的任何修改都会在多次调用之间保留。**


<a id="splat-operator"></a>
拆包运算符
--------------
### Inside Function Call
**拆包运算符将集合展开为位置参数，而双拆包运算符将字典展开为关键字参数。**
```python
args   = (1, 2)
kwargs = {'x': 3, 'y': 4, 'z': 5}
func(*args, **kwargs)
```

#### Is the same as:
```python
func(1, 2, x=3, y=4, z=5)
```

### Inside Function Definition
**拆包运算符将零个或多个位置参数组合为一个元组，而双拆包运算符将零个或多个关键字参数组合为一个字典。**
```python
def add(*a):
    return sum(a)
```

```python
>>> add(1, 2, 3)
6
```

#### Legal argument combinations:
```python
def f(*args): ...               # f(1, 2, 3)
def f(x, *args): ...            # f(1, 2, 3)
def f(*args, z): ...            # f(1, 2, z=3)
```

```python
def f(**kwargs): ...            # f(x=1, y=2, z=3)
def f(x, **kwargs): ...         # f(x=1, y=2, z=3) | f(1, y=2, z=3)
```

```python
def f(*args, **kwargs): ...     # f(x=1, y=2, z=3) | f(1, y=2, z=3) | f(1, 2, z=3) | f(1, 2, 3)
def f(x, *args, **kwargs): ...  # f(x=1, y=2, z=3) | f(1, y=2, z=3) | f(1, 2, z=3) | f(1, 2, 3)
def f(*args, y, **kwargs): ...  # f(x=1, y=2, z=3) | f(1, y=2, z=3)
```

```python
def f(*, x, y, z): ...          # f(x=1, y=2, z=3)
def f(x, *, y, z): ...          # f(x=1, y=2, z=3) | f(1, y=2, z=3)
def f(x, y, *, z): ...          # f(x=1, y=2, z=3) | f(1, y=2, z=3) | f(1, 2, z=3)
```

### Other Uses
```python
<list>  = [*<coll.> [, ...]]    # Or: list(<collection>) [+ ...]
<tuple> = (*<coll.>, [...])     # Or: tuple(<collection>) [+ ...]
<set>   = {*<coll.> [, ...]}    # Or: set(<collection>) [| ...]
<dict>  = {**<dict> [, ...]}    # Or: dict(**<dict> [, ...])
```

```python
head, *body, tail = <coll.>     # Head or tail can be omitted.
```

**[🔼Back to Top](#content-outlines)**

<a id="inline"></a>
内联
------
<a id="lambda"></a>
### Lambda
```python
<func> = lambda: <return_value>                     # A single statement function.
<func> = lambda <arg_1>, <arg_2>: <return_value>    # Also accepts default arguments.
```

<a id="comprehensions"></a>
### Comprehensions
```python
<list> = [i+1 for i in range(10)]                   # Or: [1, 2, ..., 10]
<iter> = (i for i in range(10) if i > 5)            # Or: iter([6, 7, 8, 9])
<set>  = {i+5 for i in range(10)}                   # Or: {5, 6, ..., 14}
<dict> = {i: i*2 for i in range(10)}                # Or: {0: 0, 1: 2, ..., 9: 18}
```

```python
>>> [l+r for l in 'abc' for r in 'abc']
['aa', 'ab', 'ac', ..., 'cc']
```

### Map, Filter, Reduce
```python
<iter> = map(lambda x: x + 1, range(10))            # Or: iter([1, 2, ..., 10])
<iter> = filter(lambda x: x > 5, range(10))         # Or: iter([6, 7, 8, 9])
<obj>  = reduce(lambda out, x: out + x, range(10))  # Or: 45
```
* **reduce 必须从 functools 模块导入。**

### Any, All
```python
<bool> = any(<collection>)                          # Is `bool(el)` True for any element.
<bool> = all(<collection>)                          # Is True for all elements or empty.
```

### Conditional Expression
```python
<obj> = <exp> if <condition> else <exp>             # Only one expression gets evaluated.
```

```python
>>> [a if a else 'zero' for a in (0, 1, 2, 3)]
['zero', 1, 2, 3]
```

### Named Tuple, Enum, Dataclass
```python
from collections import namedtuple
Point = namedtuple('Point', 'x y')                  # Creates a tuple's subclass.
point = Point(0, 0)                                 # Returns its instance.
```

```python
from enum import Enum
Direction = Enum('Direction', 'n e s w')            # Creates an enum.
direction = Direction.n                             # Returns its member.
```

```python
from dataclasses import make_dataclass
Player = make_dataclass('Player', ['loc', 'dir'])   # Creates a class.
player = Player(point, direction)                   # Returns its instance.
```

**[🔼Back to Top](#content-outlines)**

<a id="imports"></a>
导入
-------
```python
import <module>            # Imports a built-in or '<module>.py'.
import <package>           # Imports a built-in or '<package>/__init__.py'.
import <package>.<module>  # Imports a built-in or '<package>/<module>.py'.
```
* **包是模块的集合，但它也可以定义自己的对象。**
* **在文件系统上，这对应于一个包含 Python 文件的目录（带有一个可选的初始化脚本）。**
* **运行 `'import <package>'` 不会自动提供对包中模块的访问，除非它们在包的初始化脚本中被显式导入。**


<a id="closure"></a>
闭包
-------
**在 Python 中，当满足以下条件时，我们拥有/得到了一个闭包：**
* **嵌套函数引用了其外层函数的一个值，并且**
* **外层函数返回了该嵌套函数。**

```python
def get_multiplier(a):
    def out(b):
        return a * b
    return out
```

```python
>>> multiply_by_3 = get_multiplier(3)
>>> multiply_by_3(10)
30
```

* **如果外层函数中的多个嵌套函数引用了同一个值，则该值会被共享。**
* **要动态访问函数的第一个自由变量，使用 `'<function>.__closure__[0].cell_contents'`。**

### Partial
```python
from functools import partial
<function> = partial(<function> [, <arg_1>, <arg_2>, ...])
```

```python
>>> import operator as op
>>> multiply_by_3 = partial(op.mul, 3)
>>> multiply_by_3(10)
30
```
* **当函数需要作为参数传递时，partial 也很有用，因为它让我们能预先设置其参数。**
* **几个例子：`'defaultdict(<function>)'`、`'iter(<function>, to_exclusive)'` 以及 dataclass 的 `'field(default_factory=<function>)'`。**

### Non-Local
**如果变量在作用域中的任何地方被赋值，则它被视为局部变量，除非它被声明为 'global' 或 'nonlocal'。**

```python
def get_counter():
    i = 0
    def out():
        nonlocal i
        i += 1
        return i
    return out
```

```python
>>> counter = get_counter()
>>> counter(), counter(), counter()
(1, 2, 3)
```

**[🔼Back to Top](#content-outlines)**

<a id="decorator"></a>
装饰器
---------
* **装饰器接受一个函数，添加一些功能并返回它。**
* **它可以是任何 [callable](#callable)，但通常实现为返回 [closure](#closure) 的函数。**

```python
@decorator_name
def function_that_gets_passed_to_decorator():
    ...
```

### Debugger Example
**在每次调用函数时打印函数名称的装饰器。**

```python
from functools import wraps

def debug(func):
    @wraps(func)
    def out(*args, **kwargs):
        print(func.__name__)
        return func(*args, **kwargs)
    return out

@debug
def add(x, y):
    return x + y
```
* **wraps 是一个辅助装饰器，它将传入函数（func）的元数据复制到它正在包装的函数（out）上。**
* **如果没有它，`'add.__name__'` 将返回 `'out'`。**

### LRU Cache
**缓存函数返回值的装饰器。函数的所有参数都必须可哈希。**

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n-2) + fib(n-1)
```
* **缓存的默认大小为 128 个值。传入 `'maxsize=None'` 可使其无界。**
* **CPython 解释器默认将递归深度限制为 1000。要增加它，使用 `'sys.setrecursionlimit(<depth>)'`。**

### Parametrized Decorator
**接受参数并返回接受函数的普通装饰器的装饰器。**
```python
from functools import wraps

def debug(print_result=False):
    def decorator(func):
        @wraps(func)
        def out(*args, **kwargs):
            result = func(*args, **kwargs)
            print(func.__name__, result if print_result else '')
            return result
        return out
    return decorator

@debug(print_result=True)
def add(x, y):
    return x + y
```
* **在这里仅使用 `'@debug'` 来装饰 add() 函数是不行的，因为那样 debug 会把 add() 函数作为 'print_result' 参数接收。不过，装饰器可以手动检查它收到的参数是否为函数，并相应地采取行动。**

**[🔼Back to Top](#content-outlines)**

<a id="class"></a>
类
-----
```python
class <name>:
    def __init__(self, a):
        self.a = a
    def __repr__(self):
        class_name = self.__class__.__name__
        return f'{class_name}({self.a!r})'
    def __str__(self):
        return str(self.a)

    @classmethod
    def get_class_name(cls):
        return cls.__name__
```
* **repr() 的返回值应当明确无歧义，而 str() 的返回值应当可读。**
* **如果只定义了 repr()，它也会用于 str()。**
* **用 `'@staticmethod'` 装饰的方法不会把 'self' 或 'cls' 作为第一个参数接收。**

#### Str() use cases:
```python
print(<el>)
f'{<el>}'
logging.warning(<el>)
csv.writer(<file>).writerow([<el>])
raise Exception(<el>)
```

#### Repr() use cases:
```python
print/str/repr([<el>])
f'{<el>!r}'
Z = dataclasses.make_dataclass('Z', ['a']); print/str/repr(Z(<el>))
>>> <el>
```

### Constructor Overloading
```python
class <name>:
    def __init__(self, a=None):
        self.a = a
```

### Inheritance
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age  = age

class Employee(Person):
    def __init__(self, name, age, staff_num):
        super().__init__(name, age)
        self.staff_num = staff_num
```

### Multiple Inheritance
```python
class A: pass
class B: pass
class C(A, B): pass
```

**MRO 决定了在查找方法或属性时遍历父类的顺序：**
```python
>>> C.mro()
[<class 'C'>, <class 'A'>, <class 'B'>, <class 'object'>]
```

### Property
**实现 getter 和 setter 的 Python 风格做法。**
```python
class Person:
    @property
    def name(self):
        return ' '.join(self._name)

    @name.setter
    def name(self, value):
        self._name = value.split()
```

```python
>>> person = Person()
>>> person.name = '\t Guido  van Rossum \n'
>>> person.name
'Guido van Rossum'
```

### Dataclass
**自动生成 init()、repr() 和 eq() 特殊方法的装饰器。**
```python
from dataclasses import dataclass, field

@dataclass(order=False, frozen=False)
class <class_name>:
    <attr_name_1>: <type>
    <attr_name_2>: <type> = <default_value>
    <attr_name_3>: list/dict/set = field(default_factory=list/dict/set)
```
* **可通过 `'order=True'` 使对象可排序，通过 `'frozen=True'` 使对象不可变。**
* **要使对象可哈希，所有属性都必须可哈希，且 'frozen' 必须为 True。**
* **需要使用 field() 函数，因为 `'<attr_name>: list = []'` 会创建一个在所有实例之间共享的列表。它的 'default_factory' 参数可以是任意 [callable](#callable)。**
* **对于任意类型的属性，使用 `'typing.Any'`。**

#### Inline:
```python
from dataclasses import make_dataclass
<class> = make_dataclass('<class_name>', <coll_of_attribute_names>)
<class> = make_dataclass('<class_name>', <coll_of_tuples>)
<tuple> = ('<attr_name>', <type> [, <default_value>])
```

#### Rest of type annotations (CPython interpreter ignores them all):
```python
def func(<arg_name>: <type> [= <obj>]) -> <type>: ...
<var_name>: typing.List/Set/Iterable/Sequence/Optional[<type>]
<var_name>: typing.Dict/Tuple/Union[<type>, ...]
```

### Slots
**一种将对象限制为 'slots' 中列出的属性，并显著减少其内存占用的机制。**

```python
class MyClassWithSlots:
    __slots__ = ['a']
    def __init__(self):
        self.a = 1
```

### Copy
```python
from copy import copy, deepcopy
<object> = copy(<object>)
<object> = deepcopy(<object>)
```

**[🔼Back to Top](#content-outlines)**

<a id="duck-types"></a>
鸭子类型
----------
**鸭子类型是一种隐式类型，它规定了一组特殊方法。任何定义了这些方法的对象都被视为该鸭子类型的成员。**

### Comparable
* **如果未重写 eq() 方法，它会返回 `'id(self) == id(other)'`，这与 `'self is other'` 相同。**
* **这意味着默认情况下所有对象比较都不相等。**
* **只有左侧对象会调用 eq() 方法，除非它返回 NotImplemented，此时会咨询右侧对象。如果两者都返回 NotImplemented，则返回 False。**
* **ne() 会自动在任何定义了 eq() 的对象上工作。**

```python
class MyComparable:
    def __init__(self, a):
        self.a = a
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.a == other.a
        return NotImplemented
```

### Hashable
* **可哈希对象需要 hash() 和 eq() 方法，且其哈希值永远不应改变。**
* **比较相等的可哈希对象必须具有相同的哈希值，这意味着返回 `'id(self)'` 的默认 hash() 并不适用。**
* **这就是为什么如果你只实现 eq()，Python 会自动让类不可哈希。**

```python
class MyHashable:
    def __init__(self, a):
        self._a = a
    @property
    def a(self):
        return self._a
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.a == other.a
        return NotImplemented
    def __hash__(self):
        return hash(self.a)
```

<a id="sortable"></a>
### Sortable
* **使用 'total_ordering' 装饰器，你只需提供 eq() 以及 lt()、gt()、le() 或 ge() 中的一个特殊方法，其余的会自动生成。**
* **sorted() 和 min() 函数只需要 lt() 方法，而 max() 只需要 gt() 方法。不过，最好把它们都定义，以免在其他上下文中产生混淆。**
* **当两个列表、字符串或 dataclass 进行比较时，会按顺序比较它们的值，直到找到一对不相等的值。然后返回这两个值的比较结果。如果所有值都相等，则较短的序列被视为较小。**

```python
from functools import total_ordering

@total_ordering
class MySortable:
    def __init__(self, a):
        self.a = a
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.a == other.a
        return NotImplemented
    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.a < other.a
        return NotImplemented
```

### Iterator
* **任何拥有 next() 和 iter() 方法的对象都是迭代器。**
* **next() 应返回下一个项或引发 StopIteration。**
* **iter() 应返回 'self'。**
```python
class Counter:
    def __init__(self):
        self.i = 0
    def __next__(self):
        self.i += 1
        return self.i
    def __iter__(self):
        return self
```

```python
>>> counter = Counter()
>>> next(counter), next(counter), next(counter)
(1, 2, 3)
```

#### Python has many different iterator objects:
* **由 [iter()](#iterator) 函数返回的序列迭代器，例如 list\_iterator 和 set\_iterator。**
* **由 [itertools](#itertools) 模块返回的对象，例如 count、repeat 和 cycle。**
* **由 [generator functions](#generator) 和 [generator expressions](#comprehensions) 返回的生成器。**
* **由 [open()](#open) 函数返回的文件对象等。**

<a id="callable"></a>
### Callable
* **所有函数和类都有 call() 方法，因此都是可调用对象。**
* **当本速查表使用 `'<function>'` 作为参数时，实际上指的是 `'<callable>'`。**
```python
class Counter:
    def __init__(self):
        self.i = 0
    def __call__(self):
        self.i += 1
        return self.i
```

```python
>>> counter = Counter()
>>> counter(), counter(), counter()
(1, 2, 3)
```

### Context Manager
* **enter() 应锁定资源并可选择返回一个对象。**
* **exit() 应释放资源。**
* **with 块内发生的任何异常都会传递给 exit() 方法。**
* **如果希望抑制该异常，它必须返回一个真值。**
```python
class MyOpen:
    def __init__(self, filename):
        self.filename = filename
    def __enter__(self):
        self.file = open(self.filename)
        return self.file
    def __exit__(self, exc_type, exception, traceback):
        self.file.close()
```

```python
>>> with open('test.txt', 'w') as file:
...     file.write('Hello World!')
>>> with MyOpen('test.txt') as file:
...     print(file.read())
Hello World!
```


<a id="iterable-duck-types"></a>
可迭代鸭子类型
-------------------
### Iterable
* **唯一需要的方法是 iter()。它应返回对象各项的迭代器。**
* **contains() 会自动在任何定义了 iter() 的对象上工作。**
```python
class MyIterable:
    def __init__(self, a):
        self.a = a
    def __iter__(self):
        return iter(self.a)
    def __contains__(self, el):
        return el in self.a
```

```python
>>> obj = MyIterable([1, 2, 3])
>>> [el for el in obj]
[1, 2, 3]
>>> 1 in obj
True
```

### Collection
* **唯一需要的方法是 iter() 和 len()。len() 应返回项的数量。**
* **本速查表在使用 `'<collection>'` 时，实际上指的是 `'<iterable>'`。**
* **我选择不使用 'iterable' 这个名字，因为它听起来比 'collection' 更吓人、更含糊。这个决定的唯一缺点是，读者可能会认为某个函数不接受迭代器，而实际上它接受，因为迭代器是唯一可迭代但不是集合的内置对象。**
```python
class MyCollection:
    def __init__(self, a):
        self.a = a
    def __iter__(self):
        return iter(self.a)
    def __contains__(self, el):
        return el in self.a
    def __len__(self):
        return len(self.a)
```

### Sequence
* **唯一需要的方法是 len() 和 getitem()。**
* **getitem() 应返回传入索引处的项，或引发 IndexError。**
* **iter() 和 contains() 会自动在任何定义了 getitem() 的对象上工作。**
* **reversed() 会自动在任何定义了 len() 和 getitem() 的对象上工作。**
```python
class MySequence:
    def __init__(self, a):
        self.a = a
    def __iter__(self):
        return iter(self.a)
    def __contains__(self, el):
        return el in self.a
    def __len__(self):
        return len(self.a)
    def __getitem__(self, i):
        return self.a[i]
    def __reversed__(self):
        return reversed(self.a)
```

#### Discrepancies between glossary definitions and abstract base classes:
* **术语表将 iterable 定义为任何具有 iter() 或 getitem() 的对象，将 sequence 定义为任何具有 getitem() 和 len() 的对象。它没有定义 collection。**
* **将 ABC Iterable 传给 isinstance() 或 issubclass() 会检查对象/类是否具有 iter() 方法，而 ABC Collection 会检查 iter()、contains() 和 len()。**

### ABC Sequence
* **它比基本序列的接口更丰富。**
* **扩展它会生成 iter()、contains()、reversed()、index() 和 count()。**
* **与 `'abc.Iterable'` 和 `'abc.Collection'` 不同，它不是鸭子类型。这就是为什么 `'issubclass(MySequence, abc.Sequence)'` 会返回 False，即使 MySequence 定义了所有方法。不过它能识别 list、tuple、range、str、bytes、bytearray、memoryview 和 deque，因为它们被注册为 Sequence 的虚拟子类。**
```python
from collections import abc

class MyAbcSequence(abc.Sequence):
    def __init__(self, a):
        self.a = a
    def __len__(self):
        return len(self.a)
    def __getitem__(self, i):
        return self.a[i]
```

#### Table of required and automatically available special methods:
```text
+------------+------------+------------+------------+--------------+
|            |  Iterable  | Collection |  Sequence  | abc.Sequence |
+------------+------------+------------+------------+--------------+
| iter()     |    REQ     |    REQ     |    Yes     |     Yes      |
| contains() |    Yes     |    Yes     |    Yes     |     Yes      |
| len()      |            |    REQ     |    REQ     |     REQ      |
| getitem()  |            |            |    REQ     |     REQ      |
| reversed() |            |            |    Yes     |     Yes      |
| index()    |            |            |            |     Yes      |
| count()    |            |            |            |     Yes      |
+------------+------------+------------+------------+--------------+
```
* **其他会生成缺失方法的 ABC 有：MutableSequence、Set、MutableSet、Mapping 和 MutableMapping。**
* **它们所需方法的名称存储在 `'<abc>.__abstractmethods__'` 中。**

**[🔼Back to Top](#content-outlines)**

<a id="enum"></a>
枚举类
----
```python
from enum import Enum, auto
```

```python
class <enum_name>(Enum):
    <member_name_1> = <value_1>
    <member_name_2> = <value_2_a>, <value_2_b>
    <member_name_3> = auto()
```
* **如果 auto() 之前没有数字值，则返回 1。**
* **否则返回最后一个数字值的增量。**

```python
<member> = <enum>.<member_name>                 # Returns a member.
<member> = <enum>['<member_name>']              # Returns a member or raises KeyError.
<member> = <enum>(<value>)                      # Returns a member or raises ValueError.
<str>    = <member>.name                        # Returns member's name.
<obj>    = <member>.value                       # Returns member's value.
```

```python
list_of_members = list(<enum>)
member_names    = [a.name for a in <enum>]
member_values   = [a.value for a in <enum>]
random_member   = random.choice(list(<enum>))
```

```python
def get_next_member(member):
    members = list(member.__class__)
    index   = (members.index(member) + 1) % len(members)
    return members[index]
```

### Inline
```python
Cutlery = Enum('Cutlery', 'fork knife spoon')
Cutlery = Enum('Cutlery', ['fork', 'knife', 'spoon'])
Cutlery = Enum('Cutlery', {'fork': 1, 'knife': 2, 'spoon': 3})
```

#### User-defined functions cannot be values, so they must be wrapped:
```python
from functools import partial
LogicOp = Enum('LogicOp', {'AND': partial(lambda l, r: l and r),
                           'OR':  partial(lambda l, r: l or r)})
```
* **成员名全部大写，因为尝试访问以保留关键字命名的成员会引发 SyntaxError。**

**[🔼Back to Top](#content-outlines)**

<a id="exceptions"></a>
异常
----------
```python
try:
    <code>
except <exception>:
    <code>
```

### Complex Example
```python
try:
    <code_1>
except <exception_a>:
    <code_2_a>
except <exception_b>:
    <code_2_b>
else:
    <code_2_c>
finally:
    <code_3>
```
* **`'else'` 块中的代码只有在 `'try'` 块没有异常时才会执行。**
* **`'finally'` 块中的代码总是会执行（除非接收到信号）。**

### Catching Exceptions
```python
except <exception>: ...
except <exception> as <name>: ...
except (<exception>, [...]): ...
except (<exception>, [...]) as <name>: ...
```
* **也会捕获该异常的子类。**
* **使用 `'traceback.print_exc()'` 将错误消息打印到 stderr。**
* **使用 `'print(<name>)'` 仅打印异常的原因（其参数）。**
* **使用 `'logging.exception(<message>)'` 记录异常。**

### Raising Exceptions
```python
raise <exception>
raise <exception>()
raise <exception>(<el> [, ...])
```

#### Re-raising caught exception:
```python
except <exception> as <name>:
    ...
    raise
```

### Exception Object
```python
arguments = <name>.args
exc_type  = <name>.__class__
filename  = <name>.__traceback__.tb_frame.f_code.co_filename
func_name = <name>.__traceback__.tb_frame.f_code.co_name
line      = linecache.getline(filename, <name>.__traceback__.tb_lineno)
traceback = ''.join(traceback.format_tb(<name>.__traceback__))
error_msg = ''.join(traceback.format_exception(exc_type, <name>, <name>.__traceback__))
```

### Built-in Exceptions
```text
BaseException
 +-- SystemExit                   # Raised by the sys.exit() function.
 +-- KeyboardInterrupt            # Raised when the user hits the interrupt key (ctrl-c).
 +-- Exception                    # User-defined exceptions should be derived from this class.
      +-- ArithmeticError         # Base class for arithmetic errors.
      |    +-- ZeroDivisionError  # Raised when dividing by zero.
      +-- AssertionError          # Raised by `assert <exp>` if expression returns false value.
      +-- AttributeError          # Raised when an attribute is missing.
      +-- EOFError                # Raised by input() when it hits end-of-file condition.
      +-- LookupError             # Raised when a look-up on a collection fails.
      |    +-- IndexError         # Raised when a sequence index is out of range.
      |    +-- KeyError           # Raised when a dictionary key or set element is missing.
      +-- MemoryError             # Out of memory. Could be too late to start deleting vars.
      +-- NameError               # Raised when an object is missing.
      +-- OSError                 # Errors such as “file not found” or “disk full” (see Open).
      |    +-- FileNotFoundError  # When a file or directory is requested but doesn't exist.
      +-- RuntimeError            # Raised by errors that don't fall into other categories.
      |    +-- RecursionError     # Raised when the maximum recursion depth is exceeded.
      +-- StopIteration           # Raised by next() when run on an empty iterator.
      +-- TypeError               # Raised when an argument is of wrong type.
      +-- ValueError              # When an argument is of right type but inappropriate value.
           +-- UnicodeError       # Raised when encoding/decoding strings to/from bytes fails.
```

#### Collections and their exceptions:
```text
+-----------+------------+------------+------------+
|           |    List    |    Set     |    Dict    |
+-----------+------------+------------+------------+
| getitem() | IndexError |            |  KeyError  |
| pop()     | IndexError |  KeyError  |  KeyError  |
| remove()  | ValueError |  KeyError  |            |
| index()   | ValueError |            |            |
+-----------+------------+------------+------------+
```

#### Useful built-in exceptions:
```python
raise TypeError('Argument is of wrong type!')
raise ValueError('Argument is of right type but inappropriate value!')
raise RuntimeError('None of above!')
```

### User-defined Exceptions
```python
class MyError(Exception): pass
class MyInputError(MyError): pass
```

**[🔼Back to Top](#content-outlines)**

<a id="exit"></a>
退出
----
**通过引发 SystemExit 异常来退出解释器。**
```python
import sys
sys.exit()                        # Exits with exit code 0 (success).
sys.exit(<el>)                    # Prints to stderr and exits with 1.
sys.exit(<int>)                   # Exits with passed exit code.
```

**[🔼Back to Top](#content-outlines)**

<a id="print"></a>
打印
-----
```python
print(<el_1>, ..., sep=' ', end='\n', file=sys.stdout, flush=False)
```
* **使用 `'file=sys.stderr'` 输出关于错误的消息。**
* **使用 `'flush=True'` 强制刷新流。**

### Pretty Print
```python
from pprint import pprint
pprint(<collection>, width=80, depth=None, compact=False, sort_dicts=True)
```
* **比 'depth' 更深的层级会被替换为 '...'。**

**[🔼Back to Top](#content-outlines)**

<a id="input"></a>
输入
-----
**从用户输入或管道（如果存在）读取一行。**

```python
<str> = input(prompt=None)
```
* **尾随的换行符会被去除。**
* **提示字符串会在读取输入之前打印到标准输出。**
* **当用户按下 EOF（ctrl-d/ctrl-z⏎）或输入流耗尽时，引发 EOFError。**

**[🔼Back to Top](#content-outlines)**

<a id="command-line-arguments"></a>
命令行参数
----------------------
```python
import sys
scripts_path = sys.argv[0]
arguments    = sys.argv[1:]
```

### Argument Parser
```python
from argparse import ArgumentParser, FileType
p = ArgumentParser(description=<str>)
p.add_argument('-<short_name>', '--<name>', action='store_true')  # Flag.
p.add_argument('-<short_name>', '--<name>', type=<type>)          # Option.
p.add_argument('<name>', type=<type>, nargs=1)                    # First argument.
p.add_argument('<name>', type=<type>, nargs='+')                  # Remaining arguments.
p.add_argument('<name>', type=<type>, nargs='*')                  # Optional arguments.
args  = p.parse_args()                                            # Exits on error.
value = args.<name>
```

* **使用 `'help=<str>'` 设置将显示在帮助消息中的参数描述。**
* **使用 `'default=<el>'` 设置默认值。**
* **对文件使用 `'type=FileType(<mode>)'`。接受 'encoding'，但 'newline' 为 None。**

**[🔼Back to Top](#content-outlines)**

<a id="open"></a>
打开
----
**打开文件并返回相应的文件对象。**

```python
<file> = open(<path>, mode='r', encoding=None, newline=None)
```
* **`'encoding=None'` 表示使用默认编码，这取决于平台。最佳实践是尽可能使用 `'encoding="utf-8"'`。**
* **`'newline=None'` 表示在读取时所有不同的行尾组合都会转换为 '\n'，而在写入时所有 '\n' 字符都会转换为系统的默认行分隔符。**
* **`'newline=""'` 表示不进行任何转换，但 readline() 和 readlines() 仍会在每个 '\n'、'\r' 和 '\r\n' 处将输入拆分为块。**

### Modes
* **`'r'`  - 读取（默认）。**
* **`'w'`  - 写入（截断）。**
* **`'x'`  - 写入，若文件已存在则失败。**
* **`'a'`  - 追加。**
* **`'w+'` - 读取并写入（截断）。**
* **`'r+'` - 从开头读取并写入。**
* **`'a+'` - 从结尾读取并写入。**
* **`'t'`  - 文本模式（默认）。**
* **`'b'`  - 二进制模式（`'br'`、`'bw'`、`'bx'` 等）。**

### Exceptions
* **以 `'r'` 或 `'r+'` 读取时可能引发 `'FileNotFoundError'`。**
* **以 `'x'` 写入时可能引发 `'FileExistsError'`。**
* **`'IsADirectoryError'` 和 `'PermissionError'` 可由任意模式引发。**
* **`'OSError'` 是所有所列异常的父类。**

### File Object
```python
<file>.seek(0)                      # Moves to the start of the file.
<file>.seek(offset)                 # Moves 'offset' chars/bytes from the start.
<file>.seek(0, 2)                   # Moves to the end of the file.
<bin_file>.seek(±offset, <anchor>)  # Anchor: 0 start, 1 current position, 2 end.
```

```python
<str/bytes> = <file>.read(size=-1)  # Reads 'size' chars/bytes or until EOF.
<str/bytes> = <file>.readline()     # Returns a line or empty string/bytes on EOF.
<list>      = <file>.readlines()    # Returns a list of remaining lines.
<str/bytes> = next(<file>)          # Returns a line using buffer. Do not mix.
```

```python
<file>.write(<str/bytes>)           # Writes a string or bytes object.
<file>.writelines(<collection>)     # Writes a coll. of strings or bytes objects.
<file>.flush()                      # Flushes write buffer. Runs every 4096/8192 B.
```
* **方法不会添加或去除尾随换行符，即使 writelines() 也不会。**

### Read Text from File
```python
def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()
```

### Write Text to File
```python
def write_to_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)
```

**[🔼Back to Top](#content-outlines)**

<a id="paths"></a>
路径
-----
```python
from os import getcwd, path, listdir, scandir
from glob import glob
```

```python
<str>  = getcwd()                   # Returns the current working directory.
<str>  = path.join(<path>, ...)     # Joins two or more pathname components.
<str>  = path.abspath(<path>)       # Returns absolute path.
```

```python
<str>  = path.basename(<path>)      # Returns final component of the path.
<str>  = path.dirname(<path>)       # Returns path without the final component.
<tup.> = path.splitext(<path>)      # Splits on last period of the final component.
```

```python
<list> = listdir(path='.')          # Returns filenames located at path.
<list> = glob('<pattern>')          # Returns paths matching the wildcard pattern.
```

```python
<bool> = path.exists(<path>)        # Or: <Path>.exists()
<bool> = path.isfile(<path>)        # Or: <DirEntry/Path>.is_file()
<bool> = path.isdir(<path>)         # Or: <DirEntry/Path>.is_dir()
```

```python
<stat> = os.stat(<path>)            # Or: <DirEntry/Path>.stat()
<real> = <stat>.st_mtime/st_size/…  # Modification time, size in bytes, …
```

### DirEntry
**与 listdir() 不同，scandir() 返回 DirEntry 对象，这些对象会缓存 isfile、isdir，在 Windows 上还会缓存 stat 信息，从而显著提高需要这些信息的代码性能。**

```python
<iter> = scandir(path='.')          # Returns DirEntry objects located at path.
<str>  = <DirEntry>.path            # Returns whole path as a string.
<str>  = <DirEntry>.name            # Returns final component as a string.
<file> = open(<DirEntry>)           # Opens the file and returns a file object.
```

### Path Object
```python
from pathlib import Path
```

```python
<Path> = Path(<path> [, ...])       # Accepts strings, Paths and DirEntry objects.
<Path> = <path> / <path> [/ ...]    # First or second path must be a Path object.
```

```python
<Path> = Path()                     # Returns relative cwd. Also Path('.').
<Path> = Path.cwd()                 # Returns absolute cwd. Also Path().resolve().
<Path> = Path.home()                # Returns user's home directory (absolute).
<Path> = Path(__file__).resolve()   # Returns script's path if cwd wasn't changed.
```

```python
<Path> = <Path>.parent              # Returns Path without the final component.
<str>  = <Path>.name                # Returns final component as a string.
<str>  = <Path>.stem                # Returns final component without extension.
<str>  = <Path>.suffix              # Returns final component's extension.
<tup.> = <Path>.parts               # Returns all components as strings.
```

```python
<iter> = <Path>.iterdir()           # Returns directory contents as Path objects.
<iter> = <Path>.glob('<pattern>')   # Returns Paths matching the wildcard pattern.
```

```python
<str>  = str(<Path>)                # Returns path as a string.
<file> = open(<Path>)               # Also <Path>.read/write_text/bytes().
```

**[🔼Back to Top](#content-outlines)**

<a id="os-commands"></a>
操作系统命令
-----------
```python
import os, shutil, subprocess
```

```python
os.chdir(<path>)                    # Changes the current working directory.
os.mkdir(<path>, mode=0o777)        # Creates a directory. Permissions are in octal.
os.makedirs(<path>, mode=0o777)     # Creates all path's dirs. Also: `exist_ok=False`.
```

```python
shutil.copy(from, to)               # Copies the file. 'to' can exist or be a dir.
shutil.copytree(from, to)           # Copies the directory. 'to' must not exist.
```


```python
os.rename(from, to)                 # Renames/moves the file or directory.
os.replace(from, to)                # Same, but overwrites 'to' if it exists.
```

```python
os.remove(<path>)                   # Deletes the file.
os.rmdir(<path>)                    # Deletes the empty directory.
shutil.rmtree(<path>)               # Deletes the directory.
```
* **路径可以是字符串、Path 或 DirEntry 对象。**
* **函数通过引发 OSError 或其 [subclasses](#exceptions-1) 之一来报告与操作系统相关的错误。**

### Shell Commands
```python
<pipe> = os.popen('<command>')      # Executes command in sh/cmd. Returns its stdout pipe.
<str>  = <pipe>.read(size=-1)       # Reads 'size' chars or until EOF. Also readline/s().
<int>  = <pipe>.close()             # Closes the pipe. Returns None on success.
```

#### Sends '1 + 1' to the basic calculator and captures its output:
```python
>>> subprocess.run('bc', input='1 + 1\n', capture_output=True, text=True)
CompletedProcess(args='bc', returncode=0, stdout='2\n', stderr='')
```

#### Sends test.in to the basic calculator running in standard mode and saves its output to test.out:
```python
>>> from shlex import split
>>> os.popen('echo 1 + 1 > test.in')
>>> subprocess.run(split('bc -s'), stdin=open('test.in'), stdout=open('test.out', 'w'))
CompletedProcess(args=['bc', '-s'], returncode=0)
>>> open('test.out').read()
'2\n'
```

**[🔼Back to Top](#content-outlines)**

<a id="json"></a>
JSON
----
**用于存储字符串和数字集合的文本文件格式。**

```python
import json
<str>    = json.dumps(<object>)     # Converts object to JSON string.
<object> = json.loads(<str>)        # Converts JSON string to object.
```

### Read Object from JSON File
```python
def read_json_file(filename):
    with open(filename, encoding='utf-8') as file:
        return json.load(file)
```

### Write Object to JSON File
```python
def write_to_json_file(filename, an_object):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(an_object, file, ensure_ascii=False, indent=2)
```

**[🔼Back to Top](#content-outlines)**

<a id="pickle"></a>
Pickle
------
**用于存储 Python 对象的二进制文件格式。**

```python
import pickle
<bytes>  = pickle.dumps(<object>)   # Converts object to bytes object.
<object> = pickle.loads(<bytes>)    # Converts bytes object to object.
```

### Read Object from File
```python
def read_pickle_file(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)
```

### Write Object to File
```python
def write_to_pickle_file(filename, an_object):
    with open(filename, 'wb') as file:
        pickle.dump(an_object, file)
```

**[🔼Back to Top](#content-outlines)**

<a id="csv"></a>
CSV
---
**用于存储电子表格的文本文件格式。**

```python
import csv
```

### Read
```python
<reader> = csv.reader(<file>)       # Also: `dialect='excel', delimiter=','`.
<list>   = next(<reader>)           # Returns next row as a list of strings.
<list>   = list(<reader>)           # Returns a list of remaining rows.
```
* **文件必须以 `'newline=""'` 参数打开，否则嵌入在引号字段中的换行符将无法被正确解释！**
* **要将电子表格打印到控制台，请使用 [Tabulate](#table) 库。**
* **对于 XML 和二进制 Excel 文件（xlsx、xlsm 和 xlsb），请使用 [Pandas](#dataframe-plot-encode-decode) 库。**

### Write
```python
<writer> = csv.writer(<file>)       # Also: `dialect='excel', delimiter=','`.
<writer>.writerow(<collection>)     # Encodes objects using `str(<el>)`.
<writer>.writerows(<coll_of_coll>)  # Appends multiple rows.
```
* **文件必须以 `'newline=""'` 参数打开，否则在使用 '\r\n' 作为行尾的平台上，每个 '\n' 前都会被添加 '\r'！**

### Parameters
* **`'dialect'` - 设置默认值的主参数。字符串或 Dialect 对象。**
* **`'delimiter'` - 用于分隔字段的单字符字符串。**
* **`'quotechar'` - 用于引用包含特殊字符的字段的字符。**
* **`'doublequote'` - 字段内的引号字符是否加倍或转义。**
* **`'skipinitialspace'` - 字段开头的空格字符是否被读取器去除。**
* **`'lineterminator'` - 写入器如何终止行。读取器硬编码为 '\n'、'\r'、'\r\n'。**
* **`'quoting'` - 0：按需，1：全部，2：除作为浮点数读取的数字外全部，3：无。**
* **`'escapechar'` - 当 doublequote 为 False 时用于转义引号字符的字符。**

### Dialects
```text
+------------------+--------------+--------------+--------------+
|                  |     excel    |   excel-tab  |     unix     |
+------------------+--------------+--------------+--------------+
| delimiter        |       ','    |      '\t'    |       ','    |
| quotechar        |       '"'    |       '"'    |       '"'    |
| doublequote      |      True    |      True    |      True    |
| skipinitialspace |     False    |     False    |     False    |
| lineterminator   |    '\r\n'    |    '\r\n'    |      '\n'    |
| quoting          |         0    |         0    |         1    |
| escapechar       |      None    |      None    |      None    |
+------------------+--------------+--------------+--------------+
```

### Read Rows from CSV File
```python
def read_csv_file(filename, dialect='excel'):
    with open(filename, encoding='utf-8', newline='') as file:
        return list(csv.reader(file, dialect))
```

### Write Rows to CSV File
```python
def write_to_csv_file(filename, rows, dialect='excel'):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, dialect)
        writer.writerows(rows)
```

**[🔼Back to Top](#content-outlines)**

<a id="sqlite"></a>
SQLite
------
**一种无服务器数据库引擎，将每个数据库存储到单独的文件中。**

```python
import sqlite3
<conn> = sqlite3.connect(<path>)                # Opens existing or new file. Also ':memory:'.
<conn>.close()                                  # Closes the connection.
```

### Read
```python
<cursor> = <conn>.execute('<query>')            # Can raise a subclass of sqlite3.Error.
<tuple>  = <cursor>.fetchone()                  # Returns next row. Also next(<cursor>).
<list>   = <cursor>.fetchall()                  # Returns remaining rows. Also list(<cursor>).
```

### Write
```python
<conn>.execute('<query>')                       # Can raise a subclass of sqlite3.Error.
<conn>.commit()                                 # Saves all changes since the last commit.
<conn>.rollback()                               # Discards all changes since the last commit.
```

#### Or:
```python
with <conn>:                                    # Exits the block with commit() or rollback(),
    <conn>.execute('<query>')                   # depending on whether any exception occurred.
```

### Placeholders
```python
<conn>.execute('<query>', <list/tuple>)         # Replaces '?'s in query with values.
<conn>.execute('<query>', <dict/namedtuple>)    # Replaces ':<key>'s with values.
<conn>.executemany('<query>', <coll_of_above>)  # Runs execute() multiple times.
```
* **传入的值可以是 str、int、float、bytes、None、bool、datetime.date 或 datetime.datetime 类型。**
* **布尔值会被存储并作为 int 返回，日期会作为 [ISO formatted strings](#encode) 返回。**

### Example
**在此示例中，值实际上并未保存，因为省略了 `'conn.commit()'`！**
```python
>>> conn = sqlite3.connect('test.db')
>>> conn.execute('CREATE TABLE person (person_id INTEGER PRIMARY KEY, name, height)')
>>> conn.execute('INSERT INTO person VALUES (NULL, ?, ?)', ('Jean-Luc', 187)).lastrowid
1
>>> conn.execute('SELECT * FROM person').fetchall()
[(1, 'Jean-Luc', 187)]
```

### SqlAlchemy
```python
# $ pip3 install sqlalchemy
from sqlalchemy import create_engine, text
<engine> = create_engine('<url>').connect()     # Url: 'dialect://user:password@host/dbname'.
<conn>   = <engine>.connect()                   # Creates a connection. Also <conn>.close().
<cursor> = <conn>.execute(text('<query>'), …)   # Replaces ':<key>'s with keyword arguments.
with <conn>.begin(): ...                        # Exits the block with commit or rollback.
```

```text
+------------+--------------+-----------+-----------------------------------+
| Dialects   | pip3 install | import    | Dependencies                      |
+------------+--------------+-----------+-----------------------------------+
| mysql      | mysqlclient  | MySQLdb   | www.pypi.org/project/mysqlclient  |
| postgresql | psycopg2     | psycopg2  | www.psycopg.org/docs/install.html |
| mssql      | pyodbc       | pyodbc    | apt install g++ unixodbc-dev      |
| oracle     | cx_oracle    | cx_Oracle | Oracle Instant Client             |
+------------+--------------+-----------+-----------------------------------+
```

**[🔼Back to Top](#content-outlines)**

<a id="bytes"></a>
字节
-----
**Bytes 对象是不可变的单字节序列。可变版本称为 bytearray。**

```python
<bytes> = b'<str>'                          # Only accepts ASCII characters and \x00-\xff.
<int>   = <bytes>[<index>]                  # Returns an int in range from 0 to 255.
<bytes> = <bytes>[<slice>]                  # Returns bytes even if it has only one element.
<bytes> = <bytes>.join(<coll_of_bytes>)     # Joins elements using bytes as a separator.
```

### Encode
```python
<bytes> = bytes(<coll_of_ints>)             # Ints must be in range from 0 to 255.
<bytes> = bytes(<str>, 'utf-8')             # Or: <str>.encode('utf-8')
<bytes> = <int>.to_bytes(n_bytes, …)        # `byteorder='little/big', signed=False`.
<bytes> = bytes.fromhex('<hex>')            # Hex pairs can be separated by whitespaces.
```

### Decode
```python
<list>  = list(<bytes>)                     # Returns ints in range from 0 to 255.
<str>   = str(<bytes>, 'utf-8')             # Or: <bytes>.decode('utf-8')
<int>   = int.from_bytes(<bytes>, …)        # `byteorder='little/big', signed=False`.
'<hex>' = <bytes>.hex()                     # Returns hex pairs. Accepts `sep=<str>`.
```

### Read Bytes from File
```python
def read_bytes(filename):
    with open(filename, 'rb') as file:
        return file.read()
```

### Write Bytes to File
```python
def write_bytes(filename, bytes_obj):
    with open(filename, 'wb') as file:
        file.write(bytes_obj)
```

**[🔼Back to Top](#content-outlines)**

<a id="struct"></a>
结构体
------
* **在数值序列与字节对象之间进行转换的模块。**
* **默认使用系统的类型大小、字节序和对齐规则。**

```python
from struct import pack, unpack
<bytes> = pack('<format>', <el_1> [, ...])  # Packages arguments into bytes object.
<tuple> = unpack('<format>', <bytes>)       # Use iter_unpack() for iterator of tuples.
```

```python
>>> pack('>hhl', 1, 2, 3)
b'\x00\x01\x00\x02\x00\x00\x00\x03'
>>> unpack('>hhl', b'\x00\x01\x00\x02\x00\x00\x00\x03')
(1, 2, 3)
```

### Format
#### For standard type sizes and manual alignment (padding) start format string with:
* **`'='` - 系统的字节序（通常是小端）。**
* **`'<'` - 小端。**
* **`'>'` - 大端（也可用 `'!'`）。**

#### Besides numbers, pack() and unpack() also support bytes objects as part of the sequence:
* **`'c'` - 单元素的字节对象。填充字节用 `'x'`。**
* **`'<n>s'` - n 个元素的字节对象。**

#### Integer types. Use a capital letter for unsigned type. Minimum and standard sizes are in brackets:
* **`'b'` - char (1/1)**
* **`'h'` - short (2/2)**
* **`'i'` - int (2/4)**
* **`'l'` - long (4/4)**
* **`'q'` - long long (8/8)**

#### Floating point types:
* **`'f'` - float (4/4)**
* **`'d'` - double (8/8)**

**[🔼Back to Top](#content-outlines)**

<a id="array"></a>
数组
-----
**只能保存预定义类型数字的列表。可用的类型及其最小字节大小如上所列。大小和字节序始终由系统决定。**

```python
from array import array
<array> = array('<typecode>', <collection>)    # Array from collection of numbers.
<array> = array('<typecode>', <bytes>)         # Array from bytes object.
<array> = array('<typecode>', <array>)         # Treats array as a sequence of numbers.
<bytes> = bytes(<array>)                       # Or: <array>.tobytes()
<file>.write(<array>)                          # Writes array to the binary file.
```

**[🔼Back to Top](#content-outlines)**

<a id="memory-view"></a>
内存视图
-----------
* **指向另一个对象内存的序列对象。**
* **根据格式，每个元素可以引用单个或多个连续的字节。**
* **元素的顺序和数量可以通过切片更改。**
* **转换只能在 char 和其他类型之间进行，并使用系统的大小。**
* **字节序始终由系统决定。**

```python
<mview> = memoryview(<bytes/bytearray/array>)  # Immutable if bytes, else mutable.
<real>  = <mview>[<index>]                     # Returns an int or a float.
<mview> = <mview>[<slice>]                     # Mview with rearranged elements.
<mview> = <mview>.cast('<typecode>')           # Casts memoryview to the new format.
<mview>.release()                              # Releases the object's memory buffer.
```

### Decode
```python
<bytes> = bytes(<mview>)                       # Returns a new bytes object.
<bytes> = <bytes>.join(<coll_of_mviews>)       # Joins mviews using bytes object as sep.
<array> = array('<typecode>', <mview>)         # Treats mview as a sequence of numbers.
<file>.write(<mview>)                          # Writes mview to the binary file.
```

```python
<list>  = list(<mview>)                        # Returns a list of ints or floats.
<str>   = str(<mview>, 'utf-8')                # Treats mview as a bytes object.
<int>   = int.from_bytes(<mview>, …)           # `byteorder='little/big', signed=False`.
'<hex>' = <mview>.hex()                        # Treats mview as a bytes object.
```

**[🔼Back to Top](#content-outlines)**

<a id="deque"></a>
双端队列
-----
**一个线程安全的列表，可从任意一端高效地追加和弹出。读作 "deck"。**

```python
from collections import deque
<deque> = deque(<collection>, maxlen=None)
```

```python
<deque>.appendleft(<el>)                       # Opposite element is dropped if full.
<deque>.extendleft(<collection>)               # Collection gets reversed.
<el> = <deque>.popleft()                       # Raises IndexError if empty.
<deque>.rotate(n=1)                            # Rotates elements to the right.
```

**[🔼Back to Top](#content-outlines)**

<a id="threading"></a>
线程
---------
* **CPython 解释器一次只能运行一个线程。**
* **因此，除非至少有一个线程包含 I/O 操作，否则使用多个线程不会带来更快的执行速度。**
```python
from threading import Thread, RLock, Semaphore, Event, Barrier
from concurrent.futures import ThreadPoolExecutor
```

### Thread
```python
<Thread> = Thread(target=<function>)           # Use `args=<collection>` to set the arguments.
<Thread>.start()                               # Starts the thread.
<bool> = <Thread>.is_alive()                   # Checks if the thread has finished executing.
<Thread>.join()                                # Waits for the thread to finish.
```
* **使用 `'kwargs=<dict>'` 将关键字参数传递给函数。**
* **使用 `'daemon=True'`，否则在线程存活时程序将无法退出。**

<a id="lock"></a>
### Lock
```python
<lock> = RLock()                               # Lock that can only be released by acquirer.
<lock>.acquire()                               # Waits for the lock to be available.
<lock>.release()                               # Makes the lock available again.
```

#### Or:
```python
with <lock>:                                   # Enters the block by calling acquire(),
    ...                                        # and exits it with release().
```

<a id="semaphore-event-barrier"></a>
### Semaphore, Event, Barrier
```python
<Semaphore> = Semaphore(value=1)               # Lock that can be acquired by 'value' threads.
<Event>     = Event()                          # Method wait() blocks until set() is called.
<Barrier>   = Barrier(n_times)                 # Wait() blocks until it's called n_times.
```

### Thread Pool Executor
* **管理线程执行的对象。**
* **一个名为 ProcessPoolExecutor、具有相同接口的对象，通过在每个进程中运行单独的解释器来提供真正的并行。所有参数都必须是 [pickable](#pickle) 的。**

```python
<Exec> = ThreadPoolExecutor(max_workers=None)  # Or: `with ThreadPoolExecutor() as <name>: …`
<Exec>.shutdown(wait=True)                     # Blocks until all threads finish executing.
```

```python
<iter> = <Exec>.map(<func>, <args_1>, ...)     # A multithreaded and non-lazy map().
<Futr> = <Exec>.submit(<func>, <arg_1>, ...)   # Starts a thread and returns its Future object.
<bool> = <Futr>.done()                         # Checks if the thread has finished executing.
<obj>  = <Futr>.result()                       # Waits for thread to finish and returns result.
```

<a id="queue"></a>
### Queue
**线程安全的 FIFO 队列。对于 LIFO 队列，请使用 LifoQueue。**
```python
from queue import Queue
<Queue> = Queue(maxsize=0)
```

```python
<Queue>.put(<el>)                              # Blocks until queue stops being full.
<Queue>.put_nowait(<el>)                       # Raises queue.Full exception if full.
<el> = <Queue>.get()                           # Blocks until queue stops being empty.
<el> = <Queue>.get_nowait()                    # Raises queue.Empty exception if empty.
```

**[🔼Back to Top](#content-outlines)**

<a id="operator"></a>
运算符
--------
**提供运算符功能的函数模块。**
```python
import operator as op
<el>      = op.add/sub/mul/truediv/floordiv/mod(<el>, <el>)  # +, -, *, /, //, %
<int/set> = op.and_/or_/xor(<int/set>, <int/set>)            # &, |, ^
<bool>    = op.eq/ne/lt/le/gt/ge(<sortable>, <sortable>)     # ==, !=, <, <=, >, >=
<func>    = op.itemgetter/attrgetter/methodcaller(<obj>)     # [index/key], .name, .name()
```

```python
elementwise_sum  = map(op.add, list_a, list_b)
sorted_by_second = sorted(<collection>, key=op.itemgetter(1))
sorted_by_both   = sorted(<collection>, key=op.itemgetter(1, 0))
product_of_elems = functools.reduce(op.mul, <collection>)
union_of_sets    = functools.reduce(op.or_, <coll_of_sets>)
first_element    = op.methodcaller('pop', 0)(<list>)
```
* **二元运算符要求对象具有 and()、or()、xor() 和 invert() 特殊方法，而逻辑运算符可作用于所有类型的对象。**
* **另有：`'<bool> = <bool> &|^ <bool>'` 和 `'<int> = <bool> &|^ <int>'`。**

**[🔼Back to Top](#content-outlines)**

<a id="introspection"></a>
内省
-------------
**在运行时检查代码。**

### Variables
```python
<list> = dir()                             # Names of local variables (incl. functions).
<dict> = vars()                            # Dict of local variables. Also locals().
<dict> = globals()                         # Dict of global variables.
```

### Attributes
```python
<list> = dir(<object>)                     # Names of object's attributes (incl. methods).
<dict> = vars(<object>)                    # Dict of writable attributes. Also <obj>.__dict__.
<bool> = hasattr(<object>, '<attr_name>')  # Checks if getattr() raises an AttributeError.
value  = getattr(<object>, '<attr_name>')  # Raises AttributeError if attribute is missing.
setattr(<object>, '<attr_name>', value)    # Only works on objects with '__dict__' attribute.
delattr(<object>, '<attr_name>')           # Same. Also `del <object>.<attr_name>`.
```

### Parameters
```python
<Sig>  = inspect.signature(<function>)     # Function's Signature object.
<dict> = <Sig>.parameters                  # Dict of Parameter objects.
<memb> = <Param>.kind                      # Member of ParameterKind enum.
<obj>  = <Param>.default                   # Default value or <Param>.empty.
<type> = <Param>.annotation                # Type or <Param>.empty.
```

**[🔼Back to Top](#content-outlines)**

<a id="metaprogramming"></a>
元编程
---------------
**生成代码的代码。**

### Type
**Type 是根类。如果只传入一个对象，它返回该对象的类型（类）。否则它会创建一个新类。**

```python
<class> = type('<class_name>', <tuple_of_parents>, <dict_of_class_attributes>)
```

```python
>>> Z = type('Z', (), {'a': 'abcde', 'b': 12345})
>>> z = Z()
```

### Meta Class
**用于创建类的类。**

```python
def my_meta_class(name, parents, attrs):
    attrs['a'] = 'abcde'
    return type(name, parents, attrs)
```

#### Or:
```python
class MyMetaClass(type):
    def __new__(cls, name, parents, attrs):
        attrs['a'] = 'abcde'
        return type.__new__(cls, name, parents, attrs)
```
* **new() 是一个在 init() 之前被调用的类方法。如果它返回其类的一个实例，则该实例会作为 'self' 参数传给 init()。**
* **它接收与 init() 相同的参数，只是第一个指定了返回实例的期望类型的参数除外（在我们的例子中是 MyMetaClass）。**
* **像我们的例子一样，new() 也可以被直接调用，通常来自子类的 new() 方法（`def __new__(cls): return super().__new__(cls)`）。**
* **上面两个例子唯一的区别在于，my\_meta\_class() 返回类型为 type 的类，而 MyMetaClass() 返回类型为 MyMetaClass 的类。**

### Metaclass Attribute
**在创建类之前，它会检查是否定义了 'metaclass' 属性。如果没有，它会递归检查其任何父类是否定义了该属性，最终回溯到 type()。**

```python
class MyClass(metaclass=MyMetaClass):
    b = 12345
```

```python
>>> MyClass.a, MyClass.b
('abcde', 12345)
```

### Type Diagram
```python
type(MyClass) == MyMetaClass         # MyClass is an instance of MyMetaClass.
type(MyMetaClass) == type            # MyMetaClass is an instance of type.
```

```text
+-------------+-------------+
|   Classes   | Metaclasses |
+-------------+-------------|
|   MyClass --> MyMetaClass |
|             |     v       |
|    object -----> type <+  |
|             |     ^ +--+  |
|     str ----------+       |
+-------------+-------------+
```

### Inheritance Diagram
```python
MyClass.__base__ == object           # MyClass is a subclass of object.
MyMetaClass.__base__ == type         # MyMetaClass is a subclass of type.
```

```text
+-------------+-------------+
|   Classes   | Metaclasses |
+-------------+-------------|
|   MyClass   | MyMetaClass |
|      v      |     v       |
|    object <----- type     |
|      ^      |             |
|     str     |             |
+-------------+-------------+
```

**[🔼Back to Top](#content-outlines)**

<a id="eval"></a>
求值
----
```python
>>> from ast import literal_eval
>>> literal_eval('[1, 2, 3]')
[1, 2, 3]
>>> literal_eval('1 + 2')
ValueError: malformed node or string
```

**[🔼Back to Top](#content-outlines)**

<a id="coroutines"></a>
协程
----------
* **协程与线程有很多共同点，但与线程不同的是，它们只在调用另一个协程时才让出控制权，且使用的内存更少。**
* **协程定义以 `'async'` 开头，调用以 `'await'` 开头。**
* **`'asyncio.run(<coroutine>)'` 是异步程序的主入口点。**
* **wait()、gather() 和 as_completed() 函数可同时启动多个协程。**
* **Asyncio 模块还提供了自己的 [Queue](#queue)、[Event](#semaphore-event-barrier)、[Lock](#lock) 和 [Semaphore](#semaphore-event-barrier) 类。**

#### Runs a terminal game where you control an asterisk that must avoid numbers:

```python
import asyncio, collections, curses, curses.textpad, enum, random

P = collections.namedtuple('P', 'x y')         # Position
D = enum.Enum('D', 'n e s w')                  # Direction
W, H = 15, 7                                   # Width, Height

def main(screen):
    curses.curs_set(0)                         # Makes cursor invisible.
    screen.nodelay(True)                       # Makes getch() non-blocking.
    asyncio.run(main_coroutine(screen))        # Starts running asyncio code.

async def main_coroutine(screen):
    moves = asyncio.Queue()
    state = {'*': P(0, 0), **{id_: P(W//2, H//2) for id_ in range(10)}}
    ai    = [random_controller(id_, moves) for id_ in range(10)]
    mvc   = [human_controller(screen, moves), model(moves, state), view(state, screen)]
    tasks = [asyncio.create_task(cor) for cor in ai + mvc]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

async def random_controller(id_, moves):
    while True:
        d = random.choice(list(D))
        moves.put_nowait((id_, d))
        await asyncio.sleep(random.triangular(0.01, 0.65))

async def human_controller(screen, moves):
    while True:
        ch = screen.getch()
        key_mappings = {258: D.s, 259: D.n, 260: D.w, 261: D.e}
        if ch in key_mappings:
            moves.put_nowait(('*', key_mappings[ch]))
        await asyncio.sleep(0.005)

async def model(moves, state):
    while state['*'] not in (state[id_] for id_ in range(10)):
        id_, d = await moves.get()
        x, y   = state[id_]
        deltas = {D.n: P(0, -1), D.e: P(1, 0), D.s: P(0, 1), D.w: P(-1, 0)}
        state[id_] = P((x + deltas[d].x) % W, (y + deltas[d].y) % H)

async def view(state, screen):
    offset = P(curses.COLS//2 - W//2, curses.LINES//2 - H//2)
    while True:
        screen.erase()
        curses.textpad.rectangle(screen, offset.y-1, offset.x-1, offset.y+H, offset.x+W)
        for id_, p in state.items():
            screen.addstr(offset.y + (p.y - state['*'].y + H//2) % H,
                          offset.x + (p.x - state['*'].x + W//2) % W, str(id_))
        await asyncio.sleep(0.005)

if __name__ == '__main__':
    curses.wrapper(main)
```
<br>

**[🔼Back to Top](#content-outlines)**

Libraries
=========

<a id="progress-bar"></a>
进度条
------------
```python
# $ pip3 install tqdm
>>> from tqdm import tqdm
>>> from time import sleep
>>> for el in tqdm([1, 2, 3], desc='Processing'):
...     sleep(1)
Processing: 100%|████████████████████| 3/3 [00:03<00:00,  1.00s/it]
```

**[🔼Back to Top](#content-outlines)**

<a id="plot"></a>
绘图
----
```python
# $ pip3 install matplotlib
import matplotlib.pyplot as plt
plt.plot(<x_data>, <y_data> [, label=<str>])   # Or: plt.plot(<y_data>)
plt.legend()                                   # Adds a legend.
plt.savefig(<path>)                            # Saves the figure.
plt.show()                                     # Displays the figure.
plt.clf()                                      # Clears the figure.
```

**[🔼Back to Top](#content-outlines)**

<a id="table"></a>
表格
-----
#### Prints a CSV file as an ASCII table:
```python
# $ pip3 install tabulate
import csv, tabulate
with open('test.csv', encoding='utf-8', newline='') as file:
    rows   = csv.reader(file)
    header = next(rows)
    table  = tabulate.tabulate(rows, header)
print(table)
```

**[🔼Back to Top](#content-outlines)**

<a id="curses"></a>
Curses
------
#### Runs a basic file explorer in the terminal:
```python
import curses, curses.ascii, os
from curses import A_REVERSE, KEY_DOWN, KEY_UP, KEY_LEFT, KEY_RIGHT, KEY_ENTER

def main(screen):
    ch, first, selected, paths = 0, 0, 0, os.listdir()
    while ch != curses.ascii.ESC:
        height, _ = screen.getmaxyx()
        screen.erase()
        for y, filename in enumerate(paths[first : first+height]):
            screen.addstr(y, 0, filename, A_REVERSE * (selected == first + y))
        ch = screen.getch()
        selected += (ch == KEY_DOWN) - (ch == KEY_UP)
        selected = max(0, min(len(paths)-1, selected))
        first += (first <= selected - height) - (first > selected)
        if ch in [KEY_LEFT, KEY_RIGHT, KEY_ENTER, 10, 13]:
            new_dir = '..' if ch == KEY_LEFT else paths[selected]
            if os.path.isdir(new_dir):
                os.chdir(new_dir)
                first, selected, paths = 0, 0, os.listdir()

if __name__ == '__main__':
    curses.wrapper(main)
```

**[🔼Back to Top](#content-outlines)**

<a id="logging"></a>
日志
-------
```python
# $ pip3 install loguru
from loguru import logger
```

```python
logger.add('debug_{time}.log', colorize=True)  # Connects a log file.
logger.add('error_{time}.log', level='ERROR')  # Another file for errors or higher.
logger.<level>('A logging message.')           # Logs to file/s and prints to stderr.
```
* **级别：`'debug'`、`'info'`、`'success'`、`'warning'`、`'error'`、`'critical'`。**

<a id="exceptions-1"></a>
### Exceptions
**异常描述、堆栈跟踪和变量值会被自动附加。**

```python
try:
    ...
except <exception>:
    logger.exception('An error happened.')
```

### Rotation
**设置何时创建新日志文件的条件参数。**
```python
rotation=<int>|<datetime.timedelta>|<datetime.time>|<str>
```
* **`'<int>'` - 最大文件大小（字节）。**
* **`'<timedelta>'` - 文件的最大存在时间。**
* **`'<time>'` - 一天中的时间。**
* **`'<str>'` - 上述任意形式的字符串：`'100 MB'`、`'1 month'`、`'monday at 12:00'` 等。**

### Retention
**设置删除哪些旧日志文件的条件。**
```python
retention=<int>|<datetime.timedelta>|<str>
```
* **`'<int>'` - 最大文件数量。**
* **`'<timedelta>'` - 文件的最大存在时间。**
* **`'<str>'` - 最大存在时间（字符串形式）：`'1 week, 3 days'`、`'2 months'` 等。**

**[🔼Back to Top](#content-outlines)**

<a id="scraping"></a>
爬取
--------
#### Scrapes Python's URL, version number and logo from its Wikipedia page:
```python
# $ pip3 install requests beautifulsoup4
import requests, bs4, os, sys

WIKI_URL = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
try:
    html       = requests.get(WIKI_URL).text
    document   = bs4.BeautifulSoup(html, 'html.parser')
    table      = document.find('table', class_='infobox vevent')
    python_url = table.find('th', text='Website').next_sibling.a['href']
    version    = table.find('th', text='Stable release').next_sibling.strings.__next__()
    logo_url   = table.find('img')['src']
    logo       = requests.get(f'https:{logo_url}').content
    filename   = os.path.basename(logo_url)
    with open(filename, 'wb') as file:
        file.write(logo)
    print(f'{python_url}, {version}, file://{os.path.abspath(filename)}')
except requests.exceptions.ConnectionError:
    print("You've got problems with connection.", file=sys.stderr)
```

**[🔼Back to Top](#content-outlines)**

<a id="web"></a>
Web
---
```python
# $ pip3 install bottle
from bottle import run, route, static_file, template, post, request, response
import json
```

### Run
```python
run(host='localhost', port=8080)        # Runs locally.
run(host='0.0.0.0', port=80)            # Runs globally.
```

### Static Request
```python
@route('/img/<filename>')
def send_file(filename):
    return static_file(filename, root='img_dir/')
```

### Dynamic Request
```python
@route('/<sport>')
def send_html(sport):
    return template('<h1>{{title}}</h1>', title=sport)
```

### REST Request
```python
@post('/<sport>/odds')
def send_json(sport):
    team = request.forms.get('team')
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache'
    return json.dumps({'team': team, 'odds': [2.09, 3.74, 3.68]})
```

#### Test:
```python
# $ pip3 install requests
>>> import threading, requests
>>> threading.Thread(target=run, daemon=True).start()
>>> url = 'http://localhost:8080/football/odds'
>>> request_data = {'team': 'arsenal f.c.'}
>>> response = requests.post(url, data=request_data)
>>> response.json()
{'team': 'arsenal f.c.', 'odds': [2.09, 3.74, 3.68]}
```

**[🔼Back to Top](#content-outlines)**

<a id="profiling"></a>
性能分析
---------
### Stopwatch
```python
from time import perf_counter
start_time = perf_counter()
...
duration_in_seconds = perf_counter() - start_time
```

### Timing a Snippet
```python
>>> from timeit import timeit
>>> timeit("''.join(str(i) for i in range(100))",
...        number=10000, globals=globals(), setup='pass')
0.34986
```

### Profiling by Line
```python
# $ pip3 install line_profiler memory_profiler
@profile
def main():
    a = [*range(10000)]
    b = {*range(10000)}
main()
```

```text
$ kernprof -lv test.py
Line #   Hits     Time  Per Hit   % Time  Line Contents
=======================================================
     1                                    @profile
     2                                    def main():
     3      1    955.0    955.0     43.7      a = [*range(10000)]
     4      1   1231.0   1231.0     56.3      b = {*range(10000)}
```

```text
$ python3 -m memory_profiler test.py
Line #         Mem usage      Increment   Line Contents
=======================================================
     1        37.668 MiB     37.668 MiB   @profile
     2                                    def main():
     3        38.012 MiB      0.344 MiB       a = [*range(10000)]
     4        38.477 MiB      0.465 MiB       b = {*range(10000)}
```

### Call Graph
#### Generates a PNG image of the call graph with highlighted bottlenecks:
```python
# $ pip3 install pycallgraph2; apt/brew install graphviz
import pycallgraph2 as cg, datetime

filename = f'profile-{datetime.datetime.now():%Y%m%d_%H%M%S}.png'
drawer = cg.output.GraphvizOutput(output_file=filename)
with cg.PyCallGraph(drawer):
    <code_to_be_profiled>
```

**[🔼Back to Top](#content-outlines)**

<a id="numpy"></a>
NumPy
-----
**数组操作迷你语言。运行速度可比等效的 Python 代码快达一百倍。在 GPU 上运行的更快替代方案称为 CuPy。**

```python
# $ pip3 install numpy
import numpy as np
```

```python
<array> = np.array(<list/list_of_lists>)                # Returns 1d/2d NumPy array.
<array> = np.zeros/ones(<shape>)                        # Also np.full(<shape>, <el>).
<array> = np.arange(from_inc, to_exc, ±step)            # Also np.linspace(start, stop, num).
<array> = np.random.randint(from_inc, to_exc, <shape>)  # Also np.random.random(<shape>).
```

```python
<view>  = <array>.reshape(<shape>)                      # Also `<array>.shape = <shape>`.
<array> = <array>.flatten()                             # Collapses array into one dimension.
<view>  = <array>.squeeze()                             # Removes dimensions of length one.
```

```python
<array> = <array>.sum/min/mean/var/std(axis)            # Passed dimension gets aggregated.
<array> = <array>.argmin(axis)                          # Returns indexes of smallest elements.
<array> = np.apply_along_axis(<func>, axis, <array>)    # Func can return a scalar or array.
```

* **Shape 是维度大小组成的元组。一张 100x50 的 RGB 图像的形状为 (50, 100, 3)。**
* **Axis 是被聚合维度的索引。最左边的维度索引为 0。沿 axis 2 对 RGB 图像求和将返回形状为 (50, 100) 的灰度图像。**
* **传入轴元组将链式调用操作，如：`'<array>.<method>(axis_1, keepdims=True).<method>(axis_2).squeeze()'`。**

### Indexing
```bash
<el>       = <2d_array>[row_index, column_index]        # <3d_a>[table_i, row_i, column_i]
<1d_view>  = <2d_array>[row_index]                      # <3d_a>[table_i, row_i]
<1d_view>  = <2d_array>[:, column_index]                # <3d_a>[table_i, :, column_i]
```

```bash
<1d_array> = <2d_array>[row_indexes, column_indexes]    # <3d_a>[table_is, row_is, column_is]
<2d_array> = <2d_array>[row_indexes]                    # <3d_a>[table_is, row_is]
<2d_array> = <2d_array>[:, column_indexes]              # <3d_a>[table_is, :, column_is]
```

```bash
<2d_bools> = <2d_array> ><== <el>                       # <3d_array> ><== <1d_array>
<1d_array> = <2d_array>[<2d_bools>]                     # <3d_array>[<2d_bools>]
```
* **所有示例也都允许赋值。**

### Broadcasting
**广播是一组规则，NumPy 函数依据这些规则对大小/维度不同的数组进行操作。**

```python
left  = [[0.1], [0.6], [0.8]]                           # Shape: (3, 1)
right = [ 0.1 ,  0.6 ,  0.8 ]                           # Shape: (3,)
```

#### 1. If array shapes differ in length, left-pad the shorter shape with ones:
```python
left  = [[0.1], [0.6], [0.8]]                           # Shape: (3, 1)
right = [[0.1 ,  0.6 ,  0.8]]                           # Shape: (1, 3) <- !
```

#### 2. If any dimensions differ in size, expand the ones that have size 1 by duplicating their elements:
```python
left  = [[0.1,  0.1,  0.1],                             # Shape: (3, 3) <- !
         [0.6,  0.6,  0.6],
         [0.8,  0.8,  0.8]]

right = [[0.1,  0.6,  0.8],                             # Shape: (3, 3) <- !
         [0.1,  0.6,  0.8],
         [0.1,  0.6,  0.8]]
```

#### 3. If neither non-matching dimension has size 1, raise an error.


### Example
#### For each point returns index of its nearest point (`[0.1, 0.6, 0.8] => [1, 2, 1]`):

```python
>>> points = np.array([0.1, 0.6, 0.8])
 [ 0.1,  0.6,  0.8]
>>> wrapped_points = points.reshape(3, 1)
[[ 0.1],
 [ 0.6],
 [ 0.8]]
>>> distances = wrapped_points - points
[[ 0. , -0.5, -0.7],
 [ 0.5,  0. , -0.2],
 [ 0.7,  0.2,  0. ]]
>>> distances = np.abs(distances)
[[ 0. ,  0.5,  0.7],
 [ 0.5,  0. ,  0.2],
 [ 0.7,  0.2,  0. ]]
>>> i = np.arange(3)
[0, 1, 2]
>>> distances[i, i] = np.inf
[[ inf,  0.5,  0.7],
 [ 0.5,  inf,  0.2],
 [ 0.7,  0.2,  inf]]
>>> distances.argmin(1)
[1, 2, 1]
```

**[🔼Back to Top](#content-outlines)**

<a id="image"></a>
图像
-----
```python
# $ pip3 install pillow
from PIL import Image
```

```python
<Image> = Image.new('<mode>', (width, height))   # Also: `color=<int/tuple/str>`.
<Image> = Image.open(<path>)                     # Identifies format based on file contents.
<Image> = <Image>.convert('<mode>')              # Converts image to the new mode.
<Image>.save(<path>)                             # Selects format based on the path extension.
<Image>.show()                                   # Opens image in default preview app.
```

```python
<int/tuple> = <Image>.getpixel((x, y))           # Returns a pixel.
<Image>.putpixel((x, y), <int/tuple>)            # Writes a pixel to the image.
<ImagingCore> = <Image>.getdata()                # Returns a flattened sequence of pixels.
<Image>.putdata(<list/ImagingCore>)              # Writes a flattened sequence of pixels.
<Image>.paste(<Image>, (x, y))                   # Writes passed image to the image.
```

```bash
<2d_array> = np.array(<Image_L>)                 # Creates NumPy array from greyscale image.
<3d_array> = np.array(<Image_RGB/A>)             # Creates NumPy array from color image.
<Image>    = Image.fromarray(np.uint8(<array>))  # Use <array>.clip(0, 255) to clip the values.
```

### Modes
* **`'1'` - 1 位像素，黑白，每字节存储一个像素。**
* **`'L'` - 8 位像素，灰度。**
* **`'RGB'` - 3x8 位像素，真彩色。**
* **`'RGBA'` - 4x8 位像素，带透明蒙版的彩色。**
* **`'HSV'` - 3x8 位像素，色相、饱和度、明度色彩空间。**

### Examples
#### Creates a PNG image of a rainbow gradient:
```python
WIDTH, HEIGHT = 100, 100
n_pixels = WIDTH * HEIGHT
hues = (255 * i/n_pixels for i in range(n_pixels))
img = Image.new('HSV', (WIDTH, HEIGHT))
img.putdata([(int(h), 255, 255) for h in hues])
img.convert('RGB').save('test.png')
```

#### Adds noise to a PNG image:
```python
from random import randint
add_noise = lambda value: max(0, min(255, value + randint(-20, 20)))
img = Image.open('test.png').convert('HSV')
img.putdata([(add_noise(h), s, v) for h, s, v in img.getdata()])
img.convert('RGB').save('test.png')
```

### Image Draw
```python
from PIL import ImageDraw
<ImageDraw> = ImageDraw.Draw(<Image>)
```

```python
<ImageDraw>.point((x, y))                        # Truncates floats into ints.
<ImageDraw>.line((x1, y1, x2, y2 [, ...]))       # To get anti-aliasing use Image's resize().
<ImageDraw>.arc((x1, y1, x2, y2), deg1, deg2)    # Always draws in clockwise direction.
<ImageDraw>.rectangle((x1, y1, x2, y2))          # To rotate use Image's rotate() and paste().
<ImageDraw>.polygon((x1, y1, x2, y2, ...))       # Last point gets connected to the first.
<ImageDraw>.ellipse((x1, y1, x2, y2))            # To rotate use Image's rotate() and paste().
```
* **使用 `'fill=<color>'` 设置主要颜色。**
* **使用 `'width=<int>'` 设置线或轮廓的宽度。**
* **使用 `'outline=<color>'` 设置轮廓的颜色。**
* **颜色可以是 int、tuple、`'#rrggbb[aa]'` 字符串或颜色名称。**


<a id="animation"></a>
动画
---------
#### Creates a GIF of a bouncing ball:
```python
# $ pip3 install imageio
from PIL import Image, ImageDraw
import imageio

WIDTH, HEIGHT, R = 126, 126, 10
frames = []
for velocity in range(1, 16):
    y = sum(range(velocity))
    frame = Image.new('L', (WIDTH, HEIGHT))
    draw  = ImageDraw.Draw(frame)
    draw.ellipse((WIDTH/2-R, y, WIDTH/2+R, y+R*2), fill='white')
    frames.append(frame)
frames += reversed(frames[1:-1])
imageio.mimsave('test.gif', frames, duration=0.03)
```

**[🔼Back to Top](#content-outlines)**

<a id="audio"></a>
音频
-----
```python
import wave
```

```python
<Wave_read>  = wave.open('<path>', 'rb')        # Opens the WAV file.
framerate    = <Wave_read>.getframerate()       # Number of frames per second.
nchannels    = <Wave_read>.getnchannels()       # Number of samples per frame.
sampwidth    = <Wave_read>.getsampwidth()       # Sample size in bytes.
nframes      = <Wave_read>.getnframes()         # Number of frames.
<params>     = <Wave_read>.getparams()          # Immutable collection of above.
<bytes>      = <Wave_read>.readframes(nframes)  # Returns next 'nframes' frames.
```

```python
<Wave_write> = wave.open('<path>', 'wb')        # Truncates existing file.
<Wave_write>.setframerate(<int>)                # 44100 for CD, 48000 for video.
<Wave_write>.setnchannels(<int>)                # 1 for mono, 2 for stereo.
<Wave_write>.setsampwidth(<int>)                # 2 for CD quality sound.
<Wave_write>.setparams(<params>)                # Sets all parameters.
<Wave_write>.writeframes(<bytes>)               # Appends frames to the file.
```
* **字节对象包含一系列帧，每帧由一个或多个样本组成。**
* **在立体声信号中，一帧的第一个样本属于左声道。**
* **每个样本由一个或多个字节组成，将其转换为整数后表示给定时刻扬声器膜的位移。**
* **如果样本宽度为 1 字节，则整数应编码为无符号。**
* **对于所有其他大小，整数应编码为有符号，且字节序为小端。**

### Sample Values
```text
+-----------+-----------+------+-----------+
| sampwidth |    min    | zero |    max    |
+-----------+-----------+------+-----------+
|     1     |         0 |  128 |       255 |
|     2     |    -32768 |    0 |     32767 |
|     3     |  -8388608 |    0 |   8388607 |
+-----------+-----------+------+-----------+
```

### Read Float Samples from WAV File
```python
def read_wav_file(filename):
    def get_int(bytes_obj):
        an_int = int.from_bytes(bytes_obj, 'little', signed=(sampwidth != 1))
        return an_int - 128 * (sampwidth == 1)
    with wave.open(filename, 'rb') as file:
        sampwidth = file.getsampwidth()
        frames = file.readframes(-1)
    bytes_samples = (frames[i : i+sampwidth] for i in range(0, len(frames), sampwidth))
    return [get_int(b) / pow(2, sampwidth * 8 - 1) for b in bytes_samples]
```

### Write Float Samples to WAV File
```python
def write_to_wav_file(filename, float_samples, nchannels=1, sampwidth=2, framerate=44100):
    def get_bytes(a_float):
        a_float = max(-1, min(1 - 2e-16, a_float))
        a_float += sampwidth == 1
        a_float *= pow(2, sampwidth * 8 - 1)
        return int(a_float).to_bytes(sampwidth, 'little', signed=(sampwidth != 1))
    with wave.open(filename, 'wb') as file:
        file.setnchannels(nchannels)
        file.setsampwidth(sampwidth)
        file.setframerate(framerate)
        file.writeframes(b''.join(get_bytes(f) for f in float_samples))
```

### Examples
#### Saves a 440 Hz sine wave to a mono WAV file:
```python
from math import pi, sin
samples_f = (sin(i * 2 * pi * 440 / 44100) for i in range(100000))
write_to_wav_file('test.wav', samples_f)
```

#### Adds noise to a mono WAV file:
```python
from random import random
add_noise = lambda value: value + (random() - 0.5) * 0.03
samples_f = (add_noise(f) for f in read_wav_file('test.wav'))
write_to_wav_file('test.wav', samples_f)
```

#### Plays a WAV file:
```python
# $ pip3 install simpleaudio
from simpleaudio import play_buffer
with wave.open('test.wav', 'rb') as file:
    p = file.getparams()
    frames = file.readframes(-1)
    play_buffer(frames, p.nchannels, p.sampwidth, p.framerate)
```

### Text to Speech
```python
# $ pip3 install pyttsx3
import pyttsx3
engine = pyttsx3.init()
engine.say('Sally sells seashells by the seashore.')
engine.runAndWait()
```


<a id="synthesizer"></a>
合成器
-----------
#### Plays Popcorn by Gershon Kingsley:
```python
# $ pip3 install simpleaudio
import itertools as it, math, struct, simpleaudio

F  = 44100
P1 = '71♩,69♪,,71♩,66♪,,62♩,66♪,,59♩,,'
P2 = '71♩,73♪,,74♩,73♪,,74♪,,71♪,,73♩,71♪,,73♪,,69♪,,71♩,69♪,,71♪,,67♪,,71♩,,'
get_pause   = lambda seconds: it.repeat(0, int(seconds * F))
sin_f       = lambda i, hz: math.sin(i * 2 * math.pi * hz / F)
get_wave    = lambda hz, seconds: (sin_f(i, hz) for i in range(int(seconds * F)))
get_hz      = lambda key: 8.176 * 2 ** (int(key) / 12)
parse_note  = lambda note: (get_hz(note[:2]), 1/4 if '♩' in note else 1/8)
get_samples = lambda note: get_wave(*parse_note(note)) if note else get_pause(1/8)
samples_f   = it.chain.from_iterable(get_samples(n) for n in f'{P1},{P1},{P2}'.split(','))
samples_b   = b''.join(struct.pack('<h', int(f * 30000)) for f in samples_f)
simpleaudio.play_buffer(samples_b, 1, 2, F)
```

**[🔼Back to Top](#content-outlines)**

<a id="pygame"></a>
Pygame
------
```python
# $ pip3 install pygame
import pygame as pg

pg.init()
screen = pg.display.set_mode((500, 500))
rect = pg.Rect(240, 240, 20, 20)
while all(event.type != pg.QUIT for event in pg.event.get()):
    deltas = {pg.K_UP: (0, -1), pg.K_RIGHT: (1, 0), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0)}
    for ch, is_pressed in enumerate(pg.key.get_pressed()):
        rect = rect.move(deltas[ch]) if ch in deltas and is_pressed else rect
    screen.fill((0, 0, 0))
    pg.draw.rect(screen, (255, 255, 255), rect)
    pg.display.flip()
```

### Rectangle
**用于存储矩形坐标的对象。**
```python
<Rect> = pg.Rect(x, y, width, height)           # Floats get truncated into ints.
<int>  = <Rect>.x/y/centerx/centery/…           # Top, right, bottom, left. Allows assignments.
<tup.> = <Rect>.topleft/center/…                # Topright, bottomright, bottomleft. Same.
<Rect> = <Rect>.move((x, y))                    # Use move_ip() to move in-place.
```

```python
<bool> = <Rect>.collidepoint((x, y))            # Checks if rectangle contains a point.
<bool> = <Rect>.colliderect(<Rect>)             # Checks if two rectangles overlap.
<int>  = <Rect>.collidelist(<list_of_Rect>)     # Returns index of first colliding Rect or -1.
<list> = <Rect>.collidelistall(<list_of_Rect>)  # Returns indexes of all colliding rectangles.
```

### Surface
**用于表示图像的对象。**
```python
<Surf> = pg.display.set_mode((width, height))   # Returns a display surface.
<Surf> = pg.Surface((width, height))            # New RGB surface. RGBA if `flags=pg.SRCALPHA`.
<Surf> = pg.image.load('<path>')                # Loads the image. Format depends on source.
<Surf> = <Surf>.subsurface(<Rect>)              # Returns a subsurface.
```

```python
<Surf>.fill(color)                              # Tuple, Color('#rrggbb[aa]') or Color(<name>).
<Surf>.set_at((x, y), color)                    # Updates pixel.
<Surf>.blit(<Surf>, (x, y))                     # Draws passed surface to the surface.
```

```python
from pygame.transform import scale, ...
<Surf> = scale(<Surf>, (width, height))         # Returns scaled surface.
<Surf> = rotate(<Surf>, anticlock_degrees)      # Returns rotated and scaled surface.
<Surf> = flip(<Surf>, x_bool, y_bool)           # Returns flipped surface.
```

```python
from pygame.draw import line, ...
line(<Surf>, color, (x1, y1), (x2, y2), width)  # Draws a line to the surface.
arc(<Surf>, color, <Rect>, from_rad, to_rad)    # Also: ellipse(<Surf>, color, <Rect>, width=0)
rect(<Surf>, color, <Rect>, width=0)            # Also: polygon(<Surf>, color, points, width=0)
```

### Font
```python
<Font> = pg.font.SysFont('<name>', size)        # Loads the system font or default if missing.
<Font> = pg.font.Font('<path>', size)           # Loads the TTF file. Pass None for default.
<Surf> = <Font>.render(text, antialias, color)  # Background color can be specified at the end.
```

### Sound
```python
<Sound> = pg.mixer.Sound('<path>')              # Loads the WAV file.
<Sound>.play()                                  # Starts playing the sound.
```

### Basic Mario Brothers Example
```python
import collections, dataclasses, enum, io, itertools as it, pygame as pg, urllib.request
from random import randint

P = collections.namedtuple('P', 'x y')          # Position
D = enum.Enum('D', 'n e s w')                   # Direction
W, H, MAX_S = 50, 50, P(5, 10)                  # Width, Height, Max speed

def main():
    def get_screen():
        pg.init()
        return pg.display.set_mode((W*16, H*16))
    def get_images():
        url = 'https://gto76.github.io/python-cheatsheet/web/mario_bros.png'
        img = pg.image.load(io.BytesIO(urllib.request.urlopen(url).read()))
        return [img.subsurface(get_rect(x, 0)) for x in range(img.get_width() // 16)]
    def get_mario():
        Mario = dataclasses.make_dataclass('Mario', 'rect spd facing_left frame_cycle'.split())
        return Mario(get_rect(1, 1), P(0, 0), False, it.cycle(range(3)))
    def get_tiles():
        border = [(x, y) for x in range(W) for y in range(H) if x in [0, W-1] or y in [0, H-1]]
        platforms = [(randint(1, W-2), randint(2, H-2)) for _ in range(W*H // 10)]
        return [get_rect(x, y) for x, y in border + platforms]
    def get_rect(x, y):
        return pg.Rect(x*16, y*16, 16, 16)
    run(get_screen(), get_images(), get_mario(), get_tiles())

def run(screen, images, mario, tiles):
    clock = pg.time.Clock()
    while all(event.type != pg.QUIT for event in pg.event.get()):
        keys = {pg.K_UP: D.n, pg.K_RIGHT: D.e, pg.K_DOWN: D.s, pg.K_LEFT: D.w}
        pressed = {keys.get(ch) for ch, is_prsd in enumerate(pg.key.get_pressed()) if is_prsd}
        update_speed(mario, tiles, pressed)
        update_position(mario, tiles)
        draw(screen, images, mario, tiles, pressed)
        clock.tick(28)

def update_speed(mario, tiles, pressed):
    x, y = mario.spd
    x += 2 * ((D.e in pressed) - (D.w in pressed))
    x -= (x > 0) - (x < 0)
    y += 1 if D.s not in get_boundaries(mario.rect, tiles) else (D.n in pressed) * -10
    mario.spd = P(x=max(-MAX_S.x, min(MAX_S.x, x)), y=max(-MAX_S.y, min(MAX_S.y, y)))

def update_position(mario, tiles):
    x, y = mario.rect.topleft
    n_steps = max(abs(s) for s in mario.spd)
    for _ in range(n_steps):
        mario.spd = stop_on_collision(mario.spd, get_boundaries(mario.rect, tiles))
        x, y = x + mario.spd.x / n_steps, y + mario.spd.y / n_steps
        mario.rect.topleft = x, y

def get_boundaries(rect, tiles):
    deltas = {D.n: P(0, -1), D.e: P(1, 0), D.s: P(0, 1), D.w: P(-1, 0)}
    return {d for d, delta in deltas.items() if rect.move(delta).collidelist(tiles) != -1}

def stop_on_collision(spd, bounds):
    return P(x=0 if (D.w in bounds and spd.x < 0) or (D.e in bounds and spd.x > 0) else spd.x,
             y=0 if (D.n in bounds and spd.y < 0) or (D.s in bounds and spd.y > 0) else spd.y)

def draw(screen, images, mario, tiles, pressed):
    def get_marios_image_index():
        if D.s not in get_boundaries(mario.rect, tiles):
            return 4
        return next(mario.frame_cycle) if {D.w, D.e} & pressed else 6
    screen.fill((85, 168, 255))
    mario.facing_left = (D.w in pressed) if {D.w, D.e} & pressed else mario.facing_left
    screen.blit(images[get_marios_image_index() + mario.facing_left * 9], mario.rect)
    for t in tiles:
        screen.blit(images[18 if t.x in [0, (W-1)*16] or t.y in [0, (H-1)*16] else 19], t)
    pg.display.flip()

if __name__ == '__main__':
    main()
```

**[🔼Back to Top](#content-outlines)**

<a id="pandas"></a>
Pandas
------
```python
# $ pip3 install pandas matplotlib
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
```

### Series
**带有名称的有序字典。**

```python
>>> Series([1, 2], index=['x', 'y'], name='a')
x    1
y    2
Name: a, dtype: int64
```

```python
<Sr> = Series(<list>)                          # Assigns RangeIndex starting at 0.
<Sr> = Series(<dict>)                          # Takes dictionary's keys for index.
<Sr> = Series(<dict/Series>, index=<list>)     # Only keeps items with keys specified in index.
```

```python
<el> = <Sr>.loc[key]                           # Or: <Sr>.iloc[index]
<Sr> = <Sr>.loc[keys]                          # Or: <Sr>.iloc[indexes]
<Sr> = <Sr>.loc[from_key : to_key_inclusive]   # Or: <Sr>.iloc[from_i : to_i_exclusive]
```

```python
<el> = <Sr>[key/index]                         # Or: <Sr>.key
<Sr> = <Sr>[keys/indexes]                      # Or: <Sr>[<key_range/range>]
<Sr> = <Sr>[bools]                             # Or: <Sr>.i/loc[bools]
```

```python
<Sr> = <Sr> ><== <el/Sr>                       # Returns a Series of bools.
<Sr> = <Sr> +-*/ <el/Sr>                       # Items with non-matching keys get value NaN.
```

```python
<Sr> = <Sr>.append(<Sr>)                       # Or: pd.concat(<coll_of_Sr>)
<Sr> = <Sr>.combine_first(<Sr>)                # Adds items that are not yet present.
<Sr>.update(<Sr>)                              # Updates items that are already present.
```

```python
<Sr>.plot.line/area/bar/pie/hist()             # Generates a Matplotlib plot.
plt.show()                                     # Displays the plot. Also plt.savefig(<path>).
```

#### Series — Aggregate, Transform, Map:
```python
<el> = <Sr>.sum/max/mean/idxmax/all()          # Or: <Sr>.agg(lambda <Sr>: <el>)
<Sr> = <Sr>.rank/diff/cumsum/ffill/interpl()   # Or: <Sr>.agg/transform(lambda <Sr>: <Sr>)
<Sr> = <Sr>.fillna(<el>)                       # Or: <Sr>.agg/transform/map(lambda <el>: <el>)
```

```python
>>> sr = Series([1, 2], index=['x', 'y'])
x    1
y    2
```

```text
+-----------------+-------------+-------------+---------------+
|                 |    'sum'    |   ['sum']   | {'s': 'sum'}  |
+-----------------+-------------+-------------+---------------+
| sr.apply(…)     |      3      |    sum  3   |     s  3      |
| sr.agg(…)       |             |             |               |
+-----------------+-------------+-------------+---------------+
```

```text
+-----------------+-------------+-------------+---------------+
|                 |    'rank'   |   ['rank']  | {'r': 'rank'} |
+-----------------+-------------+-------------+---------------+
| sr.apply(…)     |             |      rank   |               |
| sr.agg(…)       |     x  1    |   x     1   |    r  x  1    |
| sr.transform(…) |     y  2    |   y     2   |       y  2    |
+-----------------+-------------+-------------+---------------+
```
* **最后一个结果具有分层索引。使用 `'<Sr>[key_1, key_2]'` 获取其值。**

**[🔼Back to Top](#content-outlines)**

<a id="opencv"></a>
OpenCV
------

```python
# Importing an Image & Viewing it
import cv2
image = cv2.imread("./path/to/image.jpg")
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

裁剪图像
```python 
import cv2
image = cv2.imread("./path/to/image.jpg")
crop_img = image[y:y+h, x:x+w]
cv2.imshow("cropped", crop_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
```
缩放图像
```python
import cv2
image = cv2.imread("./path/to/image.jpg")
resized_image = cv2.resize(image, (100, 100))
cv2.imshow("Resized image", resized_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```
保存图像
```python
import cv2
image = cv2.imread("./path/to/image.jpg")
cv2.imwrite("./path/to/save/image.jpg", image)
```
将图像转换为灰度图
```python
import cv2
image = cv2.imread("./path/to/image.jpg")
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow("Grayscale image", gray_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```
将图像转换为 HSV
```python
import cv2
image = cv2.imread("./path/to/image.jpg")
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
cv2.imshow("HSV image", hsv_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```
将图像转换为 LAB
```python
import cv2
image = cv2.imread("./path/to/image.jpg")
lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
cv2.imshow("LAB image", lab_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```
将图像转换为 RGB
```python
import cv2
image = cv2.imread("./path/to/image.jpg")
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
cv2.imshow("RGB image", rgb_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

**[🔼Back to Top](#content-outlines)**

<a id="dataframe"></a>
DataFrame
**带有标签行和列的表。**

```python
>>> DataFrame([[1, 2], [3, 4]], index=['a', 'b'], columns=['x', 'y'])
   x  y
a  1  2
b  3  4
```

```python
<DF>    = DataFrame(<list_of_rows>)            # Rows can be either lists, dicts or series.
<DF>    = DataFrame(<dict_of_columns>)         # Columns can be either lists, dicts or series.
```

```python
<el>    = <DF>.loc[row_key, column_key]        # Or: <DF>.iloc[row_index, column_index]
<Sr/DF> = <DF>.loc[row_key/s]                  # Or: <DF>.iloc[row_index/es]
<Sr/DF> = <DF>.loc[:, column_key/s]            # Or: <DF>.iloc[:, column_index/es]
<DF>    = <DF>.loc[row_bools, column_bools]    # Or: <DF>.iloc[row_bools, column_bools]
```

```python
<Sr/DF> = <DF>[column_key/s]                   # Or: <DF>.column_key
<DF>    = <DF>[row_bools]                      # Keeps rows as specified by bools.
<DF>    = <DF>[<DF_of_bools>]                  # Assigns NaN to False values.
```

```python
<DF>    = <DF> ><== <el/Sr/DF>                 # Returns DF of bools. Sr is treated as a row.
<DF>    = <DF> +-*/ <el/Sr/DF>                 # Items with non-matching keys get value NaN.
```

```python
<DF>    = <DF>.set_index(column_key)           # Replaces row keys with values from a column.
<DF>    = <DF>.reset_index()                   # Moves row keys to a column named index.
<DF>    = <DF>.sort_index(ascending=True)      # Sorts rows by row keys.
<DF>    = <DF>.sort_values(column_key/s)       # Sorts rows by the passed column/s.
```

#### DataFrame — Merge, Join, Concat:
```python
>>> l = DataFrame([[1, 2], [3, 4]], index=['a', 'b'], columns=['x', 'y'])
   x  y
a  1  2
b  3  4
>>> r = DataFrame([[4, 5], [6, 7]], index=['b', 'c'], columns=['y', 'z'])
   y  z
b  4  5
c  6  7
```

```text
+------------------------+---------------+------------+------------+--------------------------+
|                        |    'outer'    |   'inner'  |   'left'   |       Description        |
+------------------------+---------------+------------+------------+--------------------------+
| l.merge(r, on='y',     |    x   y   z  | x   y   z  | x   y   z  | Joins/merges on column.  |
|            how=…)      | 0  1   2   .  | 3   4   5  | 1   2   .  | Also accepts left_on and |
|                        | 1  3   4   5  |            | 3   4   5  | right_on parameters.     |
|                        | 2  .   6   7  |            |            | Uses 'inner' by default. |
+------------------------+---------------+------------+------------+--------------------------+
| l.join(r, lsuffix='l', |    x yl yr  z |            | x yl yr  z | Joins/merges on row keys.|
|           rsuffix='r', | a  1  2  .  . | x yl yr  z | 1  2  .  . | Uses 'left' by default.  |
|           how=…)       | b  3  4  4  5 | 3  4  4  5 | 3  4  4  5 | If r is a Series, it is  |
|                        | c  .  .  6  7 |            |            | treated as a column.     |
+------------------------+---------------+------------+------------+--------------------------+
| pd.concat([l, r],      |    x   y   z  |     y      |            | Adds rows at the bottom. |
|           axis=0,      | a  1   2   .  |     2      |            | Uses 'outer' by default. |
|           join=…)      | b  3   4   .  |     4      |            | A Series is treated as a |
|                        | b  .   4   5  |     4      |            | column. Use l.append(sr) |
|                        | c  .   6   7  |     6      |            | to add a row instead.    |
+------------------------+---------------+------------+------------+--------------------------+
| pd.concat([l, r],      |    x  y  y  z |            |            | Adds columns at the      |
|           axis=1,      | a  1  2  .  . | x  y  y  z |            | right end. Uses 'outer'  |
|           join=…)      | b  3  4  4  5 | 3  4  4  5 |            | by default. A Series is  |
|                        | c  .  .  6  7 |            |            | treated as a column.     |
+------------------------+---------------+------------+------------+--------------------------+
| l.combine_first(r)     |    x   y   z  |            |            | Adds missing rows and    |
|                        | a  1   2   .  |            |            | columns. Also updates    |
|                        | b  3   4   5  |            |            | items that contain NaN.  |
|                        | c  .   6   7  |            |            | R must be a DataFrame.   |
+------------------------+---------------+------------+------------+--------------------------+
```

#### DataFrame — Aggregate, Transform, Map:
```python
<Sr> = <DF>.sum/max/mean/idxmax/all()          # Or: <DF>.apply/agg(lambda <Sr>: <el>)
<DF> = <DF>.rank/diff/cumsum/ffill/interpl()   # Or: <DF>.apply/agg/transfrm(lambda <Sr>: <Sr>)
<DF> = <DF>.fillna(<el>)                       # Or: <DF>.applymap(lambda <el>: <el>)
```
* **默认情况下，所有操作都作用于列。传入 `'axis=1'` 可改为处理行。**

```python
>>> df = DataFrame([[1, 2], [3, 4]], index=['a', 'b'], columns=['x', 'y'])
   x  y
a  1  2
b  3  4
```

```text
+-----------------+-------------+-------------+---------------+
|                 |    'sum'    |   ['sum']   | {'x': 'sum'}  |
+-----------------+-------------+-------------+---------------+
| df.apply(…)     |             |       x  y  |               |
| df.agg(…)       |     x  4    |  sum  4  6  |     x  4      |
|                 |     y  6    |             |               |
+-----------------+-------------+-------------+---------------+
```

```text
+-----------------+-------------+-------------+---------------+
|                 |    'rank'   |   ['rank']  | {'x': 'rank'} |
+-----------------+-------------+-------------+---------------+
| df.apply(…)     |      x  y   |      x    y |        x      |
| df.agg(…)       |   a  1  1   |   rank rank |     a  1      |
| df.transform(…) |   b  2  2   | a    1    1 |     b  2      |
|                 |             | b    2    2 |               |
+-----------------+-------------+-------------+---------------+
```
* **使用 `'<DF>[col_key_1, col_key_2][row_key]'` 获取第五个结果的值。**

<a id="dataframe-plot-encode-decode"></a>
#### DataFrame — Plot, Encode, Decode:
```python
<DF>.plot.line/bar/hist/scatter/box()          # Also: `x=column_key, y=column_key/s`.
plt.show()                                     # Displays the plot. Also plt.savefig(<path>).
```

```python
<DF> = pd.read_json/html('<str/path/url>')     # Run `$ pip3 install beautifulsoup4 lxml`.
<DF> = pd.read_csv/pickle/excel('<path/url>')  # Use `sheet_name=None` to get all Excel sheets.
<DF> = pd.read_sql('<table/query>', <conn.>)   # Accepts SQLite3 or SQLAlchemy connection.
<DF> = pd.read_clipboard()                     # Reads a copied table from the clipboard.
```

```python
<dict> = <DF>.to_dict(['d/l/s/…'])             # Returns columns as dicts, lists or series.
<str>  = <DF>.to_json/html/csv([<path>])       # Also to_markdown/latex([<path>]).
<DF>.to_pickle/excel(<path>)                   # Run `$ pip3 install openpyxl` for xlsx files.
<DF>.to_sql('<table_name>', <connection>)      # Accepts SQLite3 or SQLAlchemy connection.
```

### GroupBy
**根据传入列的值将 DataFrame 的行分组的对象。**

```python
>>> df = DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 6]], index=list('abc'), columns=list('xyz'))
>>> df.groupby('z').get_group(6)
   x  y
b  4  5
c  7  8
```

```python
<GB> = <DF>.groupby(column_key/s)              # Splits DF into groups based on passed column.
<DF> = <GB>.apply(<func>)                      # Maps each group. Func can return DF, Sr or el.
<GB> = <GB>[column_key]                        # Single column GB. All operations return a Sr.
```

#### GroupBy — Aggregate, Transform, Map:
```python
<DF> = <GB>.sum/max/mean/idxmax/all()          # Or: <GB>.agg(lambda <Sr>: <el>)
<DF> = <GB>.rank/diff/cumsum/ffill()           # Or: <GB>.transform(lambda <Sr>: <Sr>)
<DF> = <GB>.fillna(<el>)                       # Or: <GB>.transform(lambda <Sr>: <Sr>)
```

```python
>>> gb = df.groupby('z')
      x  y  z
3: a  1  2  3
6: b  4  5  6
   c  7  8  6
```

```text
+-----------------+-------------+-------------+-------------+---------------+
|                 |    'sum'    |    'rank'   |   ['rank']  | {'x': 'rank'} |
+-----------------+-------------+-------------+-------------+---------------+
| gb.agg(…)       |      x   y  |      x  y   |      x    y |        x      |
|                 |  z          |   a  1  1   |   rank rank |     a  1      |
|                 |  3   1   2  |   b  1  1   | a    1    1 |     b  1      |
|                 |  6  11  13  |   c  2  2   | b    1    1 |     c  2      |
|                 |             |             | c    2    2 |               |
+-----------------+-------------+-------------+-------------+---------------+
| gb.transform(…) |      x   y  |      x  y   |             |               |
|                 |  a   1   2  |   a  1  1   |             |               |
|                 |  b  11  13  |   b  1  1   |             |               |
|                 |  c  11  13  |   c  2  2   |             |               |
+-----------------+-------------+-------------+-------------+---------------+
```

### Rolling
**用于滚动窗口计算的对象。**

```python
<RSr/RDF/RGB> = <Sr/DF/GB>.rolling(win_size)   # Also: `min_periods=None, center=False`.
<RSr/RDF/RGB> = <RDF/RGB>[column_key/s]        # Or: <RDF/RGB>.column_key
<Sr/DF>       = <R>.mean/sum/max()             # Or: <R>.apply/agg(<agg_func/str>)
```


<a id="plotly"></a>
Plotly
------
```python
# $ pip3 install plotly kaleido
from plotly.express import line
<Figure> = line(<DF>, x=<col_name>, y=<col_name>)        # Or: line(x=<list>, y=<list>)
<Figure>.update_layout(margin=dict(t=0, r=0, b=0, l=0))  # Or: paper_bgcolor='rgba(0, 0, 0, 0)'
<Figure>.write_html/json/image('<path>')                 # Also: <Figure>.show()
```

#### Covid deaths by continent:

![Covid Deaths](web/covid_deaths.png)
<div id="2a950764-39fc-416d-97fe-0a6226a3095f" class="plotly-graph-div" style="height:340px; width:100%;"></div>

```python
covid = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv',
                    usecols=['iso_code', 'date', 'total_deaths', 'population'])
continents = pd.read_csv('https://gist.githubusercontent.com/stevewithington/20a69c0b6d2ff'
                         '846ea5d35e5fc47f26c/raw/country-and-continent-codes-list-csv.csv',
                         usecols=['Three_Letter_Country_Code', 'Continent_Name'])
df = pd.merge(covid, continents, left_on='iso_code', right_on='Three_Letter_Country_Code')
df = df.groupby(['Continent_Name', 'date']).sum().reset_index()
df['Total Deaths per Million'] = df.total_deaths * 1e6 / df.population
df = df[df.date > '2020-03-14']
df = df.rename({'date': 'Date', 'Continent_Name': 'Continent'}, axis='columns')
line(df, x='Date', y='Total Deaths per Million', color='Continent').show()
```

#### Confirmed covid cases, Dow Jones, Gold, and Bitcoin price:

![Covid Cases](web/covid_cases.png)
<div id="e23ccacc-a456-478b-b467-7282a2165921" class="plotly-graph-div" style="height:315px; width:100%;"></div>

```python
import pandas as pd
import plotly.graph_objects as go

def main():
    display_data(wrangle_data(*scrape_data()))

def scrape_data():
    def scrape_covid():
        url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
        df = pd.read_csv(url, usecols=['location', 'date', 'total_cases'])
        return df[df.location == 'World'].set_index('date').total_cases
    def scrape_yahoo(slug):
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{slug}' + \
              '?period1=1579651200&period2=9999999999&interval=1d&events=history'
        df = pd.read_csv(url, usecols=['Date', 'Close'])
        return df.set_index('Date').Close
    out = scrape_covid(), scrape_yahoo('BTC-USD'), scrape_yahoo('GC=F'), scrape_yahoo('^DJI')
    return map(pd.Series.rename, out, ['Total Cases', 'Bitcoin', 'Gold', 'Dow Jones'])

def wrangle_data(covid, bitcoin, gold, dow):
    df = pd.concat([bitcoin, gold, dow], axis=1)  # Joins columns on dates.
    df = df.sort_index().interpolate()            # Sorts by date and interpolates NaN-s.
    df = df.loc['2020-02-23':]                    # Discards rows before '2020-02-23'.
    df = (df / df.iloc[0]) * 100                  # Calculates percentages relative to day 1.
    df = df.join(covid)                           # Adds column with covid cases.
    return df.sort_values(df.index[-1], axis=1)   # Sorts columns by last day's value.

def display_data(df):
    figure = go.Figure()
    for col_name in reversed(df.columns):
        yaxis = 'y1' if col_name == 'Total Cases' else 'y2'
        trace = go.Scatter(x=df.index, y=df[col_name], name=col_name, yaxis=yaxis)
        figure.add_trace(trace)
    figure.update_layout(
        yaxis1=dict(title='Total Cases', rangemode='tozero'),
        yaxis2=dict(title='%', rangemode='tozero', overlaying='y', side='right'),
        legend=dict(x=1.1),
        height=450
    ).show()

if __name__ == '__main__':
    main()
```


<a id="pysimplegui"></a>
PySimpleGUI
-----------
```python
# $ pip3 install PySimpleGUI
import PySimpleGUI as sg
layout = [[sg.Text("What's your name?")], [sg.Input()], [sg.Button('Ok')]]
window = sg.Window('Window Title', layout)
event, values = window.read()
print(f'Hello {values[0]}!' if event == 'Ok' else '')
```


<a id="appendix"></a>
附录
--------
### Cython
**将 Python 代码编译为 C 的库。**

```python
# $ pip3 install cython
import pyximport; pyximport.install()
import <cython_script>
<cython_script>.main()
```

#### Definitions:
* **所有 `'cdef'` 定义都是可选的，但它们有助于加速。**
* **脚本需要以 `'pyx'` 扩展名保存。**

```python
cdef <ctype> <var_name> = <el>
cdef <ctype>[n_elements] <var_name> = [<el_1>, <el_2>, ...]
cdef <ctype/void> <func_name>(<ctype> <arg_name>): ...
```

```python
cdef class <class_name>:
    cdef public <ctype> <attr_name>
    def __init__(self, <ctype> <arg_name>):
        self.<attr_name> = <arg_name>
```

```python
cdef enum <enum_name>: <member_name_1>, <member_name_2>, ...
```

### PyInstaller
```bash
$ pip3 install pyinstaller
$ pyinstaller script.py                        # Compiles into './dist/script' directory.
$ pyinstaller script.py --onefile              # Compiles into './dist/script' console app.
$ pyinstaller script.py --windowed             # Compiles into './dist/script' windowed app.
$ pyinstaller script.py --add-data '<path>:.'  # Adds file to the root of the executable.
```
* **文件路径需要更新为 `'os.path.join(sys._MEIPASS, <path>)'`。**

### Basic Script Template
```python
#!/usr/bin/env python3
#
# Usage: .py
#

from sys import argv, exit
from collections import defaultdict, namedtuple
from dataclasses import make_dataclass
from enum import Enum
import functools as ft, itertools as it, operator as op, re


def main():
    pass


###
##  UTIL
#

def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()


if __name__ == '__main__':
    main()
```


<a id="index"></a>
索引
-----
* **仅在 [PDF](https://transactions.sendowl.com/products/78175486/4422834F/view) 中提供。**
* **Ctrl+F / ⌘F 通常已足够。**
* **在 [网页](https://gto76.github.io/python-cheatsheet/) 上搜索 `'#<title>'` 可将搜索范围限定在标题内。**

**[🔼Back to Top](#content-outlines)**
