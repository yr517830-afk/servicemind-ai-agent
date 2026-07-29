# ServiceMind AI Agent

ServiceMind 是一个使用 Python 和 FastAPI 开发的智能客服工单系统。
项目支持客户输入校验、工单优先级判断、处理团队分配、SLA 计算、CLI 操作和 HTTP API。目前保留 SQLite 作为第一阶段 CLI 数据库，同时使用 Docker、PostgreSQL 和 SQLAlchemy 支撑 FastAPI 工单 CRUD。
当前 FastAPI 已通过 Service 和 Repository 正式连接 PostgreSQL，支持工单创建、查询、部分更新、分页和组合筛选，以及客户与订单详情查询；创建与关键字段更新会自动调用第一周规则引擎，所有资源不存在错误使用统一 404 响应。

## 当前学习进度

### Day 1：Python 与 Git 基础

- 创建 Python 虚拟环境
- 配置 Git 仓库和 `.gitignore`
- 完成 10 个 Python 基础函数
- 使用 `assert` 验证函数结果
- 使用 Ruff 检查代码质量

### Day 2：数据模型与输入校验

- 使用 `Enum` 定义问题类型和工单优先级
- 使用 `dataclass` 定义 `TicketInput`、`CustomerProfile` 和 `TicketDecision`
- 创建自定义异常
- 校验客户名称、问题类型和等待时间
- 完成 8 条工单规则测试

### Day 3：工单规则引擎

- 实现 `decide_ticket()` 工单决策函数
- 根据问题类型、客户等级和等待时间判断工单
- 自动生成工单优先级、处理团队、SLA 和判断原因
- 完成 12 条规则测试

当前规则顺序：

1. 账号或支付问题：P0
2. 等待时间超时：P1
3. VIP 客户：P1
4. 退款问题：P2
5. 普通咨询：P3

### Day 4：配置、日志与数据持久化

- 将路由规则迁移到 `routing_rules.json`
- 使用 `pathlib` 定位配置文件
- 使用 `json.load()` 读取 JSON
- 修改配置即可调整团队、优先级和 SLA
- 使用 `logging` 记录程序运行过程
- 使用 SQLite 保存和查询工单
- 使用 Ruff 清理无用导入和重复导入

### Day 5：CLI 与异常路径

- 创建 `ticket_cli.py` 命令行操作入口
- 实现工单录入、规则判断和结果预览
- 支持确认保存和取消保存
- 支持查询最近的历史工单
- 处理空输入、错误枚举、非法数字和错误菜单选项
- 使用 `ticket_exists()` 拦截重复工单
- 完成“录入 → 判断 → 保存 → 查询”完整业务流程

### Day 6：pytest 测试与重构

- 使用 pytest 建立自动化测试体系
- 使用 fixture 复用普通客户、VIP 客户和工单工厂
- 使用 parametrize 批量生成测试场景
- 完成 7 个输入校验测试
- 完成 8 个规则引擎测试
- 覆盖正常路径、异常路径、边界值和规则优先级
- 全部 15 个测试通过
- Ruff 全项目检查通过

### Day 7：第一周复盘与交付验证

- 完善项目README和安装说明
- 创建`requirements.txt`锁定开发依赖版本
- 从GitHub重新克隆项目进行独立验证
- 在全新虚拟环境中成功安装依赖
- 全部15个pytest测试通过
- Ruff全项目检查通过
- CLI在全新环境中正常运行
- 总结本周3个主要问题和3个设计取舍
- 项目达到“其他用户按照README可以运行”的验收标准

### Day 8：FastAPI起步与请求校验

- 安装FastAPI、Uvicorn、Pydantic和httpx2
- 创建`app/main.py`和`app/schemas.py`
- 实现`GET /health`健康检查接口
- 实现`POST /tickets`工单创建接口
- 定义`TicketCreate`请求模型
- 定义`TicketResponse`响应模型
- 使用Pydantic校验字符串、枚举和数值范围
- 使用Swagger UI在`/docs`调用接口
- 非法请求能够返回清晰的422错误
- 新增3个FastAPI自动化测试
- 全项目18个pytest测试通过
- Ruff全项目检查通过

### Day 9：分层结构与环境配置

- 使用 `pydantic-settings` 建立统一配置系统
- 使用 `.env` 保存本地环境配置
- 提供 `.env.example` 作为安全的配置模板
- 将 `.env` 加入 `.gitignore`，避免敏感配置上传
- 将 FastAPI 项目拆分为 API、Schema、Service、Repository 和 Core 层
- 将健康检查和工单接口迁移到独立路由模块
- 将请求和响应模型迁移到 Schema 层
- 将工单处理逻辑迁移到 Service 层
- 使用 Repository 层统一封装数据库访问
- FastAPI 应用名称、版本和调试状态由环境配置提供
- 新增 2 个配置自动化测试
- 全项目 20 个 pytest 测试通过
- Ruff 全项目检查通过

