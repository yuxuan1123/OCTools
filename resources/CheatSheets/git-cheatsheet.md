---
title: Git 速查表
description: 这里列出了最常用的 git 命令。
created: 2022-10-18
---

<a id="table-of-contents"></a>
## 目录

- [面向开发者的 Git 速查表](#git-cheatsheet-for-developers)
  - [Git 配置](#git-configuration)
  - [获取与创建项目](#getting--creating-projects)
  - [基础命令](#basic-commands)
  - [分支与合并](#branching--merging)
  - [丢弃更改](#discard-changes)
  - [设置上游分支](#set-upstream-branch)
  - [共享与更新项目](#sharing--updating-projects)
  - [检查与比较](#inspection--comparison)
  - [跟踪路径变更](#tracking-path-changes)
  - [设置别名](#setting-up-alias)
  - [重写历史](#rewrite-history)
  - [删除](#deletion)
  - [临时提交](#temporary-commits)

<a id="git-cheatsheet-for-developers"></a>
# 面向开发者的 Git 速查表

<a id="git-configuration"></a>
## Git 配置

| Command | Description |
| ------- | ----------- |
| `git config` | 查看所有配置选项 |
| `git config --list` | 查看所有配置选项（含用户名和邮箱）|
| `git clone [https://url]` | 从远程仓库克隆源代码 |
| `git config --global user.name "Your name"` | 配置用户名 |
| `git config --global user.email "Your email"` | 配置邮箱 | 
| `git config --global core.editor vim` | 配置编辑器 | 
| `git config user.name` | 列出用户名 | 
| `git config user.email` | 列出邮箱 | 

**[🔼Back to Top](#table-of-contents)**

<a id="getting--creating-projects"></a>
## 获取与创建项目

| Command | Description |
| ------- | ----------- |
| `git init` | 初始化本地 Git 仓库 |

**[🔼Back to Top](#table-of-contents)**

<a id="basic-commands"></a>
## 基础命令

| Command | Description |
| ------- | ----------- |
| `git status` | 查看状态 |
| `git diff` | 比较并显示更新后的代码 |
| `git add [file name]` | 将文件更改加入下一次提交 |
| `git add .` | 将所有未暂存的更改加入下一次提交 |
| `git reset [file name]` | 用于取消已暂存文件的暂存 |
| `git clean -f` | 强制删除或移除未暂存的文件 |
| `git commit -m "message about updates"` | 将更改提交到当前分支 |
| `git commit -amend` | 修补上一次提交，但沿用上一次的提交日志信息 |
| `git rm --cached [file]` | 将文件从暂存区移除（取消暂存）|
| `git rm [file]` | 从工作目录中删除文件并暂存该删除操作 |
| `git pull` | 获取并合并远程服务器上的更改到你的工作目录 |
| `git pull --allow-unrelated-histories`| 拉取具有无关历史的远程分支更改|
| `git fetch` | 收集远程提交但不像 `pull` 那样合并它们 |
| `git remote add origin [url]` | 添加远程仓库 | 
| `git show` | 显示任意 git 对象的信息 |
| `gitk` | 显示本地仓库的图形界面 |

**[🔼Back to Top](#table-of-contents)**

<a id="branching--merging"></a>
## 分支与合并

| Command | Description |
| ------- | ----------- |
| `git branch` | 列出分支 |
| `git branch [branch-name]` | 创建本地分支 |
| `git branch -m [old branch name] [new branch name]` | 重命名本地分支 |
| `git branch -d [branch-name]` | 删除分支 |
| `git branch -D [branch name]` | 强制删除分支 |
| `git branch -a` | 查看所有分支（本地和远程）|
| `git checkout [branch-name]` | 切换到另一个分支 |
| `git checkout -b "branch name"` | 创建新分支并切换到该分支 |
| `git checkout -b [branch name] origin/[branch name]` | 克隆远程分支并切换过去 |
| `git switch [branch-name]` | 切换到另一个分支 |
| `git merge [branch-name]` | 合并分支 |
| `git merge [source branch] [target branch]` | 将某分支合并到目标分支 |
| `git merge --allow-unrelated-histories`| 合并无关历史 |
| `git cherry-pick [commit-ID]` | 将一个（或多个）特定提交的更改带入当前分支。 |

**[🔼Back to Top](#table-of-contents)**

<a id="discard-changes"></a>
## 丢弃更改

| Command | Description |
| :-----: | ----------- |
| `git checkout -` | 切换到上一次检出的分支 |
| `git checkout -- [file-name.txt]` | 丢弃对文件的更改 |
| `git checkout [file]` | 将文件与最后一次提交进行匹配 |
| `git restore .` | 恢复当前目录下的所有文件 |
| `git revert [commit-ID]` | 创建新的提交，撤销指定提交在远程分支中的更改 |
| `git help -a` | 显示所有可用 Git 命令的列表 |

**[🔼Back to Top](#table-of-contents)**

<a id="set-upstream-branch"></a>
## 设置上游分支

| Command | Description |
| :-----: | ----------- |
| `git push --set-upstream origin current-branch-name` <br /> or <br /> `git push -u origin current-branch-name` | - 推送当前分支并将远程设置为上游 <br /> - `git push --set-upstream origin development` <br /> - `git push -u origin development` |
| `git pull origin main` <br /> or <br /> `git pull origin development` | - 从 `main` 分支更新 ___当前分支___ <br /> - 从 `development` 分支更新 ___当前分支___ <br /> - 更新前，请将你的所有修改 ___push___ 到 ___远程分支___ <br /> - 否则每次 ___修改都将被移除___ |

**[🔼Back to Top](#table-of-contents)**

<a id="sharing--updating-projects"></a>
## 共享与更新项目

| Command | Description |
| ------- | ----------- |
| `git push origin [branch name]` | 将分支推送到远程仓库 |
| `git pull origin [branch name]` | 从远程仓库拉取分支 |
| `git remote origin [branch name]` | 将仓库连接到本地服务器 |
| `git push <remote> --force` | 强制推送，即使会导致非快进合并。使用 `--force` 选项前请确保没有人已经拉取了这些提交。 |


**[🔼Back to Top](#table-of-contents)**

<a id="inspection--comparison"></a>
## 检查与比较

| Command | Description |
| ------- | ----------- |
| `git log` | 查看更改 |
| `git log --summary` | 查看更改（详细）|
| `git log --follow [file]` | 显示更改了该文件的提交，即使文件被重命名过 |
| `git log --oneline` | 查看更改（简略）|
| `git log branchB..branchA` | 查看 branchA 上但不在 branchB 上的更改|
| `git log --graph` | 以图形方式查看 git 日志 |
| `git log --decorate` | 让 git log 显示指向每个提交的所有引用（如分支、标签等）|
| `git log --author="name_of_author"` | 搜索特定作者 |
| `git shortlog` | 按作者对每个提交分组，并显示每个提交信息的第一行 |
| `git reflog ` | Git 通过一种称为 reflog 的机制跟踪分支顶端的更新。即使这些更改集没有被任何分支或标签引用，也能让你回溯到它们 |
| `git diff branchB...branchA` | 查看 branchA 上有而 branchB 上没有的差异 |
| `git blame [file name]` | 显示文件每一行的修改信息 |
| `git diff --name-only` | 只显示更改文件的名称 |
| `git bisect start` | 开始二分查找过程，以找出引入了当前 bug 的那个错误提交 |
| `git bisect good` <br /> `git bisect good [Commit ID]` | 标记好的提交，即该提交中没有 bug |
| `git bisect bad [Commit ID]` | 标记坏的提交，即该提交中存在 bug。若未提供提交 ID，则将当前提交视为坏提交 |
| `git grep "hello"` | 对目录下所有文件进行文本搜索 |
| `git bugreport` | 在 `git-bugreport-2022-10-25-1228.txt` 创建新报告 |

**[🔼Back to Top](#table-of-contents)**

<a id="tracking-path-changes"></a>
## 跟踪路径变更

| Command | Description |
| ------- | ----------- |
| `git rm [file]` | 从项目中删除文件并为提交暂存删除操作 |
| `git mv [existing-path] [new-path]` | 更改现有文件路径并暂存移动 |
| `git log --stat -M` | 显示所有提交日志，并标注任何发生移动的路径 |

**[🔼Back to Top](#table-of-contents)**

<a id="setting-up-alias"></a>
## 设置别名

| Command | Description |
| ------- | ----------- |
| `git config --global alias.[short name for command]  [actual command]` | 别名让命令更简短、更顺手 | (## ex:- git config --global alias.st status) |

**[🔼Back to Top](#table-of-contents)**

<a id="rewrite-history"></a>
## 重写历史

| Command | Description |
| ------- | ----------- |
| `git rebase [branch]` | 将当前分支的提交应用到指定分支之前 |
| `git reset --hard [commit]` | 清暂存区，按指定提交重写工作树 |
| `git reset HEAD "file-name"` | 回到当前所在的指针位置，从暂存区移除 |
| `git reset --soft "commit-hash"` | 保留你的更改并返回/撤销你所做的提交，但文件会保持已暂存状态，准备再次提交 |
| `git reset --mixed "commit-hash"` | 同样返回/撤销该提交，但将文件恢复到暂存之前的状态，即已修改但处于未暂存状态 |
| `git reset --hard "commit-hash"` | 直接忽略该提交的存在并撤销此提交中所做的所有更改。 <br /> 这是一种非常彻底的重置，通常在将提交推送到远程仓库之前使用。 |

**[🔼Back to Top](#table-of-contents)**

<a id="deletion"></a>
## 删除

| Command | Description |
| ------- | ----------- |
| `git gc` | 清理不必要的文件并优化本地仓库 |
| `git prune` | 删除没有任何引用指向的对象 |

**[🔼Back to Top](#table-of-contents)**

<a id="temporary-commits"></a>
## 临时提交

| command | Description |
| ------- | ----------- |
| `git stash` | 保存已修改和已暂存的更改|
| `git stash list` | 列出暂存文件更改的栈顺序|
| `git stash pop` | 从暂存栈顶部写出工作更改|
| `git stash drop` | 丢弃暂存栈顶部的更改|

**[🔼Back to Top](#table-of-contents)**
