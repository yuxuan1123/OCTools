---
title: NVM 速查表
description: 这里列出了最常用的 nvm 命令。
created: 2022-10-19
---

<a id="table-of-contents"></a>
## 目录

- [NVM 面向开发者速查表](#nvm-cheatsheet-for-developers)
  - [Node 版本管理器基础语法](#basic-syntax-of-node-version-manager)

<a id="nvm-cheatsheet-for-developers"></a>
# NVM 面向开发者速查表

<a id="basic-syntax-of-node-version-manager"></a>
## Node 版本管理器基础语法

| Command                         | Description                         |
| ------------------------------- | ----------------------------------- |
| `nvm ls-remote`                 | 列出所有可用的 Node 版本            |
| `nvm ls`                        | 列出所有本地已安装的版本            |
| `nvm install node`              | 安装最新发布的 Node 版本            |
| `nvm install <version>`         | 安装指定的 Node 版本                |
| `nvm use <version>`             | 切换并使用指定的 Node 版本          |
| `nvm which <version>`           | 显示指定 Node 版本的路径            |
| `nvm current`                   | 显示当前正在使用的 Node 版本        |
| `nvm alias default <version>`   | 将默认的 Node 版本设置为指定版本    |
| `nvm unalias <alias_name>`      | 删除名为 <alias_name> 的别名        |
| `nvm --help`                    | 显示 NVM 帮助文档                    |
| `nvm exec <version> node app.js`| 使用指向指定 node 版本的 PATH 运行 Node app.js |
| `nvm set-colors cgYmW`          | 将文本颜色设置为青色、绿色、粗体黄色、品红色和白色 |
| `nvm run <version> app.js`      | 使用指定的 Node 版本运行 app.js      |
| `nvm install-latest-npm`        | 如果你使用通过 nvm 安装的 Node，则更新你的 npm 版本 |
| `nvm root <path>`               | 设置 nvm 存储不同 node.js 版本的目录 |
| `nvm proxy [url]`               | 设置用于下载的代理。留空 [url] 可查看当前代理。将 [url] 设为 "none" 可移除代理。 |
| `nvm -v`                        | 检查是否已安装 nvm                                                                                  |
| `nvm uninstall <version>`       | 卸载特定版本                                                                                        |
| `nvm ls`                        | 显示本地可用的版本                                                                                  |
| `nvm uninstall --lts`           | 卸载最新的长期支持版本                                                                              |

**[🔼返回顶部](#table-of-contents)**
