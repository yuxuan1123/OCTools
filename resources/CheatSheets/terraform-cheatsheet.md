---
title: Terraform 速查表
description: 此处列出了最常用的 Terraform 命令。
created: 2022-10-27
---

<a id="table-of-contents"></a>
## 目录

- [面向开发者的 Terraform 速查表](#terraform-cheatsheet-for-developers)
  - [格式化与校验 Terraform 代码](#format-and-validate-terraform-code)
  - [初始化 Terraform 工作目录](#initialize-your-terraform-working-directory)
  - [计划、部署与清理基础设施](#plan-deploy-and-cleanup-infrastructure)
  - [Terraform 工作区](#terraform-workspace)
  - [Terraform 状态操作](#terraform-state-manipulation)
  - [Terraform 导入与输出](#terraform-import-and-outputs)
  - [Terraform 杂项命令](#terraform-miscelleneous-commands)

<a id="terraform-cheatsheet-for-developers"></a>
# Terraform CheatSheet for Developers

<a id="format-and-validate-terraform-code"></a>
## Format and Validate Terraform code

| Command                               | Description                              |
| :-----------------------------------: | ---------------------------------------- |
| `terraform fmt`                       | 按照 HCL 规范标准格式化代码   |
| `terraform validate`                  | 校验代码的语法                 |
| `terraform validate -backend=false`   | 校验代码时跳过后端                 |

**[🔼Back to Top](#table-of-contents)**

<a id="initialize-your-terraform-working-directory"></a>
## Initialize your Terraform working directory

| Command                                   | Description                                                           |
| :---------------------------------------: | --------------------------------------------------------------------- |
| `terraform init`                          | 初始化目录，拉取 provider                             |
| `terraform init -get-plugins=false`       | 初始化目录，但不下载插件                         |
| `terraform init -verify-plugins=false`    | 初始化目录，但不校验插件的 Hashicorp 签名   |

**[🔼Back to Top](#table-of-contents)**

<a id="plan-deploy-and-cleanup-infrastructure"></a>
## Plan, Deploy and Cleanup Infrastructure

| Command                                              | Description                                                                                      |
| :--------------------------------------------------: | ------------------------------------------------------------------------------------------------ |
| `terraform apply --auto-approve`                     | 应用变更，无需提示输入 "yes"                                              |
| `terraform destroy --auto-approve`                   | 销毁/清理部署，无需提示输入 "yes"                                      |
| `terraform plan -out plan.out`                       | 将部署计划输出到 plan.out                                                           |
| `terraform apply plan.out`                           | 使用 plan.out 计划文件部署基础设施                                              |
| `terraform plan -destroy`                            | 输出销毁计划                                                                           |
| `terraform apply -target=aws_instance.my_ec2`        | 仅对目标资源应用/部署变更                                               |
| `terraform apply -var my_region_variable=us-east-1 ` | 在应用配置时通过命令行传递变量                                  |
| `terraform apply -lock=true`                         | 锁定状态文件，使其无法被任何其他 Terraform apply 或修改操作改动  |
| `terraform apply refresh=false`                      | 不与真实资源协调状态文件                                            |
| `terraform apply --parallelism=5`                    | 并发资源操作的数量                                                       |
| `terraform refresh`                                  | 将 Terraform 状态文件中的状态与真实资源协调                            |
| `terraform providers`                                | 获取当前配置中所用 provider 的信息                                    |

**[🔼Back to Top](#table-of-contents)**

<a id="terraform-workspace"></a>
## Terraform Workspace

| Command                                   | Description                           |
| :---------------------------------------: | ------------------------------------- |
| `terraform workspace new mynewworkspace`  | 创建新工作区                |
| `terraform workspace select default`      | 切换到所选工作区      |
| `terraform workspace list`                | 列出所有工作区               |

**[🔼Back to Top](#table-of-contents)**

<a id="terraform-state-manipulation"></a>
## Terraform State Manipulation

| Command                                                                   | Description                                                         |
| :-----------------------------------------------------------------------: | ------------------------------------------------------------------- |
| `terraform state show aws_instance.my_ec2`                                | 显示 Terraform 状态中该资源的详细信息             |
| `terraform state pull > terraform.tfstate`                                | 下载并将 terraform 状态输出到文件                       |
| `terraform state mv aws_iam_role.my_ssm_role module.custom_module`        | 将状态跟踪的资源移动到不同模块               |
| `terraform state replace-provider hashicorp/aws registry.custom.com/aws`  | 用另一个 provider 替换现有 provider                           |
| `terraform state list`                                                    | 列出当前状态文件跟踪的所有资源       |
| `terraform state rm  aws_instance.myinstace`                              | 取消管理某个资源，将其从 Terraform 状态文件中删除            |

**[🔼Back to Top](#table-of-contents)**

<a id="terraform-import-and-outputs"></a>
## Terraform Import And Outputs

| Command                                                      | Description                               |
| :----------------------------------------------------------: | ----------------------------------------- |
| `terraform import aws_instance.new_ec2_instance i-abcd1234`  | 将 id 为 i-abcd1234 的 EC2 实例导入到名为 "new_ec2_instance"、类型为 "aws_instance" 的 Terraform 资源中 |
| `terraform output`                                           | 列出代码中声明的所有输出         |
| `terraform output instance_public_ip`                        | 列出某个特定声明的输出               |
| `terraform output -json`                                     | 以 JSON 格式列出所有输出            |

**[🔼Back to Top](#table-of-contents)**

<a id="terraform-miscelleneous-commands"></a>
## Terraform Miscelleneous commands

| Command                                   | Description                                                              |
| :---------------------------------------: | ------------------------------------------------------------------------ |
| `terraform version`                       | 显示 Terraform 二进制版本，版本过旧时会给出警告           |
| `terraform get -update=true`              | 下载并更新 "root" 模块中的模块。                        |

**[🔼Back to Top](#table-of-contents)**
