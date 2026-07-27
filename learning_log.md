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

# Day 5 学习日志：CLI 与异常路径

日期：2026-07-22

## 今日目标

开发 ServiceMind 命令行操作入口，将工单录入、输入校验、规则判断、保存和查询功能连接起来，并处理常见的异常输入和重复提交。

## 今日完成内容

### 1. 创建命令行主菜单

创建了项目根目录下的：

```text
ticket_cli.py
```

主菜单支持以下操作：

1. 创建新工单
2. 查询历史工单
0. 退出系统

使用 `while True` 保持菜单持续运行，并使用 `break` 正常退出程序。

### 2. 实现工单信息录入

CLI 可以录入：

- 客户名称
- 问题类型
- 问题描述
- 等待分钟数
- VIP 状态

支持的问题类型包括：

- 物流
- 退款
- 账号
- 支付
- 其他

### 3. 处理异常输入

实现了以下异常路径：

- 客户名称不能为空
- 问题描述不能为空
- 问题类型必须属于已有枚举
- 等待时间必须是整数
- 等待时间不能小于零
- VIP 状态只能输入 `y` 或 `n`
- 菜单只能输入 `0`、`1` 或 `2`

输入错误时程序不会崩溃，而是显示提示并要求重新输入。

### 4. 创建并校验工单对象

将终端输入转换为：

```python
TicketInput
CustomerProfile
```

然后调用：

```python
validate_ticket_input(ticket)
```

对工单进行业务校验。

### 5. 调用工单规则引擎

调用：

```python
decide_ticket(ticket, customer)
```

根据工单和客户信息自动生成：

- 优先级
- 处理团队
- SLA
- 判断原因

测试 VIP 物流工单时，系统正确输出：

```text
优先级：P1
处理团队：VIP 客服组
SLA：30 分钟
```

### 6. 实现确认保存

保存前询问用户：

```text
是否确认保存？（y/n）
```

输入 `y` 后调用：

```python
save_ticket(ticket, decision)
```

将工单写入 SQLite。输入 `n` 时取消保存，不修改数据库。

### 7. 实现历史工单查询

调用：

```python
list_tickets()
```

显示最近保存的工单，包括：

- 工单编号
- 客户名称
- 问题类型
- 优先级
- 处理团队
- SLA
- 创建时间

### 8. 处理重复提交

在 `repository.py` 中新增：

```python
ticket_exists()
```

通过客户名称、问题类型和问题描述判断相同工单是否已经存在。

发现相同工单时显示：

```text
发现相同工单，请勿重复提交。
```

系统不会再次写入数据库。

## 今日遇到的问题

### 问题一：`return` 缩进错误

`return wait_minutes` 最初写在 `while True` 外面，导致输入正确数字后仍然不断重复询问。

将 `return wait_minutes` 放入循环内部后解决。

### 问题二：函数名称拼写错误

最初将：

```python
input_wait_minutes
```

拼写成了：

```python
input_wait_miutes
```

统一修改函数定义和调用位置后解决。

### 问题三：换行符写错

最初把：

```python
\n
```

写成了：

```text
/n
```

`\n` 使用反斜杠，作用是在终端输出中换行。

## 今日收获

1. 学会使用 `input()` 接收终端输入。
2. 学会使用 `while True` 构建持续运行的菜单。
3. 学会使用 `try/except` 处理数字转换错误。
4. 学会将字符串转换成枚举、整数和布尔值。
5. 学会把多个模块连接成完整业务流程。
6. 学会在数据库写入前进行用户确认。
7. 学会查询并格式化显示 SQLite 数据。
8. 学会检测并阻止重复业务数据。
9. 理解了友好的错误提示比直接让程序崩溃更适合真实系统。

## 对求职的帮助

Day 5 将前四天的模型、校验、规则、配置、日志和数据库连接成了一个完整可运行的命令行应用。

这个功能能够体现：

- Python 命令行程序开发能力
- 用户输入和类型转换能力
- 异常处理能力
- 分层模块调用能力
- 业务流程设计能力
- SQLite 数据操作能力
- 重复数据防护意识
- 用户体验和错误提示意识

## 面试表达

