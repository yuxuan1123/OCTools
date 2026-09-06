---
title: Docker 速查表
description: 这里列出了最常用的 docker 命令。
created: 2022-10-22
---

<a id="table-of-contents"></a>
## 目录

- [Docker 面向开发者速查表](#docker-cheatsheet-for-developers)
  - [运行新容器](#run-a-new-container)
  - [管理容器](#manage-containers)
  - [管理镜像](#manage-images)
  - [管理系统](#manage-system)
  - [信息与统计](#info-and-stats)

<a id="docker-cheatsheet-for-developers"></a>
# Docker 面向开发者速查表

<a id="run-a-new-container"></a>
## 运行新容器

| Command                                        | Description                              |
| ---------------------------------------------- | ---------------------------------------- |
| `docker run IMAGE`                             | 从镜像启动一个新容器                     |
| `docker run --name CONTAINER IMAGE`            | 指定容器名称                             |
| `docker run -p HOSTPORT:CONTAINERPORT IMAGE`   | 映射端口                                 |
| `docker run -P IMAGE`                          | 映射所有端口                             |
| `docker run -d IMAGE`                          | 在后台启动容器                           |
| `docker run --hostname HOSTNAME IMAGE`         | 指定主机名                               |
| `docker run --add-host HOSTNAME:IP IMAGE`      | 添加 DNS 条目                            |
| `docker run -v HOSTDIR:TARGETDIR IMAGE`        | 将本地目录挂载进容器                     |
| `docker run -it --entrypoint EXECUTABLE IMAGE` | 更改入口点                               |

**[🔼返回顶部](#table-of-contents)**

<a id="manage-containers"></a>
## 管理容器

| Command                                | Description                              |
| -------------------------------------- | ---------------------------------------- |
| `docker ps`                            | 显示正在运行的容器列表                   |
| `docker ps -a`                         | 显示所有容器列表                         |
| `docker rm CONTAINER`                  | 删除容器                                 |
| `docker rm -f CONTAINER`               | 删除正在运行的容器                       |
| `docker CONTAINER prune`               | 删除已停止的容器                         |
| `docker stop CONTAINER`                | 停止正在运行的容器                       |
| `docker start CONTAINER`               | 启动已停止的容器                         |
| `docker cp CONTAINER:SOURCE TARGET`    | 将文件从容器复制到宿主机                 |
| `docker cp TARGET CONTAINER:SOURCE`    | 将文件从宿主机复制到容器                 |
| `docker exec -it CONTAINER EXECUTABLE` | 在正在运行的容器内启动一个 shell         |
| `docker rename OLD_NAME NEW_NAME`      | 重命名容器                               |
| `docker commit CONTAINER`              | 根据容器创建镜像                         |

**[🔼返回顶部](#table-of-contents)**

<a id="manage-images"></a>
## 管理镜像

| Command                           | Description                              |
| --------------------------------- | ---------------------------------------- |
| `docker pull IMAGE[:TAG]`         | 下载镜像                                 |
| `docker push IMAGE`               | 将镜像上传到仓库                         |
| `docker rmi IMAGE`                | 删除镜像                                 |
| `docker images`                   | 显示所有镜像列表                         |
| `docker image prune`              | 删除悬空镜像                             |
| `docker image prune -a`           | 删除所有未使用的镜像                     |
| `docker build DIRECTORY`          | 从 Dockerfile 构建镜像                   |
| `docker tag IMAGE NEWIMAGE`       | 为镜像打标签                             |
| `docker build -t IMAGE DIRECTORY` | 从 Dockerfile 构建并为镜像打标签         |
| `docker save IMAGE > FILE`        | 将镜像保存为 .tar 文件                   |
| `docker load -i TARFILE`          | 从 .tar 文件加载镜像                     |

**[🔼返回顶部](#table-of-contents)**

<a id="manage-system"></a>
## 管理系统

| Command                           | Description                              |
| --------------------------------- | ---------------------------------------- |
| `docker system prune --all --force` | 移除所有未使用的资源                   |

**[🔼返回顶部](#table-of-contents)**

<a id="info-and-stats"></a>
## 信息与统计

| Command                 | Description                            |
| ----------------------- | -------------------------------------- |
| `docker logs CONTAINER` | 显示容器的日志                         |
| `docker stats`          | 显示正在运行容器的统计信息             |
| `docker top CONTAINER`  | 显示容器的进程                         |
| `docker version`        | 显示已安装的 docker 版本               |
| `docker inspect NAME`   | 获取对象的详细信息                     |
| `docker diff CONTAINER` | 显示容器中所有被修改的文件             |
| `docker port CONTAINER` | 显示容器的映射端口                     |

**[🔼返回顶部](#table-of-contents)**
