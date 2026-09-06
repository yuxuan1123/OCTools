---
title: Node.js 速查表
description: 这里列出了最常用的 node 命令。
created: 2022-10-27
---

<a id="table-of-contents"></a>
## 目录

- [Node.js 开发者速查表](#nodejs-cheatsheet-for-developers)
  - [Node.js 基础命令](#nodejs-basic-commands)
  - [内置方法](#built-in-methods)
  - [重要关键字](#important-keyword)
  - [控制台](#console)
  - [定时器](#timers)
  - [模块](#modules)
  - [进程](#process)
  - [子进程](#child-process)
  - [UTIL（工具）](#util)
  - [EVENTS（事件）](#events)
  - [STREAM（流）](#stream)
    - [读取](#read)
    - [写入](#write)
  - [文件系统](#file-system)
  - [路径](#path)
  - [HTTP](#http)
  - [URL](#url)
  - [查询字符串](#query-string)
  - [断言](#assert)
  - [操作系统](#os)
  - [缓冲区](#buffer)

<a id="nodejs-cheatsheet-for-developers"></a>
# Node.js 开发者速查表

<a id="nodejs-basic-commands"></a>
## Node.js 基础命令

|      Command       | Description                          |
| :----------------: | ------------------------------------ |
|       `node`       | 在终端中运行 Node REPL               |
|  `node —version`   | 打印当前 Node 版本                   |
| `node filename.js` | 执行 filename.js 中的 Node 代码      |

**[🔼Back to Top](#table-of-contents)**

<a id="built-in-methods"></a>
## 内置方法

|  Command  | Description                                                                                                                                            |
| :-------: | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
|   `fs`    | 在文件系统上读写文件                                                                                                                                   |
|  `path`   | 无论使用什么操作系统都能拼接路径                                                                                                                       |
|  `http`   | 发起请求并创建 HTTP 服务器                                                                                                                             |
|  `https`  | 使用 SSL/TLS 处理安全的 HTTP 服务器                                                                                                                    |
| `events`  | 使用 EventEmitter                                                                                                                                      |
| `crypto`  | 加密与哈希等密码学工具                                                                                                                                |
| `process` | 关于当前运行进程的信息，例如 <br /> - `process.argv` 用于传入的参数 <br /> - `process.env` 用于环境变量                          |

**[🔼Back to Top](#table-of-contents)**

<a id="important-keyword"></a>
## 重要关键字

|   keyword    | description                                                                                                                          |
| :----------: | ----------------------------------------------------------------------------------------------------------------------------------- |
| `__filename` | 正在执行的代码的文件名（绝对路径）                                                                                                  |
| `__dirname`  | 当前执行脚本所在目录的名称（绝对路径）                                                                                              |
|   `module`   | 对当前模块的引用。特别是 module.exports 用于定义模块通过 require() 导出和提供的内容。                                              |
|  `exports`   | 对 module.exports 的引用，输入更简短。                                                                                               |
|  `process`   | process 对象是一个全局对象，可从任何地方访问。它是 EventEmitter 的一个实例。                                                        |
|   `Buffer`   | Buffer 类是用于直接处理二进制数据的全局类型。                                                                                       |

**[🔼Back to Top](#table-of-contents)**

<a id="console"></a>
## 控制台

|                 keyword                 | description                                                                                                    |
| :-------------------------------------: | -------------------------------------------------------------------------------------------------------------- |
|      `console.log([data], [...])`       | 打印到 stdout，并换行。                                                                                        |
|      `console.info([data], [...])`      | 与 console.log 相同。                                                                                          |
|     `console.error([data], [...])`      | 与 console.log 相同，但打印到 stderr。                                                                         |
|      `console.warn([data], [...])`      | 与 console.error 相同。                                                                                        |
|           `console.dir(obj)`            | 对 obj 使用 util.inspect 并将结果字符串打印到 stdout。                                                         |
|          `console.time(label)`          | 标记一个时间。                                                                                                 |
|        `console.timeEnd(label)`         | 结束计时器，记录输出。                                                                                         |
|         `console.trace(label)`          | 将当前位置的堆栈跟踪打印到 stderr。                                                                            |
| `console.assert(expression, [message])` | 与 assert.ok() 相同，当表达式求值为 false 时抛出带有 message 的 AssertionError。                              |

**[🔼Back to Top](#table-of-contents)**

<a id="timers"></a>
## 定时器

|                   keyword                    | description                                                                                                                                |
| :------------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `setTimeout(callback, delay, [arg], [...])`  | 在 delay 毫秒后安排一次性回调的执行。也可选择性地向回调传递参数。                                                                          |
|              `clearTimeout(t)`               | 停止之前用 setTimeout() 创建的定时器。                                                                                                      |
| `setInterval(callback, delay, [arg], [...])` | 每隔 delay 毫秒安排回调的重复执行。也可选择性地向回调传递参数。                                                                            |
|              `clearInterval(t)`              | 停止之前用 setInterval() 创建的定时器。                                                                                                     |
|    `setImmediate(callback, [arg], [...])`    | 在 I/O 事件回调之后、setTimeout 和 setInterval 之前安排回调的"立即"执行。                                                                   |
|      `clearImmediate(immediateObject)`       | 停止之前用 setImmediate() 创建的定时器。                                                                                                    |
|                  `unref()`                   | 允许创建一个处于活动状态的定时器，但如果是事件循环中唯一剩下的项，node 不会保持程序运行。                                                  |
|                   `ref()`                    | 如果之前调用过 unref() 取消引用定时器，可以调用 ref() 显式请求定时器保持程序运行。                                                         |

**[🔼Back to Top](#table-of-contents)**

<a id="modules"></a>
## 模块

|                 keyword                 | description                                                                       |
| :-------------------------------------: | --------------------------------------------------------------------------------- |
|  `var module = require('./module.js')`  | 加载同一目录下的 module.js 模块。                                                 |
| `module.require('./another_module.js')` | 加载 another_module，如同从模块自身调用 require() 一样。                          |
|               `module.id`               | 模块的标识符。通常这是完全解析后的文件名。                                        |
|            `module.filename`            | 模块完全解析后的文件名。                                                          |
|             `module.loaded`             | 模块是否加载完成，或正在加载过程中。                                              |
|             `module.parent`             | 引用此模块的模块。                                                                |
|            `module.children`            | 此模块所引用的模块对象。                                                          |

**[🔼Back to Top](#table-of-contents)**

<a id="process"></a>
## 进程

|                       keyword                       | description                                                                                                                                                                      |
| :-------------------------------------------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|       `process.on('exit', function(code) {})`       | 进程即将退出时触发                                                                                                                                                               |
| `process.on('uncaughtException', function(err) {})` | 异常一直冒泡回到事件循环时触发（不应使用）                                                                                                                                       |
|                  `process.stdout`                   | 指向 stdout 的可写流。                                                                                                                                                           |
|                  `process.stderr`                   | 指向 stderr 的可写流。                                                                                                                                                           |
|                   `process.stdin`                   | 指向 stdin 的可读流。                                                                                                                                                            |
|                   `process.argv`                    | 包含命令行参数的数组。                                                                                                                                                           |
|                    `process.env`                    | 包含用户环境变量的对象。                                                                                                                                                         |
|                 `process.execPath`                  | 启动该进程的该可执行文件的绝对路径名。                                                                                                                                           |
|                 `process.execArgv`                  | 启动该进程的可执行文件所带的一组 node 特定命令行选项。                                                                                                                           |
|                   `process.arch`                    | 你运行的处理器架构：'arm'、'ia32' 或 'x64'。                                                                                                                                     |
|                  `process.config`                   | 包含用于编译当前 node 可执行文件的配置选项的 JavaScript 表示的对象。                                                                                                            |
|                    `process.pid`                    | 进程的 PID。                                                                                                                                                                     |
|                 `process.platform`                  | 你运行的平台：'darwin'、'freebsd'、'linux'、'sunos' 或 'win32'。                                                                                                                 |
|                   `process.title`                   | 用于设置 'ps' 中显示的标题的 getter/setter。                                                                                                                                     |
|                  `process.version`                  | 暴露 NODE_VERSION 的内置编译属性。                                                                                                                                               |
|                 `process.versions`                  | 暴露 node 及其依赖项版本字符串的属性。                                                                                                                                           |
|                  `process.abort()`                  | 导致 node 发出 abort。这将使 node 退出并生成 core 文件。                                                                                                                        |
|                `process.chdir(dir)`                 | 更改进程的当前工作目录，失败则抛出异常。                                                                                                                                         |
|                   `process.cwd()`                   | 返回进程的当前工作目录。                                                                                                                                                         |
|               `process.exit([code])`                | 以指定的代码结束进程。若省略，exit 使用 'success' 代码 0。                                                                                                                       |
|                 `process.getgid()`                  | 获取进程的组标识。                                                                                                                                                               |
|                `process.setgid(id)`                 | 设置进程的组标识。                                                                                                                                                               |
|                 `process.getuid()`                  | 获取进程的用户标识。                                                                                                                                                             |
|                `process.setuid(id)`                 | 设置进程的用户标识。                                                                                                                                                             |
|                `process.getgroups()`                | 返回包含补充组 ID 的数组。                                                                                                                                                       |
|              `process.setgroups(grps)`              | 设置补充组 ID。                                                                                                                                                                  |
|        `process.initgroups(user, extra_grp)`        | 读取 /etc/group 并使用用户所属的所有组初始化组访问列表。                                                                                                                        |
|            `process.kill(pid, [signal])`            | 向进程发送信号。pid 是进程 ID，signal 是描述要发送信号的字符串。                                                                                                                |
|               `process.memoryUsage()`               | 返回描述以字节计的 Node 进程内存使用情况的对象。                                                                                                                                |
|            `process.nextTick(callback)`             | 在事件循环的下一轮调用此回调。                                                                                                                                                   |
|               `process.maxTickDepth`                | 传给 process.nextTick 的回调通常会在当前执行流的末尾调用，因此速度大致与同步调用函数相当。                                                                                      |
|               `process.umask([mask])`               | 设置或读取进程的文件模式创建掩码。                                                                                                                                               |
|                 `process.uptime()`                  | Node 已运行的秒数。                                                                                                                                                              |
|                 `process.hrtime()`                  | 以 [seconds, nanoseconds] 元组数组形式返回当前高分辨率实时时间。                                                                                                                |

**[🔼Back to Top](#table-of-contents)**

<a id="child-process"></a>
## 子进程

|                            keyword                            | description                                                                                                                                                                                                         |
| :-----------------------------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|                        `ChildProcess`                         | 类。ChildProcess 是一个 EventEmitter。                                                                                                                                                                              |
|                         `child.stdin`                         | 表示子进程 stdin 的 Writable 流                                                                                                                                                                                     |
|                        `child.stdout`                         | 表示子进程 stdout 的 Readable 流                                                                                                                                                                                    |
|                        `child.stderr`                         | 表示子进程 stderr 的 Readable 流。                                                                                                                                                                                  |
|                          `child.pid`                          | 子进程的 PID                                                                                                                                                                                                        |
|                       `child.connected`                       | 如果 .connected 为 false，则无法再发送消息                                                                                                                                                                          |
|                    `child.kill([signal])`                     | 向子进程发送信号                                                                                                                                                                                                    |
|              `child.send(message, [sendHandle])`              | 使用 child_process.fork() 时，可以通过 child.send(message, [sendHandle]) 向子进程写入消息，消息由子进程上的 'message' 事件接收。                                                    |
|                     `child.disconnect()`                      | 关闭父进程与子进程之间的 IPC 通道，在没有其他连接维持时允许子进程优雅退出。                                                                                                        |
|       `child_process.spawn(command, [args], [options])`       | 使用给定命令启动新进程，命令行参数在 args 中。若省略，args 默认为空数组。                                                                                                          |
|      `child_process.exec(command, [options], callback)`       | 在 shell 中运行命令并缓冲输出。                                                                                                                                                                                     |
| `child_process.execFile(file, [args], [options], [callback])` | 在 shell 中运行命令并缓冲输出。                                                                                                                                                                                     |
|      `child_process.fork(modulePath, [args], [options])`      | 这是 spawn() 功能用于生成 Node 进程的特殊情况。除普通 ChildProcess 实例的所有方法外，返回的对象还内置了通信通道。                                                                  |

**[🔼Back to Top](#table-of-contents)**

<a id="util"></a>
## UTIL（工具）

|                    keyword                     | description                                                                                                                  |
| :--------------------------------------------: | ---------------------------------------------------------------------------------------------------------------------------- |
|          `util.format(format, [...])`          | 使用第一个参数作为类似 printf 的格式返回格式化字符串（%s、%d、%j）                                                          |
|              `util.debug(string)`              | 同步输出函数。会阻塞进程并立即将字符串输出到 stderr。                                                                        |
|              `util.error([...])`               | 与 util.debug() 相同，但会立即将所有参数输出到 stderr。                                                                      |
|               `util.puts([...])`               | 同步输出函数。会阻塞进程并将所有参数输出到 stdout，每个参数后换行。                                                          |
|              `util.print([...])`               | 同步输出函数。会阻塞进程，将每个参数转为字符串后输出到 stdout（不换行）。                                                    |
|               `util.log(string)`               | 在 stdout 上带时间戳输出。                                                                                                   |
|         `util.inspect(object, [opts])`         | 返回对象的字符串表示，便于调试（选项：showHidden、depth、colors、customInspect）。                                          |
|             `util.isArray(object)`             | 如果给定 "object" 是数组则返回 true，否则返回 false。                                                                        |
|            `util.isRegExp(object)`             | 如果给定 "object" 是正则表达式则返回 true，否则返回 false。                                                                  |
|             `util.isDate(object)`              | 如果给定 "object" 是日期则返回 true，否则返回 false。                                                                        |
|             `util.isError(object)`             | 如果给定 "object" 是错误则返回 true，否则返回 false。                                                                        |
|              `util.promisify(fn)`              | 接受一个最后参数为回调的函数，返回一个返回 Promise 的版本。                                                                  |
| `util.inherits(constructor, superConstructor)` | 将一个构造函数的原型方法继承到另一个构造函数中。                                                                             |

**[🔼Back to Top](#table-of-contents)**

<a id="events"></a>
## EVENTS（事件）

|                   keyword                    | description                                                                                                                        |
| :------------------------------------------: | ---------------------------------------------------------------------------------------------------------------------------------- |
|    `emitter.addListener(event, listener)`    | 将监听器添加到指定事件监听器数组的末尾。                                                                                           |
|        `emitter.on(event, listener)`         | 与 emitter.addListener() 相同。                                                                                                    |
|       `emitter.once(event, listener)`        | 为事件添加一次性监听器。该监听器仅在下次事件触发时调用，之后被移除。                                                               |
|  `emitter.removeListener(event, listener)`   | 从指定事件的监听器数组中移除一个监听器。                                                                                           |
|    `emitter.removeAllListeners([event])`     | 移除所有监听器，或指定事件的监听器。                                                                                               |
|         `emitter.setMaxListeners(n)`         | 默认情况下，如果为某个事件添加超过 10 个监听器，EventEmitter 会打印警告。                                                         |
|          `emitter.listeners(event)`          | 返回指定事件的监听器数组。                                                                                                         |
| `emitter.emit(event, [arg1], [arg2], [...])` | 按顺序执行各监听器，并传入提供的参数。如果事件有监听器则返回 true，否则返回 false。                                               |
| `EventEmitter.listenerCount(emitter, event)` | 返回给定事件的监听器数量。                                                                                                         |

**[🔼Back to Top](#table-of-contents)**

<a id="stream"></a>
## STREAM（流）

<a id="read"></a>
### 读取

|                   keyword                   | description                                                                                                                                                                                                                       |
| :-----------------------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `var readable = getReadableStreamSomehow()` |
|  `readable.on('readable', function() {})`   | 当可以从流中读取数据块时，它会触发 'readable' 事件。                                                                                                              |
|  `readable.on('data', function(chunk) {})`  | 如果附加了一个 data 事件监听器，流会切换到流动模式，数据一旦可用就会传给你的处理函数。                                                                            |
|     `readable.on('end', function() {})`     | 当没有更多数据可读时触发此事件。                                                                                                                                                                  |
|    `readable.on('close', function() {})`    | 底层资源（例如底层文件描述符）关闭时触发。并非所有流都会触发此事件。                                                                                                                              |
|    `readable.on('error', function() {})`    | 接收数据出错时触发。                                                                                                                                                                              |
|           `readable.read([size])`           | read() 方法从内部缓冲区取出一些数据并返回。如果没有可用数据，则返回 null。                                                                                                                       |
|      `readable.setEncoding(encoding)`       | 调用此函数让流返回指定编码的字符串，而不是 Buffer 对象。                                                                                                                                          |
|             `readable.resume()`             | 此方法使可读流恢复触发 data 事件。                                                                                                                                                                |
|             `readable.pause()`              | 此方法使处于流动模式的流停止触发 data 事件。                                                                                                                                                     |
|   `readable.pipe(destination, [options])`   | 此方法从可读流中取出所有数据并写入提供的目标，自动管理流以避免目标被快速的可读流淹没。                                                                            |
|      `readable.unpipe([destination])`       | 此方法移除之前 pipe() 调用设置的钩子。如果未指定目标，则移除所有管道。                                                                                                                            |
|          `readable.unshift(chunk)`          | 在流被解析器消费、需要"取消费"某些已乐观地从源中取出的数据以便将流传递给其他方时，这很有用。                                                                      |

**[🔼Back to Top](#table-of-contents)**

<a id="write"></a>
### 写入

|                     keyword                     | description                                                                                                                                        |
| :---------------------------------------------: | -------------------------------------------------------------------------------------------------------------------------------------------------- |
|    `var writer = getWritableStreamSomehow()`    | Writable 流接口是你写入数据的目标的抽象。                                                                                                          |
| `writable.write(chunk, [encoding], [callback])` | 此方法将一些数据写入底层系统，并在数据完全处理完毕后调用提供的回调。                                                                              |
|          `writer.once('drain', write)`          | 如果 writable.write(chunk) 调用返回 false，则 drain 事件会指示何时适合开始向流写入更多数据。                                                       |
| `writable.end([chunk], [encoding], [callback])` | 当不再向流写入数据时调用此方法。                                                                                                                  |
|      `writer.on('finish', function() {})`       | 当调用 end() 方法且所有数据都已刷新到底层系统时触发此事件。                                                                                      |
|      `writer.on('pipe', function(src) {})`      | 每当在可读流上调用 pipe() 方法、将此可写流加入其目标集合时触发。                                                                                  |
|     `writer.on('unpipe', function(src) {})`     | 每当在可读流上调用 unpipe() 方法、将此可写流从其目标集合中移除时触发。                                                                            |
|     `writer.on('error', function(src) {})`      | 写入或管道传输数据出错时触发。                                                                                                                    |

**[🔼Back to Top](#table-of-contents)**

<a id="file-system"></a>
## 文件系统

|                          keyword                           | description                                                                                                                                                                                                                                             |
| :--------------------------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|          `fs.rename(oldPath, newPath, callback)`           | 异步重命名。完成回调除可能的异常外不接收其他参数。异步 ftruncate。完成回调除可能的异常外不接收其他参数。                                                                                                               |
|             `fs.renameSync(oldPath, newPath)`              | 同步重命名。                                                                                                                                                                                                                                            |
|             `fs.ftruncate(fd, len, callback)`              | 异步 ftruncate。完成回调除可能的异常外不接收其他参数。                                                                                                                                                                  |
|                `fs.ftruncateSync(fd, len)`                 | 同步 ftruncate。                                                                                                                                                                                                                                        |
|             `fs.truncate(path, len, callback)`             | 异步 truncate。完成回调除可能的异常外不接收其他参数。                                                                                                                                                                   |
|                `fs.truncateSync(path, len)`                | 同步 truncate。                                                                                                                                                                                                                                        |
|            `fs.chown(path, uid, gid, callback)`            | 异步 chown。完成回调除可能的异常外不接收其他参数。                                                                                                                                                                      |
|               `fs.chownSync(path, uid, gid)`               | 同步 chown。                                                                                                                                                                                                                                           |
|            `fs.fchown(fd, uid, gid, callback)`             | 异步 fchown。完成回调除可能的异常外不接收其他参数。                                                                                                                                                                     |
|               `fs.fchownSync(fd, uid, gid)`                | 同步 fchown。                                                                                                                                                                                                                                          |
|           `fs.lchown(path, uid, gid, callback)`            | 异步 lchown。完成回调除可能的异常外不接收其他参数。                                                                                                                                                                     |
|              `fs.lchownSync(path, uid, gid)`               | 同步 lchown。                                                                                                                                                                                                                                          |
|              `fs.chmod(path, mode, callback)`              | 异步 chmod。完成回调除可能的异常外不接收其他参数。                                                                                                                                                                      |
|                 `fs.chmodSync(path, mode)`                 | 同步 chmod。                                                                                                                                                                                                                                           |
|              `fs.fchmod(fd, mode, callback)`              | 异步 fchmod。完成回调除可能的异常外不接收其他参数。                                                                                                                                                                     |
|                 `fs.fchmodSync(fd, mode)`                  | 同步 fchmod。                                                                                                                                                                                                                                          |
|             `fs.lchmod(path, mode, callback)`              | 异步 lchmod。完成回调除可能的异常外不接收其他参数。                                                                                                                                                                     |
|                `fs.lchmodSync(path, mode)`                 | 同步 lchmod。                                                                                                                                                                                                                                          |
|                 `fs.stat(path, callback)`                  | 异步 stat。回调接收两个参数 (err, stats)，其中 stats 是 fs.Stats 对象。                                                                                                  |
|                    `fs.statSync(path)`                     | 同步 stat。返回 fs.Stats 的实例。                                                                                                                                                                        |
|                 `fs.lstat(path, callback)`                 | 异步 lstat。回调接收两个参数 (err, stats)，其中 stats 是 fs.Stats 对象。lstat() 与 stat() 相同，但如果 path 是符号链接，则 stat 的是链接本身，而非其指向的文件。                          |
|                    `fs.lstatSync(path)`                    | 同步 lstat。返回 fs.Stats 的实例。                                                                                                                                                                      |
|                  `fs.fstat(fd, callback)`                  | 异步 fstat。回调接收两个参数 (err, stats)，其中 stats 是 fs.Stats 对象。fstat() 与 stat() 相同，但待 stat 的文件由文件描述符 fd 指定。                                           |
|                     `fs.fstatSync(fd)`                     | 同步 fstat。返回 fs.Stats 的实例。                                                                                                                                                                        |
|           `fs.link(srcpath, dstpath, callback)`            | 异步 link。完成回调除可能的异常外不接收其他参数。                                                                                                                                                         |
|              `fs.linkSync(srcpath, dstpath)`               | 同步 link。                                                                                                                                                                                                                                            |
|      `fs.symlink(srcpath, dstpath, [type], callback)`      | 异步 symlink。完成回调除可能的异常外不接收其他参数。type 参数可设为 'dir'、'file' 或 'junction'（默认 'file'），且仅在 Windows 上可用（其他平台忽略）。                              |
|         `fs.symlinkSync(srcpath, dstpath, [type])`         | 同步 symlink。                                                                                                                                                                                                                                         |
|               `fs.readlink(path, callback)`                | 异步 readlink。回调接收两个参数 (err, linkString)。                                                                                                                                                      |
|                  `fs.readlinkSync(path)`                   | 同步 readlink。返回符号链接的字符串值。                                                                                                                                                                  |
|                `fs.unlink(path, callback)`                 | 异步 unlink。完成回调除可能的异常外不接收其他参数。                                                                                                                                                      |
|                   `fs.unlinkSync(path)`                    | 同步 unlink。                                                                                                                                                                                                                                          |
|           `fs.realpath(path, [cache], callback)`           | 异步 realpath。回调接收两个参数 (err, resolvedPath)。                                                                                                                                                  |
|              `fs.realpathSync(path, [cache])`              | 同步 realpath。返回解析后的路径。                                                                                                                                                                   |
|                 `fs.rmdir(path, callback)`                 | 异步 rmdir。完成回调除可能的异常外不接收其他参数。                                                                                                                                                     |
|                    `fs.rmdirSync(path)`                    | 同步 rmdir。                                                                                                                                                                                                                                           |
|             `fs.mkdir(path, [mode], callback)`             | 异步 mkdir。完成回调除可能的异常外不接收其他参数。mode 默认为 0777。                                                                                                                       |
|                `fs.mkdirSync(path, [mode])`                | 同步 mkdir。                                                                                                                                                                                                                                           |
|                `fs.readdir(path, callback)`                | 异步 readdir。读取目录内容。回调接收两个参数 (err, files)，其中 files 是目录中文件名（不含 '.' 和 '..'）组成的数组。                                                       |
|                   `fs.readdirSync(path)`                   | 同步 readdir。返回不含 '.' 和 '..' 的文件名数组。                                                                                                                                          |
|                  `fs.close(fd, callback)`                  | 异步 close。完成回调除可能的异常外不接收其他参数。                                                                                                                                                     |
|                     `fs.closeSync(fd)`                     | 同步 close。                                                                                                                                                                                                                                           |
|          `fs.open(path, flags, [mode], callback)`          | 异步打开文件。                                                                                                                                                                         |
|             `fs.openSync(path, flags, [mode])`             | fs.open() 的同步版本。                                                                                                                                                                                 |
|         `fs.utimes(path, atime, mtime, callback)`          | 更改所提供的 path 所引用文件的时间戳。                                                                                                                                                              |
|            `fs.utimesSync(path, atime, mtime)`             | fs.utimes() 的同步版本。                                                                                                                                                                              |
|          `fs.futimes(fd, atime, mtime, callback)`          | 更改所提供的文件描述符所引用文件的时间戳。                                                                                                                                                          |
|             `fs.futimesSync(fd, atime, mtime)`             | fs.futimes() 的同步版本。                                                                                                                                                                            |
|                  `fs.fsync(fd, callback)`                  | 异步 fsync。完成回调除可能的异常外不接收其他参数。                                                                                                                                                     |
|                     `fs.fsyncSync(fd)`                     | 同步 fsync。                                                                                                                                                                                                                                           |
| `fs.write(fd, buffer, offset, length, position, callback)` | 将 buffer 写入 fd 指定的文件。                                                                                                                                                                      |
|    `fs.writeSync(fd, buffer, offset, length, position)`    | fs.write() 的同步版本。返回写入的字节数。                                                                                                                                                           |
| `fs.read(fd, buffer, offset, length, position, callback)`  | 从 fd 指定的文件读取数据。                                                                                                                                                                         |
|    `fs.readSync(fd, buffer, offset, length, position)`     | fs.read 的同步版本。返回读取的字节数。                                                                                                                                                              |
|        `fs.readFile(filename, [options], callback)`        | 异步读取文件的全部内容。                                                                                                                                                                     |
|           `fs.readFileSync(filename, [options])`           | fs.readFile 的同步版本。返回文件内容。如果指定了 encoding 选项，则返回字符串，否则返回 buffer。                                                                                  |
|    `fs.writeFile(filename, data, [options], callback)`     | 异步将数据写入文件，若文件已存在则替换。data 可以是字符串或 buffer。                                                                                                                |
|       `fs.writeFileSync(filename, data, [options])`        | fs.writeFile 的同步版本。                                                                                                                                                                       |
|    `fs.appendFile(filename, data, [options], callback)`    | 异步将数据追加到文件，若文件不存在则创建。data 可以是字符串或 buffer。                                                                                                             |
|       `fs.appendFileSync(filename, data, [options])`       | fs.appendFile 的同步版本。                                                                                                                                                                      |
|        `fs.watch(filename, [options], [listener])`         | 监视 filename 上的更改，filename 可以是文件或目录。返回的对象是 fs. FSWatcher。监听器回调接收两个参数 (event, filename)。event 为 'rename' 或 'change'，filename 是触发事件的文件名。  |
|                `fs.exists(path, callback)`                 | 通过文件系统检查给定路径是否存在。然后以 true 或 false 调用回调参数（不应使用）。                                                                                                  |
|                   `fs.existsSync(path)`                    | fs.exists 的同步版本（不应使用）。                                                                                                                                                              |
|           `fs.createReadStream(path, [options])`           | 返回一个新的 ReadStream 对象。                                                                                                                                                                |
|          `fs.createWriteStream(path, [options])`          | 返回一个新的 WriteStream 对象。                                                                                                                                                               |

**[🔼Back to Top](#table-of-contents)**

<a id="path"></a>
## 路径

|               keyword                | description                                                                                           |
| :----------------------------------: | ----------------------------------------------------------------------------------------------------- |
|         `path.normalize(p)`          | 规范化字符串路径，处理 '..' 和 '.' 部分。                                                             |
| `path.join([path1], [path2], [...])` | 将所有参数拼接在一起并规范化结果路径。                                                               |
|    `path.resolve([from ...], to)`    | 将 'to' 解析为绝对路径。                                                                              |
|      `path.relative(from, to)`       | 求解从 'from' 到 'to' 的相对路径。                                                                    |
|          `path.dirname(p)`           | 返回路径的目录名。类似 Unix 的 dirname 命令。                                                         |
|      `path.basename(p, [ext])`       | 返回路径的最后一部分。类似 Unix 的 basename 命令。                                                    |
|          `path.extname(p)`           | 返回路径的扩展名，即路径最后一部分中从最后一个 '.' 到字符串末尾的部分。                              |
|              `path.sep`              | 平台特定的文件分隔符，'\\' 或 '/'。                                                                    |
|           `path.delimiter`           | 平台特定的路径分隔符, '`                                                              | ' or ':'。 |

**[🔼Back to Top](#table-of-contents)**

<a id="http"></a>
## HTTP

|                            keyword                             | description                                                                                                                                                                                                                 |
| :------------------------------------------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|                      `http.STATUS_CODES`                       | 所有标准 HTTP 响应状态码及其简短描述的集合。                                                                                                                                                                               |
|              `http.request(options, [callback])`               | 此函数允许透明地发起请求。                                                                                                                                                                   |
|                `http.get(options, [callback])`                 | 将方法设为 GET 并自动调用 req.end()。                                                                                                                                                                                     |
|        `server = http.createServer([requestListener])`         | 返回一个新的 Web 服务器对象。requestListener 是一个自动添加到 'request' 事件的函数。                                                                                                     |
|    `server.listen(port, [hostname], [backlog], [callback])`    | 在指定端口和主机名上开始接受连接。                                                                                                                                                         |
|               `server.listen(path, [callback])`                | 启动监听给定路径上连接的 UNIX socket 服务器。                                                                                                                                             |
|              `server.listen(handle, [callback])`               | handle 对象可以是一个 server 或 socket（任何带有底层 _handle 成员的对象），或 {fd: <n>} 对象。                                                                                          |
|                   `server.close([callback])`                   | 停止服务器接受新连接。                                                                                                                                                                       |
|              `server.setTimeout(msecs, callback)`              | 设置 socket 的超时值，并在发生超时时在 Server 对象上触发 'timeout' 事件，将 socket 作为参数传入。                                                                                        |
|                    `server.maxHeadersCount`                    | 限制最大传入请求头数量，默认 1000。设为 0 则不限制。                                                                                                                                       |
|                        `server.timeout`                        | socket 被假定超时前的空闲毫秒数。                                                                                                                                                          |
|    `server.on('request', function (request, response) { })`    | 每次有请求时触发。                                                                                                                                                                         |
|        `server.on('connection', function (socket) { })`        | 当新的 TCP 流建立时。                                                                                                                                                                       |
|             `server.on('close', function () { })`              | 服务器关闭时触发。                                                                                                                                                                         |
| `server.on('checkContinue', function (request, response) { })` | 每次收到带有 http Expect: 100-continue 的请求时触发。                                                                                                                                     |
|  `server.on('connect', function (request, socket, head) { })`  | 每次客户端请求 http CONNECT 方法时触发。                                                                                                                                                   |
|  `server.on('upgrade', function (request, socket, head) { })`  | 每次客户端请求 http upgrade 时触发。                                                                                                                                                        |
|  `server.on('clientError', function (exception, socket) { })`  | 如果客户端连接触发 'error' 事件，会被转发到这里。                                                                                                                                           |
|               `request.write(chunk, [encoding])`               | 发送请求体的一部分。                                                                                                                                                                       |
|               `request.end([data], [encoding])`                | 完成请求发送。如果请求体有未发送部分，会将其刷新到流。                                                                                                                                     |
|                       `request.abort()`                        | 中止请求。                                                                                                                                                                                 |
|           `request.setTimeout(timeout, [callback])`            | 一旦 socket 分配给此请求并连接，就会调用 socket.setTimeout()。                                                                                                                            |
|                `request.setNoDelay([noDelay])`                 | 一旦 socket 分配给此请求并连接，就会调用 socket.setNoDelay()。                                                                                                                            |
|     `request.setSocketKeepAlive([enable], [initialDelay])`     | 一旦 socket 分配给此请求并连接，就会调用 socket.setKeepAlive()。                                                                                                                         |
|        `request.on('response', function(response) { })`        | 收到此请求的响应时触发。此事件仅触发一次。                                                                                                                                                 |
|          `request.on('socket', function(socket) { })`          | socket 分配给此请求后触发。                                                                                                                                                                |
| `request.on('connect', function(response, socket, head) { })`  | 每次服务器以 CONNECT 方法响应请求时触发。如果没有监听此事件，收到 CONNECT 方法的客户端连接将被关闭。                                                                                     |
| `request.on('upgrade', function(response, socket, head) { })`  | 每次服务器以 upgrade 响应请求时触发。如果没有监听此事件，收到 upgrade 头的客户端连接将被关闭。                                                                                          |
|            `request.on('continue', function() { })`            | 当服务器发送 '100 Continue' HTTP 响应时触发，通常因为请求包含 'Expect: 100-continue'。这是客户端应发送请求体的指示。                                                                   |
|              `response.write(chunk, [encoding])`               | 发送响应体的一部分。如果调用此方法但还未调用 response.writeHead()，会切换到隐式响应头模式并刷新隐式响应头。                                                                             |
|                   `response.writeContinue()`                   | 向客户端发送 HTTP/1.1 100 Continue 消息，表示应发送请求体。                                                                                                                              |
|  `response.writeHead(statusCode, [reasonPhrase], [headers])`   | 向请求发送响应头。                                                                                                                                                                         |
|             `response.setTimeout(msecs, callback)`             | 将 Socket 的超时值设为 msecs。如果提供回调，则作为监听器添加到 response 对象的 'timeout' 事件。                                                                                        |
|               `response.setHeader(name, value)`                | 为隐式响应头设置单个头值。如果该头已存在于待发送头中，其值会被替换。如需发送多个同名头，可在此使用字符串数组。                                                                         |
|                   `response.getHeader(name)`                   | 读取已排队但尚未发送给客户端的响应头。注意名称不区分大小写。                                                                                                                             |
|                 `response.removeHeader(name)`                  | 移除已排队等待隐式发送的头。                                                                                                                                                               |
|                `response.addTrailers(headers)`                 | 此方法向响应添加 HTTP 拖尾头（位于消息末尾的头）。                                                                                                                                        |
|               `response.end([data], [encoding])`               | 此方法向服务器表示所有响应头和响应体已发送，服务器应将此消息视为完成。response.end() 必须在每个响应上调用。                                                                             |
|                     `response.statusCode`                      | 使用隐式响应头（不显式调用 response.writeHead()）时，此属性控制刷新头时发送给客户端的状态码。                                                                                         |
|                     `response.headersSent`                     | 布尔值（只读）。如果头已发送则为 true，否则为 false。                                                                                                                                     |
|                      `response.sendDate`                       | 为 true 时，如果头中还没有 Date 头，会自动生成并在响应中发送。默认为 true。                                                                                                             |
|            `response.on('close', function () { })`             | 表示底层连接在 response.end() 被调用或刷新前已终止。                                                                                                                                     |
|            `response.on('finish', function() { })`             | 响应已发送时触发。                                                                                                                                                                         |
|                      `message.httpVersion`                      | 对于服务器请求，为客户端发送的 HTTP 版本；对于客户端响应，为所连接服务器的 HTTP 版本。                                                                                                 |
|                       `message.headers`                        | 请求/响应头对象。                                                                                                                                                                         |
|                       `message.trailers`                       | 请求/响应拖尾头对象。仅在 'end' 事件后填充。                                                                                                                                              |
|                        `message.method`                        | 请求方法（字符串）。只读。例如：'GET'、'DELETE'。                                                                                                                                         |
|                         `message.url`                          | 请求 URL 字符串。仅包含实际 HTTP 请求中出现的 URL。                                                                                                                                       |
|                      `message.statusCode`                      | 三位数的 HTTP 响应状态码，例如 404。                                                                                                                                                      |
|                        `message.socket`                        | 与连接关联的 net.Socket 对象。                                                                                                                                                            |
|             `message.setTimeout(msecs, callback)`              | 调用 message.connection.setTimeout(msecs, callback)。                                                                                                                                    |

**[🔼Back to Top](#table-of-contents)**

<a id="url"></a>
## URL

|                           keyword                            | description                                                                             |
| :----------------------------------------------------------: | --------------------------------------------------------------------------------------- |
| `url.parse(urlStr, [parseQueryString], [slashesDenoteHost])` | 接受 URL 字符串并返回对象。                                                            |
|                     `url.format(urlObj)`                     | 接受解析后的 URL 对象并返回格式化 URL 字符串。                                          |
|                   `url.resolve(from, to)`                    | 接受基准 URL 和 href URL，并像浏览器对锚点标签那样解析它们。                           |

**[🔼Back to Top](#table-of-contents)**

<a id="query-string"></a>
## 查询字符串

|                     keyword                      | description                                                                                                               |
| :----------------------------------------------: | ------------------------------------------------------------------------------------------------------------------------- |
|    `querystring.stringify(obj, [sep], [eq])`     | 将对象序列化为查询字符串。可选择性覆盖默认分隔符（'&'）和赋值符（'='）。                                                 |
| `querystring.parse(str, [sep], [eq], [options])` | 将查询字符串反序列化为对象。可选择性覆盖默认分隔符（'&'）和赋值符（'='）。                                               |

**[🔼Back to Top](#table-of-contents)**

<a id="assert"></a>
## 断言

|                       keyword                        | description                                                                                                                    |
| :--------------------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------ |
|  `assert.fail(actual, expected, message, operator)`  | 抛出异常，显示由提供的 operator 分隔的 actual 和 expected 值。                                                |
|               `assert(value, message)`               | assert.ok(value, [message])`                                                                                                   | 测试 value 是否为真值，等价于 assert.equal(true, !!value, message) |
|     `assert.equal(actual, expected, [message])`      | 使用相等比较运算符（==）测试浅层强制相等。                                                                                    |
|    `assert.notEqual(actual, expected, [message])`    | 使用不相等比较运算符（!=）测试浅层强制不相等。                                                                                |
|   `assert.deepEqual(actual, expected, [message])`    | 测试深度相等。                                                                                                               |
|  `assert.notDeepEqual(actual, expected, [message])`  | 测试任何深度不相等。                                                                                                         |
|  `assert.strictEqual(actual, expected, [message])`   | 测试严格相等，由严格相等运算符（===）决定。                                                                                  |
| `assert.notStrictEqual(actual, expected, [message])` | 测试严格不相等，由严格不相等运算符（!==）决定。                                                                              |
|      `assert.throws(block, [error], [message])`      | 期望 block 抛出错误。error 可以是构造函数、RegExp 或验证函数。                                                              |
|       `assert.doesNotThrow(block, [message])`        | 期望 block 不抛出错误，详见 assert.throws。                                                                                  |
|               `assert.ifError(value)`                | 测试 value 是否为非假值，若为真值则抛出。在测试回调中的第一个参数 error 时很有用。                                         |

**[🔼Back to Top](#table-of-contents)**

<a id="os"></a>
## 操作系统

|         keyword          | description                                                                                                                                                                                                                 |
| :----------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|      `os.tmpdir()`       | 返回操作系统的临时文件默认目录。                                                                                                                                                           |
|    `os.endianness()`     | 返回 CPU 的字节序。可能的值为 "BE" 或 "LE"。                                                                                                                                              |
|     `os.hostname()`      | 返回操作系统的主机名。                                                                                                                                                                     |
|       `os.type()`        | 返回操作系统名称。                                                                                                                                                                         |
|     `os.platform()`      | 返回操作系统平台。                                                                                                                                                                         |
|       `os.arch()`        | 返回操作系统 CPU 架构。                                                                                                                                                                    |
|      `os.release()`      | 返回操作系统发行版本。                                                                                                                                                                     |
|      `os.uptime()`       | 返回系统运行时间（秒）。                                                                                                                                                                   |
|      `os.loadavg()`      | 返回包含 1、5、15 分钟平均负载的数组。                                                                                                                                                     |
|     `os.totalmem()`      | 返回系统内存总量（字节）。                                                                                                                                                                 |
|      `os.freemem()`      | 返回系统空闲内存量（字节）。                                                                                                                                                               |
|       `os.cpus()`        | 返回包含每个已安装 CPU/核信息的对象数组：model、speed（MHz）、times（包含 CPU/核在 user、nice、sys、idle、irq 上花费毫秒数的对象）。                                                 |
| `os.networkInterfaces()` | 获取网络接口列表。                                                                                                                                                                         |
|         `os.EOL`         | 定义操作系统适当换行符的常量。                                                                                                                                                             |

**[🔼Back to Top](#table-of-contents)**

<a id="buffer"></a>
## 缓冲区

|                               keyword                               | description                                                                                                                                                                                                           |
| :-----------------------------------------------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|                         `Buffer.from(size)`                         | 分配大小为 size 个字节的新 buffer。                                                                                                                                                                                  |
|                        `Buffer.from(array)`                         | 使用字节数组分配新 buffer。                                                                                                                                                                                         |
|                   `Buffer.from(str, [encoding])`                    | 分配包含给定 str 的新 buffer。encoding 默认为 'utf8'。                                                                                                                                                              |
|                    `Buffer.isEncoding(encoding)`                    | 如果 encoding 是有效的编码参数则返回 true，否则返回 false。                                                                                                                                                         |
|                       `Buffer.isBuffer(obj)`                        | 测试 obj 是否为 Buffer                                                                                                                                                                                              |
|                `Buffer.concat(list, [totalLength])`                 | 返回将列表中所有 buffer 拼接在一起的结果 buffer。                                                                                                                                                                  |
|               `Buffer.byteLength(string, [encoding])`               | 返回字符串的实际字节长度。                                                                                                                                                                                          |
|         `buf.write(string, [offset], [length], [encoding])`         | 使用给定编码将 string 写入 buffer 的 offset 处                                                                                                                                                                     |
|             `buf.toString([encoding], [start], [end])`              | 从以 encoding 编码的 buffer 数据中解码并返回字符串，从 start（默认 0）开始，到 end（默认 buffer.length）结束（encoding 默认 'utf8'）。                                             |
|                           `buf.toJSON()`                            | 返回 Buffer 实例的 JSON 表示，与 JSON 数组的输出相同                                                                                                                                                               |
| `buf.copy(targetBuffer, [targetStart], [sourceStart], [sourceEnd])` | 在 buffer 之间复制。源区域和目标区域可以重叠                                                                                                                                                                       |
|                     `buf.slice([start], [end])`                     | 返回引用同一内存的新 buffer，但按 start（默认 0）和 end（默认 buffer.length）索引偏移和裁剪。负索引从 buffer 末尾开始。                                                                                            |
|                 `buf.fill(value, [offset], [end])`                  | 用指定的值填充 buffer                                                                                                                                                                                              |
|                            `buf[index]`                             | 获取和设置 index 处的字节                                                                                                                                                                                           |
|                            `buf.length`                             | buffer 的字节大小，注意这不一定是内容的大小                                                                                                                                                                       |
|                     `buffer.INSPECT_MAX_BYTES`                      | 调用 buffer.inspect() 时返回的字节数。可被用户模块覆盖。                                                                                                                                                           |

**[🔼Back to Top](#table-of-contents)**