我为 ServiceMind 开发了命令行操作入口，将输入校验、工单规则引擎、JSON 配置和 SQLite 数据库串联起来，实现了工单录入、决策预览、确认保存和历史查询。同时处理了空输入、错误枚举、非法数字和重复提交等异常路径。

## Day 5 完成情况

- [x] CLI 主菜单正常运行
- [x] 能够录入工单
- [x] 能够校验异常输入
- [x] 能够生成处理决策
- [x] 能够预览工单结果
- [x] 能够确认或取消保存
- [x] 能够保存到 SQLite
- [x] 能够查询历史工单
- [x] 能够拦截重复提交
- [x] Ruff 检查通过

# Day 6 学习日志：pytest 测试与重构

日期：2026-07-24

## 今日目标

学习 pytest、fixture 和 parametrize，为工单输入校验与规则引擎建立 15 个自动化测试，并使用 Ruff 检查项目代码质量。

## 今日完成内容

### 1. 安装并验证 pytest

当前项目虚拟环境中的 pytest 版本为：

```text
pytest 9.1.1
```

安装位置：

```text
E:\AIProjects\servicemind-ai-agent\.venv\Lib\site-packages
```

这证明 pytest 安装在当前项目的虚拟环境中，不会影响系统中的其他 Python 项目。

### 2. 创建测试目录

创建了以下测试结构：

```text
tests/
├── conftest.py
├── test_validators.py
└── test_rules.py
```

其中：

- `conftest.py`：保存多个测试共享的 fixture。
- `test_validators.py`：测试工单输入校验。
- `test_rules.py`：测试工单规则引擎。

### 3. 使用 fixture 准备测试数据

在 `conftest.py` 中创建了：

- `normal_customer`：普通客户 fixture。
- `vip_customer`：VIP 客户 fixture。
- `ticket_factory`：测试工单创建工厂。

fixture 可以让多个测试复用相同的准备逻辑，避免重复创建客户和工单对象。

### 4. 编写 7 个输入校验测试

为 `validate_ticket_input()` 编写了以下测试：

1. 合法工单可以通过校验。
2. 客户名称为空时抛出异常。
3. 客户名称只有空格时抛出异常。
4. 工单消息为空时抛出异常。
5. 工单消息只有空格时抛出异常。
6. 等待时间小于零时抛出异常。
7. 问题类型不是 `IssueType` 时抛出异常。

使用：

```python
with pytest.raises(...):
```

验证指定异常是否被正确抛出。

### 5. 使用 parametrize 生成多组测试

使用：

```python
@pytest.mark.parametrize(...)
```

让同一个测试函数使用不同输入运行多次。

例如，客户名称测试分别使用：

```python
""
"   "
```

从而覆盖空字符串和纯空格两种情况。

### 6. 编写 8 个规则引擎测试

为 `decide_ticket()` 测试了：

1. 支付问题命中 P0。
2. 账号问题命中 P0。
3. 等待满 120 分钟命中 P1。
4. VIP 物流工单命中 P1。
5. 普通退款工单命中 P2。
6. 普通咨询工单命中 P3。
7. 安全规则优先于等待超时和 VIP 规则。
8. 等待超时规则优先于 VIP 和普通退款规则。

每个测试同时验证：

```python
assert decision.priority == expected_priority
assert decision.assigned_team == expected_team
assert decision.sla_minutes > 0
assert decision.reason
```

### 7. 完成全部自动化测试

运行：

```powershell
python -m pytest -v
```

最终结果：

```text
collected 15 items
15 passed
```

简洁模式命令：

```powershell
python -m pytest -q
```

最终输出：

```text
...............    [100%]
15 passed in 0.19s
```

### 8. 使用 Ruff 检查代码

运行：

```powershell
ruff check .
```

Ruff 发现 `test_rules.py` 中存在无用导入：

```python
from email import message
```

删除无用导入后再次检查，结果为：

```text
All checks passed!
```

删除代码后重新运行全部测试，15 个测试仍然通过，证明清理没有破坏功能。

## 今日遇到的问题

### 问题一：parametrize 参数名不一致

在问题描述测试中，装饰器写的是：

```python
"customer_name"
```

函数参数却写成：

```python
message
```

pytest 因此无法收集测试，并提示：

```text
function uses no argument 'customer_name'
```

将装饰器参数改为 `message` 后解决。

