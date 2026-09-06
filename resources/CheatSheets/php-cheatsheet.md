---
title: PHP 速查表
description: 这里列出了最常用的 PHP 概念。
created: 2022-10-23
---

<a id="table-of-contents"></a>

## 目录

- [PHP 开发者速查表](#php-cheatsheet-for-developers)
  - [转义序列](#escape-sequence)
  - [运算符](#operators)
    - [算术运算符](#arithmetic-operators)
    - [比较运算符](#comparison-operators)
    - [逻辑运算符](#logicaloperators)
    - [字符串运算符](#string-operators)
    - [数组运算符](#array-operators)
    - [条件赋值运算符](#conditional-assignment-operators)
    - [自增/自减运算符](#incrementdecrement-operators)
  - [超级全局变量](#super-global-variable)
  - [重要关键字 $_SERVER](#important-keywords-_server)
  - [函数](#functions)
    - [数组函数](#array-function)
    - [PHP 标准函数](#php-standard-functions)
    - [字符串函数](#string-function)
    - [文件函数](#file-function)
  - [读取文件](#read-file)
  - [Cookie 与 Session](#cookies-and-session)
  - [最重要函数](#most-important-function)
    - [日历函数](#calender-function)
    - [日期/时间函数](#datetime-function)
    - [过滤函数](#filter-function)
    - [MySQLi 函数](#mysqli--function)
    - [PHP 正则表达式函数](#php-regular-expression-functions)


<a id="php-cheatsheet-for-developers"></a>

# PHP 开发者速查表

<a id="escape-sequence"></a>

## 转义序列

| Command                | Description                                     |
| :--------------------: | :----------------------------------------------- |
| `// Comment Message` | 这是单行注释 |
| `$Title = "Title"` | 定义变量 |
| `\n` | 换行 |
| `\r` | 在文本此处插入一个回车符。 |
| `\t` | 提供水平制表符空格 |
| `\v` | 提供垂直制表符空格 |
| `\\` | 添加一个反斜杠 |
| `\$` | 将下一个字符作为美元符号输出，而不是变量的一部分 |
| `\'` | 将下一个字符作为单引号输出，而不是字符串结束符 |
| `\"` | 将下一个字符作为双引号输出，而不是字符串结束符 |

**[🔼Back to Top](#table-of-contents)**

<a id="operators"></a>

## 运算符

<a id="arithmetic-operators"></a>

### 算术运算符

|operator|name |syntax|
|:--------:|:------:|:-----:|
|`+`|	加法|	$x + $y|
|`-`|	减法|	$x - $y|
|`*` |	乘法|	$x * $y |
| `/` |	除法|	$x / $y|	
|`%`|	取模|	$x % $y|	
|` ** `|	幂运算 |	$x ** $y	|	

**[🔼Back to Top](#table-of-contents)**

<a id="comparison-operators"></a>

### 比较运算符

|operator|name |syntax|
|:--------:|:------:|:-----:|
|`==`|	等于|	$x == $y|	
|`===`|	全等|	$x === $y|
| `!= `| 	Not equal|	$x != $y|	
| `<>` |	不等于 |	$x <> $y	|	
|`!==` |	不全等|	$x !== $y |	
|`>`|	大于|	$x > $y|	
|`<`|	小于|	$x < $y|	
|`>=`|	大于等于|	$x >= $y|	
|`<=`|	小于等于|	$x <= $y|	
|`<=>`|	太空船运算符|	$x <=> $y	|

**[🔼Back to Top](#table-of-contents)**

<a id="logicaloperators"></a>

### 逻辑运算符

|operator|name |syntax|
|:--------:|:------:|:-----:|
|`and`|	与|	$x and $y|
|`or`	|或|	$x or $y	|
|`xor`|	异或|	$x xor $y	|
|`&&`|	与|	$x && $y|	
| `\|` | 或 | $x \| $y |
|`!`	|非	|!$x |	

**[🔼Back to Top](#table-of-contents)**

<a id="string-operators"></a>

### 字符串运算符

|operator|name |syntax|
|:--------:|:------:|:-----:|
|`.`|	连接|	$txt1 . $txt2	|
|`.=`|	连接赋值|	$txt1 .= $txt2|	

**[🔼Back to Top](#table-of-contents)**

<a id="array-operators"></a>

### 数组运算符

|operator|name |syntax|
|:--------:|:------:|:-----:|
|`+`|	合并|	$x + $y|	
|`==`|	相等|	$x == $y	|
|`===`|	恒等|	$x === $y |
|`!=`|	不等|	$x != $y	|
|`<>`|	不等|	$x <> $y	|
|`!==`|	不恒等|	$x !== $y	|	

**[🔼Back to Top](#table-of-contents)**

<a id="conditional-assignment-operators"></a>

### 条件赋值运算符

|operator|name |syntax|
|:--------:|:------:|:-----:|
|`?:	`|三元运算符|	$x = expr1 ? expr2 : expr3|
|`??`|	空合并运算符|	$x = expr1 ?? expr2|

**[🔼Back to Top](#table-of-contents)**

<a id="incrementdecrement-operators"></a>

### 自增/自减运算符

|operator|name |description|
|:--------:|:------:|:-----:|
|`++$x`|	前置自增|	先将 $x 自增 1|
|`$x++`|	后置自增|	先返回 $x，再将 $x 自增 1	|
|`--$x`|	前置自减	|先将 $x 自减 1，再返回 $x|
|`$x--`	|后置自减	|先返回 $x，再将 $x 自减 1	|	

**[🔼Back to Top](#table-of-contents)**

<a id="super-global-variable"></a>

## 超级全局变量

|keyword|description|
|:--------:|:------|
|`$GLOBALS`| 用于在 PHP 脚本的任何位置访问全局变量 |
|`$_SERVER`|保存有关请求头、路径和脚本位置的信息|
|` $_REQUEST`|用于在提交 HTML 表单后收集数据|
|`$_POST`|用于在以 method="post" 提交 HTML 表单后收集表单数据|
|`$_GET`|用于在以 method="get" 提交 HTML 表单后收集表单数据|
|`$_FILES`| 包含通过 HTTP POST 方法上传的条目的关联数组|
|`$_ENV`|通过环境变量传递给当前脚本的关联数组。|
|`$_COOKIE`|获取 cookie 的值|
|`$_SESSION`|会话是一种跨多个页面存储信息（以变量形式）的方式。|

**[🔼Back to Top](#table-of-contents)**

<a id="important-keywords-_server"></a>

## 重要关键字 $_SERVER

|Element/Code|	Description|
|:--------:|:------|
|`$_SERVER['PHP_SELF']`|	返回当前正在执行的脚本的文件名|
|`$_SERVER['GATEWAY_INTERFACE']`	|返回服务器使用的通用网关接口（CGI）版本|
|`$_SERVER['SERVER_ADDR']`	|返回主机服务器的 IP 地址|
|`$_SERVER['SERVER_NAME']`	|返回主机服务器的名称（例如 www.w3schools.com）|
|`$_SERVER['SERVER_SOFTWARE']`	|返回服务器标识字符串（例如 Apache/2.2.24）|
|`$_SERVER['SERVER_PROTOCOL']`	|返回信息协议的名称和版本（例如 HTTP/1.1）|
|`$_SERVER['REQUEST_METHOD']`	|返回访问页面所使用的请求方法（例如 POST）|
|`$_SERVER['REQUEST_TIME']`	|返回请求开始的时间戳（例如 1377687496）|
|`$_SERVER['QUERY_STRING']`	|如果页面通过查询字符串访问，则返回查询字符串|
|`$_SERVER['HTTP_ACCEPT']`	|返回当前请求的 Accept 请求头|
|`$_SERVER['HTTP_ACCEPT_CHARSET']`|	返回当前请求的 Accept_Charset 请求头（例如 utf-8,ISO-8859-1）|
|`$_SERVER['HTTP_HOST']`	|返回当前请求的 Host 请求头|
|`$_SERVER['HTTP_REFERER']`|	返回当前页面的完整 URL（不可靠，因为并非所有用户代理都支持）|
|`$_SERVER['HTTPS']`	|脚本是否通过安全的 HTTP 协议访问|
|`$_SERVER['REMOTE_ADDR']`|	返回用户查看当前页面的 IP 地址|
|`$_SERVER['REMOTE_HOST']	`|返回用户查看当前页面的主机名|
|`$_SERVER['REMOTE_PORT']	`|返回用户机器上用于与 Web 服务器通信的端口|
|`$_SERVER['SCRIPT_FILENAME']`|	返回当前正在执行的脚本的绝对路径名|
|`$_SERVER['SERVER_ADMIN']`	|返回 Web 服务器配置文件中 SERVER_ADMIN 指令的值（如果脚本运行在虚拟主机上，则为该虚拟主机定义的值）（例如 someone@hools.com）|
|`$_SERVER['SERVER_PORT']	`|返回 Web 服务器用于通信的服务器机器端口（例如 80）|
|`$_SERVER['SERVER_SIGNATURE']`	|返回被添加到服务器生成页面中的服务器版本和虚拟主机名|
|`$_SERVER['PATH_TRANSLATED']`	|返回当前脚本的基于文件系统的路径|
|`$_SERVER['SCRIPT_NAME']`	|返回当前脚本的路径|
|`$_SERVER['SCRIPT_URI']`	|返回当前页面的 URI|

**[🔼Back to Top](#table-of-contents)**

<a id="functions"></a>

## 函数

<a id="array-function"></a>

### 数组函数 

|Function |Description|
|:--------:|:------|
|`count(arr)`| 返回数组 arr 的长度|
|`print_r(arr)`| 打印 arr 的内容|
|`array_pop(arr)`| 弹出（移除）数组 arr 末尾的一个元素|
|`array_shift(arr)`| 移出（移除）数组 arr 开头的一个元素|
|`array_push(arr, el)`| 将一个或多个元素压入（添加）到数组 arr 的末尾|
|`array_unshift(arr, el)`| 将一个或多个元素前置到数组 arr 的开头|
|`sort(arr)`| 对数组 arr 进行排序|
|`array_reverse(arr)`| 返回元素顺序反转的数组 arr|
|`in_array(el, arr)`| 返回值 el 是否存在于数组 arr 中|
|`list(a, b, ...)` |将变量作为数组进行赋值|
|`implode(glue, pieces)`| 用字符串（glue）连接数组元素（pieces）|
|`array_rand(arr)`| 从数组中随机选择一个随机条目并返回随机条目的键（或键）|

**[🔼Back to Top](#table-of-contents)**

<a id="php-standard-functions"></a>

### PHP 标准函数

|Function| Description|
|:--------:|:------|
|`isset(el)` |如果 el 已被赋值为常量 NULL、el 尚未被赋值（未定义）或 el 已使用 unset 函数删除，则返回 false|
|`print str` <br /> or <br /> `echo str` | 打印 str |
|`time()`| 以秒为单位返回当前时间|
|`date(format, time)`| 根据 format 将可选的时间（秒）转换为日期|
|`mt_rand(min, max)`| 返回 min 和 max 之间（含）的随机整数|
|`header(string)`| 发送原始 HTTP 头。 |
|`die(message)`| 结束执行并返回可选消息|
|`include "path"` |包含并求值指定的文件路径，例如 "hidden/config.php"|

**[🔼Back to Top](#table-of-contents)**

<a id="string-function"></a>

### 字符串函数

|Function| Description|
|:--------:|:------|
|`strlen(s)`| 返回字符串 s 的长度|
|`strpos(str, substr)`| 返回 substr 在 str 中首次出现的位置，未找到则返回 FALSE|
|`substr(s, start,len)`| 返回从 start 开始、长度最多为 len 个字符的 s 的子串。如果 s 的长度小于 start 个字符，则返回 FALSE|
|`trim(s)`| 去除字符串 s 两端的空白字符|
|`strtolower(s)`| 返回 s 的小写版本|
|`strtoupper(s)` |返回 s 的大写版本|
|`explode(delimiter,s)`| 返回以 delimiter 分割 s 得到的子串数组|

**[🔼Back to Top](#table-of-contents)**

<a id="file-function"></a>

### 文件函数

|Function| Description|
|:--------:|:------|
|`file(path, [int flags = 0])`| 将整个文件 path 读入一个数组。可传入可选 flags 参数，例如 FILE_IGNORE_NEW_LINES 或 FILE_SKIP_EMPTY_LINES|
|`file_exists(path) `|返回文件或目录 path 是否存在|
|`file_get_contents(path) `|将整个文件 path 读入字符串|
|`file_put_contents(path, data)`| 将字符串 data 写入文件 path|
|`scandir(path) `|返回指定 path 内所有文件和目录的数组，包括 . 和 ..|
|`glob(pattern) `|返回匹配 pattern 的路径名数组|
|`basename(path)`|给定文件名 path，该函数会去除文件路径中的任何前导目录，仅返回文件名|

**[🔼Back to Top](#table-of-contents)**

<a id="read-file"></a>

## 读取文件

|Modes	|Description|pointer|
|:--------:|:------|:-------|
|`r`|	以只读方式打开文件。| 文件指针位于文件开头|
|`w`|	以只写方式打开文件。| 清空文件内容，如果文件不存在则创建新文件。文件指针位于文件开头|
|`a`|	以只写方式打开文件。| 保留文件中已有数据。文件指针位于文件末尾。如果文件不存在则创建新文件|
|`x`|	创建只写新文件。| 如果文件已存在则返回 FALSE 并报错|
|`r+`|	以读写方式打开文件。| 文件指针位于文件开头|
|`w+`|	以读写方式打开文件。| 清空文件内容，如果文件不存在则创建新文件。文件指针位于文件开头|
|`a+`|	以读写方式打开文件。| 保留文件中已有数据。文件指针位于文件末尾。如果文件不存在则创建新文件|
|`x+`|	创建读写新文件。| 如果文件已存在则返回 FALSE 并报错|

**[🔼Back to Top](#table-of-contents)**

<a id="cookies-and-session"></a>

## Cookie 与 Session

|keyword	|Description
|:--------:|:------|
|`setcookie(name, value)`|用于通过 HTTP 响应设置 cookie|
|`$_COOKIE`|获取 cookie 的值|
|`session_start()`|启动一个会话 |
|`$_SESSION`|会话变量通过 PHP 全局变量设置|
|`session_unset() and session_destroy()`|用于移除所有全局会话变量并销毁会话|

**[🔼Back to Top](#table-of-contents)**

<a id="most-important-function"></a>

## 最重要函数  

<a id="calender-function"></a>

### 日历函数

|Function|	Description|
|:--------:|:------|
|`cal_days_in_month()`|	返回指定年份和日历中一个月的天数|
|`cal_from_jd()`|	将儒略日计数转换为指定日历的日期|
|`cal_info()`|	返回有关指定日历的信息|
|`cal_to_jd()`|	将指定日历中的日期转换为儒略日计数|
|`easter_date()`|	返回指定年份复活节午夜的 Unix 时间戳|
|`easter_days()`|	返回指定年份中复活节距离 3 月 21 日的天数|
|`frenchtojd()`|	将法兰西共和历日期转换为儒略日计数|
|`gregoriantojd()`|	将公历日期转换为儒略日计数|
|`jddayofweek()`|	返回星期几|
|`jdmonthname()`|	返回月份名称|
|`jdtofrench()`|	将儒略日计数转换为法兰西共和历日期|
|`jdtogregorian()`|	将儒略日计数转换为公历日期|
|`jdtojewish()`|	将儒略日计数转换为犹太历日期|
|`jdtojulian()`|	将儒略日计数转换为儒略历日期|
|`jdtounix()`|	将儒略日计数转换为 Unix 时间戳|
|`jewishtojd()`|	将犹太历日期转换为儒略日计数|
|`juliantojd()`|	将儒略历日期转换为儒略日计数|
|`unixtojd()`|	将 Unix 时间戳转换为儒略日计数|

**[🔼Back to Top](#table-of-contents)**

<a id="datetime-function"></a>

### 日期/时间函数

|Function|	Description|
|:--------:|:------|
|`checkdate()	`|校验公历日期|
|`date_add()`|	向日期添加天、月、年、时、分、秒|
|`date_create_from_format()	`|返回一个按指定格式格式化的新 DateTime 对象|
|`date_create()`|返回一个新 DateTime 对象|
|`date_date_set()`|	设置新日期|
|`date_default_timezone_get()`|	返回所有日期/时间函数使用的默认时区|
|`date_default_timezone_set()`|	设置所有日期/时间函数使用的默认时区|
|`date_diff()`|	返回两个日期之间的差值|
|`date_format()	`|返回按指定格式格式化的日期|
|`date_get_last_errors()`|	返回在日期字符串中发现的警告/错误|
|`date_interval_create_from_date_string()`|	根据字符串的相对部分设置 DateInterval|
|`date_interval_format()`|	格式化时间间隔|
|`date_isodate_set()`|	设置 ISO 日期|
|`date_modify()`|	修改时间戳|
|`date_offset_get()`|	返回时区偏移量|
|`date_parse_from_format()`|	根据指定格式返回包含指定日期详细信息的关联数组|
|`date_parse()`|	返回包含指定日期详细信息的关联数组|
|`date_sub()`|	从日期中减去天、月、年、时、分、秒|
|`date_sun_info()`|	返回包含指定日期和地点的日落/日出及晨昏始末信息的数组|
|`date_sunrise()`|	返回指定日期和地点的日出时间|
|`date_sunset()	`|返回指定日期和地点的日落时间|
|`date_time_set()	`|设置时间|
|`date_timestamp_get()`|	返回 Unix 时间戳|
|`date_timestamp_set()`|	基于 Unix 时间戳设置日期和时间|
|`date_timezone_get()	`|返回给定 DateTime 对象的时区|
|`date_timezone_set()`|	设置 DateTime 对象的时区|
|`date()	`|格式化本地日期和时间|
|`getdate()	`|返回时间戳或当前本地日期/时间的日期/时间信息|
|`gettimeofday()`|	返回当前时间|
|`gmdate()`|	格式化 GMT/UTC 日期和时间|
|`gmmktime()`|	返回 GMT 日期的 Unix 时间戳|
|`gmstrftime()`|	根据区域设置格式化 GMT/UTC 日期和时间|
|`idate()	`|将本地时间/日期格式化为整数|
|`localtime()`|	返回本地时间|
|`microtime()`|	返回带微秒的当前 Unix 时间戳|
|`mktime()	`|返回日期的 Unix 时间戳|
|`strftime()`|	根据区域设置格式化本地时间和/或日期|
|`strptime()`|	解析由 strftime() 生成的时间/日期|
|`strtotime()`|	将英文文本日期时间解析为 Unix 时间戳|
|`time()`|	以 Unix 时间戳形式返回当前时间|
|`timezone_abbreviations_list()`|	返回包含 dst、偏移量和时区名称的关联数组|
|`timezone_identifiers_list()`|	返回包含所有时区标识符的索引数组|
|`timezone_location_get()`|	返回指定时区的位置信息|
|`timezone_name_from_ abbr()`|	根据缩写返回时区名称|
|`timezone_name_get()`|	返回时区的名称|
|`timezone_offset_get()`|	返回相对于 GMT 的时区偏移量|
|`timezone_open()`|	创建新的 DateTimeZone 对象|
|`timezone_transitions_get()`|	返回该时区的所有转换|
|`timezone_version_get()`|	返回 timezonedb 的版本|

**[🔼Back to Top](#table-of-contents)**

<a id="filter-function"></a>

### 过滤函数

|Function|	Description|
|:--------:|:------|
|`filter_has_var()`|	检查指定输入类型的变量是否存在|
|`filter_id()`|	返回指定过滤名称的过滤器 ID|
|`filter_input()`|	获取外部变量（例如来自表单输入）并可选择性地对其进行过滤|
|`filter_input_array()`|	获取外部变量（例如来自表单输入）并可选择性地对其进行过滤|
|`filter_list()`|	返回所有受支持过滤名称的列表|
|`filter_var()`|	使用指定过滤器过滤变量|
|`filter_var_array()`|	获取多个变量并对其进行过滤|

**[🔼Back to Top](#table-of-contents)**

<a id="mysqli--function"></a>

### MySQLi 函数

|Function|	Description|
|:--------:|:------|
|`affected_rows()`|	返回上一次 MySQL 操作受影响的行数|
|`autocommit()`|	开启或关闭数据库修改的自动提交|
|`begin_transaction()`|	开始一个事务|
|`change_user()`|	更改指定数据库连接使用的用户|
|`character_set_name()`|	返回数据库连接的默认字符集|
|`close()`|	关闭先前打开的数据库连接|
|`commit()`|	提交当前事务|
|`connect()`|	打开到 MySQL 服务器的新连接|
|`connect_errno()`|	返回上次连接错误的错误代码|
|`connect_error()`|	返回上次连接错误的错误描述|
|`data_seek()`| 将结果指针调整到结果集中的任意行|
|`debug()`|	执行调试操作|
|`dump_debug_info()`|	将调试信息转储到日志中|
|`errno()`|	返回最近一次函数调用的最后一个错误代码|
|`error()`|	返回最近一次函数调用的最后一个错误描述|
|`error_list()`|	返回最近一次函数调用的错误列表|
|`fetch_all()`|	以关联数组、数字数组或两者形式获取所有结果行|
|`fetch_array()`|	以关联数组、数字数组或两者形式获取结果行|
|`fetch_assoc()`|	以关联数组形式获取结果行|
|`fetch_field()`|	以对象形式返回结果集中的下一个字段|
|`fetch_field_direct()`|	以对象形式返回结果集中单个字段的元数据|
|`fetch_fields()`|	返回表示结果集中字段的对象数组|
|`fetch_lengths()`|	返回结果集中当前行的各列长度|
|`fetch_object()`|	以对象形式返回结果集的当前行|
|`fetch_row()`|	从结果集中获取一行并将其作为枚举数组返回|
|`field_count()`|	返回最近一次查询的列数|
|`field_seek()`|	将字段游标设置到给定的字段偏移量|
|`info()`|	返回有关最后执行查询的信息|
|`init()`|	初始化 MySQLi 并返回供 real_connect() 使用的资源|
|`insert_id()`|	返回上一次查询自动生成的 id|
|`kill()`|	请求服务器杀死一个 MySQL 线程|
|`more_results()`|	检查多查询是否还有更多结果|
|`multi_query()`|	对数据库执行一个或多个查询|
|`next_result()`|	为 multi_query() 准备下一个结果集|
|`options()`|	设置额外的连接选项并影响连接的行为|
|`ping()`|	Ping 服务器连接，或在连接已断开时尝试重新连接|
|`poll()`|	轮询连接|
|`prepare()`|	准备要执行的 SQL 语句|
|`query()`|	对数据库执行查询|
|`real_connect()`|	打开到 MySQL 服务器的新连接|
|`real_escape_string()`|	转义字符串中的特殊字符以用于 SQL 语句|
|`real_query()`|	执行单个 SQL 查询|
|`reap_async_query()`|	返回异步 SQL 查询的结果|
|`refresh()`|	刷新/清空表或缓存，或重置复制服务器信息|
|`rollback()`|	回滚数据库的当前事务|
|`select_db()`|	选择用于数据库查询的默认数据库|
|`set_charset()`|	设置默认客户端字符集|
|`set_local_infile_default()`|	取消为 load local infile 命令设置的用户自定义处理程序|
|`set_local_infile_handler()`|	为 LOAD DATA LOCAL INFILE 命令设置回调函数|
|`sqlstate()`|	返回该错误的 SQLSTATE 错误代码|
|`ssl_set()`|	用于使用 SSL 建立安全连接|
|`stat()`|	返回当前系统状态|
|`stmt_init()`|	初始化语句并返回供 stmt_prepare() 使用的对象|
|`store_result()`|	传输上一次查询的结果集|
|`thread_id()`|	返回当前连接的线程 ID|
|`thread_safe()`|	返回客户端库是否编译为线程安全|
|`use_result()`|	开始检索上一次执行查询的结果集|
|`warning_count()`|	返回连接中上一次查询产生的警告数量 |

**[🔼Back to Top](#table-of-contents)**

<a id="php-regular-expression-functions"></a>

### PHP 正则表达式函数

|Function|	Description|
|:--------:|:------|
|`preg_filter()`|	返回替换了模式匹配项的字符串或数组，但仅当找到匹配项时|
|`preg_grep()`|	返回仅由输入数组中匹配该模式的元素组成的数组|
|`preg_last_error()`|	返回指示最近一次正则表达式调用失败原因的错误代码|
|`preg_match()`|	查找字符串中模式的第一个匹配项|
|`preg_match_all()`|	查找字符串中模式的所有匹配项|
|`preg_replace()`|	返回在给定字符串中将模式的匹配项（或模式数组）替换为子串（或子串数组）后的字符串|
|`preg_replace_callback()`|	给定表达式和回调函数，返回将表达式中所有匹配项替换为回调函数返回的子串后的字符串|
|`preg_replace_callback_array()`|	给定关联表达式与回调函数的数组，返回将每个表达式的所有匹配项替换为回调函数返回的子串后的字符串|
|`preg_split()`|	使用正则表达式的匹配项作为分隔符，将字符串拆分为数组|
|`preg_quote()`|	通过在具有特殊含义的字符前加反斜杠来转义它们|

**[🔼Back to Top](#table-of-contents)**