Day 9 阶段的真实调用结构：

```text
POST /tickets
    ↓
API 路由层
    ↓
Service 业务层
    ↓
返回临时响应

Repository 数据访问层
    ↓
SQLite 数据库
```

说明：Repository 封装已经建立，但当时尚未接入 FastAPI 工单创建流程。

### Day 10：PostgreSQL 与 SQLAlchemy ORM

- 安装并配置 Docker Desktop 和 WSL 2
- 使用 `compose.yaml` 启动 PostgreSQL 17
- 使用 Docker 命名卷持久化数据库数据
- 使用 `.env` 管理数据库名称、用户、密码和连接 URL
- 安装 SQLAlchemy 2.0.51 和 psycopg 3.3.4
- 创建统一的 `Base`、`engine` 和 `SessionLocal`
- 创建 `Customer`、`Order` 和 `Ticket` ORM 模型
- 建立客户与订单、客户与工单、订单与工单的外键关系
- 使用 `Numeric` 和 `Decimal` 精确保存订单金额
- 使用 ORM 插入可重复执行的种子数据
- 使用 `selectinload()` 和 `joinedload()` 查询关联实体
- 新增 2 个 ORM metadata 自动化测试
- 全项目 22 个 pytest 测试通过
- Ruff 全项目检查通过
- PostgreSQL 容器健康检查通过

Day 10 阶段的数据链路：

```text
CLI 工单流程
    ↓
ticket_core
    ↓
SQLite

ORM 验证脚本
    ↓
SQLAlchemy Session
    ↓
PostgreSQL 17

FastAPI
    ↓
API 路由
    ↓
Service
    ↓
当前返回临时响应
    ↓
Day 11 接入 PostgreSQL CRUD
```

### Day 11：工单 CRUD 与规则引擎集成

- 将 FastAPI Service 和 Repository 正式切换到 SQLAlchemy Session
- 实现 `POST /tickets` 创建并持久化工单
- 实现 `GET /tickets/{ticket_id}` 查询单张工单
- 实现 `GET /tickets` 分页查询
- 支持按状态、优先级和问题类型组合筛选
- 实现 `PATCH /tickets/{ticket_id}` 部分更新
- 创建工单时从 PostgreSQL 读取真实客户和订单
- 验证订单必须属于指定客户
- 创建与关键字段更新时自动调用第一周规则引擎
- 将资源不存在转换为 HTTP 404
- 将空更新等业务错误转换为 HTTP 400
- 使用独立 SQLite 内存数据库完成 API 自动化测试
- API 测试不会污染本地 PostgreSQL 开发数据
- Swagger 完成创建、查询、更新和分页筛选验收
- FastAPI API 测试从 3 个增加到 10 个
- 全项目 29 个 pytest 测试通过
- Ruff 与 Python 依赖检查通过

当前 FastAPI 数据链路：

```text
HTTP 请求
    ↓
FastAPI API 路由
    ↓
Pydantic Schema
    ↓
Service 业务层
    ├── 客户与订单校验
    ├── 第一周输入校验器
    └── 第一周规则引擎
    ↓
SQLAlchemy Repository
    ↓
Session 与事务
    ↓
PostgreSQL 17
```

### Day 12：客户、订单工具接口与统一 404

- 实现 `GET /customers/{customer_id}`
- 实现 `GET /orders/{order_id}`
- 使用独立 Customer、Order Repository 管理各自资源
- 使用独立 Customer、Order Service 处理资源查询
- 建立统一的 `ResourceNotFoundError` 基类
- 为客户、订单和工单定义稳定的机器可读错误码
- 使用全局异常处理器统一生成 HTTP 404 JSON
- 统一错误响应包含错误码、消息、资源类型和资源编号
- 使用 Pydantic `Field` 为客户、订单和错误响应补充字段说明
- 在 OpenAPI 中声明两个新接口的 404 响应模型
- Swagger 验证客户、订单正常查询与统一 404
- 工单接口同步切换到全局资源异常处理
- Customer、Order、Ticket Repository 职责完成去重
- FastAPI API 测试从 10 个增加到 15 个
- 全项目 34 个 pytest 测试通过
- Ruff 与 Python 依赖检查通过

统一资源错误格式：

```json
{
  "error": {
    "code": "CUSTOMER_NOT_FOUND",
    "message": "客户 999 不存在。",
    "resource": "customer",
    "resource_id": 999
  }
}
```


## 项目结构