### 问题二：异常消息不一致

业务代码中的消息是：

```text
工单消息不能为空
```

测试最初写成了“工单信息不能为空”。测试预期必须与真实异常内容一致。

### 问题三：预期团队名称写错

测试中曾出现以下错误名称：

```text
账户与支付安全组
VIP客服组
```

配置中的准确名称是：

```text
账号与支付安全组
VIP 客服组
```

自动化测试成功发现了肉眼容易忽略的文字和空格差异。

### 问题四：Ruff 发现无用导入

`from email import message` 没有被测试使用。删除后 Ruff 和 pytest 都重新通过。

## 今日收获

1. 理解 pytest 如何自动发现测试文件和测试函数。
2. 学会使用 fixture 复用测试准备数据。
3. 学会使用 parametrize 批量生成测试场景。
4. 学会使用 `pytest.raises()` 验证异常。
5. 学会测试正常路径、异常路径和边界值。
6. 学会验证规则之间的优先级。
7. 学会通过测试失败信息区分业务错误和测试预期错误。
8. 学会在清理或重构后重新运行测试。
9. 理解自动化测试是代码重构的安全网。

## 对求职的帮助

Day 6 证明项目不仅“可以运行”，还具有自动化质量保障能力。

能够体现：

- pytest 自动化测试能力
- fixture 测试数据复用能力
- parametrize 参数化测试能力
- 异常测试与边界测试能力
- 业务规则优先级测试能力
- 回归测试意识
- Ruff 静态检查能力
- 重构后重新验证的工程习惯

## 面试表达

我使用 pytest 为 ServiceMind 的输入校验和工单规则引擎建立了 15 个自动化测试，通过 fixture 复用普通客户、VIP 客户和工单工厂，并使用 parametrize 覆盖不同问题类型、异常输入、边界值和规则优先级。代码清理后重新运行全部测试和 Ruff，确保修改没有造成回归。

## Day 6 完成情况

- [x] pytest 安装在项目虚拟环境
- [x] 创建 tests 测试目录
- [x] 创建 3 个 fixture
- [x] 完成 7 个输入校验测试
- [x] 完成 8 个规则引擎测试
- [x] 15 个测试全部通过
- [x] Ruff 检查通过
- [x] 清理代码后重新执行回归测试

# Day 7 学习日志：第一周复盘与交付验证

日期：2026-07-25

## 今日目标

整理项目说明和运行环境，验证其他用户能否按照 README 独立运行项目，并总结第一周遇到的问题和设计取舍。

## 今日完成内容

### 1. 完善 README

补充了以下内容：

- 项目简介
- Day 1～Day 6 学习进度
- 项目目录结构
- 环境要求
- GitHub 克隆方法
- 虚拟环境创建和激活方法
- 项目依赖安装方法
- CLI运行方法
- pytest测试命令
- Ruff检查命令
- 项目亮点和后续计划

### 2. 创建依赖文件

在项目根目录创建：

```text
requirements.txt
```

内容为：

```text
pytest==9.1.1
ruff==0.15.22
```

其他用户可以运行：

```powershell
python -m pip install -r requirements.txt
```

安装项目需要的测试和代码检查工具。

### 3. 完成全新环境验证

从GitHub重新克隆项目：

```powershell
git clone https://github.com/yr517830-afk/servicemind-ai-agent.git servicemind-ai-agent-check
```

