---
title: npm 速查表
description: 这里列出了最常用的 npm 命令。
created: 2022-10-18
---

<a id="table-of-contents"></a>
## 目录

- [NPM 面向开发者速查表](#npm-cheatsheet-for-developers)
  - [Node 包管理器基础语法](#basic-syntax-of-node-package-manager)

<a id="npm-cheatsheet-for-developers"></a>
# NPM 面向开发者速查表

<a id="basic-syntax-of-node-package-manager"></a>
## Node 包管理器基础语法

| Command                                                        | Description                                          |
| -------------------------------------------------------------- | ---------------------------------------------------- |
| `npm init`                                                     | 初始化一个 node.js 项目                              |
| `npm install` <br /> `npm i`                                   | 安装 package.json 中的依赖                           |
| `npm install --global [package]` <br /> `npm i -g [package]`   | 全局安装包                                           |
| `npm install-latest-npm`                                       | 更新 npm                                             |
| `npm run`                                                      | 列出可运行的脚本                                     |
| `npm run bar`                                                  | 运行名为 bar 的脚本                                  |
| `npm test`                                                     | 运行项目测试                                         |
| `npm list`                                                     | 查看本地包                                           |
| `npm un <package_name> ` <br /> `npm uninstall <package_name>` | 从项目中卸载包                                       |
| `npm -g uninstall <name> `                                     | 卸载全局包                                           |
| `npm update -g <package_name> `                                | 更新单个全局包                                       |
| `npm up <package_name>`                                        | 更新 npm 包                                          |
| `npm list -g --depth-0`                                        | 列出全局安装的包                                     |
| `npm-windows-upgrades`                                         | 在 Windows 上升级 npm                                |
| `npm outdated -g --depth-0`                                    | 已更新的全局包                                       |
| `npm alias default 16`                                         | 设置默认的 node 版本                                 |
| `npm i <package>`                                              | 安装包                                               |
| `npm u <package>`                                              | 更新包                                               |
| `npm rm <package>`                                             | 移除包                                               |
| `npm audit`                                                    | 扫描并列出包中的所有漏洞                             |
| `npm audit fix`                                                | 修复已发现的漏洞                                     |
| `npm edit`                                                     | 编辑已安装的包                                       |
| `npm publish`                                                  | 发布包                                               |
| `npm rebuild`                                                  | - 重新构建包 <br /> - 该命令会在匹配的文件夹上运行 `npm build` 命令 |

**[🔼返回顶部](#table-of-contents)**
