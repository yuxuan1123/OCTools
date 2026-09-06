---
title: Yarn 速查表
description: 这里列出了最常用的 yarn 命令。
created: 2022-10-20
---

<a id="table-of-contents"></a>
## 目录

- [Yarn 面向开发者速查表](#yarn-cheatsheet-for-developers)
  - [Yarn 基础语法](#basic-syntax-of-yarn)

<a id="yarn-cheatsheet-for-developers"></a>
# Yarn 面向开发者速查表

<a id="basic-syntax-of-yarn"></a>
## Yarn 基础语法

| Command                         | Description                         |
| ------------------------------- | ----------------------------------- |
| `yarn`                          | 安装依赖                             |
| `yarn add [package]`            | 安装包                               |
| `yarn add --dev [package]`      | 安装开发依赖包                       |
| `yarn autoclean`                | 从依赖中释放不必要的文件和文件夹     |
| `yarn cache clean`              | 移除共享缓存文件                     |
| `yarn global add [package]`     | 全局安装包                           |
| `yarn global remove [package]`  | 全局卸载包                           |
| `yarn help`                     | 访问命令列表                         |
| `yarn info`                     | 查看与包相关的信息                   |
| `yarn init`                     | 创建一个新包                         |
| `yarn link <destination>`       | 将本地项目连接到另一个项目           |
| `yarn npm login`                | 存储新的登录信息以访问 npm 仓库      |
| `yarn npm logout`               | 退出 npm 仓库                        |
| `yarn npm publish`              | 将当前工作区发布到 npm 仓库          |
| `yarn pack`                     | 从当前工作区生成 tar 包              |
| `yarn remove [package]`         | 卸载包                               |
| `yarn remove [package]`         | 卸载开发依赖包                       |
| `yarn run <scriptName>`         | 运行 package.json 中定义的脚本       |
| `yarn set version <version>`    | 锁定项目使用的 Yarn 版本             |
| `yarn up [package]`             | 升级项目中的依赖                     |
| `yarn upgrade`                  | 已更新                               |
| `yarn upgrade [package]`        | 更新包                               |

**[🔼返回顶部](#table-of-contents)**