在全新的项目目录中依次完成：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
ruff check .
python ticket_cli.py
```

最终结果：

```text
15 passed
All checks passed!
```

CLI系统能够正常启动和退出。

这证明其他用户可以只按照README完成项目安装和运行。


### 4. 上传Day 7成果

提交信息：

```text
Day 7: Improve README and add dependency setup
```

提交编号：

```text
a55fabf
```

README和`requirements.txt`已经上传到GitHub。

## 本周遇到的3个主要问题

### 问题一：命令运行环境容易混淆

最初没有完全区分：

- PowerShell终端
- Python交互环境
- PyCharm运行窗口

例如曾将：

```powershell
python -V
```

写成：

```powershell
python-V
```

也曾在Python交互环境中输入Git命令。

通过这些问题，我理解了不同运行环境的用途，也认识到命令、参数和空格必须准确书写。

### 问题二：类名拼写不一致

曾将：

```python
TicketInput
TicketDecision
```

拼写成：

```python
TicketInupt
TicketDicison
```

导致其他模块出现`ImportError`和`NameError`。

这让我理解了：类名和函数名属于模块之间的接口，命名不一致会影响所有依赖模块。

### 问题三：配置读取和测试参数错误

读取JSON时曾错误使用：

```python
json.loads(file)
```

正确方式是：

```python
json.load(file)
```

编写pytest测试时，也遇到过参数化名称与测试函数参数不一致的问题。

这让我理解了：

- `json.load()`读取文件对象。
- `json.loads()`解析JSON字符串。
- pytest参数名必须与测试函数参数一致。
- 自动化测试可以帮助发现细小错误。

## 本周的3个设计取舍

### 取舍一：JSON配置与硬编码

最终选择将优先级、团队和SLA写入JSON配置，而不是全部写死在Python代码中。

这样修改业务规则时不需要修改核心代码，更接近真实项目的配置化设计。

### 取舍二：SQLite与大型数据库

第一阶段选择SQLite，没有直接使用MySQL或PostgreSQL。

SQLite不需要安装数据库服务，适合本地学习、快速开发和项目演示。以后开发Web服务时，可以再迁移到PostgreSQL。

### 取舍三：CLI与网页界面

第一周优先开发CLI，没有立即制作网页界面。

这样可以先验证数据模型、输入校验、规则引擎和数据库流程，减少界面开发带来的额外复杂度。

后续可以使用FastAPI为现有核心逻辑提供HTTP接口。

## 今日收获

1. 学会使用`requirements.txt`记录项目依赖。
2. 学会编写能够指导他人运行项目的README。
3. 学会通过全新克隆验证项目可复现性。
4. 理解“我的电脑能运行”不等于“其他人能运行”。
5. 学会用演示视频展示项目功能。
6. 学会总结真实开发问题和解决过程。
7. 学会分析技术方案的优点、限制和适用场景。
8. 完成第一周项目成果的整理和交付验证。

## 对求职的帮助

Day 7让项目从“个人练习代码”变成了“可以公开展示的GitHub项目”。

能够体现：

- 项目文档编写能力
- Python环境管理能力
- 依赖管理能力
- GitHub项目交付能力
- 自动化测试能力
- 项目可复现意识
- 技术方案分析能力
- 项目演示与表达能力

## 面试表达

我为ServiceMind项目补充了完整的README和依赖文件，并从GitHub重新克隆项目，在全新的虚拟环境中完成依赖安装、15个自动化测试、Ruff检查和CLI启动验证，确保其他用户能够按照文档独立运行项目。并总结了配置化、数据库和用户界面方面的设计取舍。

## Day 7完成情况

- [x] 完善README
- [x] 创建requirements.txt
- [x] 上传README和依赖文件
- [x] 从GitHub重新克隆项目
- [x] 在全新环境中安装依赖
- [x] 15个pytest测试全部通过
- [x] Ruff检查通过
- [x] CLI在全新环境中正常运行
- [x] 总结本周3个主要问题
- [x] 总结本周3个设计取舍

# Day 8 学习日志：FastAPI起步与请求校验

日期：2026-07-26

## 今日目标

把ServiceMind从只能在本地终端运行的CLI程序，升级为可以通过HTTP访问的Web API，并使用Pydantic自动校验请求数据。

## 今日完成内容

### 1. 安装FastAPI相关依赖

安装：

```powershell
python -m pip install "fastapi[standard]"
```

当前主要版本：

```text
FastAPI 0.140.0
Uvicorn 0.51.0
Pydantic 2.13.4
httpx2 2.9.1
```

同时更新了`requirements.txt`，确保其他用户可以安装相同版本的依赖。

### 2. 创建FastAPI应用目录

新增项目结构：

```text
app/
├── __init__.py
├── main.py
└── schemas.py
```

文件作用：

- `__init__.py`：将`app`标记为Python包。
- `main.py`：创建FastAPI应用并注册接口。
- `schemas.py`：定义API请求和响应的数据结构。

### 3. 创建FastAPI应用

在`main.py`中创建：

```python
app = FastAPI(
    title="ServiceMind API",
    description="智能客服工单系统 HTTP API",
    version="0.1.0",
)
```

这个`app`对象是整个HTTP服务的入口。

### 4. 实现健康检查接口

实现：

```text
GET /health
```

返回：

```json
{
  "status": "ok",
  "service": "ServiceMind"
}
```

浏览器和Swagger UI调用结果：

```text
200 OK
```

健康检查接口可以用于判断服务是否正常启动。

### 5. 定义TicketCreate请求模型

使用Pydantic定义创建工单时允许提交的字段：

- `customer_name`
- `issue_type`
- `message`
- `wait_minutes`
- `is_vip`

通过`Field`设置：

- 字符串最小长度
- 字符串最大长度
- 等待时间不能小于0
- 默认值
- Swagger文档示例

### 6. 定义TicketResponse响应模型

`TicketResponse`继承`TicketCreate`，并增加：

```text
ticket_id
status
```

这样可以复用请求模型已有字段，同时明确接口成功后应该返回的数据结构。

### 7. 实现工单创建接口

实现：

```text
POST /tickets
```

合法请求示例：

```json
{
  "customer_name": "小王",
  "issue_type": "物流",
  "message": "我的订单什么时候送到？",
  "wait_minutes": 15,
  "is_vip": true
}
```

接口成功返回：

```text
201 Created
```

目前`ticket_id`暂时固定为1，主要用于学习请求模型、响应模型和接口校验。后续再连接现有规则引擎与SQLite数据库。

### 8. 使用自动接口文档

启动服务：

```powershell
python -m uvicorn app.main:app --reload
```

访问：

```text
http://127.0.0.1:8000/docs
```

FastAPI自动生成Swagger UI，可以直接查看和调用：

```text
GET  /health
POST /tickets
```

### 9. 验证422异常响应

提交以下非法数据：

```json
{
  "customer_name": "",
  "issue_type": "售后",
  "message": "",
  "wait_minutes": -10,
  "is_vip": false
}
```

接口返回：

```text
422 Unprocessable Entity
```

错误响应准确指出：

- 客户名称太短
- 问题类型不属于已有枚举
- 问题描述太短
- 等待时间不能小于0

说明非法请求在进入接口函数之前，已经被Pydantic拦截。

### 10. 新增API自动化测试

新增：

```text
tests/test_api.py
```

包含3个测试：

1. 健康检查返回200。
2. 合法工单创建返回201。
3. 非法工单请求返回422。

测试命令：

```powershell
python -m pytest tests/test_api.py -v
```

结果：

```text
3 passed
```

### 11. 处理测试客户端弃用警告

第一次运行API测试时出现：

```text
StarletteDeprecationWarning
```

警告原因是测试客户端仍在使用旧`httpx`兼容方式。

安装：

```powershell
python -m pip install httpx2
```

重新运行测试后：

```text
3 passed
```

并且警告消失。

### 12. 完成全项目回归测试

运行：

```powershell
python -m pytest -q
ruff check .
```

最终结果：

```text
18 passed
All checks passed!
```

这说明新增FastAPI功能没有破坏前七天已经完成的业务逻辑。

## 今日遇到的问题

### 问题一：浏览器提示连接被拒绝

浏览器访问`127.0.0.1`时曾出现：

```text
ERR_CONNECTION_REFUSED
```

原因是Uvicorn服务器已经停止，没有程序监听8000端口。

重新运行：

```powershell
python -m uvicorn app.main:app --reload
```

并保持终端运行后解决。

### 问题二：根路径返回404

访问：

```text
http://127.0.0.1:8000/
```

终端显示：

```text
GET / 404 Not Found
```

这是因为当前只定义了`/health`和`/tickets`，没有定义`/`接口，并不代表FastAPI启动失败。

### 问题三：TestClient出现弃用警告

API测试虽然通过，但Starlette提示旧`httpx`兼容方式已经弃用。

安装`httpx2`后，API测试继续通过并且警告消失。

这让我理解了：测试通过不代表可以忽略所有警告，弃用警告可能意味着未来升级后代码会失效。

## 今日收获

1. 理解HTTP API与CLI程序的区别。
2. 学会创建FastAPI应用对象。
3. 学会使用装饰器注册GET和POST接口。
4. 学会使用Uvicorn启动ASGI服务。
5. 学会使用Pydantic定义请求和响应模型。
6. 学会设置字符串、枚举和数值校验规则。
7. 学会使用Swagger UI查看和调用接口。
8. 理解200、201、404和422状态码。
9. 学会使用TestClient测试FastAPI接口。
10. 学会处理第三方库弃用警告。
11. 学会在新增功能后运行全项目回归测试。

## 对求职的帮助

Day 8让ServiceMind从命令行项目升级为具有HTTP接口的后端应用。

能够体现：

- FastAPI后端开发能力
- REST API基础设计能力
- Pydantic数据建模能力
- HTTP状态码理解
- Swagger接口文档使用能力
- 请求和响应校验能力
- API自动化测试能力
- 第三方依赖与兼容性处理能力
- 回归测试意识

## 面试表达

我使用FastAPI为ServiceMind增加了HTTP服务入口，实现了健康检查和工单创建接口，并使用Pydantic定义请求与响应模型。接口能够自动校验字符串长度、问题类型和等待时间，非法请求会返回包含具体字段信息的422响应。我还使用TestClient编写了3个API测试，最终全项目18个测试和Ruff检查全部通过。

## Day 8完成情况

- [x] 安装FastAPI标准依赖
- [x] 创建app应用目录
- [x] 创建FastAPI应用
- [x] 实现GET /health
- [x] 定义TicketCreate
- [x] 定义TicketResponse
- [x] 实现POST /tickets
- [x] Swagger UI可以调用接口
- [x] 合法请求返回201
- [x] 非法请求返回422
- [x] 新增3个API自动化测试
- [x] 解决TestClient弃用警告
- [x] 全项目18个测试通过
- [x] Ruff检查通过
- [x] README已更新

---

# Day 9：分层结构与环境配置

## 今日目标

1. 将 FastAPI 项目改造成清晰的分层结构。
2. 使用 `pydantic-settings` 统一管理环境配置。
3. 使用 `.env.example` 提供安全的配置模板。
4. 将路由、模型、业务服务和数据库访问分离。
5. 保证重构前后的接口功能保持一致。
6. 为配置系统增加自动化测试。

## 今日完成内容

### 1. 安装配置管理依赖

安装：

```powershell
python -m pip install pydantic-settings
```

确认版本：

```powershell
python -m pip show pydantic-settings
```

当前版本：

```text
pydantic-settings 2.14.2
```

同时在 `requirements.txt` 中增加：

```text
pydantic-settings==2.14.2
```

`pydantic-settings` 可以通过 Pydantic 模型读取环境变量和 `.env` 文件，避免把数据库地址、调试开关和密钥直接写死在代码中。

### 2. 建立 FastAPI 分层目录

在 `app` 中建立：

```text
app/
├── api/
│   └── routes/
├── core/
├── repositories/
├── schemas/
└── services/
```

各层职责：

- `api/routes`：接收 HTTP 请求并返回响应。
- `schemas`：定义请求和响应的数据格式。
- `services`：负责业务流程和业务逻辑。
- `repositories`：负责数据库访问。
- `core`：负责配置等全局基础设施。

分层后的目标调用方向：

```text
HTTP 请求
    ↓
