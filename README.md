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

## 项目结构

```text
servicemind-ai-agent/
├── config/
│   └── routing_rules.json
├── tests/
│   ├── conftest.py
│   ├── test_rules.py
│   └── test_validators.py
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
├── ticket_cli.py
├── learning_log.md
├── README.md
└── .gitignore
```

> 数据库和日志属于本地运行文件，已经通过 `.gitignore` 排除，不会上传到 GitHub。

## 运行环境

- Python 3.14
- pytest 9.1.1
- Windows PowerShell
- PyCharm
- SQLite
- Git

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

### 5. 验证项目环境

```powershell
python -m pytest -q
ruff check .
```

预期结果：

```text
15 passed
All checks passed!
```

## 运行方式

进入项目根目录并激活虚拟环境后运行。

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
15 passed
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

### 规则引擎：8个测试

- 支付安全工单
- 账号安全工单
- 等待超时工单
- VIP 物流工单
- 普通退款工单
- 普通咨询工单
- 安全规则优先级
- 超时规则优先级

## 已实现的核心功能

- 工单和客户数据模型
- 输入参数校验与自定义异常
- 工单优先级判断
- 处理团队自动分配
- SLA 自动计算
- JSON 动态配置
- 运行日志记录
- SQLite 工单持久化
- CLI 工单录入与结果预览
- 用户确认保存
- 历史工单查询
- 重复工单拦截
- pytest 自动化测试
- Ruff 代码质量检查

## 项目亮点

1. 使用 `dataclass` 和 `Enum` 建立清晰的数据模型。
2. 通过自定义异常统一处理不合法输入。
3. 将业务规则和 JSON 配置分离，修改配置无需修改核心代码。
4. 使用日志记录配置加载、规则命中和数据库操作。
5. 使用 SQLite 实现工单数据持久化。
6. 使用参数化 SQL，避免直接拼接用户输入。
7. 使用 CLI 串联录入、判断、保存和查询流程。
8. 在写入数据库前检查重复工单。
9. 使用 pytest fixture 和 parametrize 建立 15 个自动化测试。
10. 使用 Ruff 保持代码规范，并在代码清理后执行回归测试。

## 后续计划

- 使用 FastAPI 提供 HTTP 接口
- 接入大模型进行工单分类和回复生成
- 增加测试覆盖率统计和数据库测试
- 增加用户认证和权限控制
- 完成项目部署