```text
servicemind-ai-agent/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── customers.py
│   │       ├── health.py
│   │       ├── orders.py
│   │       └── tickets.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exception_handlers.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── entities.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── customer_repository.py
│   │   ├── order_repository.py
│   │   └── ticket_repository.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── customers.py
│   │   ├── errors.py
│   │   ├── orders.py
│   │   └── tickets.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── customer_service.py
│   │   ├── order_service.py
│   │   └── ticket_service.py
│   ├── __init__.py
│   └── main.py
├── config/
│   └── routing_rules.json
├── scripts/
│   ├── __init__.py
│   ├── query_database.py
│   └── seed_database.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_rules.py
│   └── test_validators.py
├── ticket_core/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── exceptions.py
│   ├── logging_config.py
│   ├── models.py
│   ├── repository.py
│   ├── rules.py
│   └── validators.py
├── .env.example
├── .gitignore
├── compose.yaml
├── day1_python_review.py
├── learning_log.md
├── README.md
├── requirements.txt
└── ticket_cli.py
```

> 数据库、日志和 `.env` 属于本地运行文件，已经通过 `.gitignore` 排除，不会上传到 GitHub；仓库仅提供 `.env.example` 配置模板。


## 运行环境

- Python 3.14
- pytest 9.1.1
- Windows PowerShell
- PyCharm
- SQLite
- Git
- Docker Desktop 4.83
- Docker Compose 5.3
- PostgreSQL 17
- SQLAlchemy 2.0.51
- psycopg 3.3.4

## 安装步骤

### 1. 克隆项目

```powershell
git clone https://github.com/yr517830-afk/servicemind-ai-agent.git
cd servicemind-ai-agent
```

### 2. 创建 Python 虚拟环境

```powershell
python -m venv .venv
```

### 3. 激活虚拟环境

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

激活成功后，终端开头会显示：

```text
(.venv)
```

### 4. 安装项目依赖

```powershell
python -m pip install -r requirements.txt
```

### 5. 创建本地环境配置

```powershell
Copy-Item .env.example .env
```

打开 `.env`，修改 `POSTGRES_PASSWORD`，并将 `DATABASE_URL`
中的密码同步修改为相同值，否则 SQLAlchemy 将无法连接数据库。

`.env` 已被 Git 忽略，不能上传或公开其中的真实数据库密码。

### 6. 启动 PostgreSQL

确保 Docker Desktop 正常运行，然后执行：

```powershell
docker compose up -d postgres
docker compose ps
```

PostgreSQL 状态应显示：

```text
healthy
```

### 7. 创建数据表并插入演示数据

```powershell
python -c "import app.models; from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
python -m scripts.seed_database
python -m scripts.query_database
```

### 8. 验证项目

```powershell
python -m pytest -q
ruff check .
python -m pip check
```

预期结果：

```text
34 passed
All checks passed!
No broken requirements found.
```

## 运行方式

进入项目根目录并激活虚拟环境后运行。

### PostgreSQL 数据库

启动：

```powershell
docker compose up -d postgres
```

查看状态：

```powershell
docker compose ps
```

停止容器：

```powershell
docker compose down
```

停止容器不会删除命名卷中的数据。

查询 ORM 演示数据：

```powershell
python -m scripts.query_database
```


### 启动FastAPI服务

```powershell
python -m uvicorn app.main:app --reload
```

服务启动后可以访问：

```text
健康检查：http://127.0.0.1:8000/health
接口文档：http://127.0.0.1:8000/docs
```

当前接口：

```text
GET   /health
GET   /customers/{customer_id}
GET   /orders/{order_id}
POST  /tickets
GET   /tickets
GET   /tickets/{ticket_id}
PATCH /tickets/{ticket_id}
```

### 启动命令行工单系统

```powershell
python ticket_cli.py
```

CLI 支持：

```text
1. 创建新工单
2. 查询历史工单
0. 退出系统
```

### 运行全部自动化测试

详细模式：

```powershell
python -m pytest -v
```

简洁模式：

```powershell
python -m pytest -q
```

当前测试结果：

```text
34 passed
```

### 单独运行输入校验测试

```powershell
python -m pytest tests/test_validators.py -v
```

### 单独运行规则引擎测试

```powershell
python -m pytest tests/test_rules.py -v
```

### 检查配置文件

```powershell
python -m ticket_core.config_loader
```

### 测试 SQLite 数据持久化

```powershell
python -m ticket_core.repository
```

### 检查代码质量

```powershell
ruff check .
```

## 自动化测试覆盖

### 输入校验：7个测试

- 合法工单
- 空客户名称
- 纯空格客户名称
- 空工单消息
- 纯空格工单消息
- 负数等待时间
- 错误问题类型

### 规则引擎：9个测试

- 支付安全工单
- 账号安全工单
- 等待超时工单
- VIP 物流工单
- 普通退款工单
- 普通咨询工单
- 安全规则优先级
- 超时规则优先级
- 使用 `caplog` 验证规则命中、优先级、团队和 SLA 日志

### FastAPI 接口：15个测试

