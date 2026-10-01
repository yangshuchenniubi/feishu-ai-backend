# feishu-ai-backend

一个用于读取飞书多维表格、整理工作记录并发送飞书通知的 Python 小项目。

目前表格读写、人员查询、消息发送和完整工作流已经可以运行。项目支持 `mock` 和 `live` 两种模型模式，真实模型接口已经完成连通与完整流程测试；密钥只保存在本地 `.env` 中。

## 功能

- 获取飞书应用凭证
- 读取、新增和修改多维表格记录
- 分页读取、条件筛选和批量处理
- 按人员和日期去重
- 统计人数、人次和提交记录
- 查询飞书用户信息
- 发送飞书消息和状态通知
- 生成 LLM 输入和 JSON 输出结构
- 使用 mock 模式测试完整流程

## 环境

- Python 3.10+
- 飞书企业自建应用
- 一个用于测试的飞书多维表格

安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 配置

复制配置模板：

```powershell
Copy-Item .env.example .env
```

然后在本机填写 `.env`。不要把真实 `.env` 提交到仓库。

主要配置项：

```text
FEISHU_APP_ID=
FEISHU_APP_SECRET=
FEISHU_APP_TOKEN=
FEISHU_TABLE_ID=
FEISHU_USER_EMAIL=
FEISHU_RECEIVER_OPEN_ID=

LLM_MODE=mock
LLM_API_URL=
LLM_API_KEY=
LLM_MODEL=
```

邮箱和手机号只需要填写一种。如果使用手机号，需要带国家代码。

## 飞书权限

测试时用到的权限：

- 查看、评论、编辑和管理多维表格
- `contact:user.id:readonly`
- `contact:contact.base:readonly`
- `im:message`

通讯录相关权限要使用应用身份。修改权限后需要重新发布应用版本。

## 运行

运行完整流程：

```powershell
.\.venv\Scripts\python.exe .\run_workflow.py
```

运行本地检查：

```powershell
.\.venv\Scripts\python.exe .\self_check.py
```

按条件查询记录：

```powershell
.\.venv\Scripts\python.exe .\query_records.py --department "技术部" --status "已交"
```

## 流程

```text
飞书多维表格
  -> 分页读取
  -> 过滤和去重
  -> 生成统计材料
  -> LLM 或 mock 分析
  -> 校验 JSON
  -> 发送飞书通知
```

没有 API Key 或只做本地联调时保持：

```text
LLM_MODE=mock
```

需要调用真实模型时改为 `live`，并在本地填写接口地址、API Key 和模型名称。当前的 `llm_client.py` 按 OpenAI 兼容格式发送请求，接入其他格式的模型时需要调整请求体和响应解析。

## 主要文件

| 文件 | 作用 |
| --- | --- |
| `read_all_records.py` | 分页读取表格记录 |
| `query_records.py` | 条件查询 |
| `build_summary.py` | 去重和统计 |
| `llm_client.py` | mock/live 模式切换 |
| `send_message.py` | 发送飞书消息 |
| `notification_service.py` | 统一通知 |
| `run_workflow.py` | 串联完整流程 |
| `self_check.py` | 检查配置和输出文件 |

## 说明

- mock 结果只用于开发和联调，不能当作真实分析结论。
- 没有完整人员名单时，不能把“没有日志”直接判断为“未提交”。
- `.env`、访问 Token、手机号、邮箱和真实用户数据不要提交到公开仓库。
