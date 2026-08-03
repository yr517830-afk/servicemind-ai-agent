# ServiceMind API 文档

ServiceMind 是一个基于 FastAPI、SQLAlchemy 和 PostgreSQL 的智能客服工单 API。

## 启动服务

复制环境变量示例：

```powershell
Copy-Item .env.example .env
```

构建并启动数据库与 API：

```powershell
docker compose up --build -d
```

检查容器：

```powershell
docker compose ps
```

停止服务：

```powershell
docker compose down
```

## 服务地址

- API 基础地址：`http://127.0.0.1:8000`
- Swagger UI：`http://127.0.0.1:8000/docs`
- OpenAPI JSON：`http://127.0.0.1:8000/openapi.json`
- 健康检查：`http://127.0.0.1:8000/health`
- LLM 配置健康检查：`http://127.0.0.1:8000/health/llm`

## 接口列表

| 方法 | 路径 | 功能 | 成功状态码 |
|---|---|---|---:|
| GET | `/health` | 服务健康检查 | 200 |
| GET | `/health/llm` | 检查 LLM 客户端配置状态 | 200 |
| POST | `/tickets` | 创建工单并执行路由规则 | 201 |
| GET | `/tickets` | 分页及组合筛选工单 | 200 |
| GET | `/tickets/{ticket_id}` | 查询工单详情 | 200 |
| PATCH | `/tickets/{ticket_id}` | 部分更新工单并重新计算规则 | 200 |
| GET | `/customers/{customer_id}` | 查询客户详情 | 200 |
| GET | `/orders/{order_id}` | 查询订单详情 | 200 |

## LLM 配置健康检查

```http
GET /health/llm
```

无 API Key 时：

```json
{
  "status": "not_configured",
  "configured": false,
  "model": "gpt-5.6-sol",
  "timeout_seconds": 20.0,
  "max_retries": 1
}
```

该接口只检查本地配置，不会向模型服务发送请求，不会消耗 Token，也不会返回 API Key。

LLM 配置通过以下环境变量提供：

```dotenv
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6-sol
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TIMEOUT_SECONDS=20
OPENAI_MAX_RETRIES=1
```

真实 API Key 只能写入本地 `.env`，不能提交到 Git。

## 创建工单

请求：

```http
POST /tickets
Content-Type: application/json
```

```json
{
  "customer_id": 1,
  "order_id": 1,
  "issue_type": "物流",
  "message": "我的订单什么时候送到？",
  "wait_minutes": 15
}
```

PowerShell 示例：

```powershell
$body = @{
    customer_id = 1
    order_id = 1
    issue_type = "物流"
    message = "我的订单什么时候送到？"
    wait_minutes = 15
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/tickets" `
    -ContentType "application/json; charset=utf-8" `
    -Body ([Text.Encoding]::UTF8.GetBytes($body))
```

创建成功后，系统会自动计算：

- 工单优先级
- 负责团队
- SLA 时限
- 路由原因

## 分页查询工单

```http
GET /tickets?page=1&page_size=20
```

支持的查询参数：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---:|---|
| `page` | integer | 1 | 页码，最小为 1 |
| `page_size` | integer | 20 | 每页数量，范围为 1～100 |
| `status` | string | 空 | `received`、`processing`、`resolved`、`closed` |
| `priority` | string | 空 | `P0`、`P1`、`P2`、`P3` |
| `issue_type` | string | 空 | 按问题类型筛选 |

组合筛选示例：

```http
GET /tickets?page=1&page_size=10&status=processing&priority=P1&issue_type=物流
```

## 查询工单

```http
GET /tickets/1
```

## 更新工单

请求：

```http
PATCH /tickets/1
Content-Type: application/json
```

```json
{
  "wait_minutes": 180,
  "status": "processing"
}
```

修改等待时间后，系统会重新执行路由规则并更新优先级、团队、SLA 和原因。

## 查询客户

```http
GET /customers/1
```

## 查询订单

```http
GET /orders/1
```

## 统一资源错误

当客户、订单或工单不存在时返回 HTTP 404：

```json
{
  "error": {
    "code": "TICKET_NOT_FOUND",
    "message": "工单 999 不存在。",
    "resource": "ticket",
    "resource_id": 999
  }
}
```

常见错误码：

| 状态码 | 错误码或场景 | 说明 |
|---:|---|---|
| 400 | 非法业务请求 | 空 PATCH、订单不属于客户等 |
| 404 | `CUSTOMER_NOT_FOUND` | 客户不存在 |
| 404 | `ORDER_NOT_FOUND` | 订单不存在 |
| 404 | `TICKET_NOT_FOUND` | 工单不存在 |
| 422 | 请求参数校验失败 | 字段缺失、范围或枚举错误 |

## 自动化验证

```powershell
python -m pytest -q
ruff check .
python -m pip check
```

当前验收结果：

```text
35 passed
All checks passed!
No broken requirements found.
```
