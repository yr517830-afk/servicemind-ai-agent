# Day 1 学习日志

日期：2026-07-18

## 今天完成的内容

1. 在 PyCharm 中创建了 `servicemind-ai-agent` 项目和 Python 虚拟环境 `.venv`。
2. 安装并验证了 Python、Git，完成 Git 仓库初始化。
3. 创建了 `.gitignore`，避免提交 `.idea`、`.venv`、缓存文件和密钥文件。
4. 完成了 10 个 Python 基础函数，并使用 `assert` 验证函数结果。
5. 安装并运行 Ruff，修复了未使用的 `from unittest import result` 导入问题。
6. 学习了字符串处理、列表去重、字典统计、条件判断、循环、列表推导式和 f-string。

## 今天遇到的问题

1. 一开始把 `python -V` 写成了 `python -v`，进入了详细输出模式。
2. 一开始在 Python 控制台 `>>>` 中输入 Git 命令，后来明白 Git 命令要在终端中执行。
3. 一开始把 `.gitignore` 创建成了 `.gitignore.py`，后来改成正确文件名。
4. Ruff 提示 `result` 重复定义，删除未使用的导入后解决。

## 明天计划

学习 `dataclass`、`Enum`、自定义异常，并开始定义工单数据模型。
# Day 2 学习日志

1. 我使用 Enum 统一了工单类型和优先级。
2. 我使用 dataclass 定义了工单、客户和处理决策模型。
3. 我创建了自定义异常，并用 validate_ticket_input 校验不合法输入。
4. 我实现了 decide_ticket 规则引擎，自动输出优先级、处理团队、SLA 和原因。
5. 我完成了 8 条规则测试，理解了高风险规则、VIP 规则和边界值的判断顺序。

# Day 3 学习日志：工单规则引擎

## 今日目标

让系统根据工单类型、客户等级和等待时间，自动判断工单的优先级、处理团队、SLA 和判断原因。

## 今日完成内容

1. 在 `ticket_core/rules.py` 中实现了 `decide_ticket()` 函数。
2. 使用 `TicketInput` 和 `CustomerProfile` 作为输入。
3. 使用 `TicketDecision` 统一返回决策结果，包括：
   - `priority`：工单优先级
   - `assigned_team`：处理团队
   - `sla_minutes`：要求处理时限
   - `reason`：判定原因
4. 实现了以下规则优先级：

   1. 账号或支付安全问题：P0，分配给账号与支付安全组，SLA 为 15 分钟。
   2. 等待时间达到或超过 120 分钟：P1，优先处理。
   3. VIP 客户：P1，分配给 VIP 服务组。
   4. 退款问题：P2，分配给退款组。
   5. 其他普通问题：P3，分配给综合客服组。

5. 使用 `assert` 编写并运行 12 条规则测试，覆盖了支付、账号安全、退款、VIP、等待超时和普通工单等场景。
6. 测试通过后，终端输出：

```text
12 条工单规则测试全部通过！

# Day 4 学习日志：配置、日志与 SQLite 持久化

日期：2026-07-21

## 今日目标

将 Day 3 写死在 Python 代码中的工单路由规则迁移到 JSON 配置文件，并使用日志记录运行过程，最后通过 SQLite 保存和查询工单。

## 今日完成内容

### 1. 创建 JSON 路由配置

创建了：

```text
config/routing_rules.json
```

配置文件包含以下规则：

- 账号与支付安全：P0
- 等待时间超时：P1
- VIP 客户：P1
- 普通退款：P2
- 普通咨询：P3

每条规则都包含：

- `priority`：优先级
- `assigned_team`：处理团队
- `sla_minutes`：处理时限
- `reason`：判断原因

修改 JSON 中的 SLA 后，不需要修改 Python 规则代码，重新运行程序即可得到新的结果。

### 2. 使用 pathlib 定位配置文件

创建了：

```text
ticket_core/config_loader.py
```

通过以下代码定位项目根目录：

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
```

然后拼接配置文件路径：

```python
DEFAULT_CONFIG_PATH = (
    PROJECT_ROOT
    / "config"
    / "routing_rules.json"
)
```

这样不需要写死完整的 Windows 路径，项目移动到其他目录后仍然能够找到配置文件。

### 3. 使用 json.load 读取配置

通过下面的方式读取 JSON：

```python
with config_path.open(
    "r",
    encoding="utf-8",
) as file:
    rules = json.load(file)
```

配置加载成功后，可以遍历并显示五组路由规则。

### 4. 改造工单规则引擎

修改了：

```text
ticket_core/rules.py
```