API 路由层
    ↓
Service 业务层
    ↓
Repository 数据访问层
    ↓
SQLite 数据库
```

### 3. 创建统一配置类

创建：

```text
app/core/config.py
```

核心代码：

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ServiceMind AI Agent"
    app_version: str = "0.1.0"
    debug: bool = False
    database_path: str = "data/servicemind.db"
    routing_rules_path: str = "config/routing_rules.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

主要作用：

- `BaseSettings`：读取环境变量和 `.env`。
- `SettingsConfigDict`：指定环境配置文件的位置和编码。
- `extra="ignore"`：忽略配置文件中暂时未定义的字段。
- `@lru_cache`：避免重复创建配置对象。
- `settings`：供项目其他模块直接读取统一配置。

### 4. 创建环境配置文件

项目根目录新增：

```text
.env
.env.example
```

配置内容：

```dotenv
APP_NAME=ServiceMind AI Agent
APP_VERSION=0.1.0
DEBUG=false
DATABASE_PATH=data/servicemind.db
ROUTING_RULES_PATH=config/routing_rules.json
```

两者区别：

- `.env`：本机实际配置，可能包含密码和密钥，不能上传 GitHub。
- `.env.example`：公开配置模板，可以上传 GitHub，不能包含真实密钥。

在 `.gitignore` 中加入：

```gitignore
.env
```

使用下面的命令确认 `.env` 已被忽略：

```powershell
git check-ignore .env
```

结果：

```text
.env
```

### 5. 将 Schema 迁移到独立目录

原来的：

```text
app/schemas.py
```

迁移为：

```text
app/schemas/tickets.py
```

文件中保留：

```text
TicketCreate
TicketResponse
```

Schema 层只负责描述输入和输出数据，不负责处理 HTTP 请求，也不直接访问数据库。

迁移后运行 API 测试，原有 3 个测试仍然通过，说明重构没有改变接口行为。

### 6. 拆分健康检查路由

创建：

```text
app/api/routes/health.py
```

核心代码：

```python
from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ServiceMind",
    }
