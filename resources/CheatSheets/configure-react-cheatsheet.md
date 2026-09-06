---
title: 配置 React 速查表
description: 帮助你以行业标准更快配置 React 应用的包。
created: 2022-10-30
---

<a id="table-of-contents"></a>
## 目录

- [配置 React 面向开发者速查表](#configure-react-cheatsheet-for-developers)
  - [创建 React 集群应用](#create-react-cluster-app)
  - [更快配置 React 应用的命令](#react-commands-to-configure-react-app-faster)

<a id="configure-react-cheatsheet-for-developers"></a>
# 配置 React 面向开发者速查表

<a id="create-react-cluster-app"></a>
## 创建 React 集群应用

> 使用 `Configure-React` 包，可以在一秒内创建 `一个项目中的多个 react 应用`。有关该包的更多信息，请访问 [Configure-React](https://www.npmjs.com/package/configure-react)，并在 [Youtube](https://www.youtube.com/watch?v=2MO1_mCXuds&t=3s) 上观看视频。

| Command | Description |
| :-------: | ----------- |
| `npx configure-react create-cluster <clustername>` | 创建包含 Tailwind、React Router Dom、Chakra UI、Context API、Redux、Redux Thunk、Redux Saga、Redux Persist、Utils、Axios 的大型 React 项目 |
| `npx configure-react cluster-app <projectname>` | 创建包含 Tailwind、React Router Dom、Chakra UI、Context API、Redux、Redux Thunk、Redux Saga、Redux Persist、Utils、Axios 的集群应用 |
| `npx configure-react ic <package-name>` | 在集群应用中安装包 |
| `npx configure-react help` | 显示命令帮助信息 |

**[🔼返回顶部](#table-of-contents)**

<a id="react-commands-to-configure-react-app-faster"></a>
## 更快配置 React 应用的命令

___(专为初学者)___

| Command | Description |
| :-------: | ----------- |
| `npx configure-react axios . ` | 安装 axios 并创建名为 `api` 的文件夹，以及名为 `axios.js`、`login.js`、`register.js`、`post.js`、`getdata.js` 的文件 |
| `npx configure-react react-redux-app <projectname>` | 安装 react-redux 并创建名为 `redux` 的文件夹，以及名为 `store.js`、`actions.js`、`reducers.js`、`types.js` 的文件 |
| `npx configure-react tailwind . ` | 为现有 React 应用配置 Tailwind，以便使用 Tailwind 类 |
| `npx configure-react browser-router . ` | 为现有 React 应用配置 React Router Dom，以便使用 React Router Dom，同时创建名为 `routes` 的文件夹，并创建名为 `index.js` 和 `AppRouter.js` 的文件，并修改 `App.js` 文件和 index.js 文件 |
| `npx configure-react chakra-ui . ` | 为现有 React 应用配置 Chakra UI，以便使用 Chakra UI，同时修改 `index.js` 文件以用 ChakraProvider 包裹 App |
| `npx configure-react context-api . ` | 为现有 React 应用配置 Context API，以便使用 Context API，同时创建名为 `context` 的文件夹，并创建名为 `context.js` 和 `reducer.js` 的文件，并修改 `App.js` 文件 |
| `npx configure-react redux . ` | 为现有 React 应用配置 Redux，以便使用 Redux，同时创建名为 `redux` 的文件夹，并创建名为 `store.js`、`actions.js`、`reducers.js`、`types.js` 的文件 |
| `npx configure-react utils . ` | 为现有 React 应用配置 Utils，以便使用 Utils，同时创建名为 `utils` 的文件夹，并创建名为 `utils.js` 的文件 |
| `npx configure-react redux-thunk . ` | 为现有 React 应用配置 Redux Thunk，以便使用 Redux Thunk，同时创建名为 `redux` 的文件夹，并创建名为 `store.js`、`actions.js`、`reducers.js`、`types.js` 的文件 |
| `npx configure-react redux-saga . ` | 为现有 React 应用配置 Redux Saga，以便使用 Redux Saga，同时创建名为 `redux` 的文件夹，并创建名为 `store.js`、`actions.js`、`reducers.js`、`types.js` 的文件 |
| `npx configure-react redux-persist . ` | 为现有 React 应用配置 Redux Persist，以便使用 Redux Persist，同时创建名为 `redux` 的文件夹，并创建名为 `store.js`、`actions.js`、`reducers.js`、`types.js` 的文件 |
| `npx configure-react refresh . ` | 刷新文件并在包有改动时更新文件 |
| `npx configure-react help` | 显示命令帮助信息 |

**[🔼返回顶部](#table-of-contents)**