`decide_ticket()` 不再写死团队、SLA 和原因，而是读取 `routing_rules.json` 中的配置。

新增 `_build_decision()`，负责把 JSON 字典转换为 `TicketDecision` 对象。

规则判断顺序仍然是：

1. 账号或支付安全
2. 等待时间超时
3. VIP 客户
4. 普通退款
5. 默认普通咨询

修改 JSON 后，Day 3 的规则函数无需修改即可使用新配置。

### 5. 添加 logging 日志

创建了：

```text
ticket_core/logging_config.py
```

日志会同时输出到终端和文件：

```text
logs/servicemind.log
```

日志记录了：

- 配置加载位置
- 命中的规则名称
- 工单优先级
- 处理团队
- SLA
- 数据库初始化结果
- 工单保存编号

没有记录客户的完整消息，避免日志泄露用户隐私。

### 6. 使用 SQLite 持久化工单

创建了：

```text
ticket_core/repository.py
```

数据库保存在：

```text
data/servicemind.db
```

创建了 `tickets` 表，保存：

- 客户名称
- 问题类型
- 工单消息
- 等待时间
- 优先级
- 处理团队
- SLA
- 判断原因
- 创建时间

编写了以下函数：

```python
initialize_database()
save_ticket()
list_tickets()
```

连续运行程序两次后，数据库分别生成了编号 `1` 和编号 `2` 的工单。第二次运行仍然能够查询编号 `1`，证明数据已经持久化，不会随程序退出而消失。

## 今日遇到的问题

### 问题一：把 JSON 粘贴到了终端

PowerShell 出现了 `PSConsoleReadLine` 显示异常。

原因是 JSON 内容应该写入 `routing_rules.json` 编辑器，而终端只能输入运行命令。

解决方式：

- 使用 `Ctrl + C` 终止输入；
- 重新打开终端；
- 将 JSON 粘贴到文件编辑区域；
- 终端只运行检查命令。

### 问题二：混淆 json.load 和 json.loads

错误代码：

```python
rules = json.loads(file)
```

报错提示：

```text
TypeError: the JSON object must be str,
bytes or bytearray, not TextIOWrapper
```

正确代码：

```python
rules = json.load(file)
```

记忆方法：

```text
json.load(file)   → 读取文件
json.loads(text)  → 读取字符串
```

### 问题三：重复导入和无用导入

Ruff 检查发现：

- `unittest.mock.DEFAULT` 被导入但没有使用；
- `rules.py` 中重复导入了模型类和 `load_routing_rules`。

使用下面的命令自动清理：

```powershell
ruff check ticket_core --fix
ruff check ticket_core
```

这些问题不会改变业务逻辑，但会降低代码可读性，因此需要在提交前修复。

### 问题四：数据库时间与日志时间相差 8 小时

日志显示中国时间，SQLite 的 `CURRENT_TIMESTAMP` 默认保存 UTC 时间，因此相差 8 小时。

这不是程序错误。真实系统通常统一保存 UTC 时间，在展示时再转换为用户所在时区。

## 今日收获

1. 配置文件用于保存经常调整的业务参数，Python 代码负责执行稳定逻辑。
2. `pathlib` 可以避免写死本机绝对路径。
3. `logging` 比 `print()` 更适合真实项目的问题排查。
4. SQLite 可以让数据在程序退出后继续保存。
5. SQL 参数占位符 `?` 可以避免直接拼接用户输入。
6. Ruff 能发现重复导入、无用导入等代码质量问题。
7. 配置、业务规则、日志和数据存储应该分别承担不同职责。

## 对求职的帮助

Day 4 将项目从普通 Python 练习升级为具有工程结构的后端项目，能够体现：

- JSON 配置管理能力
- Python 文件和路径处理能力
- 业务规则与配置解耦能力
- 日志记录和故障排查意识
- SQLite 数据库基础
- SQL 参数化查询意识
- 数据持久化能力
- Ruff 代码质量检查能力

## 面试表达

我将 ServiceMind 的工单路由规则从 Python 代码迁移到了 JSON 配置中，通过 pathlib 稳定定位配置文件，并通过 logging 记录配置加载、规则命中和数据库操作。同时使用 SQLite 保存工单及其决策结果，实现了配置、业务逻辑和数据存储的职责分离。

## Day 4 完成情况

- [x] JSON 配置能够正常读取
- [x] 修改 JSON 可以改变 SLA
- [x] 规则引擎使用 JSON 配置
- [x] 日志同时写入终端和日志文件
- [x] SQLite 能够保存工单
- [x] 程序重新启动后仍能查询历史工单
- [x] Ruff 最终检查通过
- [x] Git 提交完成