```

`main.py` 通过 `include_router()` 注册该路由，不再直接定义健康检查函数。

### 7. 拆分工单路由

创建：

```text
app/api/routes/tickets.py
```

路由配置：

```python
router = APIRouter(
    prefix="/tickets",
    tags=["工单"],
)
```

接口使用：

```python
@router.post(
    "",
    response_model=TicketResponse,
    status_code=201,
)
```

`prefix="/tickets"` 与空路径 `""` 组合后，最终接口仍然是：

```text
POST /tickets
```

路由函数只负责接收请求、调用 Service 并返回结果。

### 8. 创建 Service 业务服务层

创建：

```text
app/services/ticket_service.py
```

核心代码：

```python
def process_ticket(ticket: TicketCreate) -> TicketResponse:
    return TicketResponse(
        ticket_id=1,
        status="received",
        **ticket.model_dump(),
    )
```

工单响应的创建逻辑从路由文件迁移到 Service 层。

当前 `ticket_id=1` 仍然是学习阶段的临时返回值。Repository 数据库封装已经建立，后续会继续将 FastAPI 工单接口与规则引擎和 SQLite 持久化流程连接起来。

### 9. 创建 Repository 数据访问层

创建：

```text
app/repositories/ticket_repository.py
```

Repository 对已有的 `ticket_core.repository` 进行封装，提供：

```text
save()
list_recent()
```

数据库路径不再直接写在 Repository 中，而是读取：

```python
settings.database_path
```

这一层的价值是让 Service 不需要知道 SQLite 文件地址，也不需要直接操作 SQL。

### 10. 让 FastAPI 使用统一配置

`app/main.py` 改为从配置对象读取：

```python
app = FastAPI(
    title=settings.app_name,
    description="智能工单系统 HTTP API",
    version=settings.app_version,
    debug=settings.debug,
)
```

配置来源变为：

```text
.env
  ↓
