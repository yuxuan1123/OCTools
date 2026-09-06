---
title: MongoDB 速查表
description: 这里给出最常用的 MongoDB 命令。
created: 2022-10-27
---

<a id="table-of-contents"></a>
## Table of Contents

- [MongoDB 开发者速查表](#mongo-db-cheatsheet-for-developers)
  - [数据库命令](#database-commands)
  - [集合命令](#collection-commands)
  - [行（文档）命令](#rowdocument-commands)
  - [MongoDB 查询运算符](#mongodb-query-operators)
    - [比较运算符](#comparison-operators)
    - [逻辑运算符](#logical-operators)
    - [评估运算符](#evaluation-operators)
  - [MongoDB 更新运算符](#mongodb-update-operators)
    - [字段](#fields)
    - [数组](#array)
  - [MongoDB - 聚合](#mongodb---aggregation)

<a id="mongo-db-cheatsheet-for-developers"></a>
# Mongo-DB CheatSheet for Developers

<a id="database-commands"></a>
## Database Commands

|       命令       | 说明                                    |
| :-----------------: | :--------------------------------------------- |
|    `createUser`     | 创建一个新用户。                            |
|     `show dbs`      | 查看所有数据库                             |
|    `use dbName`     | 创建新数据库或切换数据库               |
|        `db`         | 查看当前数据库                          |
| `db.dropDatabase()` | 删除数据库                                |
|     `usersInfo`     | 返回指定用户的信息。 |

**[🔼Back to Top](#table-of-contents)**

<a id="collection-commands"></a>
## Collection Commands

|                命令                  | 说明                                 |
| :--------------------------------------: | :------------------------------------------ |
| `db.createCollection('collection_name')` | 创建一个名为 'collection_name' 的集合 |
|       `db.collection_name.drop()`        | 删除名为 'collection_name' 的集合   |

**[🔼Back to Top](#table-of-contents)**

<a id="rowdocument-commands"></a>
## Row(Document) Commands

|                                                                                            命令                                                                                             | 说明                                |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :----------------------------------------- |
|                                                                                   `db.collection_name.find()`                                                                                   | 显示集合中的所有行              |
|                                                                              `db.collection_name.find().pretty()`                                                                               | 显示集合中的所有行（格式化） |
|                                                                         `db.collection_name.findOne({name: 'ritwik'})`                                                                          | 查找匹配该对象的第一个行     |
|                                                        `db.collection_name.insert({'name': 'Ritwik','lang': 'sql','member_since': 5 })`                                                         | 插入一行                             |
| `db.collection_name.insertMany([{'name': 'Ritwik','lang': 'sql','member_since': 5}, {'name': 'Rohan','lang': 'Python','member_since': 3},{'name': 'Lovish','lang': 'Java','member_since': 4}])` | 插入多行                           |
|                                                                           `db.collection_name.find({lang:'Python'})`                                                                            | 在 MongoDB 数据库中搜索               |
|                                                                              `db.collection_name.find().limit(2)`                                                                               | 限制输出中的行数         |
|                                                                               `db.collection_name.find().count()`                                                                               | 统计输出中的行数     |
|                               `db.collection_name.updateOne({name: 'Shubham'},{$set: {'name': 'Harry','lang': 'JavaScript','member_since': 51}},{upsert: true})`                                | 更新一行                               |
|                                                              `db.collection_name.update({name: 'Rohan'},{$inc:{member_since: 2}})`                                                              | MongoDB 自增运算符                 |
|                                                         `db.collection_name.update({name: 'Rohan'},{$rename:{member_since: 'member'}})`                                                         | MongoDB 重命名运算符                    |
|                                                                          `db.collection_name.remove({name: 'Harry'})`                                                                           | 删除行                                 |
|                                                                         `db.collection_name.deleteOne({name: 'Harry'})`                                                                         | 删除一行                             |
|                                                                      `db.collection_name.deleteMany({lang: 'JavaScript'})`                                                                      | 删除多行                            |

**[🔼Back to Top](#table-of-contents)**

<a id="mongodb-query-operators"></a>
## MongoDB Query Operators

> 有许多查询运算符可用于比较和引用文档字段。

<a id="comparison-operators"></a>
### Comparison Operators

> 以下运算符可用于查询中以比较值：

| 命令 | 说明                                     |
| :-----: | :---------------------------------------------- |
|  `$eq`  | 值相等                                |
|  `$ne`  | 值不相等                            |
|  `$gt`  | 值大于另一个值             |
| `$gte`  | 值大于或等于另一个值 |
|  `$lt`  | 值小于另一个值             |
| `$lte`  | 值小于或等于另一个值    |
|  `$in`  | 值在数组中匹配                |

**[🔼Back to Top](#table-of-contents)**

<a id="logical-operators"></a>
### Logical Operators

> 以下运算符可以逻辑地比较多个查询。

| 命令 | 说明                                        |
| :-----: | :------------------------------------------------- |
| `$and`  | 返回两个查询都匹配的文档         |
|  `$or`  | 返回任一查询匹配的文档       |
| `$nor`  | 返回两个查询都不匹配的文档 |
| `$not`  | 返回查询不匹配的文档   |

**[🔼Back to Top](#table-of-contents)**

<a id="evaluation-operators"></a>
### Evaluation Operators

> 以下运算符用于辅助评估文档。

| 命令  | 说明                                                        |
| :------: | :----------------------------------------------------------------- |
| `$regex` | 在评估字段值时允许使用正则表达式 |
| `$text`  | 执行文本搜索                                             |
| `$where` | 使用 JavaScript 表达式匹配文档                    |

**[🔼Back to Top](#table-of-contents)**

<a id="mongodb-update-operators"></a>
## MongoDB Update Operators

> 在文档更新期间可以使用许多更新运算符。

<a id="fields"></a>
### Fields

> 以下运算符可用于更新字段：

|    命令     | 说明                              |
| :------------: | :--------------------------------------- |
| `$currentDate` | 将字段值设置为当前日期 |
|     `$inc`     | 递增字段值               |
|   `$rename`    | 重命名字段                        |
|     `$set`     | 设置字段的值                |
|    `$unset`    | 从文档中移除该字段      |

**[🔼Back to Top](#table-of-contents)**

<a id="array"></a>
### Array

> 以下运算符用于辅助更新数组。

|  命令   | 说明                                             |
| :---------: | :------------------------------------------------------ |
| `$addToSet` | 向数组添加不重复的元素                      |
|   `$pop`    | 移除数组的第一个或最后一个元素           |
|   `$pull`   | 移除数组中所有匹配查询的元素 |
|   `$push`   | 向数组添加一个元素                             |

**[🔼Back to Top](#table-of-contents)**

<a id="mongodb---aggregation"></a>
## MongoDB - Aggregation

| 表达式  | 说明                                                                                                                                                       |
| :---------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|   `$sum`    | 对集合中来自所有文档的指定值求和。                                                                                                   |
|   `$avg`    | 计算集合中所有给定值的平均值。                                                                                                  |
|   `$min`    | 获取集合中所有文档对应值的最小值。                                                                                                |
|   `$max`    | 获取集合中所有文档对应值的最大值。                                                                                                |
|   `$push`   | 将值插入结果文档的数组中。                                                                                                          |
| `$addToSet` | 将值插入结果文档的数组中，但不创建重复项。                                                                           |
|  `$first`   | 根据分组从源文档中获取第一个文档。通常这仅在配合某些已应用的“$sort”阶段时才有意义。 |
|   `$last`   | 根据分组从源文档中获取最后一个文档。通常这仅在配合某些已应用的“$sort”阶段时才有意义。  |

**[🔼Back to Top](#table-of-contents)**
