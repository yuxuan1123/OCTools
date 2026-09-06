---
title: Angular 速查表
description: Angular 速查表包含 Angular 绑定与 Angular CLI 的基础知识。
created: 2022-10-24
---

## 目录

- #面向开发者的-angular-速查表
  - #什么是-angular
  - #angular-绑定
  - #angular-生命周期钩子
  - #angular-cli-命令

# 面向开发者的 Angular 速查表

## 什么是 Angular？

> Angular 是一个应用设计框架和开发平台，用于创建高效且复杂的单页应用。

**#目录**

## Angular 绑定：

| 描述 | 命令 |
| ------- | ----------- |
| `单向绑定` | `<p>title</p>` <br /> - 对变量的更改不会反映回变量本身。 |
| `双向绑定` | `<input [(ngMo­del­)]=­"­student.F­ir­stN­ame­">` <br /> - 对变量的更改会反映回变量本身。 |
| `属性绑定` | `<img [src]=­"­student.profilePicUrl">` |
| `属性绑定（Attribute）` | `<button [attr.a­ri­a-l­abe­l]=­"­ok">­Ok<­/bu­tto­n>` |
| `类绑定` | `<div [class.Focused]="isFocused">S­ele­cte­d</­div>` |
| `ngClass` | `<div [ngClass]="assignClasses()"> <h1>{{student.FirstName}}</h1> </div>` |
| `样式绑定` | `<p [style.co­lor­]="i­sSe­lected ? 'green' : 'red'">Option {{i}}</p>` |
| `ngStyle` | `<div [ngStyle]="setStyles()"> {{student.name}} </div>` |
| `组件绑定` | `<student-details [student]="currStudent"></student-details>` |
| `指令绑定` | `<div [ngClass] = "­{se­lected: isSele­cte­d}">­Student<­/di­v>` |
| `事件绑定` | `<button (click­)="test()">­Test</­but­ton>` |
| `$event` | `<input [value]="student.name" (input)="student.name=$event.target.value">` |

**#目录**

## Angular 生命周期钩子：

| 命令 | 描述 |
| ------- | ----------- |
| `ngOnInit()` | 当 Angular 初始化组件或指令时调用。 |
| `ngOnChanges()` | 当 Angular 设置数据绑定的输入属性（即 @Input()）时调用。 |
| `ngDoCheck()` | 每次变更检测时调用。 |
| `ngAfterContentInit()` | 当 Angular 将外部内容投影到视图后调用。 |
| `ngAfterContentChecked()` | 当 Angular 检查完投影内容的绑定后调用。 |
| `ngAfterViewInit()` | 当 Angular 创建完组件视图后调用。 |
| `ngAfterViewChecked()` | 当 Angular 检查完组件视图的绑定后调用。 |
| `ngOnDestroy()` | 当 Angular 销毁组件或指令之前调用。 |

**#目录**

## Angular CLI 命令：

| 命令 | 描述 |
| ------- | ----------- |
| `ng new project-name` | 创建一个***新项目*** |
| `ng g component <name>` | 生成一个***组件*** |
| `ng g directive <name>` | 生成***指令*** |
| `ng g pipe <name>` | 生成***管道*** |
| `ng g service <name>` | 生成***服务*** |
| `ng g class <name>` | 生成***类*** |
| `ng g interface <name>` | 生成***接口*** |
| `ng serve` | 在本地服务器上***运行应用程序*** |
| `ng build [--e=<name>]` | 构建并切换环境 |
| `ng test` &#124; `e2e` | ***测试***你的应用程序 |

| 命令 | 描述 |
| ------- | ----------- |
| `ng generate universal [options]` <br /> 或 <br /> `ng g universal [options]` | - ***universal 命令*** <br /> - 此命令用于将该示意图传递给 `run` 命令，以便为应用设置服务器端渲染 |
| `--defaults=true` &#124; `false:` | - ***以及 [options]*** <br /> - 当为 true 时，禁用带有默认值的选项的交互式输入提示。 |
| `--dryRun=true` &#124; `false:` | - ***以及 [options]*** <br /> - 当为 true 时，模拟运行并报告活动，但不写出结果。|

**#目录**