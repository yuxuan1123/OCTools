---
title: Conda 速查表
description: 这里列出了最常用的 conda 命令。
created: 2022-10-22
---

## 目录

- #面向开发者的-conda-速查表
  - #conda-环境的基本语法
  - #使用环境

# 面向开发者的 Conda 速查表

## conda 环境的基本语法

| 命令 | 描述 |
| ------------------------------- | ----------------------------------- |
| `conda create --name env_name` | 创建一个新的环境 |
| `conda env list` | 列出所有可用的环境 |
| `conda activate env_name` | 激活特定的环境 |
| `conda install package_name` | 安装一个包 |
| `conda info` | 检查 conda 版本 |
| `conda update conda` | 更新 conda 版本 |
| `conda update package_name` | 更新任何已安装的包 |

**#目录**

## 使用环境

| 命令 | 描述 |
| -------------------------------------- | ------------------------------------------------------- |
| `conda create --name py35 python=3.5` | 创建一个名为 py35 的新环境，并安装 Python 3.5 |

**#目录**