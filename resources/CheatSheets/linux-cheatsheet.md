<!-- Heading section doesn't work -->
<!-- ---
title: Linux 速查表
description: 此处列出了最常用的 Linux 命令。
created: 2022-10-21
--- -->

<a id="table-of-contents"></a>
## 目录

- [面向开发者的 Linux 速查表](#linux-cheatsheet-for-developers)
  - [文件命令](#file-commands)
  - [文件权限](#file-permissions)
  - [权限提升](#privilege-escalation)
  - [SSH](#ssh)
  - [系统信息](#system-info)
  - [快捷键](#shortcuts)
  - [文本编辑器](#text-editors)
  - [归档](#archives)
  - [磁盘使用情况](#disk-usage)
  - [搜索](#search)
  - [网络](#networking)
  - [环境变量命令](#environment-variables-command)

<a id="linux-cheatsheet-for-developers"></a>
# Linux CheatSheet for Developers

<a id="file-commands"></a>
## File Commands

| Command | Description |
| ------- | ----------- |
| `pwd` | 显示当前目录 | 
| `mkdir dir` | 创建名为 *dir* 的目录 | 
| `mkdir -p folder/folder2` | 创建目录 *folder*，并在其中再创建目录 *folder2*|
| `cd dir` | 切换到目录 *dir* |
| `cd ..` | 返回上一级目录 | 
| `cd` | 切换到主目录 |
| `ls` | 列出目录内容|
| `ls -r` | 反向列出目录内容 |
| `ls -t` | 按时间列出目录内容 |
| `ls -al` | 以格式化方式列出目录内容，包括隐藏文件 |
| `rm file` | 删除文件 | 
| `rm -r dir` | 删除目录 *dir* | 
| `rm -f file` | 强制删除文件 | 
| `rm -rf dir` | 强制删除目录 *dir* | 
| `rm -rfv dir` | 以详细输出模式强制删除目录 *dir* |
| `cp file1 dir` | 将 *file1* 复制到 *dir* 内部 | 
| `mv file1 dir` | 将 *file1* 移动/剪切到 *dir* 内部 | 
| `touch file` | 创建 *file*|
| `cat file` | 显示文件内容 | 
| `head file` | 显示文件前 10 行 | 
| `tail file` | 显示文件后 10 行 | 
| `gpg -c file` | 加密文件 | 
| `gpg file` | 解密文件 | 
| `wc` | 显示文件中的单词数、行数和字节数 |

**[🔼Back to Top](#table-of-contents)**

<a id="file-permissions"></a>
## File Permissions

| Command | Description |
| ------- | ----------- |
| `chmod octal file` | 通过相加以下数值将文件权限更改为八进制值，分别对应所有者、组和其他人：**4 - 读( r )， 2 - 写( w ), 1 - 执行 ( x )**|
| `chmod 777 file` | 所有人可读、写、执行 | 
| `chmod 755 file` | 所有者 rwx，组和其他人 rx | 

**[🔼Back to Top](#table-of-contents)**

<a id="privilege-escalation"></a>
 ## Privilege Escalation
 
| Command | Description |
| ------- | ----------- |
| `sudo command` | 以 root 身份运行 *command*。（如果某命令需要更高权限，可能需要使用 sudo 运行）|
| `su` | 以 root 身份运行交互式 shell |

**[🔼Back to Top](#table-of-contents)**

<a id="ssh"></a>
## SSH

| Command | Description |
| ------- | ----------- |
| `ssh user@host` | 以 user 身份连接到 host |
| `ssh -p port user@host` | 以 user 身份在 *port* 端口连接到 host|

**[🔼Back to Top](#table-of-contents)**

<a id="system-info"></a>
## System Info

| Command | Description |
| ------- | ----------- |
| `date` | 显示系统日期和时间 |
| `cal` | 显示本月日历 |
| `uptime` | 显示系统运行时长 |
| `free` | 显示系统中空闲和已用内存的数量 |
| `w` | 查看谁在线 |
| `whoami` | 查看当前登录身份|
| `uname -a` | 显示内核信息 |
| `man command` | 显示任意命令的手册（按 **q** 退出） 

**[🔼Back to Top](#table-of-contents)**

<a id="shortcuts"></a>
## Shortcuts

| Command | Description |
| ------- | ----------- |
| `Ctrl + A` | 将光标移动到行首 |
| `Ctrl + E` | 将光标移动到行尾 |
| `Ctrl + F` | 向前移动一个字符 |
| `Ctrl + B` | 向后移动一个字符 |
| `Ctrl + L` | 清屏 |
| `Ctrl + C` | 终止当前命令 |
| `Ctrl + D` | 注销当前会话 |
| `Ctrl + W` | 删除当前行中的一个单词 |
| `Ctrl + U` | 删除整行 |

**[🔼Back to Top](#table-of-contents)**

<a id="text-editors"></a>
## Text Editors
| Command | Description |
| ------- | ----------- |
| `nano file` | nano 是一个小巧易用的编辑器 |
| `vi file` | vi 是一个功能强大的文本编辑器，所有操作均通过键盘完成。[如何退出 vim/vi](https://www.cyberciti.biz/faq/linux-unix-exit-vim-editor/)（相信你会需要用到它） |
| `vim file` | vim - Vi IMproved 是 vi 编辑器的增强版本。与 vi 一样，所有操作均通过键盘完成。|

**[🔼Back to Top](#table-of-contents)**

<a id="archives"></a>
## Archives
| Command | Description |
| ------- | ----------- |
| `tar cf archive.tar directory` | 创建名为 archive.tar 的 tar 归档，包含 directory |
| `tar xf archive.tar` | 从 archive.tar 中提取内容 |
| `tar czf archive.tar.gz directory` | 创建 gzip 压缩的 tar 文件，名为 archive.tar.gz|
| `tar xzf archive.tar.gz` | 提取 gzip 压缩的 tar 文件|
| `tar cjf archive.tar.bz2 directory` | 创建使用 bzip2 压缩的 tar 文件|
| `tar xjf archive.tar.bz2` | 提取 bzip2 压缩的 tar 文件|

**[🔼Back to Top](#table-of-contents)**

<a id="disk-usage"></a>
## Disk Usage
| Command | Description |
| ------- | ----------- |
| `df -h` | 显示已挂载文件系统的空闲和已用空间 |
| `df -i` | 显示已挂载文件系统的空闲和已用 inode 数 |
| `fdisk -l` | 显示磁盘分区的大小和类型|
| `du -ah` | 以易读格式显示所有文件和目录的磁盘使用情况|
| `du -sh` | 显示当前目录的总磁盘使用量|

**[🔼Back to Top](#table-of-contents)**

<a id="search"></a>
## Search
| Command | Description |
| ------- | ----------- |
| `grep pattern file` | 在文件中搜索 pattern |
| `grep -r pattern directory` | 在目录中递归搜索 pattern |
| `locate name` | 按名称查找文件和目录|
| `find /home/xyz -name 'prefix*'` | 在 /home/xyz 中查找以 "prefix" 开头的文件 |
| `find /home -size +100M` | 在 /home 中查找大于 100MB 的文件|

**[🔼Back to Top](#table-of-contents)**

<a id="networking"></a>
## Networking
| Command | Description |
| ------- | ----------- |
| `ip a` | 显示所有网络接口和 IP 地址 |
| `ip addr show dev eth0` | 显示 eth0 的地址和详情 |
| `ethtool eth0` | 查询或控制网络驱动及硬件设置|
| `ping host` | 向 host 发送 ICMP 回显请求 |
| `whois domain` | 显示 domain 的 whois 信息 |
| `dig domain` | 显示 domain 的 DNS 信息 |
| `dig -x IP_ADDRESS` | 对 IP_ADDRESS 进行反向查找 |
| `host domain` | 显示 domain 的 DNS IP 地址 |
| `hostname -i` | 显示主机名的网络地址 |
| `hostname -I` | 显示主机的所有本地 IP 地址 |
| `wget http://domain.com/file` |Download http[]()://domain.com/file |
| `netstat -nutlp` |显示正在监听的 tcp 和 udp 端口及对应程序|

**[🔼Back to Top](#table-of-contents)**

<a id="environment-variables-command"></a>
## Environment variables command
| Command | Description |
| ------- | ----------- |
| `env` | 显示所有环境变量 |
| `echo $VARIABLE` | 显示变量的值 |

**[🔼Back to Top](#table-of-contents)**
