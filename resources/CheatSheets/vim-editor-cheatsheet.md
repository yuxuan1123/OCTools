---
title: Vim 编辑器 速查表
description: 这里列出了最常用的 vim 编辑器快捷键。
created: 2022-10-23
---

<a id="table-of-contents"></a>
## 目录

- [面向开发者的 VIM-Editor 速查表](#vim-editor-cheatsheet-for-developers)
  - [简介](#introduction)
  - [如何在 vim 中打开文件](#how-to-open-a-file-in-vim)
  - [按字符、单词和标记移动](#moving-by-characters-words-and-tokens)
  - [按行移动](#moving-by-lines)
  - [按屏幕移动](#moving-by-screens)
  - [插入文本](#inserting-text)
  - [编辑文本](#editing-text)
  - [剪切、复制与粘贴](#cutting-copying-and-pasting)
  - [标记文本（可视模式）](#marking-text-visual-mode)
  - [可视命令](#visual-commands)
  - [在文件中搜索](#search-in-file)
  - [保存与退出文件](#saving-and-exiting-file)
  - [启用 Vim 配色方案](#enabling-vim-color-schemes)

<a id="vim-editor-cheatsheet-for-developers"></a>
# 面向开发者的 VIM-Editor 速查表

<a id="introduction"></a>
## 简介

> Vim 是一款被广泛使用的开源 Unix 文本编辑器。学习使用 Vim 命令需要多加练习和积累经验。因此，在掌握它们的过程中，准备一份便捷的参考表会很有帮助。

**[🔼Back to Top](#table-of-contents)**

<a id="how-to-open-a-file-in-vim"></a>
## 如何在 vim 中打开文件

| Commands           | Descriptions              | Examples                                                         |
| -------------------| --------------------------| ---------------------------------------------------------------- |
| `$ vim <file path>`| 在 Vim 编辑器中打开文件 | - `$ vim './myRepo/README.md'` <br/> or <br/> - `vim README.md` |

**[🔼Back to Top](#table-of-contents)**

<a id="moving-by-characters-words-and-tokens"></a>
## 按字符、单词和标记移动

> 按单个字符移动光标的基本按键如下：

|Commands         |Description                   |
|-----------------|------------------------------|
|`h`              |将光标向左移动          |
|`j`              |将光标向下移动          |
|`k`              |将光标向上移动         |
|`l`              |将光标向右移动         |

> 你也可以将这些按键与数字前缀配合使用，以在指定方向上多次移动。例如，运行 5j 会将光标向下移动 5 行。

|Commands         |Description                          |
|-----------------|-------------------------------------|
|`b`              | 移动到单词开头         |
|`B`              | 移动到标记开头        |  
|`w`              | 移动到下一个单词开头  |
|`W`              | 移动到下一个标记开头 |
|`e`              | 移动到单词结尾           |
|`E`              | 移动到标记结尾          |

**[🔼Back to Top](#table-of-contents)**

<a id="moving-by-lines"></a>
## 按行移动

|Commands             |Description                                                      |
|---------------------|-----------------------------------------------------------------|
|`0` (zero)           | 跳到行首                               |
|`$`                  | 跳到行尾                                     |
|`^`                  | 跳到行的第一个（非空白）字符             |
|`#G` / `#gg` / `:#`  | 移动到指定行号（将 # 替换为行号）|

**[🔼Back to Top](#table-of-contents)**

<a id="moving-by-screens"></a>
## 按屏幕移动

|Commands         |Description                                             |
|-----------------|--------------------------------------------------------|
|`Ctrl + b`       | 向后移动一整屏                              |
|`Ctrl + f`       |向前移动一整屏                            |
|`Ctrl + d`       | 向前移动半屏                              |
|`Ctrl + u`       | 向后移动半屏                                 |
|`Ctrl + e`       | 屏幕向下移动一行（不移动光标）  |
|`Ctrl + y`       | 屏幕向上移动一行（不移动光标）    |
|`Ctrl + o`       | 在跳转历史中向后移动                 |
|`Ctrl + i`       | 在跳转历史中向前移动                  |

<br/>

|Commands         |Description                                             |
|-----------------|--------------------------------------------------------|
|`H`              | 移动到屏幕顶部（H=high）                 |
|`M`              | 移动到屏幕中间（M=middle）            |
|`L`              | 移动到屏幕底部（L=low）               |

**[🔼Back to Top](#table-of-contents)**

<a id="inserting-text"></a>
## 插入文本

|Commands         |Description                                             |
|-----------------|--------------------------------------------------------|
|`i`              |光标前切换到插入模式                 |
|`I`              |在行首插入文本                |
|`a`              |光标后切换到插入模式                  |
|`A`              |在行尾插入文本                      |
|`o`              |在当前行下方新建一行                   |
|`O`              |在当前行上方新建一行                   |
|`ea`             |在单词结尾处插入文本                      |
|`Esc`            |退出插入模式；切换到命令模式                |

> 其中一些命令会在命令模式和插入模式之间切换。默认情况下，Vim 以命令模式启动，允许你在文件中移动并编辑文件。要切换到命令模式，请使用 Esc 键。 

> 另一方面，插入模式允许你输入文本并将其添加到文件中。要进入插入模式，请按 i。

**[🔼Back to Top](#table-of-contents)**

<a id="editing-text"></a>
## 编辑文本

|Commands         |Description                                                           |
|-----------------|----------------------------------------------------------------------|
|`r`              |替换单个字符（并回到命令模式）               |
|`cc`             |替换整行（删除该行并进入插入模式）  |
|`C` / `c$`       |从光标处替换到行尾                          |
|`cw`             |从光标处替换到单词结尾                          |
|`s`              |删除一个字符（并进入插入模式）                        |
|`J`              |将下一行与当前行合并，中间用一个空格隔开  |
|`gJ`             |将下一行与当前行合并，中间不留空格 |
|`u`              |撤消                                                                  |
|`Ctrl + r`       |重做                                                                  |
|`.`              |重复上一条命令                                                   |

**[🔼Back to Top](#table-of-contents)**

<a id="cutting-copying-and-pasting"></a>
## 剪切、复制与粘贴

|Commands         |Description                                             |
|-----------------|--------------------------------------------------------|
|`yy`             | 复制（yank）整行                                |
|`#yy`            | 复制指定数量的行                     |
|`dd`             | 剪切（删除）整行                               |
|`#dd`            | 剪切指定数量的行                      |
|`p`              | 在光标后粘贴                                 |
|`P`              | 在光标前粘贴                                |
  
> 将 # 替换为数字

**[🔼Back to Top](#table-of-contents)**

<a id="marking-text-visual-mode"></a>
## 标记文本（可视模式）

> 除了命令模式和插入模式，Vim 还包括可视模式。该模式主要用于标记文本。

> 根据你想选择的文本块，可以在三种可视模式中选择：字符模式、行模式和块模式。

|Commands         |Description                                             |
|-----------------|--------------------------------------------------------|
|`v`              | 使用字符模式选择文本                       |          
|`V`              | 使用行模式选择行                           |            
|`Ctrl+v`         | 使用块模式选择文本                           |            

> 一旦启用了其中一种模式，请使用导航键选择所需的文本。

|Commands         |Description                                             |
|-----------------|--------------------------------------------------------|
| `o`             |从所选文本的一端移动到另一端     |
| `aw`            | 选择一个单词                                          |
| `ab`            | 选择 () 包围的块                                 |
| `aB`            | 选择 {} 包围的块                                 |
| `at`            | 选择 <> 包围的块                                 |
| `ib`            | 选择 () 内部块                                 |
| `iB`            | 选择 {} 内部块                                 |
| `it`            | 选择 <> 内部块                                 |

**[🔼Back to Top](#table-of-contents)**

<a id="visual-commands"></a>
## 可视命令

> 在可视模式下选中所需文本后，可以使用以下可视命令之一对其进行操作。其中包括：

|Commands         |Description                                             |
|-----------------|--------------------------------------------------------|
|`y`              | yank（复制）标记的文本                            |
|`d`              | 删除（剪切）标记的文本                           |
|`p`              | 在光标后粘贴文本                        |
|`u`              | 将标记文本改为小写                    |
|`U`              | 将标记文本改为大写                    |

**[🔼Back to Top](#table-of-contents)**

<a id="search-in-file"></a>
## 在文件中搜索

|Commands         |Description                                             |
|-----------------|--------------------------------------------------------|
|`*`              | 跳到当前单词的下一个实例          |
|`#`              | 跳到当前单词的上一个实例          |
|`/pattern`       | 向前搜索指定模式               |
|`?pattern`       | 向后搜索指定模式              |
|`n`              | 按相同方向重复搜索                |
|`N`              | 按相反方向重复搜索            |

**[🔼Back to Top](#table-of-contents)**

<a id="saving-and-exiting-file"></a>
## 保存与退出文件

|Commands             |Description                                                        |
|---------------------|-------------------------------------------------------------------|
|`:w`                 | 保存文件                                                     |   
|`:wq` / `:x` / `ZZ`  | 保存并关闭文件                                           |   
|`:q`                 | 退出                                                              |   
|`:q!`/ `ZQ`          | 不保存更改直接退出                                       |   
|`:w` new_file_name   | 以新名称保存文件并继续编辑原文件  |   
|`:sav`               | 以新名称保存文件并继续编辑新副本  |   
|`:w !sudo tee %`     | 使用 sudo 和 tee 命令写出文件                     |   

**[🔼Back to Top](#table-of-contents)**

<a id="enabling-vim-color-schemes"></a>
## 启用 Vim 配色方案

| Vim Color Schemes                 | Description                     |
| --------------------------------- | ------------------------------- |
| `:colorscheme [colorscheme_name]` | 切换到指定方案      |
| `:colorscheme [space]+Ctrl+d`     | 列出可用的 Vim 配色方案 |

**[🔼Back to Top](#table-of-contents)**