app/core/config.py
  ↓
app/main.py
```

验证结果：

```text
ServiceMind AI Agent
0.1.0
False
```

### 11. 新增配置自动化测试

新增：

```text
tests/test_config.py
```

包含两个测试：

1. 未设置环境变量时使用默认配置。
2. 环境变量能够覆盖默认配置。

测试中使用：

```python
Settings(_env_file=None)
```

避免本机 `.env` 干扰测试。

使用 `MonkeyPatch` 临时设置环境变量：

```python
monkeypatch.setenv("APP_NAME", "ServiceMind Test API")
monkeypatch.setenv("APP_VERSION", "9.9.9")
monkeypatch.setenv("DEBUG", "true")
```

测试结果：

```text
2 passed
```

### 12. 完成全项目验收

运行：

```powershell
python -m pytest -q
```

结果：

```text
20 passed
```

运行：

```powershell
ruff check .
```

结果：

```text
All checks passed!
```

说明本次目录重构和配置改造没有破坏已有的 CLI、规则引擎、输入校验和 FastAPI 接口。

## 今日遇到的问题

### 问题一：文件和目录重名

项目中原来存在：

```text
app/schemas.py
```

因此不能直接创建同名的 `app/schemas` 目录。

解决方法：

1. 将 `schemas.py` 临时重命名为 `schemas_old.py`。
2. 创建 `schemas` Python 软件包。
3. 将临时文件移动到该目录。
4. 最终重命名为 `tickets.py`。
5. 使用 PyCharm 重构功能自动更新引用。

### 问题二：路由文件中仍然使用 `@app.post`

工单接口移动到 `tickets.py` 后，第一次运行测试出现：

```text
NameError: name 'app' is not defined
```

原因是装饰器仍然写成：

```python
@app.post("/tickets")
```

但新路由文件中没有 FastAPI 应用对象 `app`，只有 `router`。

修改为：

```python
@router.post("")
```

后解决。

### 问题三：路由文件存在无用导入

`tickets.py` 中曾错误保留：

```python
from fastapi import FastAPI
from app.api.routes.health import router as health_router
```

这些内容只应由 `main.py` 使用。

删除无用导入并运行：

```powershell
ruff check app/api/routes/tickets.py
```

结果：

```text
All checks passed!
```

### 问题四：路由标签重复

最初在 `APIRouter` 和 `@router.post()` 中都设置了标签。

最终统一将：

```python
tags=["工单"]
```

放在 `APIRouter` 中，使同一模块内的接口自动共享标签。

### 问题五：README 代码框没有正确闭合

更新 README 时，调用结构代码框与项目结构代码框发生嵌套，导致 Markdown 格式错误。

通过关闭前一个代码框、恢复 `## 项目结构` 标题并删除多余的代码围栏后解决。

