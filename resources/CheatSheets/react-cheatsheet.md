--- 
title: React 速查表
description: 这里列出了 React 最重要且最实用的方法。
created: 2022-10-30
---

<a id="table-of-contents"></a>
## 目录

- [React 面向开发者速查表](#react-cheatsheet-for-developers)
  - [创建 React 应用](#create-react-app)
  - [React 组件](#react-components)
  - [React 属性](#react-props)
  - [React 子属性](#react-children-props)
  - [React 条件渲染](#react-conditionals)
  - [React 上下文](#react-context)
  - [React useEffect 钩子](#react-useeffect-hooks)

<a id="react-cheatsheet-for-developers"></a>
# React 面向开发者速查表

<a id="create-react-app"></a>
## 创建 React 应用

> Create React App 是学习 React 的舒适环境，也是开始用 React 构建新的单页应用的最佳方式。

```
npx create-react-app my-app
cd my-app
npm start
```

**[🔼返回顶部](#table-of-contents)**

<a id="react-components"></a>
## React 组件

```js
function App() {
  return <div>Hello Developers</div>;
}

export default App;
```

**[🔼返回顶部](#table-of-contents)**

<a id="react-props"></a>
## React 属性

```js
function App() {
  return <User name="Developer" />
}

function User(props) {
  return <h1>Hello, {props.name}</h1>; // Hello, Developer!
}
```

**[🔼返回顶部](#table-of-contents)**

<a id="react-children-props"></a>
## React 子属性

```js
function App() {
  return (
   <User>
     <h1>Hello, Developer!</h1>
   </User>
  );
}

function User({ children }) {
  return children;
}
```

**[🔼返回顶部](#table-of-contents)**

<a id="react-conditionals"></a>
## React 条件渲染

```js
function App() {
  const isAuthUser = useAuth();

  if (isAuthUser) {
    // if our user is authenticated, let them use the app
    return <AuthApp />;
  }

  // if user is not authenticated, show a different screen
  return <UnAuthApp />;
}
```

**[🔼返回顶部](#table-of-contents)**

<a id="react-context"></a>
## React 上下文

> React 上下文允许我们在不使用 props 的情况下，将数据传递给组件树。

```js
function App() {
  return (
    <Body name="Developer" />
  );
}

function Body({ name }) {
  return (
    <Greeting name={name} />
  );
}

function Greeting({ name }) {
  return <h1>Welcome, {name}</h1>;
}
```

**[🔼返回顶部](#table-of-contents)**

<a id="react-useeffect-hooks"></a>
## React useEffect 钩子

```js
import { useEffect } from 'react';

function MyComponent() {
   useEffect(() => {
     // perform side effect here
   }, []);
}
```

**[🔼返回顶部](#table-of-contents)**