- 健康检查返回 200
- 创建工单并执行 VIP 规则
- 查询 PostgreSQL 持久化工单
- 分页与组合筛选
- 更新工单并重新执行规则
- 不存在客户返回 404
- 不存在或不属于客户的订单返回 404
- 非法请求返回 422
- 不存在工单的查询和更新返回 404
- 空 PATCH 请求返回 400
- 查询客户详情
- 查询订单详情
- 不存在客户返回统一 404
- 不存在订单返回统一 404
- OpenAPI 包含资源字段说明和 404 响应说明

### 配置系统：2个测试

- 验证未设置环境变量时使用默认配置
- 验证环境变量能够覆盖默认配置

### ORM 模型：2个测试

- 验证 `customers`、`orders` 和 `tickets` 三张表完成注册
- 验证订单与工单的三个外键关系

## 已实现的核心功能

- 工单、客户和决策领域模型
- 输入参数校验与自定义异常
- 工单优先级判断、团队分配和 SLA 计算
- JSON 动态业务规则配置
- 运行日志记录
- SQLite 工单持久化
- CLI 工单录入、预览、保存和历史查询
- 重复工单拦截
- FastAPI 健康检查和工单 CRUD 接口
- Pydantic 请求与响应校验
- API、Schema、Service、Repository 和 Core 分层
- `pydantic-settings` 环境配置管理
- Docker Compose PostgreSQL 开发环境
- SQLAlchemy 2.0 数据库基础设施
- 客户、订单和工单 ORM 关系模型
- PostgreSQL 种子数据和关联查询
- FastAPI Service 与 SQLAlchemy Repository 正式连接
- PostgreSQL 工单创建、查询和部分更新
- 工单分页及状态、优先级、问题类型组合筛选
- PostgreSQL 客户和订单详情查询
- 创建与更新工单时自动执行规则引擎
- SQLAlchemy Session 事务提交与异常回滚
- 客户、订单和工单统一资源异常
- 全局 HTTP 404 异常处理器
- 带稳定错误码和资源信息的统一错误响应
- OpenAPI 客户、订单和错误字段说明
- 基于外层事务回滚的 SQLite 内存数据库 API 测试
- 使用 `caplog` 验证规则决策日志
- 核心 API 包含 60 个自动化断言
- 35 个 pytest 自动化测试
- Ruff 代码质量检查

## 项目亮点

1. 使用 `dataclass`、`Enum` 和 Pydantic 建立不同层次的数据模型。
2. 通过自定义异常和 Pydantic 校验统一处理不合法输入。
3. 将业务规则迁移到 JSON，修改规则无需改动核心代码。
4. 使用日志记录配置加载、规则命中和数据库操作。
5. 使用 SQLite 支撑第一阶段 CLI 工单闭环。
6. 使用参数化 SQL，避免直接拼接用户输入。
7. 使用 FastAPI 和 Swagger UI 提供可调用的 HTTP 接口。
8. 将后端拆分为 API、Schema、Service、Repository 和 Core 层。
9. 使用 `pydantic-settings` 和 `.env` 隔离环境配置与敏感信息。
10. 使用 Docker Compose 提供可复现的 PostgreSQL 17 开发环境。
11. 使用 SQLAlchemy 2.0 建立客户、订单和工单关系模型。
12. 使用外键约束保证客户、订单和工单之间的引用关系。
13. 使用幂等种子脚本避免重复插入演示数据。
14. 使用 `selectinload()` 和 `joinedload()` 验证 ORM 关联加载。
15. 使用 Service 编排客户校验、订单归属校验、规则决策和数据库事务。
16. 使用 PostgreSQL 实现工单创建、详情查询、部分更新、分页和组合筛选。
17. 工单等待时间变化时自动重新计算优先级、处理团队、SLA 和原因。
18. 使用 FastAPI 依赖覆盖、共享 SQLite 内存数据库和外层事务回滚隔离 API 测试数据。
19. 使用全局异常处理器统一客户、订单和工单的 404 JSON 格式。
20. 使用稳定错误码、资源类型和资源编号帮助前端处理异常。
21. 使用 Pydantic 字段说明和 OpenAPI 响应模型完善接口文档。
22. 使用 pytest fixture、parametrize、MonkeyPatch 和 caplog 建立 35 个自动化测试。
23. 使用 Ruff、依赖检查和完整回归测试保证代码质量。
24. 核心 API 测试包含 60 个断言，覆盖成功响应、参数校验、资源错误、分页筛选和 OpenAPI 契约。

## 后续计划

- 使用 Alembic 管理数据库迁移
- 实现客户与订单列表、创建和更新接口
- 为列表增加排序、日期范围和关键字搜索
- 增加并发更新控制与更细粒度的事务策略
- 接入大模型进行工单分类和回复生成
- 增加用户认证、权限控制和部署配置