这说明文档也需要像代码一样检查结构和最终显示效果。

## 今日收获

1. 理解 API、Schema、Service、Repository 和 Core 各层职责。
2. 学会使用 `APIRouter` 拆分 FastAPI 路由。
3. 学会使用 `include_router()` 注册路由模块。
4. 学会让路由层只处理 HTTP 请求和响应。
5. 学会把处理逻辑迁移到 Service 层。
6. 学会使用 Repository 层封装数据库模块。
7. 学会使用 `pydantic-settings` 管理环境配置。
8. 理解 `.env` 与 `.env.example` 的区别。
9. 学会避免将本地敏感配置上传 GitHub。
10. 学会使用环境变量覆盖默认配置。
11. 学会使用 `MonkeyPatch` 测试环境变量。
12. 学会在重构后执行完整回归测试。
13. 理解代码分层能够降低模块之间的耦合。

## 对求职的帮助

Day 9 将 ServiceMind 从功能集中在少量文件中的项目，改造成了具有清晰职责边界的后端项目结构。

能够体现：

- FastAPI 项目架构设计能力
- 分层架构理解
- 路由模块化能力
- Pydantic Settings 配置管理能力
- 环境变量和敏感配置管理意识
- Service 与 Repository 分层意识
- 模块重构能力
- 自动化测试能力
- 回归测试意识
- GitHub 项目交付规范意识

这种目录结构与企业后端项目更接近，后续增加数据库接口、大模型服务、用户认证或其他业务模块时，不需要把所有代码继续堆积在 `main.py` 中。

## 面试表达

我对 ServiceMind 的 FastAPI 部分进行了分层重构，将项目拆分为 API、Schema、Service、Repository 和 Core 五层。路由层只负责 HTTP 请求和响应，业务处理进入 Service，数据库访问通过 Repository 统一封装。同时使用 pydantic-settings 和 `.env` 管理应用名称、版本、调试开关及数据库路径，并提供不包含敏感信息的 `.env.example`。重构后新增了配置测试，最终全项目 20 个 pytest 测试和 Ruff 检查全部通过。

## Day 9 完成情况

- [x] 安装 `pydantic-settings`
- [x] 更新 `requirements.txt`
- [x] 创建 API、Schema、Service、Repository 和 Core 目录
- [x] 创建统一配置类
- [x] 创建 `.env`
- [x] 创建 `.env.example`
- [x] 确认 `.env` 不会上传 GitHub
- [x] 迁移请求和响应模型
- [x] 拆分健康检查路由
- [x] 拆分工单路由
- [x] 创建 Service 层
- [x] 创建 Repository 层
- [x] FastAPI 使用统一配置
- [x] 新增 2 个配置测试
- [x] 全项目 20 个测试通过
- [x] Ruff 全项目检查通过
- [x] README 已全面更新