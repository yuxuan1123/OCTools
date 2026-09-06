---
title: BASH 速查表
description: 这里列出了最常用的 bash 命令。
created: 2022-10-23
---

## 目录

- #面向开发者的-bash-速查表
  - #命令
    - #tr-命令
  - #一行脚本
    - #屏蔽恶意-ip
  - #if-语句
    - #检查是否传入了参数
    - #检查必需的变量是否存在
    - #检查环境变量是否存在
  - #while-循环
    - #运行进程-5-秒
    - #在-ttl-内持续运行直到状态改变
  - #for-循环
    - #上传所有-docker-镜像
  - #函数
  - #重定向输出
    - #标准输出标准错误
  - #文本处理
    - #删除前-3-个字符
    - #只显示最后-3-个字符

# 面向开发者的 BASH 速查表

## 命令

### `tr 命令`

> ___移除空白字符：___

```
$ echo 'foo - bar' | tr -d '[:space:]'
foo-bar
```

> ___转换为大写：___

```
$ echo 'HeLLo' | tr '[:lower:]' '[:upper:]'
HELLO
```

**#目录**

## 一行脚本

### `屏蔽恶意 IP`

> 使用 iptables 屏蔽所有恶意 IP 地址：

```
$ cat /var/log/maillog | grep 'lost connection after AUTH from unknown' | tail -n 5
May 10 11:19:49 srv4 postfix/smtpd[1486]: lost connection after AUTH from unknown[185.36.81.145]
May 10 11:21:41 srv4 postfix/smtpd[1762]: lost connection after AUTH from unknown[185.36.81.164]
May 10 11:21:56 srv4 postfix/smtpd[1762]: lost connection after AUTH from unknown[175.139.231.129]
May 10 11:23:51 srv4 postfix/smtpd[1838]: lost connection after AUTH from unknown[185.211.245.170]
May 10 11:24:02 srv4 postfix/smtpd[1838]: lost connection after AUTH from unknown[185.211.245.170]
```

> 提取出仅含 IP 的数据：

```
cat /var/log/maillog | grep 'lost connection after AUTH from unknown' | cut -d'[' -f3 | cut -d ']' -f1 | tail -n5
185.36.81.164
175.139.231.129
185.211.245.170
185.211.245.170
185.36.81.173
```

> 获取唯一的 IP 地址：

```
$ cat /var/log/maillog | grep 'lost connection after AUTH from unknown' | cut -d'[' -f3 | cut -d ']' -f1 | sort | uniq
103.194.70.16
112.196.77.202
113.172.210.19
113.173.182.119
139.59.224.234
```

> 将输出重定向到 iptables：

```
$ for ip in $(cat /var/log/maillog | grep 'lost connection after AUTH from unknown' | cut -d'[' -f3 | cut -d ']' -f1 | sort | uniq); do iptables -I INPUT -s ${ip} -p tcp --dport 25 -j DROP; done
```

**#目录**

## If 语句

### `检查是否传入了参数`

```
if [[ $# -eq 0 ]] ; then
    echo '需要传入参数'
    exit 0
fi
```

**#目录**

### `检查必需的变量是否存在`

```
if [ $1 == "one" ] || [ $1 == "two" ]
then
  echo "参数 1 的值是 one 或 two"
  exit 0
else
  echo "我需要参数 1 为 one 或 two"
  exit 1
fi
```

`或者`

```
NAME=${1}
if [ -z ${NAME} ]
  then
    echo NAME 未定义
    exit 1
  else
    echo "你好 ${NAME}"
fi
```

**#目录**

### `检查环境变量是否存在`

```
if [ -z ${OWNER} ] || [ -z ${NAME} ]
then
  echo "不满足两个环境变量都存在的要求"
  exit 1
else
  echo "所需的环境变量存在"
fi
```

**#目录**

## While 循环

### `运行进程 5 秒`

```
set -ex
count=0
echo "启动"
ping localhost &
while [ $count -le 5 ]
  do
    sleep 1
    count=$((count + 1))
    echo $count
  done
ps aux | grep ping
echo "结束"
kill $!
sleep 2
```

**#目录**

### `在 TTL 内持续运行直到状态改变`

```
UPDATE_COMPLETE=false
UPDATE_STATUS=running
COUNT=0
while [ ${UPDATE_COMPLETE} == false ]
    do
        if [ $count -gt 10 ]
            then
                echo "超时"
                exit 1
        fi
        if [ ${UPDATE_STATUS} == running ] 
            then
                echo "仍在运行"
                sleep 1
                COUNT=$((COUNT+1))
                if [ $count == 7 ]
                    then
                        UPDATE_COMPLETE=true
                fi
        elif [ ${UPDATE_STATUS} == successful ]
            then
                UPDATE_COMPLETE=successful
        else
            echo "意外的更新响应"
            exit 1
        fi
    done
echo "完成"
```

**#目录**

## For 循环

### `上传所有 Docker 镜像`

```bash
for i in $(ls | grep .tar): do
  docker load -i $i;
done
```

**#目录**

## 函数

```
message(){
    NAME=${1}
    echo "你好 ${NAME}"
}
```

`或者` ___传递所有参数：___

```
message(){
    echo "你好 $@"
}
```

**#目录**

## 重定向输出

### `标准输出、标准错误`

> 将标准错误重定向到 /dev/null：

```
grep -irl faker . 2>/dev/null
```

> 将标准输出重定向到一个文件，标准错误重定向到另一个文件：

```
grep -irl faker . > out 2>error
```

> 将标准错误重定向到标准输出 (&1)，然后将标准输出重定向到文件：

```
grep -irl faker . >out 2>&1
```

> 将两者都重定向到一个文件：

```
grep -irl faker . &> file.log
```

**#目录**

## 文本处理

### `删除前 3 个字符`

```
$ STRING="abcdefghij"
$ echo ${STRING:3}
defghij
```

**#目录**

### `只显示最后 3 个字符`

> 使用 tail 只显示最后 3 个字符：

```
$ STRING="abcdefghij"
$ echo ${STRING} | tail -c 4
hij
```

**#目录**