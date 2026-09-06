---
title: SQL 速查表
description: 这里列出了最常用的 SQL 查询。
created: 2022-10-22
---

<a id="table-of-contents"></a>

## 目录

- [SQL 开发者速查表](#sql-cheatsheet-for-developers)
- [简介——什么是 SQL？](#introduction-what-is-sql)
- [SQL 特性？](#sql-features)
- [基础 SQL](#basic-sql)
  - [创建数据库与删除数据库](#create-database-and-drop-database)
  - [字符串数据类型](#string-datatype)
  - [数值数据类型：](#numeric-datatype)
  - [日期/时间数据类型：](#datetime-datatype)
- [表](#tables)
  - [修改表](#alter-table)
  - [插入表](#insert-table)
  - [更新表](#update-table)
  - [删除表](#delete-table)
- [重要 SQL 关键字](#important-sql-keywords)
- [SQL 子句](#clauses-in-sql)
- [SQL 运算符](#sql-operators)
  - [算术运算符](#arithmetic-operators)
  - [位运算符](#bitwise-operators)
  - [关系运算符](#relational-operators)
  - [复合运算符](#compound-operators)
  - [逻辑运算符](#logical-operators)
- [SQL 中的函数](#function-in-sql)
  - [SQL Server 数值函数](#sql-server-numeric-functions)
  - [SQL Server 日期函数](#sql-server-date-functions)
  - [SQL Server 高级函数](#sql-server-advanced-functions)
- [SQL 中的连接](#joins-in-sql)

<a id="sql-cheatsheet-for-developers"></a>

# SQL 开发者速查表

<a id="introduction-what-is-sql"></a>

# 简介——什么是 SQL？

> 要了解 **SQL**，我们首先需要知道数据库和 **数据库管理系统（DBMS）**。数据基本上是与某个对象相关的事实的集合。**数据库**是以系统化方式排列的小数据单元的集合。**关系型数据库管理系统**是一组工具的集合，它允许用户在遵循某些标准规则（这些规则便于数据库与用户端之间快速响应）的同时，**操作、组织和可视化**数据库的内容。

> 在了解了数据、数据库和 **DBMS/RDBMS** 的概念之后，我们终于可以学习 SQL 了。SQL 即 **结构化查询语言**，基本上就是我们（用户）用来与数据库通信并从中获取所需数据解释的编程语言。它用于**存储、操作和检索**数据库中的数据。

**[🔼Back to Top](#table-of-contents)**

<a id="sql-features"></a>

# SQL 特性？

> 使用 SQL 可以对数据库执行以下功能：

1. `Create a Database` 或 `Delete a Database`
2. 从 ___Database___ 中 `Create a table`、`Alter a table` 或 `Delete a table`
3. `SELECT data from tables`
4. `INSERT data into tables`
5. `UPDATE data in tables`
6. `DELETE data from tables`
7. `Create Views in the database`
8. `Execute various aggregate functions`

**[🔼Back to Top](#table-of-contents)**

<a id="basic-sql"></a>

# 基础 SQL

<a id="create-database-and-drop-database"></a>

## 创建数据库与删除数据库

| COMMAND  | SYNTAX | DESCRIPTION |
| ------------- | ------------- |--------|
| CREATE DATABASE| CREATE DATABASE database-name  | 用于在服务器上创建新的 SQL 数据库        |
| DROP DATABASE  | CREATE DATABASE database-name  | 用于删除已存在的数据库   |

**[🔼Back to Top](#table-of-contents)**

<a id="string-datatype"></a>

## 字符串数据类型

> 下表列出了 SQL 中可用的所有字符串数据类型及其描述：

|Datatype |	Description|
|---------|---------------|
| CHAR(size) |	包含数字、字母或特殊字符的固定长度字符串。长度范围从 0 到 255。|
| VARCHAR(size)	|可变长度字符串，长度范围从 0 到 65535。类似于 CHAR。|
| TEXT(size)|	可包含最大 65536 字节的字符串。 |
| TINY TEXT	|可包含最多 255 个字符的字符串。|
| MEDIUM TEXT |	可包含最多 16777215 个字符的字符串。|
| LONG TEXT|	可包含最多 4294967295 个字符的字符串。|
| BINARY(size)|	类似于 CHAR()，但存储二进制字节字符串。|
| VARBINARY(size)|	类似于 VARCHAR()，但存储二进制字节字符串。|
| BLOB(size)|	保存最大 65536 字节的二进制大对象。|
| TINYBLOB|	用于二进制大对象，最大大小为 255 字节。|
| MEDIUMBLOB|	保存最大 16777215 字节的二进制大对象。|
| LONGBLOB	| 保存最大 4294967295 字节的二进制大对象。|
| ENUM(val1,val2) |	字符串对象，只能从最多 65536 个值的 ENUM 列表中取 1 个可能值。如果未插入值，则插入空值。|
| SET(val1,val2,…)	|具有 0 个或多个值的字符串对象，从可能值列表中选择，最大值限制为 64 个值。|

**[🔼Back to Top](#table-of-contents)**

<a id="numeric-datatype"></a>

## 数值数据类型：

> 下表列出了 SQL 中所有的数值数据类型及其描述：

|Datatype	|Description|
|-------|-------------|
| BIT(size) |	位值类型，size 范围为 1 到 64。默认值：1|
| INT(size)	|整数，有符号范围为 -2147483648 到 2147483647，无符号范围为 0 到 4294967295。|
| TINYINT(size)	|整数，有符号范围为 -128 到 127，无符号范围为 0 到 255。|
| SMALLINT(size)|	整数，有符号范围为 -32768 到 32767，无符号范围为 0 到 65535。|
| MEDIUMINT(size)	|整数，有符号范围为 -8388608 到 8388607，无符号范围为 0 到 16777215。|
| BIGINT(size) |	整数，有符号范围为 9223372036854775808 到 9223372036854775807，无符号范围为 0 到 18446744073709551615。|
| BOOLEAN	|布尔值，其中 0 视为 FALSE，非 0 值视为 TRUE。|
| FLOAT (p)	|存储浮点数。如果精度参数设置在 0 到 24 之间，类型则为 FLOAT()，如果介于 25 到 53 之间，数据类型则为 DOUBLE()。|
| DECIMAL(size,d) |	十进制数，小数点前的位数由 size 参数设置，小数点后的位数由 d 参数设置。默认值：size = 10，d = 10。最大值：size = 65，d = 30。|

**[🔼Back to Top](#table-of-contents)**

<a id="datetime-datatype"></a>

## 日期/时间数据类型：

> SQL 中用于有效处理日期/时间操作的数据类型称为日期/时间数据类型。<br /> 下表列出了 SQL 中所有的日期/时间变量及其描述：

|Datatype|	Description|
|-------|---------|
| DATE	|以 YYYY-MM-DD 格式存储日期，日期范围为 ‘1000-01-01’ 到 ‘9999-12-31’。|
| TIME(fsp)	|以 hh:mm:ss 格式存储时间，时间范围为 ‘-838:59:59’ 到 ‘838:59:59’。|
| DATETIME(fsp)	|以 YYYY-MM-DD 和 hh:mm:ss 格式存储日期和时间的组合，值范围为 ‘1000-01-01 00:00:00’ 到 ‘9999-12-31 23:59:59’。|
| TIMESTAMP(fsp)	|存储相对于 Unix 纪元的值，即 Unix 时间戳。值范围为 ‘1970-01-01 00:00:01’ UTC 到 ‘2038-01-09 03:14:07’ UTC。|
| YEAR	|以 4 位数字格式存储年份值，范围为 -1901 到 2155。|

**[🔼Back to Top](#table-of-contents)**

<a id="tables"></a>

# 表

| COMMAND  | SYNTAX | DESCRIPTION |
| ------------- | ------------- |--------|
| CREATE TABLE| CREATE TABLE table_name (column1 datatype,column2 datatype,column3 datatype)  | 用于创建新表        |
| DROP DATABASE  | CREATE DATABASE database-name  | 用于删除已存在的数据库   |
|TRUNCATE TABLE|TRUNCATE TABLE table_name|用于删除表内的数据，而不删除表本身。|

**[🔼Back to Top](#table-of-contents)**

<a id="alter-table"></a>

## 修改表

| COMMAND  | SYNTAX | DESCRIPTION |
| ------------- | ------------- |--------|
| ALTER TABLE ADD| ALTER TABLE table_name ADD column_name datatype  | 用于向已有表中添加列        |
| ALTER TABLE DROP  | ALTER TABLE table_name DROP COLUMN column_name  | 用于从已有表中删除列   |
| ALTER TABLE MODIFY|ALTER TABLE table_name MODIFY COLUMN column_name datatype |用于修改已有表中的列 |

**[🔼Back to Top](#table-of-contents)**

<a id="insert-table"></a>

## 插入表

| COMMAND  | SYNTAX | DESCRIPTION |
| ------------- | ------------- |--------|
| INSERT INTO| INSERT INTO table_name (column1, column2, column3, ...) VALUES (value1, value2, value3, ...); | 用于为特定列插入数据，以向已有表中添加新记录        |
| INSERT INTO  |INSERT INTO table_name VALUES (value1, value2, value3, ...);  | 用于向已有表中插入包含所有列的新记录  |

**[🔼Back to Top](#table-of-contents)**


<a id="update-table"></a>

## 更新表

| COMMAND  | SYNTAX | DESCRIPTION |
| ------------- | ------------- |--------|
| UPDATE| UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition;  | 用于为已有表中现有记录的特定行更新数据        |
| UPDATE| UPDATE table_name SET column1 = value1, column2 = value2, ... ;| 用于为已有表中存在的所有行更新数据        |

**[🔼Back to Top](#table-of-contents)**


<a id="delete-table"></a>

## 删除表 

| COMMAND  | SYNTAX | DESCRIPTION |
| ------------- | ------------- |--------|
| DELETE|DELETE FROM table_name WHERE condition;  | 用于为已有表中现有记录的特定行删除数据        |
| DELETE| DELETE FROM table_name;| 用于为已有表中存在的所有行删除数据        |

**[🔼Back to Top](#table-of-contents)**


<a id="important-sql-keywords"></a>

# 重要 SQL 关键字

|Keyword |	Description |	Example|
|----------|---------|------------|
|ADD |	向已有表中添加新列。|	ALTER TABLE student ADD email_address VARCHAR(255)|
|ALTER TABLE |	添加、编辑或删除表中的列|	ALTER TABLE student DROP COLUMN email_address|
|ALTER COLUMN|	可以更改表列的数据类型|	ALTER TABLE student ALTER COLUMN phone VARCHAR(15)|
|AS	|使用仅在查询期间存在的别名重命名表/列。|	SELECT name AS student_name, phone FROM student|
|ASC |与 ORDER BY 配合使用，按升序对数据进行排序。|	SELECT column1, column2, … FROM table_name ORDER BY column1, column2, … ASC|
|DESC |	与 ORDER BY 配合使用，按降序对数据进行排序。|	SELECT column1, column2, … FROM table_name ORDER BY column1, column2, … DESC|
|CHECK	|限制可添加到列中的值。|	CREATE TABLE student(fullName varchar(255), age INT, CHECK(age >= 18))|
|CREATE DATABASE|	创建新数据库。	|CREATE DATABASE student;|
|DEFAULT|	为给定列设置默认值。|	CREATE TABLE products(ID int, name varchar(255) DEFAULT ‘Username’, from date DEFAULT GETDATE())|
|DELETE	|从表中删除值。	|DELETE FROM users WHERE user_id= 674|
|DROP COLUMN|	从表中删除/移除列。|	ALTER TABLE student DROP COLUMN name|
|DROP DATABASE|	彻底删除数据库及其所有内容。|	DROP DATABASE student|
|DROP DEFAULT|	移除列的默认值。	|ALTER TABLE student ALTER COLUMN age DROP DEFAULT|
|DROP TABLE|	从数据库中删除表。|	DROP TABLE students|
|FROM|	确定从哪个表读取或删除数据。|	SELECT * FROM students|
|IN	|与 WHERE 子句配合使用，用于多个 OR 条件。|	SELECT * FROM students WHERE name IN(‘Scaler’, ‘Interviewbit’,‘Academy’)|
|ORDER BY|	用于按升序或降序对给定数据进行排序。|	SELECT * FROM student ORDER BY age ASC|
|SELECT DISTINCT|	作用与 SELECT 相同，只是结果中只包含唯一值。|	SELECT DISTINCT age from student|
|TOP|	与 SELECT 配合使用，从表中选择固定数量的记录。|SELECT TOP 5 * FROM students|
|VALUES|	与 INSERT INTO 关键字一起使用，向表中添加新值。|INSERT INTO Customers (CustomerName, City, Country) VALUES (‘Cardinal’, ‘Stavanger’, ‘Norway’)|
|WHERE|	根据某些给定条件筛选数据。|	SELECT * FROM students WHERE age >= 18|
|UNIQUE|	确保列中的所有值都不同。|	UNIQUE (ID)|
|UNION|	用于合并两个或多个 SELECT 语句的结果集。|	SELECT column_name(s) FROM Table1 UNION SELECT column_name(s) FROM Table2|
|UNION ALL|	合并两个或多个 SELECT 语句的结果集（允许重复值）|	SELECT City FROM table1 UNION ALL SELECT City FROM table2 ORDER BY City;|
|SELECT TOP|	用于指定要返回的记录数量。|	SELECT TOP 3 * FROM Students|
|LIMIT|	限制查询返回的行数。|	SELECT * FROM table1 LIMIT 3|
|UPDATE|	修改表中的现有记录。|	UPDATE Customers SET ContactName = ‘Scaler’, City = ‘India’ WHERE CustomerID = 1;|
|SET|	与 UPDATE 配合使用，指定表中应更新哪些列和值。|	UPDATE Customers SET ContactName = ‘Scaler’, City= ‘India’ WHERE |CustomerID = 1|
|IS NULL|	使用此运算符测试列值是否为 NULL。|	SELECT CustomerName, ContactName, Address FROM Customers WHERE Address IS NULL|
|LIKE	|用于在列中搜索指定模式。|	SELECT * FROM Students WHERE Name LIKE ‘a%’|
|ROWNUM|	返回一个数字，指示 Oracle 从表或连接行集合中选取行的顺序。|	SELECT * FROM Employees WHERE ROWNUM < 10;|
|GROUP BY|	将具有相同值的行分组为汇总行。|	SELECT COUNT(StudentID), State FROM Students GROUP BY State|
|HAVING	|使用户能够指定过滤哪些分组结果出现在结果中的条件。|	HAVING COUNT(CustomerID) > 5|

**[🔼Back to Top](#table-of-contents)**



<a id="clauses-in-sql"></a>

# SQL 子句


|Name|	Description|	Example|
|-------|-------|-------|
|WHERE|	用于根据某些条件从数据库中选择数据。|	SELECT * from Employee WHERE age >= 18;|
|AND |	用于组合 2 个或多个条件，仅当所有条件都为 True 时返回 true。|	SELECT * from Employee WHERE age >= 18 AND salary >= 45000 ;|
|OR |	类似于 AND，但只要有任一条件为 True 就返回 true。|	Select * from Employee where salary >= 45000 OR age >= 18|
|LIKE |	用于在列中搜索指定模式。|	SELECT * FROM Students WHERE Name LIKE ‘a%’;|
|LIMIT|	限制查询返回的行数。|	SELECT * FROM table1 LIMIT 3;|
|ORDER BY|	用于按升序或降序对给定数据进行排序。|	SELECT * FROM student ORDER BY age ASC|
|GROUP BY|	将具有相同值的行分组为汇总行。|	SELECT COUNT(StudentID), State FROM Students GROUP BY State;|
|HAVING	|作用与 WHERE 子句相同，但也可与聚合函数一起使用。|	SELECT COUNT(ID), AGE FROM Students GROUP BY AGE HAVING COUNT(ID) > 5;|

**[🔼Back to Top](#table-of-contents)**

<a id="sql-operators"></a>

 # SQL 运算符
 
 SQL 中有 3 种主要类型的运算符：算术、比较和逻辑运算符，下面将分别介绍。
 
<a id="arithmetic-operators"></a>

## 算术运算符

算术运算符允许用户在 SQL 中执行算术运算。下表显示了 SQL 中可用的算术运算符列表：

|Operator|	Description|
|-----|-------|
|+|	加法|
|-|	减法| 
|* |	乘法|
| / |	除法|
| % |	取模|

**[🔼Back to Top](#table-of-contents)**

<a id="bitwise-operators"></a>

## 位运算符

位运算符用于在 SQL 中执行位操作。下表显示了 SQL 中可用的位运算符列表：

|Operator|	Description|
|---------|----------|
|&|	按位与 |
| ![image](https://user-images.githubusercontent.com/47249568/197326193-77622f96-20cd-4f8f-b4b6-997fb54b2d69.png)|	按位或|
|^|	按位异或|

**[🔼Back to Top](#table-of-contents)**

<a id="relational-operators"></a>

## 关系运算符

关系运算符用于在 SQL 中执行关系表达式，即那些值为真或假的表达式。下表显示了 SQL 中可用的关系运算符列表：

|Operator|	Description|
|---------|---------|
|=|	等于|
|>|	大于|
|<|	小于|
|>=|	大于等于|
|<=|	小于等于|
|<>|	不等于|

**[🔼Back to Top](#table-of-contents)**

<a id="compound-operators"></a>

## 复合运算符

复合运算符基本上是 2 个或多个算术或关系运算符的组合，可在编写代码时作为简写使用。下表显示了 SQL 中可用的复合运算符列表：

|Operator|	Description|
|------|---------|
|+=|	加等于|
|-=|	减等于|
|*=|	乘等于|
|/=|	除等于|
|%=|	取模等于|
|&=|	与等于|
| ![image](https://user-images.githubusercontent.com/47249568/197326390-7087561c-34d3-450e-aacb-0282cfd17922.png)= |	或等于|
|^=|	异或等于|

**[🔼Back to Top](#table-of-contents)**

<a id="logical-operators"></a>

## 逻辑运算符

逻辑运算符用于将 2 个或多个关系语句组合成 1 个复合语句，其真值作为一个整体进行求值。下表显示了带有描述的 SQL 逻辑运算符：

|Operator|	Description|
|---------|-----------|
|ALL|	如果所有子查询都满足给定条件，则返回 True。|
|AND|	如果所有条件都为真，则返回 True|
|ANY|	如果有任一子查询满足给定条件，则返回 True|
|BETWEEN|	如果操作数位于条件范围内，则返回 True|
|EXISTS	|如果子查询返回一条或多条记录，则返回 True|
|IN|	如果操作数等于给定表达式列表中的至少一个操作数，则返回 True|
|LIKE|	如果操作数与某个给定模式匹配，则返回 True。|
|NOT|	如果给定条件集合为假，则显示某些记录|
|OR|	如果有任一条件为真，则返回 True|
|SOME|	如果有任一子查询满足给定条件，则返回 True。|

**[🔼Back to Top](#table-of-contents)**

<a id="function-in-sql"></a>

# SQL 中的函数

<a id="sql-server-numeric-functions"></a>

## SQL Server 数值函数

下表列出了 SQL 中一些数值函数及其描述：

|Name|	Description|
|------|-------|
|ABS|	返回数字的绝对值。|
|ASIN|	返回数字的反正弦值。|
|AVG|	返回表达式的平均值。|
|COUNT|	统计 SELECT 查询返回的记录数。|
|EXP|	返回 e 的指定次幂。|
|FLOOR|	返回小于等于该数字的最大整数。|
|RAND|	返回随机数。|
|SIGN|	返回数字的符号。|
|SQRT|	返回数字的平方根。|
|SUM|	返回一组值的总和。|

**[🔼Back to Top](#table-of-contents)**

<a id="sql-server-date-functions"></a>

## SQL Server 日期函数

下表列出了 SQL 中一些日期函数及其描述：

|Name|	Description|
|----|------|
|CURRENT_TIMESTAMP|	返回当前日期和时间。|
|DATEADD|	向日期添加日期/时间间隔并返回新日期。|
|DATENAME|	返回日期的指定部分（以字符串形式）。|
|DATEPART|	返回日期的指定部分（以整数形式）。|
|DAY|	返回指定日期的月份中的第几天。|
|GETDATE|	从数据库返回当前日期和时间。|

**[🔼Back to Top](#table-of-contents)**

<a id="sql-server-advanced-functions"></a>

## SQL Server 高级函数

下表列出了 SQL 中一些高级函数及其描述：

|Name|	Description|
|------|---------|
|CAST|	将值类型转换为指定的数据类型。|
|CONVERT|	将值转换为指定的数据类型。|
|IIF|	如果条件求值为 True 则返回一个值，否则返回另一个值。|
|ISNULL|	如果表达式为 NULL 则返回指定值，否则返回表达式。|
|ISNUMERIC|	检查表达式是否为数值。|
|SYSTEM_USER|	返回当前用户的登录名|
|USER_NAME|	根据指定的 id 返回数据库用户名。|

**[🔼Back to Top](#table-of-contents)**

<a id="joins-in-sql"></a>

# SQL 中的连接

| COMMAND  | SYNTAX | DESCRIPTION |
| ------------- | ------------- |--------|
| INNER JOIN| SELECT column_name(s) FROM table1 INNER JOIN table2 ON table1.column_name = table2.column_name;| 选择在两个表中具有匹配值的记录。       |
| LEFT JOIN| SELECT column_name(s) FROM table1 LEFT JOIN table2 ON table1.column_name = table2.column_name;| 返回左表（table1）的所有记录，以及右表（table2）的匹配记录。如果没有匹配，右侧结果为 0 条记录。|
|RIGHT JOIN|SELECT column_name(s) FROM table1 RIGHT JOIN table2 ON table1.column_name = table2.column_name;|返回右表（table2）的所有记录，以及左表（table1）的匹配记录。如果没有匹配，左侧结果为 0 条记录。|
|FULL JOIN|SELECT column_name(s) FROM table1 FULL OUTER JOIN table2 ON table1.column_name = table2.column_name WHERE condition;|当左表（table1）或右表（table2）记录中存在匹配时，返回所有记录。|
|SELF JOIN |SELECT column_name(s) FROM table1 T1, table1 T2 WHERE condition;|自连接是一种常规连接，但表是与自身连接的。|

**[🔼Back to Top](#table-of-contents)**
