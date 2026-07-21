# ServiceMind AI Agent

ServiceMind 是一个使用 Python 开发的智能客服工单系统。  
项目可以校验客户输入、判断工单优先级、分配处理团队、计算 SLA，并将工单保存到 SQLite 数据库。

## 当前学习进度

### Day 1：Python 与 Git 基础

- 创建 Python 虚拟环境
- 配置 Git 仓库和 `.gitignore`
- 完成 10 个 Python 基础函数
- 使用 `assert` 验证函数结果
- 使用 Ruff 检查代码质量

### Day 2：数据模型与输入校验

- 使用 `Enum` 定义问题类型和工单优先级
- 使用 `dataclass` 定义：
  - `TicketInput`
  - `CustomerProfile`
  - `TicketDecision`
- 创建自定义异常
- 校验客户名称、问题类型和等待时间
- 完成 8 条工单规则测试

### Day 3：工单规则引擎

- 实现 `decide_ticket()` 工单决策函数
- 根据问题类型、客户等级和等待时间判断工单
- 自动生成：
  - 工单优先级
  - 处理团队
  - SLA
  - 判断原因
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

## 项目结构

```text
servicemind-ai-agent/
├── config/
│   └── routing_rules.json
├── ticket_core/
│   ├── __init__.py
│   ├── models.py
│   ├── exceptions.py
│   ├── validators.py
│   ├── rules.py
│   ├── config_loader.py
│   ├── logging_config.py
│   └── repository.py
├── data/
│   └── servicemind.db
├── logs/
│   └── servicemind.log
├── day1_python_review.py
├── learning_log.md
├── README.md
└── .gitignore
```

> 数据库和日志属于本地运行文件，已经通过 `.gitignore` 排除，不会上传到 GitHub。

## 运行环境

- Python 3.14
- Windows PowerShell
- PyCharm
- SQLite
- Git

## 运行方式

进入项目根目录并激活虚拟环境后运行。

### 检查配置文件

```powershell
python -m ticket_core.config_loader
```

### 测试输入校验

```powershell
python -m ticket_core.validators
```

### 测试工单规则

```powershell
python -m ticket_core.rules
```

### 测试 SQLite 数据持久化

```powershell
python -m ticket_core.repository
```

### 检查代码质量

```powershell
ruff check .
```

## 已实现的核心功能

- 工单数据模型
- 客户资料模型
- 输入参数校验
- 自定义异常
- 工单优先级判断
- 处理团队自动分配
- SLA 自动计算
- JSON 动态配置
- 运行日志记录
- SQLite 工单持久化
- 历史工单查询

## 项目亮点

1. 使用 `dataclass` 和 `Enum` 建立清晰的数据模型。
2. 通过自定义异常统一处理不合法输入。
3. 将业务规则和 JSON 配置分离，修改配置无需修改核心代码。
4. 使用日志记录配置加载、规则命中和数据库操作。
5. 使用 SQLite 实现工单数据持久化。
6. 使用参数化 SQL，避免直接拼接用户输入。
7. 使用 Ruff 保持代码规范。

## 后续计划

- 开发命令行工单操作界面
- 支持工单录入、预览、保存和查询
- 增加重复工单校验
- 使用 FastAPI 提供 HTTP 接口
- 接入大模型进行工单分类和回复生成
- 增加自动化测试和项目部署