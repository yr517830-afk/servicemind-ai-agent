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

---

# Day 10：PostgreSQL 与 SQLAlchemy ORM

日期：2026-07-27

## 今日目标

1. 安装并配置 Docker Desktop。
2. 使用 Docker Compose 启动 PostgreSQL。
3. 使用环境变量管理数据库连接配置。
4. 使用 SQLAlchemy 2.0 建立 ORM 基础设施。
5. 创建客户、订单和工单三张关系表。
6. 使用 ORM 插入和查询关联数据。
7. 为 ORM 表结构和外键关系增加自动化测试。

## 今日完成内容

### 1. 配置 WSL 2 与 Docker Desktop

检查 WSL：

```powershell
wsl --version
```

实际环境：

```text
WSL 2.7.11.0
Linux 内核 6.18.33.2
```

安装 Docker Desktop 时选择了：

```text
Per-user installation
WSL 2 backend
Linux containers
```

安装完成后验证：

```powershell
docker version
docker compose version
```

实际版本：

```text
Docker Engine 29.6.2
Docker Desktop 4.83.0
Docker Compose 5.3.1
```

### 2. 解决 Docker 虚拟化启动问题

Docker Desktop 首次启动时提示：

```text
Virtualization support not detected
```

任务管理器显示硬件虚拟化已经启用，因此问题不是 BIOS，而是 Windows 虚拟机平台未完全启用。

使用管理员 PowerShell 启用：

```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
bcdedit /set hypervisorlaunchtype auto
```

重启 Windows 后，Docker Engine 成功启动。

### 3. 处理 WSLg 远程桌面弹窗

重启后出现与以下组件有关的错误：

```text
rdclientax.dll
RemoteApp
```

检查发现该文件位于：

```text
C:\Program Files\WSL
```

说明弹窗来自 WSLg 的 Linux 图形应用支持，不是未知第三方软件。

Day 10 只需要 Docker 和无图形界面的 WSL 2，因此在用户目录的 `.wslconfig` 中设置：

```ini
[wsl2]
guiApplications=false
```

然后执行：

```powershell
wsl --shutdown
```

重新启动 Docker 后，Docker 仍能正常运行，WSLg 弹窗不再影响开发。

### 4. 添加 PostgreSQL 环境变量

在本地 `.env` 中增加：

```dotenv
POSTGRES_DB=servicemind
POSTGRES_USER=servicemind
POSTGRES_PASSWORD=本机开发密码
DATABASE_URL=postgresql+psycopg://servicemind:本机开发密码@localhost:5432/servicemind
```

在 `.env.example` 中只保存安全示例：

```dotenv
POSTGRES_DB=servicemind
POSTGRES_USER=servicemind
POSTGRES_PASSWORD=change_me
DATABASE_URL=postgresql+psycopg://servicemind:change_me@localhost:5432/servicemind
```

通过以下命令确认真实 `.env` 不会进入 Git：

```powershell
git check-ignore .env
```

### 5. 使用 Docker Compose 启动 PostgreSQL

创建：

```text
compose.yaml
```

使用：

```text
postgres:17-alpine
```

并配置：

- 数据库名称
- 数据库用户
- 数据库密码
- `5432` 端口映射
- PostgreSQL 命名卷
- `pg_isready` 健康检查

启动：

```powershell
docker compose up -d postgres
```

检查：

```powershell
docker compose ps
```

结果：

```text
servicemind-postgres
postgres:17-alpine
Up (healthy)
0.0.0.0:5432->5432/tcp
```

命名卷用于保存 PostgreSQL 数据。执行普通的：

```powershell
docker compose down
```

不会删除数据库数据。

### 6. 验证 PostgreSQL 连接

在容器中执行：

```powershell
docker compose exec postgres psql `
  -U servicemind `
  -d servicemind `
  -c "SELECT current_database(), current_user, version();"
```

结果确认：

```text
数据库：servicemind
用户：servicemind
PostgreSQL：17.10
```

建表前执行：

```powershell
docker compose exec postgres psql `
  -U servicemind `
  -d servicemind `
  -c "\dt"
```

结果为：

```text
Did not find any relations.
```

说明数据库连接正常，但当时还没有创建实体表。

### 7. 安装 ORM 与数据库驱动

安装：

```powershell
python -m pip install "SQLAlchemy>=2.0,<2.1" "psycopg[binary]>=3.2,<4"
```

实际版本：

```text
SQLAlchemy 2.0.51
psycopg 3.3.4
psycopg-binary 3.3.4
```

在 `requirements.txt` 中记录：

```text
SQLAlchemy==2.0.51
psycopg[binary]==3.3.4
```

执行：

```powershell
python -m pip check
```

结果：

```text
No broken requirements found.
```

### 8. 扩展统一配置系统

在 `Settings` 中保留原有 SQLite 配置：

```python
database_path: str = "data/servicemind.db"
```

并增加：

```python
database_url: str = "sqlite:///data/servicemind.db"
```

默认值使用 SQLite，使不读取 `.env` 的单元测试能够独立运行。

正常开发时，`.env` 中的 `DATABASE_URL` 会覆盖默认值，并连接 PostgreSQL。

验证结果：

```text
postgresql+psycopg localhost 5432 servicemind servicemind
```

验证过程没有打印包含密码的完整连接 URL。

### 9. 创建 SQLAlchemy 基础设施

创建：

```text
app/core/database.py
```

其中包含：

```text
Base
engine
SessionLocal
get_db()
```

各组件职责：

- `Base`：所有 ORM 模型的共同基类。
- `engine`：管理数据库连接与连接池。
- `SessionLocal`：创建数据库会话。
- `get_db()`：为 FastAPI 请求提供会话并自动关闭。
- `pool_pre_ping=True`：使用连接前验证连接是否有效。

使用 SQLAlchemy 执行：

```sql
SELECT 1
```

结果：

```text
Database result: 1
```

证明 Python、psycopg、SQLAlchemy 和 PostgreSQL 已经形成完整连接链路。

### 10. 创建三个 ORM 实体

创建：

```text
app/models/
├── __init__.py
└── entities.py
```

定义三个模型：

```text
Customer
Order
Ticket
```

主要关系：

```text
Customer 1 ─── N Order
Customer 1 ─── N Ticket
Order    1 ─── N Ticket
```

外键：

```text
orders.customer_id  → customers.id
tickets.customer_id → customers.id
tickets.order_id    → orders.id
```

订单金额使用：

```python
Numeric(12, 2)
Decimal("299.00")
```

避免使用浮点数保存金额产生精度误差。

### 11. 创建 PostgreSQL 数据表

加载 ORM 模型并执行：

```python
Base.metadata.create_all(bind=engine)
```

最终创建：

```text
customers
orders
tickets
```

外键查询确认三条关系全部正确。

`create_all()` 适合当前学习阶段和首次建表，但它不会管理已有表的字段变更。后续项目需要使用 Alembic 管理数据库迁移。

### 12. 编写幂等种子脚本

创建：

```text
scripts/seed_database.py
```

插入：

- 一名 VIP 客户
- 一张物流订单
- 一张物流咨询工单

第一次运行：

```text
Seed data created
```

第二次运行：

```text
Seed data already exists
```

脚本会先通过客户邮箱检查数据是否存在，因此重复运行不会重复插入同一组演示数据。

### 13. 查询三个关联实体

创建：

```text
scripts/query_database.py
```

查询结果：

```text
Customer: 1 小王 VIP orders=1 tickets=1
Order: 1 SM-20260727-001 299.00 customer=小王
Ticket: 1 物流 P2 customer=小王 order=SM-20260727-001
```

使用：

```python
selectinload()
```

加载一对多集合关系，并使用：

```python
joinedload()
```

加载订单或工单关联的单个实体。

这证明三个实体不仅能分别查询，也能通过 ORM 关系互相访问。

### 14. 添加 ORM 自动化测试

新增：

```text
tests/test_models.py
```

包含两个测试：

1. 验证 `customers`、`orders` 和 `tickets` 已注册到 metadata。
2. 验证订单和工单的三个外键关系。

这些测试只检查 SQLAlchemy metadata，不依赖正在运行的 PostgreSQL，因此适合本地测试和未来 CI。

配置测试也增加了：

- 默认 `database_url` 验证
- 环境变量覆盖 `database_url` 验证

### 15. 完成全项目验收

执行：

```powershell
python -m pytest -q
ruff check .
python -m pip check
docker compose ps
python -m scripts.query_database
```

最终结果：

```text
22 passed
All checks passed!
No broken requirements found.
PostgreSQL healthy
三个 ORM 实体查询成功
```

## 今日遇到的问题

### 问题一：PyCharm 终端找不到 Docker

安装 Docker 后，原有 PyCharm 终端仍提示：

```text
docker is not recognized
```

原因是终端在安装前已经启动，仍然保留旧的 `PATH`。

关闭并重新打开 PyCharm 后，新终端成功读取 Docker 路径。

### 问题二：Docker 检测不到虚拟化

虽然 BIOS 硬件虚拟化已经启用，但 Windows 虚拟机平台和 Hypervisor 没有完整启动。

启用相关 Windows 功能并重启后解决。

### 问题三：WSLg 出现 RemoteApp 弹窗

`rdclientax.dll` 属于 WSLg 图形远程组件。

当前项目不需要 Linux GUI，因此关闭 `guiApplications`，同时保留 WSL 2 和 Docker 功能。

### 问题四：找不到 `app.models.entities`

运行模型注册验证时出现：

```text
ModuleNotFoundError: No module named 'app.models.entities'
```

原因是已经创建 `app/models/__init__.py`，但遗漏了真正的：

```text
app/models/entities.py
```

补建文件并保存三个 ORM 模型后解决。

### 问题五：Git 显示 `AM`

例如：

```text
AM compose.yaml
```

表示文件已经暂存，但暂存后又被修改。

这不是代码错误，最终提交前重新执行 `git add` 即可让暂存区包含最新版本。

## 今日收获

1. 理解镜像、容器、端口和命名卷之间的区别。
2. 学会使用 Docker Compose 管理 PostgreSQL。
3. 学会使用健康检查判断数据库是否真正可用。
4. 学会使用 SQLAlchemy 2.0 声明式 ORM。
5. 理解 `Base`、`engine`、`Session` 和事务的职责。
6. 学会使用外键表达实体之间的关系。
7. 学会使用 `Numeric` 与 `Decimal` 保存金额。
8. 学会使用环境变量隔离数据库凭据。
9. 学会编写可重复运行的种子数据脚本。
10. 学会查询 ORM 实体及其关联关系。
11. 理解 metadata 测试不需要连接真实数据库。
12. 理解 `create_all()` 与数据库迁移工具的区别。
13. 学会在引入新数据库后执行完整回归测试。

## 对求职的帮助

Day 10 将 ServiceMind 从 SQLite 单机练习项目升级为具备 PostgreSQL 和 ORM 基础设施的后端项目。

能够体现：

- Docker Desktop 与 Docker Compose 使用能力
- PostgreSQL 数据库使用能力
- SQLAlchemy 2.0 ORM 建模能力
- 关系型数据库设计能力
- 外键和实体关系理解
- 数据库连接池与 Session 管理意识
- 环境变量和敏感配置管理意识
- 种子数据与幂等设计意识
- 自动化测试与回归验证能力
- 数据库问题排查能力

## 面试表达

我使用 Docker Compose 为 ServiceMind 搭建了 PostgreSQL 17 开发环境，并通过健康检查和命名卷保证数据库的可用性与数据持久化。后端使用 SQLAlchemy 2.0 和 psycopg 建立统一的 Engine 与 Session，设计了 Customer、Order 和 Ticket 三个 ORM 实体以及三条外键关系。我还编写了幂等种子脚本和关联查询脚本，并使用 metadata 测试验证表结构和外键。最终全项目 22 个 pytest 测试、Ruff 和依赖检查全部通过。

## 当前边界

Day 10 已经完成 PostgreSQL 建表、数据插入和 ORM 查询，但 FastAPI 的 `POST /tickets` 仍然返回临时响应，尚未真正写入 PostgreSQL。

Day 11 将完成：

- 工单创建
- 工单查询
- 工单更新
- 分页和筛选
- FastAPI Service、Repository 与 SQLAlchemy 的正式连接

## Day 10 完成情况

- [x] WSL 2 与 Docker Desktop 正常运行
- [x] PostgreSQL 17 容器健康
- [x] PostgreSQL 数据使用命名卷持久化
- [x] 数据库凭据通过 `.env` 管理
- [x] 安装 SQLAlchemy 和 psycopg
- [x] 创建 `Base`、`engine` 和 `SessionLocal`
- [x] 创建客户、订单和工单 ORM 模型
- [x] 创建三张 PostgreSQL 数据表
- [x] 验证三条外键关系
- [x] 编写幂等种子脚本
- [x] 查询三个实体及其关联数据
- [x] 新增 2 个 ORM metadata 测试
- [x] 全项目 22 个测试通过
- [x] Ruff 全项目检查通过
- [x] README 已全面更新

---

# Day 11：工单 CRUD 与 PostgreSQL 持久化

日期：2026-07-28

## 今日目标

1. 将 FastAPI Service 和 Repository 正式连接 SQLAlchemy。
2. 实现工单创建、查询和部分更新接口。
3. 为工单列表增加分页与组合筛选。
4. 创建和更新工单时自动调用第一周规则。
5. 使用独立测试数据库验证完整 API 流程。
6. 通过 Swagger 完成创建、查询和更新验收。

## 今日完成内容

### 1. 验证 Day 10 基线

开始开发前执行：

```powershell
git status --short
docker compose ps
python -m pytest -q
ruff check .
```

代码工作区保持干净，原有测试结果为：

```text
22 passed
All checks passed!
```

Docker Desktop 最初尚未启动，启动 Docker Engine 后执行：

```powershell
docker compose up -d postgres
docker compose ps
```

PostgreSQL 恢复为：

```text
servicemind-postgres
Up (healthy)
```

### 2. 重新设计工单 API Schema

Day 10 的临时接口由客户端提交：

```text
customer_name
is_vip
```

这种方式不适合真实数据库系统，因为客户端不应自行声明 VIP 身份。

Day 11 改为提交：

```text
customer_id
order_id
issue_type
message
wait_minutes
```

Service 根据 `customer_id` 从 PostgreSQL 读取真实客户资料，再把客户等级和 VIP 状态交给规则引擎。

新增 Schema：

```text
TicketCreate
TicketUpdate
TicketResponse
TicketListResponse
TicketStatus
```

`TicketUpdate` 支持部分修改：

```text
message
wait_minutes
status
```

`TicketResponse` 使用：

```python
ConfigDict(from_attributes=True)
```

从 SQLAlchemy ORM 对象生成 API 响应。

### 3. 将 Repository 切换到 SQLAlchemy

Day 9 的 `ticket_repository.py` 仍然封装第一阶段 SQLite 函数。

Day 11 将其替换为 SQLAlchemy Repository，提供：

```text
get_customer_by_id()
get_order_for_customer()
add_ticket()
get_ticket_by_id()
list_tickets()
```

列表查询支持：

- 页码
- 每页数量
- 状态
- 优先级
- 问题类型

分页通过：

```python
offset((page - 1) * page_size)
limit(page_size)
```

实现，总数通过：

```python
select(func.count(Ticket.id))
```

单独查询。

### 4. Service 连接数据库与规则引擎

Service 创建工单时执行以下流程：

```text
读取客户
    ↓
验证客户存在
    ↓
验证订单属于该客户
    ↓
转换为 TicketInput
    ↓
调用 validate_ticket_input()
    ↓
调用 decide_ticket()
    ↓
生成 Ticket ORM 对象
    ↓
Repository 写入数据库
    ↓
提交事务
```

规则引擎使用数据库中的真实客户资料构建：

```text
CustomerProfile
```

不再信任请求中自行声明的 VIP 状态。

新增资源异常：

```text
CustomerNotFoundError
OrderNotFoundError
TicketNotFoundError
```

### 5. 事务提交与回滚

新工单创建和工单更新都由 Service 控制事务：

```python
session.commit()
```

发生数据库异常时执行：

```python
session.rollback()
```

Repository 负责查询和添加对象，Service 负责决定一个完整业务操作何时提交。

这样可以避免 Repository 中多个小步骤各自提交，导致业务流程只完成一部分。

### 6. 实现四个工单接口

最终接口：

```text
POST  /tickets
GET   /tickets
GET   /tickets/{ticket_id}
PATCH /tickets/{ticket_id}
```

各接口职责：

- `POST /tickets`：校验客户与订单、执行规则并创建工单。
- `GET /tickets`：分页查询并支持组合筛选。
- `GET /tickets/{ticket_id}`：查询单张工单。
- `PATCH /tickets/{ticket_id}`：部分更新工单。

API 将异常转换为：

```text
资源不存在 → 404
业务输入错误 → 400
Pydantic 请求校验错误 → 422
```

### 7. 更新时自动重新执行规则

如果 PATCH 修改：

```text
message
wait_minutes
```

Service 会重新构建 `TicketInput` 并执行第一周规则。

如果只修改：

```text
status
```

则不需要重复计算工单优先级。

这避免无关更新产生不必要的规则计算，同时保证影响决策的数据发生变化后，优先级、团队、SLA 和原因保持一致。

### 8. 验证 FastAPI 路由

最初尝试直接遍历：

```python
app.routes
```

FastAPI 0.140 中包含没有 `path` 属性的 `_IncludedRouter`，因此出现：

```text
AttributeError: '_IncludedRouter' object has no attribute 'path'
```

改为检查 Swagger 使用的 OpenAPI：

```python
app.openapi()["paths"]
```

确认：

```text
/tickets               GET, POST
/tickets/{ticket_id}   GET, PATCH
```

这说明问题出在检查命令，不是路由注册失败。

### 9. Swagger 创建真实工单

通过 `POST /tickets` 提交：

```json
{
  "customer_id": 1,
  "order_id": 1,
  "issue_type": "物流",
  "message": "Day 11：VIP 客户查询订单物流进度。",
  "wait_minutes": 15
}
```

返回：

```text
HTTP 201
ticket_id: 2
priority: P1
assigned_team: VIP 客服组
sla_minutes: 30
status: received
```

说明以下链路已经打通：

```text
POST
→ FastAPI
→ Service
→ 第一周规则
→ SQLAlchemy
→ PostgreSQL
```

### 10. 查询持久化工单

通过：

```text
GET /tickets/2
```

返回 HTTP 200，并得到与创建响应相同的数据。

这证明创建接口返回的不是临时对象，而是 PostgreSQL 中已经提交的数据。

### 11. PATCH 更新与规则重算

通过：

```json
{
  "wait_minutes": 180,
  "status": "processing"
}
```

更新工单 2。

结果：

```text
wait_minutes: 180
status: processing
priority: P1
assigned_team: 综合客服组
sla_minutes: 30
reason: 客户等待时间已达到阈值，需要升级处理。
```

原工单命中 VIP 规则；等待时间更新为 180 分钟后，重新命中等待超时规则。

### 12. 分页与组合筛选

使用：

```text
page=1
page_size=1
status=processing
priority=P1
issue_type=物流
```

查询结果：

```text
items: ticket_id 2
page: 1
page_size: 1
total: 1
pages: 1
```

证明分页元数据和三项组合筛选均正确。

### 13. 独立 API 测试数据库

自动化测试不能直接使用开发环境 PostgreSQL，否则会产生：

- 测试垃圾数据
- 测试之间互相影响
- 依赖 Docker 是否启动
- 本地与 CI 结果不一致

Day 11 使用：

```text
SQLite 内存数据库
StaticPool
FastAPI dependency_overrides
```

测试夹具为每个 API 测试创建独立数据库，插入一个 VIP 客户和一张订单，并覆盖：

```python
get_db
```

测试结束后清理依赖覆盖并释放数据库。

真实 PostgreSQL 开发数据不会被自动化测试修改。

### 14. API 自动化测试

FastAPI 测试从 3 个增加到 10 个：

1. 健康检查。
2. 创建工单并命中 VIP 规则。
3. 查询已持久化工单。
4. 分页与组合筛选。
5. PATCH 更新并重新执行规则。
6. 不存在客户返回 404。
7. 不存在或不属于客户的订单返回 404。
8. 非法请求返回 422。
9. 不存在工单的查询和更新返回 404。
10. 空 PATCH 返回 400。

单独运行：

```powershell
python -m pytest tests/test_api.py -v
```

结果：

```text
10 passed
```

### 15. 全项目验收

执行：

```powershell
python -m pytest -q
ruff check .
python -m pip check
docker compose ps
```

最终结果：

```text
29 passed
All checks passed!
No broken requirements found.
PostgreSQL healthy
```

## 今日遇到的问题

### 问题一：Docker API 无法连接

原因是 Docker Desktop 尚未启动，命名管道不存在。

启动 Docker Desktop 后，Docker Engine 恢复；再执行：

```powershell
docker compose up -d postgres
```

PostgreSQL 容器恢复健康。

### 问题二：直接遍历 FastAPI 路由时报错

FastAPI 0.140 的 `app.routes` 中包含 `_IncludedRouter`，它没有 `path` 属性。

最终改用 `getattr()` 安全检查，并直接读取 `app.openapi()["paths"]` 验证 Swagger 路径。

### 问题三：旧 API 允许客户端声明 VIP

客户端提交 `is_vip=true` 不可信，可能绕过业务规则。

Day 11 改为提交 `customer_id`，Service 从数据库读取客户等级和 VIP 状态。

### 问题四：自动化测试可能污染 PostgreSQL

如果 API 测试直接连接开发数据库，每次运行都会插入真实工单。

使用 FastAPI 依赖覆盖和 SQLite 内存数据库后，测试可以独立、快速、重复运行。

## 今日收获

1. 学会让 FastAPI 通过依赖注入获得 SQLAlchemy Session。
2. 学会使用 Service 编排数据库查询、业务校验和规则决策。
3. 理解 Repository 负责数据访问，Service 负责事务边界。
4. 学会实现 REST 风格的 POST、GET 和 PATCH。
5. 学会设计分页响应中的 `page`、`page_size`、`total` 和 `pages`。
6. 学会实现多个可选条件的组合筛选。
7. 学会验证订单与客户的归属关系。
8. 学会把资源不存在映射为 HTTP 404。
9. 学会把业务错误与 Pydantic 422 错误区分开。
10. 学会在关键字段更新后重新执行规则。
11. 学会使用 `dependency_overrides` 替换测试依赖。
12. 学会使用 SQLite 内存数据库隔离 API 测试。
13. 学会通过 OpenAPI 验证实际路由。
14. 学会用 Swagger 验收完整 CRUD 流程。

## 对求职的帮助

Day 11 将 ServiceMind 从“具备 PostgreSQL ORM 基础设施”升级为“API 能够真正读写关系型数据库”的项目。

能够体现：

- FastAPI CRUD 开发能力
- REST API 设计能力
- SQLAlchemy Repository 实现能力
- Service 业务编排能力
- 数据库事务管理意识
- 资源关系校验能力
- 分页与动态筛选能力
- 规则引擎集成能力
- HTTP 错误语义设计能力
- 测试数据库隔离能力
- Swagger 手工验收能力
- 自动化回归测试能力

## 面试表达

我将 ServiceMind 的 FastAPI Service 和 Repository 正式连接到 SQLAlchemy 与 PostgreSQL，实现了工单创建、详情查询、部分更新、分页和状态、优先级、问题类型组合筛选。创建工单时，Service 会从数据库读取真实客户资料、校验订单归属，再调用已有的输入校验器和规则引擎生成优先级、处理团队、SLA 与原因。更新等待时间后也会自动重新执行规则。测试层使用 FastAPI 依赖覆盖和 SQLite 内存数据库隔离数据，最终 10 个 API 测试及全项目 29 个测试全部通过。

## 当前边界

Day 11 已完成工单 API 的创建、查询、更新、分页和筛选，但当前仍有以下边界：

- 尚未提供删除工单接口。
- 尚未提供客户和订单 CRUD。
- 数据库结构变更尚未使用 Alembic。
- 列表尚未支持排序、时间范围和关键字搜索。
- 尚未实现登录、权限和并发更新控制。
- 尚未接入大模型分类与回复生成。

## Day 11 完成情况

- [x] PostgreSQL 容器健康
- [x] 工单 Schema 支持创建、更新和分页响应
- [x] Repository 切换到 SQLAlchemy
- [x] Service 读取真实客户资料
- [x] Service 校验订单归属
- [x] Service 调用第一周校验器和规则引擎
- [x] Service 管理事务提交和回滚
- [x] 实现 `POST /tickets`
- [x] 实现 `GET /tickets`
- [x] 实现 `GET /tickets/{ticket_id}`
- [x] 实现 `PATCH /tickets/{ticket_id}`
- [x] 实现分页
- [x] 实现状态、优先级和问题类型筛选
- [x] 资源不存在返回 404
- [x] 空 PATCH 返回 400
- [x] Swagger 创建、查询、更新验收通过
- [x] 使用独立 SQLite 内存测试数据库
- [x] 10 个 API 自动化测试通过
- [x] 全项目 29 个测试通过
- [x] Ruff 全项目检查通过
- [x] Python 依赖检查通过
- [x] README 已全面更新

# Day 12：客户、订单工具接口与统一 404

日期：2026-07-28

## 今日目标

1. 实现 `GET /customers/{customer_id}`。
2. 实现 `GET /orders/{order_id}`。
3. 为不存在的客户、订单和工单提供统一 404。
4. 为正常响应和错误响应补充字段说明。
5. 使用 Swagger 和自动化测试完成验收。

## 今日完成内容

### 1. 验证 Day 11 基线

执行：

```powershell
git status --short
docker compose ps
python -m pytest -q
ruff check .
```

结果：

```text
Git 工作区干净
PostgreSQL healthy
29 passed
All checks passed!
```

### 2. 设计统一资源异常

创建：

```text
app/core/exceptions.py
```

定义统一基类：

```text
ResourceNotFoundError
```

并定义三个具体异常：

```text
CustomerNotFoundError
OrderNotFoundError
TicketNotFoundError
```

每个异常都包含：

```text
code
resource
resource_id
message
```

错误码示例：

```text
CUSTOMER_NOT_FOUND
ORDER_NOT_FOUND
TICKET_NOT_FOUND
```

稳定错误码便于前端和其他调用方根据错误类型执行不同逻辑，不需要解析中文消息。

### 3. 设计统一错误响应

创建：

```text
app/schemas/errors.py
```

定义：

```text
ErrorDetail
ErrorResponse
```

统一格式：

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

字段职责：

- `code`：稳定的机器可读错误码。
- `message`：供用户或开发者阅读的说明。
- `resource`：资源类型。
- `resource_id`：未找到的资源编号。

### 4. 注册全局异常处理器

创建：

```text
app/core/exception_handlers.py
```

使用：

```python
app.add_exception_handler()
```

注册 `ResourceNotFoundError`。

任何未被路由捕获的具体资源异常都会统一转换为：

```text
HTTP 404
ErrorResponse JSON
```

这样无需在每个路由中重复编写相同的 `try/except` 和 `HTTPException`。

### 5. 工单接口切换到统一异常

Day 11 的 `ticket_service.py` 在文件内部定义了三个资源异常，路由层逐个捕获并转换为 404。

Day 12 改为：

- Service 从 `app.core.exceptions` 导入统一异常。
- Service 只抛出具体资源异常。
- 路由不再捕获资源异常。
- 全局处理器统一生成响应。
- `InvalidTicketError` 仍由路由转换为 HTTP 400。

验证：

```text
GET /tickets/999
```

返回：

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

### 6. 客户响应 Schema

创建：

```text
app/schemas/customers.py
```

`CustomerResponse` 包含：

```text
customer_id
name
email
level
is_vip
created_at
```

使用：

```python
ConfigDict(from_attributes=True)
```

从 ORM Customer 对象生成响应。

每个字段都使用 Pydantic `Field` 提供：

- 类型约束。
- 字段说明。
- 示例值。

### 7. 订单响应 Schema

创建：

```text
app/schemas/orders.py
```

`OrderResponse` 包含：

```text
order_id
order_number
customer_id
status
total_amount
created_at
```

金额保持：

```text
Decimal
```

API JSON 中显示为：

```text
"299.00"
```

避免金额精度丢失。

### 8. 客户与订单 Repository

创建：

```text
app/repositories/customer_repository.py
app/repositories/order_repository.py
```

提供：

```text
get_customer_by_id()
get_order_by_id()
get_order_for_customer()
```

随后清理 `ticket_repository.py` 中重复的客户和订单查询，让：

- Customer Repository 只负责客户。
- Order Repository 只负责订单。
- Ticket Repository 只负责工单。

Ticket Service 复用 Customer 和 Order Repository，避免重复实现。

### 9. 客户与订单 Service

创建：

```text
app/services/customer_service.py
app/services/order_service.py
```

Service 查询 Repository，资源不存在时分别抛出：

```text
CustomerNotFoundError
OrderNotFoundError
```

API 路由无需了解数据库查询细节。

### 10. 客户与订单路由

创建：

```text
app/api/routes/customers.py
app/api/routes/orders.py
```

实现：

```text
GET /customers/{customer_id}
GET /orders/{order_id}
```

路径参数使用：

```python
Path(ge=1)
```

并提供参数说明。

接口 OpenAPI 中显式声明：

```text
404 → ErrorResponse
```

### 11. Swagger 正常查询验收

执行：

```text
GET /customers/1
```

返回：

```text
HTTP 200
customer_id: 1
name: 小王
email: xiaowang@example.com
level: VIP
is_vip: true
```

执行：

```text
GET /orders/1
```

返回：

```text
HTTP 200
order_id: 1
order_number: SM-20260727-001
customer_id: 1
status: shipped
total_amount: 299.00
```

### 12. Swagger 统一 404 验收

执行：

```text
GET /customers/999
```

返回：

```text
HTTP 404
code: CUSTOMER_NOT_FOUND
resource: customer
resource_id: 999
```

执行：

```text
GET /orders/999
```

返回：

```text
HTTP 404
code: ORDER_NOT_FOUND
resource: order
resource_id: 999
```

客户、订单和工单三种资源均使用相同错误结构。

### 13. 自动化测试升级

原有 Day 11 API 测试使用：

```json
{
  "detail": "..."
}
```

断言资源错误。

Day 12 更新为断言完整统一响应，并新增：

1. 查询客户详情。
2. 查询订单详情。
3. 客户不存在的统一 404。
4. 订单不存在的统一 404。
5. OpenAPI 字段说明和 404 描述。

FastAPI API 测试从：

```text
10
```

增加到：

```text
15
```

执行：

```powershell
python -m pytest tests/test_api.py -v
```

结果：

```text
15 passed
```

### 14. 全项目验收

执行：

```powershell
python -m pytest -q
ruff check .
python -m pip check
docker compose ps
```

结果：

```text
34 passed
All checks passed!
No broken requirements found.
PostgreSQL healthy
```

## 今日遇到的问题

### 问题一：旧路由重复处理 404

Day 11 每个路由都捕获具体异常并抛出 `HTTPException`，代码重复且响应格式只包含 `detail`。

通过统一异常基类和全局处理器，将重复逻辑集中到一个位置。

### 问题二：旧测试依赖 `detail`

统一错误结构后，旧测试仍访问：

```python
response.json()["detail"]
```

更新为完整断言 `error.code`、`message`、`resource` 和 `resource_id`。

### 问题三：Repository 职责重复

Ticket Repository 中同时存在客户、订单和工单查询。

Day 12 将客户与订单查询迁移到各自 Repository，Ticket Service 通过组合多个 Repository 完成业务流程。

## 今日收获

1. 学会设计机器可读的稳定错误码。
2. 学会定义统一 API 错误响应。
3. 学会使用 FastAPI 全局异常处理器。
4. 理解 Service 抛业务异常、API 统一转换 HTTP 响应的分工。
5. 学会在 OpenAPI 中声明错误响应模型。
6. 学会使用 Pydantic Field 编写字段说明和示例。
7. 学会创建客户与订单工具查询接口。
8. 理解金额应使用 Decimal。
9. 学会按资源拆分 Repository。
10. 学会测试 Swagger/OpenAPI 文档结构。
11. 学会在重构错误格式后更新回归测试。

## 对求职的帮助

Day 12 让项目不仅“接口能用”，还具备了更接近企业 API 的错误契约和接口文档。

能够体现：

- REST 资源接口设计能力
- 全局异常处理能力
- API 错误码设计意识
- Pydantic 响应建模能力
- OpenAPI 文档维护能力
- Repository 职责划分能力
- Service 异常语义设计能力
- Swagger 手工验收能力
- 自动化 API 契约测试能力

## 面试表达

我为 ServiceMind 新增了客户和订单详情查询接口，并设计了统一的资源不存在错误契约。Customer、Order 和 Ticket Service 都抛出同一基类下的资源异常，由 FastAPI 全局异常处理器统一转换为包含错误码、消息、资源类型和资源编号的 404 JSON。接口 Schema 使用 Pydantic Field 提供字段说明和示例，OpenAPI 中也显式声明 404 响应模型。测试层新增客户、订单和 OpenAPI 契约测试，最终 15 个 API 测试和全项目 34 个测试全部通过。

## 当前边界

Day 12 已完成客户和订单详情查询，但仍有以下边界：

- 尚未提供客户和订单列表。
- 尚未提供客户和订单创建、修改接口。
- 尚未实现数据库迁移工具。
- HTTP 400 和 422 尚未全部切换到同一错误外壳。
- 尚未实现认证、权限和大模型功能。

## Day 12 完成情况

- [x] 创建统一资源异常基类
- [x] 创建客户、订单和工单资源异常
- [x] 创建统一错误响应 Schema
- [x] 注册 FastAPI 全局 404 处理器
- [x] 工单接口切换到统一 404
- [x] 创建客户响应 Schema
- [x] 创建订单响应 Schema
- [x] 为响应字段增加说明和示例
- [x] 创建 Customer Repository
- [x] 创建 Order Repository
- [x] Repository 职责完成去重
- [x] 创建 Customer Service
- [x] 创建 Order Service
- [x] 实现 `GET /customers/{customer_id}`
- [x] 实现 `GET /orders/{order_id}`
- [x] Swagger 正常查询通过
- [x] Swagger 统一 404 验收通过
- [x] 15 个 API 自动化测试通过
- [x] 全项目 34 个测试通过
- [x] Ruff 全项目检查通过
- [x] Python 依赖检查通过
- [x] README 已全面更新

# Day 13：后端自动化测试、事务回滚与日志验证

## 今日目标

1. 使用 FastAPI `TestClient` 完善接口自动化测试。
2. 使用数据库外层事务隔离每个 API 测试。
3. 确保测试结束后自动回滚种子数据和业务数据。
4. 使用 pytest `caplog` 验证关键业务日志。
5. 确保核心 API 至少包含 12 个自动化断言。

## 完成内容

### 1. API 测试数据库结构复用

将 SQLite 内存数据库引擎调整为 session 级 fixture：

```python
@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
```

整套 API 测试只创建一次数据库结构，避免每个测试反复建表和删表。

### 2. 每个测试使用独立外层事务

每次创建 `api_client` 时开启独立事务：

```python
connection = test_engine.connect()
transaction = connection.begin()
```

测试结束后统一回滚：

```python
if transaction.is_active:
    transaction.rollback()

connection.close()
```

即使 Service 或 Repository 中调用了：

```python
session.commit()
```

测试产生的客户、订单和工单数据仍不会污染后续测试。

### 3. 使用 rollback-only 事务连接模式

测试 Session 配置为：

```python
testing_session_local = sessionmaker(
    bind=connection,
    autoflush=False,
    expire_on_commit=False,
    join_transaction_mode="rollback_only",
)
```

该模式允许业务代码正常调用 `commit()`，但不会提交测试最外层事务，最终仍由 fixture 统一回滚。

### 4. 使用依赖覆盖注入测试 Session

通过 FastAPI 依赖覆盖，让 API 使用测试事务中的数据库 Session：

```python
def override_get_db() -> Generator[Session, None, None]:
    with testing_session_local() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db
```

测试完成后移除覆盖，防止影响其他测试：

```python
app.dependency_overrides.pop(get_db, None)
```

### 5. 增加业务日志自动化测试

使用 pytest `caplog` 捕获 `ticket_core.rules` 的 INFO 日志：

```python
with caplog.at_level(
    logging.INFO,
    logger="ticket_core.rules",
):
    decision = decide_ticket(
        ticket,
        vip_customer,
    )
```

验证日志中包含：

```python
assert "命中规则=vip" in caplog.text
assert f"优先级={decision.priority.value}" in caplog.text
assert f"团队={decision.assigned_team}" in caplog.text
assert f"SLA={decision.sla_minutes}分钟" in caplog.text
```

日志测试能够防止关键可观测信息在后续重构中被意外删除。

### 6. 核心 API 断言统计

执行：

```powershell
(Select-String -Path tests/test_api.py -Pattern '^\s*assert ').Count
```

结果：

```text
60
```

核心 API 的自动化断言数量远高于计划要求的 12 个，覆盖：

- 成功响应状态码和响应字段
- 工单创建、查询、更新
- 分页与组合筛选
- 客户和订单查询
- 资源不存在的统一 404
- 请求参数校验 422
- 空 PATCH 请求 400
- OpenAPI 响应契约

### 7. 全项目验收

执行：

```powershell
python -m pytest -q
ruff check .
python -m pip check
docker compose ps
```

结果：

```text
35 passed
All checks passed!
No broken requirements found.
PostgreSQL healthy
```

## 今日遇到的问题

### 问题一：SQLite 保存点没有按预期回滚

最初使用：

```python
join_transaction_mode="create_savepoint"
```

第一个测试结束后，种子客户仍然保留在共享内存数据库中。第二个测试再次插入相同邮箱时触发：

```text
sqlite3.IntegrityError:
UNIQUE constraint failed: customers.email
```

将连接模式调整为：

```python
join_transaction_mode="rollback_only"
```

之后外层事务可以在每个测试结束时完整清理数据，15 个 API 测试全部通过。

### 问题二：手工修改 fixture 时出现括号和缩进错误

修改 `sessionmaker()` 代码块时曾出现：

```text
SyntaxError: '(' was never closed
```

以及：

```text
IndentationError:
expected an indented block after 'with' statement
```

通过先执行：

```powershell
python -m py_compile tests/conftest.py
```

可以在运行完整测试前快速检查 Python 语法和缩进。

## 今日收获

1. 理解测试隔离不等于每次重新创建数据库。
2. 学会使用 session 级 fixture 复用数据库结构。
3. 学会使用 function 级外层事务隔离每个测试。
4. 理解业务 `commit()` 与测试外层事务之间的关系。
5. 学会使用 `join_transaction_mode="rollback_only"`。
6. 学会通过 FastAPI 依赖覆盖注入测试 Session。
7. 学会在 fixture 清理阶段恢复依赖并释放连接。
8. 学会使用 pytest `caplog` 捕获指定 logger。
9. 学会断言日志中的业务字段，而不仅是日志是否存在。
10. 学会使用 `py_compile` 快速定位语法和缩进问题。
11. 学会统计并审查核心 API 的自动化断言。

## 对求职的帮助

Day 13 让项目测试从“接口能够通过”升级为具备数据隔离、事务清理和日志验证的后端测试体系。

能够体现：

- pytest fixture 设计能力
- FastAPI TestClient 测试能力
- SQLAlchemy 测试事务管理能力
- 数据库测试隔离意识
- FastAPI 依赖覆盖能力
- API 契约与异常场景测试能力
- pytest caplog 使用能力
- 日志可观测性测试意识
- 测试故障诊断能力

## 面试表达

我为 ServiceMind 的 FastAPI 接口测试建立了共享 SQLite 内存数据库和每测试独立事务机制。数据库结构在整套测试中只创建一次，每个测试通过独立连接开启外层事务，业务代码可以正常调用 `commit()`，但不会提交最外层测试事务，测试结束后统一回滚，因此测试数据不会相互污染。我还使用 pytest `caplog` 验证规则命中、优先级、团队和 SLA 日志。最终 15 个 API 测试、60 个核心 API 断言和全项目 35 个测试全部通过。

## 当前边界

- API 测试目前使用 SQLite，尚未增加 PostgreSQL 集成测试。
- 尚未统计测试覆盖率。
- 尚未接入持续集成流水线。
- 尚未测试并发请求和并发事务。
- 尚未验证结构化 JSON 日志。

## Day 13 完成情况

- [x] TestClient API 测试正常运行
- [x] 测试数据库结构完成复用
- [x] 每个 API 测试使用独立外层事务
- [x] 测试结束后自动回滚
- [x] FastAPI 数据库依赖完成覆盖
- [x] SQLite 唯一数据冲突问题完成修复
- [x] 使用 `caplog` 验证规则日志
- [x] 日志测试包含 5 个关键断言
- [x] 核心 API 包含 60 个断言
- [x] 15 个 API 测试通过
- [x] 全项目 35 个测试通过
- [x] Ruff 全项目检查通过
- [x] Python 依赖检查通过
- [x] PostgreSQL 容器健康
- [x] README 已更新

---

# Day 14：Docker 一键交付与技术文档

## 今日目标

1. 将 FastAPI 应用构建为 Docker 镜像。
2. 使用 Docker Compose 同时启动 PostgreSQL 和 API。
3. 为数据库与 API 配置健康检查和启动顺序。
4. 补充独立 API 文档和数据库 ER 图。
5. 让其他开发者能够通过一条命令启动完整后端。

## 完成内容

### 1. 创建 FastAPI Docker 镜像

新增 `Dockerfile`，使用：

```dockerfile
FROM python:3.14-slim
```

镜像完成以下工作：

- 关闭 `.pyc` 文件生成。
- 开启 Python 无缓冲输出。
- 安装锁定版本的项目依赖。
- 复制 FastAPI 应用、配置和脚本。
- 创建数据与日志目录。
- 使用非 root 用户运行服务。
- 暴露容器的 8000 端口。
- 使用 Uvicorn 启动 `app.main:app`。

构建命令：

```powershell
docker build -t servicemind-api:day14 .
```

镜像验证：

```powershell
docker image inspect servicemind-api:day14 --format "{{.RepoTags}}"
```

结果：

```text
[servicemind-api:day14]
```

### 2. 创建 Docker 构建排除规则

新增 `.dockerignore`，排除：

- Git 与 IDE 配置。
- Python 虚拟环境。
- pytest、Ruff 和覆盖率缓存。
- `.env` 敏感配置。
- SQLite 数据库文件。
- 本地日志和运行数据。
- 测试及学习记录。

这样可以缩小构建上下文，并避免把数据库密码和本地文件复制进镜像。

### 3. Compose 同时编排数据库与 API

`compose.yaml` 从单一 PostgreSQL 服务扩展为：

```text
Docker Compose
├── postgres
└── api
```

API 使用以下容器网络地址连接数据库：

```text
postgresql+psycopg://用户:密码@postgres:5432/servicemind
```

容器之间通过 Compose 服务名 `postgres` 通信，不能使用 `localhost`。

### 4. 控制容器启动顺序

API 配置：

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

只有 PostgreSQL 通过健康检查后，API 才会执行初始化和启动命令。

### 5. 自动初始化数据库

API 容器启动时依次执行：

```text
创建 ORM 数据表
→ 执行幂等种子脚本
→ 启动 Uvicorn
```

因此全新环境不需要先在宿主机手动执行建表脚本。

### 6. API 容器健康检查

API 通过 Python 标准库请求：

```text
http://127.0.0.1:8000/health
```

避免依赖精简镜像中可能不存在的 `curl` 命令。

### 7. Docker 一键启动

执行：

```powershell
docker compose up --build -d
```

验收结果：

```text
servicemind-api        healthy
servicemind-postgres   healthy
```

对外端口：

```text
API:        8000
PostgreSQL: 5432
```

### 8. 容器化 API 验收

验证：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

返回：

```json
{
  "status": "ok",
  "service": "ServiceMind"
}
```

Swagger UI 返回 HTTP 200：

```text
http://127.0.0.1:8000/docs
```

分页查询成功：

```text
GET /tickets?page=1&page_size=2
HTTP 200
```

API 日志中不存在 Traceback 或数据库连接错误。

### 9. 补充 API 文档

新增 `docs/api.md`，包含：

- Docker 启动与停止命令。
- 服务访问地址。
- 全部接口列表。
- 创建、查询和更新示例。
- 分页与组合筛选参数。
- 统一资源错误格式。
- 自动化验证命令。

### 10. 补充数据库 ER 图

新增 `docs/er-diagram.md`，使用 Mermaid 描述：

```text
Customer 1 ── N Order
Customer 1 ── N Ticket
Order    0..1 ── N Ticket
```

文档同时记录主键、唯一约束、外键、索引和 SQLAlchemy 双向关系。

### 11. 更新 README 首页

README 首页新增：

- Docker 一键启动步骤。
- 两个容器的健康状态。
- Swagger、健康检查和 OpenAPI 地址。
- API 文档与 ER 图入口。
- Day 13 与 Day 14 进度。
- 最新项目目录结构。

## 今日遇到的问题

### 问题一：Dockerfile 多行 CMD 解析失败

最初将 JSON 格式的 `CMD` 直接拆成多行，Docker 报错：

```text
unknown instruction: "uvicorn",
```

修改为单行 JSON 数组后构建成功：

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 问题二：容器中不能使用 localhost 连接数据库

API 与 PostgreSQL 位于不同容器。API 容器中的 `localhost` 指向 API 自身，因此数据库主机必须使用 Compose 服务名：

```text
postgres
```

### 问题三：启动容器不会自动打开浏览器

Docker Compose 只启动后台服务，不会弹出网页。Swagger 需要手动访问：

```text
http://127.0.0.1:8000/docs
```

项目当前没有独立前端首页。

### 问题四：PowerShell 显示中文乱码

Windows PowerShell 5.1 可能错误解码不带 charset 的 UTF-8 JSON。服务、数据库和浏览器 Swagger 实际运行正常，该现象不属于容器故障。

## 今日收获

1. 学会编写 Python FastAPI Dockerfile。
2. 理解 Docker 构建上下文和 `.dockerignore`。
3. 学会避免将 `.env` 复制进镜像。
4. 学会使用非 root 用户运行容器。
5. 学会使用 Docker Compose 编排多个服务。
6. 理解容器服务名和 localhost 的区别。
7. 学会使用健康检查控制服务启动顺序。
8. 学会在容器启动阶段初始化数据库。
9. 学会使用 Compose 日志诊断 API。
10. 学会编写独立 API 使用文档。
11. 学会使用 Mermaid 描述数据库 ER 关系。

## 对求职的帮助

Day 14 让项目从“开发者本机可以运行”升级为“其他人克隆后可以使用 Docker 一键启动”。

能够体现：

- Docker 镜像构建能力
- Docker Compose 多服务编排能力
- 容器网络与环境变量配置能力
- 健康检查和启动依赖设计能力
- FastAPI 容器化部署能力
- PostgreSQL 容器化能力
- API 文档维护能力
- 数据库 ER 建模表达能力
- 可复现交付意识

## 面试表达

我为 ServiceMind 编写了 Python 3.14 Docker 镜像，并使用 Docker Compose 同时编排 FastAPI 和 PostgreSQL。API 通过 Compose 服务名访问数据库，并通过 `depends_on` 等待 PostgreSQL 健康后再创建数据表、执行幂等种子脚本并启动 Uvicorn。两个服务都有独立健康检查，其他开发者只需执行 `docker compose up --build -d` 就能启动完整后端。我还补充了 API 使用文档和 Mermaid ER 图，使仓库具备可复现启动和快速理解能力。

## 当前边界

- 当前使用 ORM `create_all()` 初始化表，尚未接入 Alembic 数据库迁移。
- API 容器使用 Uvicorn 单进程，尚未配置生产级进程管理。
- 尚未实现独立前端页面。
- 尚未配置 HTTPS 和反向代理。
- 尚未建立 CI/CD 自动构建与部署。
- 尚未接入大模型、RAG 和 Agent。

## Day 14 完成情况

- [x] 创建 FastAPI Dockerfile
- [x] 使用 Python 3.14 slim 基础镜像
- [x] 使用非 root 用户运行 API
- [x] 创建 `.dockerignore`
- [x] `.env` 未进入 Docker 镜像
- [x] Compose 新增 API 服务
- [x] API 通过服务名连接 PostgreSQL
- [x] PostgreSQL 健康后启动 API
- [x] 自动创建数据库表
- [x] 自动执行幂等种子脚本
- [x] PostgreSQL 健康检查通过
- [x] API 健康检查通过
- [x] Swagger 返回 HTTP 200
- [x] 容器化分页查询通过
- [x] 新增 API 使用文档
- [x] 新增 Mermaid ER 图
- [x] README 一键启动说明已更新

# Day 15：LLM API 客户端与容错处理

## 今日目标

1. 安装并配置 OpenAI Python SDK。
2. 使用环境变量安全管理 API Key。
3. 封装独立 LLM 客户端。
4. 实现超时和常见 API 异常映射。
5. 保证无密钥时服务仍能正常运行。
6. 使用 Mock 完成不消耗 Token 的自动化测试。
7. 将 LLM 配置接入 Docker Compose。

## 完成内容

### 1. LLM 环境配置

新增以下配置：

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL`
- `OPENAI_TIMEOUT_SECONDS`
- `OPENAI_MAX_RETRIES`

真实密钥只保存在被 Git 忽略的 `.env` 中，`.env.example` 仅保留空白模板。

### 2. LLM 客户端封装

新增 `app/clients/llm_client.py`，统一封装 OpenAI Responses API。

客户端提供：

- 配置状态检查
- 文本生成
- 请求超时控制
- 自动重试次数控制
- 统一异常映射
- 空响应校验

### 3. 无密钥安全启动

未配置 API Key 时，客户端不会创建真实 SDK 连接，FastAPI 和 Docker 容器仍可正常启动。

健康状态返回：

```json
{
  "status": "not_configured",
  "configured": false,
  "model": "gpt-5.6-sol",
  "timeout_seconds": 20.0,
  "max_retries": 1
}
```

### 4. 异常映射

将 SDK 异常转换为项目内部异常：

| SDK 情况 | 项目异常 |
|---|---|
| 未配置密钥 | `LLMNotConfiguredError` |
| 请求超时 | `LLMTimeoutError` |
| 请求限流 | `LLMRateLimitError` |
| 认证失败 | `LLMAuthenticationError` |
| 连接失败 | `LLMUnavailableError` |
| API 状态异常 | `LLMUnavailableError` |
| 返回空文本 | `LLMUnavailableError` |

不直接向上层返回 SDK 原始异常，降低敏感信息泄露风险。

### 5. LLM 健康检查

新增：

```http
GET /health/llm
```

该接口只读取本地配置，不调用真实模型、不消耗 Token，也不返回 API Key。

### 6. Docker 集成

Docker Compose 在容器运行阶段传入 LLM 配置，API 镜像升级为：

```text
servicemind-api:day15
```

API 和 PostgreSQL 容器健康检查均通过。

### 7. 自动化测试

新增 7 个 LLM 客户端测试，覆盖：

- 无密钥安全行为
- 正常文本响应
- 超时异常
- 限流异常
- 认证异常
- 连接异常
- 空响应异常

新增 1 个 LLM 健康接口测试，验证响应中不包含 API Key。

最终结果：

```text
43 passed
All checks passed!
No broken requirements found.
```

## 今日遇到的问题

### PowerShell 嵌套引号冲突

使用 `python -c` 测试多行 `try/except` 时，PowerShell 与 Python 字符串引号发生冲突。

最终改用 pytest 编写正式测试，避免复杂终端转义，并使测试可以持续重复执行。

## 今日收获

1. 理解 API Key 不能写入代码或提交到 Git。
2. 学会封装独立 LLM 客户端。
3. 学会使用 Responses API。
4. 学会配置请求超时和重试。
5. 学会将第三方 SDK 异常转换为业务异常。
6. 学会在无密钥状态下保持服务可用。
7. 学会使用 Mock 测试第三方 API。
8. 学会避免测试消耗真实 Token。
9. 学会将 LLM 配置安全传入 Docker 容器。

## 面试表达

我在 ServiceMind 中封装了独立的 LLM 客户端，通过环境变量管理 API Key、模型、服务地址、超时和重试配置。客户端使用统一异常体系处理未配置、超时、限流、认证和连接失败等场景，避免第三方 SDK 异常或敏感信息直接暴露给上层。测试使用 Mock 模拟模型响应和异常，不依赖网络，也不会消耗真实 Token。即使没有配置 API Key，FastAPI 和 Docker 服务仍可正常启动并通过健康检查。

## 当前边界

- 当前尚未把 LLM 文本生成接入具体工单业务。
- 当前未配置真实 API Key，因此未进行真实模型调用。
- 当前健康检查只验证本地配置，不探测远程模型服务。
- 当前尚未实现结构化输出、流式响应和 Token 用量统计。

## Day 15 完成情况

- [x] 安装 OpenAI Python SDK
- [x] 使用环境变量管理 LLM 配置
- [x] API Key 未写入代码
- [x] 封装 LLM 客户端
- [x] 实现无密钥安全行为
- [x] 实现超时与异常映射
- [x] 新增 LLM 健康检查
- [x] Docker Compose 接入 LLM 配置
- [x] 新增 8 个自动化测试
- [x] 全项目 43 个测试通过
- [x] Ruff 检查通过
- [x] Python 依赖检查通过
- [x] API 与 PostgreSQL 容器健康

# Day 16：LLM 结构化意图提取

## 今日目标

1. 使用 Pydantic 定义结构化意图模型。
2. 让 OpenAI Responses API 返回经过校验的结构化数据。
3. 从客户消息中提取意图、订单号、风险等级和判断说明。
4. 在未配置 API Key 或解析失败时提供安全兜底。
5. 使用 Mock 验证 15 条客户输入，不消耗真实 Token。

## 完成内容

### 1. 结构化数据模型

新增 `app/schemas/intent.py`，定义 `IntentType`、`RiskLevel` 和 `IntentExtraction`。

`IntentExtraction` 包含以下必填字段：

- `intent`
- `order_number`
- `risk`
- `confidence_reason`

模型使用 `extra="forbid"`，拒绝模型返回未定义字段。

### 2. OpenAI 结构化输出

扩展 `LLMClient`，新增 `parse_structured()` 方法。该方法使用 OpenAI Responses API 的结构化解析能力，通过 Pydantic 模型校验输出，并直接返回已校验的 Python 对象，避免手动解析不可靠的 JSON 字符串。

### 3. 意图提取服务

新增 `app/services/intent_service.py`，负责：

- 清理客户输入
- 调用 LLM 结构化输出
- 提取客户意图和订单号
- 判断风险等级
- 返回置信说明
- 忽略客户消息中可能包含的提示注入指令

### 4. 安全兜底

客户消息为空、API Key 未配置、LLM 调用失败或结构化结果无效时，服务不会崩溃，而是返回：

```json
{
  "intent": "other",
  "order_number": null,
  "risk": "unknown",
  "confidence_reason": "结构化提取失败，已使用安全兜底结果。"
}
```

### 5. 自动化测试

新增 15 条参数化客户消息测试，覆盖物流、订单状态、退款、支付、账号安全、投诉、普通咨询和无法判断等场景。另外验证了：

- LLM 异常时返回兜底结果
- 空消息不调用 LLM
- `responses.parse()` 接收 Pydantic 模型
- 缺少结构化响应时抛出统一异常

最终检查结果：

```text
62 passed
All checks passed!
No broken requirements found.
```

## 今日收获

1. 学会使用 Pydantic 描述大模型结构化输出。
2. 学会使用 Responses API 的结构化解析功能。
3. 理解结构化输出比手动解析 JSON 字符串更可靠。
4. 学会在 LLM 不可用时保持业务服务稳定。
5. 学会使用参数化测试覆盖多类客户表达。
6. 学会使用 Mock 测试模型集成而不消耗真实 Token。

## 面试表达

我在 ServiceMind 中使用 Pydantic 定义了包含意图、订单号、风险等级和判断依据的结构化输出模型，并通过 OpenAI Responses API 的结构化解析能力直接获得经过校验的业务对象。为避免模型服务故障影响工单主流程，我为未配置密钥、调用异常、无效输出和空消息设计了统一安全兜底。同时使用 Mock 和参数化测试覆盖 15 类客户表达，不依赖网络，也不消耗真实 Token。

## 当前边界

- 当前没有配置真实 API Key，尚未验证真实模型的语义识别准确率。
- 当前意图提取服务尚未暴露为独立 HTTP 接口。
- 当前没有保存意图提取历史和 Token 使用情况。
- 15 条输入测试验证结构化处理流程，真实模型效果仍需配置 API Key 后评估。

## Day 16 完成情况

- [x] 定义意图枚举和风险等级枚举
- [x] 定义 `IntentExtraction`
- [x] 接入 Responses API 结构化输出
- [x] 实现意图提取服务
- [x] 实现空消息和 LLM 异常兜底
- [x] 完成 15 条输入测试
- [x] 完成结构化客户端测试
- [x] 全项目 62 项测试通过
- [x] Ruff 检查通过
- [x] Python 依赖检查通过
- [x] Docker Compose 配置检查通过

# Day 17：Prompt 版本化与同批样本对比

## 今日目标

1. 将 system prompt 和 few-shot 示例从业务代码移到 `prompts/`。
2. 为每个 Prompt 记录版本号、用途、模型家族和输出结构。
3. 支持在不修改业务代码的情况下切换 v1/v2。
4. 使用同一批 15 条样本对比两个 Prompt 版本。
5. 在没有 API Key 时安全执行 dry-run，不产生真实 API 请求。

## 完成内容

### 1. Prompt 目录结构

新增两个独立版本：

```text
prompts/intent_extraction/
├── v1/
│   ├── metadata.json
│   ├── system.md
│   └── examples.json
└── v2/
    ├── metadata.json
    ├── system.md
    └── examples.json
```

v1 是 Day16 使用的基线 Prompt，包含 3 条 few-shot 示例。v2 精简重复指令，并明确账号安全、支付、物流、订单状态、退款、投诉和其他意图之间的分类优先级，包含 5 条示例。

### 2. Prompt 元数据

每个版本记录：

- Prompt 名称和版本号
- 业务用途
- 适用模型家族
- 输出 Pydantic Schema
- 创建日期
- 来源版本和修改说明

### 3. Prompt 加载器

新增 `app/prompts/loader.py`，提供：

- 可用版本发现
- metadata、system prompt 和 examples 加载
- Pydantic 数据校验
- 版本号与元数据一致性校验
- 输出结构校验
- 非法版本和路径穿越拦截
- `lru_cache` 磁盘读取缓存

### 4. IntentService 版本切换

`IntentService` 新增 `prompt_version` 参数，默认使用 v2，也可以显式切换到 v1：

```python
IntentService(prompt_version="v1")
IntentService(prompt_version="v2")
```

Service 会把对应版本的 system prompt、few-shot 示例和当前客户消息组合为模型输入，不再维护硬编码 Prompt。

### 5. 同批样本评估

新增 `evals/intent_extraction_samples.json`，包含 15 条固定样本以及预期意图、订单号和风险等级。

新增 `scripts/compare_intent_prompts.py`：

- 默认 dry-run，不调用真实模型。
- v1/v2 使用完全相同的样本集。
- 可单独选择一个或多个版本。
- 显示示例数量、system prompt 长度和平均模型输入长度。
- 配置 API Key 后可显式使用 `--live` 比较关键字段准确率。

本次 dry-run 结果：

```text
samples: 15
v1: examples=3, system_chars=256, average_input_chars=521.8
v2: examples=5, system_chars=577, average_input_chars=853.8
```

v2 提供了更明确的分类边界，但输入更长。由于没有执行真实模型调用，目前不能判断 v2 的真实准确率是否高于 v1。

### 6. 自动化测试

新增测试覆盖：

- v1/v2 加载和元数据校验
- few-shot 输出结构校验
- 可用版本列表
- Prompt 缓存
- 非法版本和路径穿越拦截
- IntentService 版本切换
- few-shot 与当前消息渲染
- 15 条评估数据读取
- dry-run 同时使用两个版本

最终检查结果：

```text
77 passed
All checks passed!
No broken requirements found.
```

## 今日收获

1. 理解 Prompt 应作为可版本管理的工程资产，而不是散落在业务代码中的字符串。
2. 学会为 Prompt 保存用途、版本、输出契约和变更说明。
3. 学会使用同一评估集进行受控版本对比。
4. 学会将 Prompt 变化与模型变化分开，避免混淆评估结果。
5. 理解 Prompt 更长不等于效果更好，必须通过真实评估验证。
6. 学会设计默认不产生费用、需要显式授权才能调用真实模型的评估脚本。

## 面试表达

我将意图提取 Prompt 从 Service 代码中拆分为独立的版本化资产，每个版本保存 system prompt、few-shot 示例、用途和输出 Schema。应用通过经过校验的加载器切换 v1/v2，并使用同一批 15 条样本进行受控比较。评估脚本默认只做 dry-run，避免误调用付费 API；配置密钥后才允许显式执行真实模型准确率测试。这样可以追踪 Prompt 变更、复现实验并避免凭主观感觉升级 Prompt。

## 当前边界

- 当前尚未配置真实 API Key，因此没有执行 30 次真实模型请求。
- dry-run 只能比较 Prompt 结构、示例数量和输入长度，不能证明真实语义准确率。
- 当前准确率只比较意图、订单号和风险三个关键字段，不评价置信说明文本质量。
- 当前评估结果只打印到终端，尚未持久化为 JSON 或数据库记录。

## Day 17 完成情况

- [x] 创建 Prompt v1 和 v2
- [x] system prompt 移出业务代码
- [x] few-shot 示例移出业务代码
- [x] 记录版本号、用途和输出结构
- [x] 实现 Prompt 加载与缓存
- [x] 拦截非法版本和路径穿越
- [x] IntentService 支持 v1/v2 切换
- [x] 建立 15 条固定评估样本
- [x] 实现安全 dry-run 对比脚本
- [x] 完成 Prompt 版本化自动化测试
- [x] 全项目 77 项测试通过
- [x] Ruff、依赖和 Compose 配置检查通过

# Day 19：LLM 失败降级与人工兜底

## 今日目标

1. 处理结构化结果非法、模型拒答、限流和长输入。
2. 避免将第三方 SDK 异常直接展示给用户。
3. 为每类故障定义明确、稳定的降级动作。
4. 必要时回退到安全结果或建议转接人工客服。
5. 让 SSE 前端能够展示用户可理解的恢复建议。

## 完成内容

### 1. 统一失败模型

新增 `FailureCode`、`FallbackAction` 和 `FailureReply`。统一响应包含：

- 稳定故障代码
- 可直接展示的中文提示
- 降级动作
- 是否适合稍后重试

四类核心故障分别映射为：

```text
INVALID_RESPONSE -> use_rules
MODEL_REFUSAL    -> human_handoff
RATE_LIMITED     -> retry_later
INPUT_TOO_LONG   -> shorten_input
```

### 2. LLM 客户端异常细分

`LLMClient` 新增：

- `LLMInvalidResponseError`
- `LLMRefusalError`

客户端会检查 Responses API 输出内容中的 `refusal` 类型，同时将缺失或无法校验的结构化结果映射为 `LLM_INVALID_RESPONSE`。流式拒答事件也会转换为统一项目异常。

### 3. 结构化意图提取降级

`IntentService` 在调用模型前限制客户消息长度。非法响应、模型拒答和限流分别使用不同降级说明；空消息和其他模型故障仍返回可解析的 `other / unknown` 安全结果，不让模型故障中断业务链路。

### 4. SSE 聊天降级协议

聊天 Service 的 `error` 事件可返回：

```json
{
  "code": "RATE_LIMITED",
  "message": "当前咨询人数较多，智能服务暂时繁忙，请稍后重新尝试。",
  "action": "retry_later",
  "retryable": true
}
```

未配置 API Key 等既有错误继续使用原有格式，避免破坏旧客户端兼容性。

### 5. 长输入保护

聊天和意图提取的业务输入上限为 2000 个字符。服务在调用 OpenAI 前完成检查，因此过长输入不会消耗 Token，也不会占用外部模型请求额度。

### 6. 前端恢复提示

聊天页面新增降级提示卡片，根据 `action` 显示：

- 已切换到基础规则
- 建议稍后重试
- 请缩短输入内容
- 建议转接人工客服

页面继续使用 `textContent` 渲染服务端文本，避免把错误消息或模型内容当成 HTML 执行。

### 7. 自动化验证

新增或扩展测试覆盖：

- 四种统一失败策略
- 结构化结果缺失
- 模型拒答检测
- IntentService 分类降级
- 长输入不调用模型
- SSE 降级事件字段
- 长输入 API 响应
- 前端降级动作标识

最终检查结果：

```text
102 passed
All checks passed!
No broken requirements found.
```

## 今日遇到的问题

### Mock 的动态属性不是列表

旧测试中的 `Mock` 没有显式设置 `output`。直接访问该属性会生成新的 `Mock`，不能按照 Responses API 的列表结构迭代。拒答检测增加了列表或元组类型判断，使客户端面对不完整测试对象或异常响应时也不会崩溃。

### 测试函数粘贴到另一个测试内部

新增拒答测试时一度被缩进到空流测试内部，导致 pytest 没有收集该测试，并污染了原测试断言。修复后两个测试恢复独立，分别验证空流和模型拒答。

## 今日收获

1. LLM 应用必须把第三方异常转换为业务可理解的失败协议。
2. “捕获异常”不等于“完成降级”，还需要告诉上层下一步做什么。
3. 长输入应尽早拦截，避免不必要的模型成本和超时。
4. 模型拒答与服务不可用语义不同，不能使用同一个错误提示。
5. SSE 在开始返回后不能再修改 HTTP 状态码，因此错误也需要通过事件协议表达。
6. 降级路径与正常路径一样需要自动化测试。

## 面试表达

我为 ServiceMind 设计了统一的 LLM 失败降级层，将非法结构化响应、模型拒答、API 限流和输入过长映射为稳定的错误码与降级动作。IntentService 会返回可解析的安全结果，SSE 接口会向前端传递 action 和 retryable，页面据此提示规则兜底、稍后重试、缩短输入或转人工。所有故障均使用 Mock 和接口测试覆盖，不依赖真实模型，也不会消耗 Token。

## 当前边界

- `use_rules` 当前返回安全的 `other / unknown` 结果，尚未实现完整的关键词意图规则分类。
- 人工转接目前是建议动作，尚未自动创建人工工单。
- 限流提示不会在浏览器中自动重试，避免产生重试风暴。
- 输入长度目前按字符数计算，尚未按模型 Token 数量精确估算。

## Day 19 完成情况

- [x] 四类重点故障模型
- [x] 统一降级动作和用户提示
- [x] 结构化非法响应检测
- [x] 模型拒答检测
- [x] IntentService 故障降级
- [x] SSE 故障降级协议
- [x] 长输入调用前拦截
- [x] 前端降级提示卡片
- [x] 102 项自动化测试通过
- [x] Docker 镜像升级为 Day19
- [x] Ruff、依赖、Compose 和差异检查通过

# Day 20：小型意图与风险评测集

## 今日目标

1. 创建 20 条人工标注意图与风险标签的固定评测集。
2. 将金标准与模型预测分离，避免评测时污染人工标签。
3. 编写无需 API Key 也能复现的统计脚本。
4. 输出正确数、准确率、意图混淆矩阵、错误样本和错误原因。
5. 为数据校验、统计结果和异常输入补充自动化测试。

## 完成内容

### 1. JSONL 人工标注金标准

新增 `evals/intent_cases.jsonl`，每一行都是独立 JSON 对象，字段包括：

- `id`：稳定且唯一的样本标识
- `input`：客户原始消息
- `expected_intent`：人工标注意图
- `expected_risk`：人工标注风险等级
- `annotation_reason`：标注依据

20 条样本覆盖 `order_status`、`refund`、`logistics`、`payment`、`account_security`、`complaint` 和 `other` 七类意图，同时覆盖 low、medium、high、unknown 四级风险。

### 2. 可复现的基线预测

新增 `evals/intent_predictions_baseline.jsonl`，保存与 20 条样本一一对应的候选预测及预测依据。金标准和预测分开保存，既能防止评测脚本读取答案生成预测，也能让同一评测集比较不同模型或 Prompt 版本。

当前固定基线故意保留三条典型错误：

1. 把“商品损坏并投诉”误判为物流问题。
2. 把“重复扣款”误判为账户安全问题。
3. 正确识别营业时间咨询为 other，但把 low 风险判为 unknown。

这些错误让混淆矩阵和错误分析路径可以在没有真实 API Key 时被完整验证。

### 3. 评测统计脚本

新增 `scripts/evaluate_intent_cases.py`，负责：

- 逐行读取并校验 JSONL
- 拒绝空文件、无效 JSON、重复 id
- 检查预测是否存在缺失或多余 id
- 统计完全正确数、意图正确数和风险正确数
- 构建 expected 到 predicted 的意图混淆矩阵
- 输出错误样本、标签差异和预测依据
- 可选保存 Pydantic 校验后的 JSON 报告

默认运行方式：

```powershell
python -m scripts.evaluate_intent_cases
```

当前基线输出：

```text
总样本：20
完全正确：17/20 (85.0%)
意图正确：18/20 (90.0%)
风险正确：19/20 (95.0%)
错误样本：3
```

### 4. 自动化验证

新增 `tests/test_intent_evaluation.py`，覆盖：

- 评测集正好包含 20 个唯一样本
- 七类意图均被覆盖
- 所有样本都有人工标注原因
- 基线预测与金标准 id 完全一致
- 正确数和三种准确率计算正确
- 混淆矩阵计数正确
- 缺少预测时明确报错
- 重复样本 id 被拒绝
- 终端报告包含统计与错误原因

## 今日遇到的问题

### 评测集不能直接复用单元测试参数

单元测试样本主要验证代码分支，随着实现变化可能增删；评测集则需要稳定、可追踪并与候选预测严格对齐。因此 Day20 使用独立 JSONL 文件，不从 pytest 参数动态拼接数据。

### 没有 API Key 时如何验证统计链路

直接调用未配置的 LLM 会让所有结果进入兜底，无法验证混淆矩阵和错误原因。解决方式是保存一份明确标为 baseline 的固定预测快照。它只用于复现评测器行为，不冒充真实线上模型成绩。

## 今日收获

1. 金标准、候选预测和评测器应当相互独立。
2. 只报告总准确率会隐藏具体类别之间的混淆。
3. 评测数据必须带稳定 id，才能可靠对齐结果并定位回归。
4. 错误分析需要同时保存预期标签、预测标签和判断依据。
5. JSONL 适合逐条追加、审阅和处理小型评测数据。
6. 离线固定预测可以验证统计代码，但不能替代真实模型评测。

## 面试表达

我为 ServiceMind 建立了独立的小型意图评测体系：使用 JSONL 保存 20 条人工标注的意图与风险金标准，通过稳定 id 与候选预测对齐，统计完全正确率、意图准确率、风险准确率和意图混淆矩阵，并输出每条错误样本的标签差异与原因。为了让项目在没有真实 API Key 时仍可复现，我保留了一份明确标识的基线预测快照；它只验证评测链路，不用于夸大模型效果。数据加载、id 完整性、统计结果和错误路径全部有自动化测试。

## 当前边界

- 当前基线预测是固定快照，不是真实线上模型运行结果。
- 20 条样本规模较小，只适合开发阶段快速回归，不能代表生产分布。
- 当前没有按类别样本量加权，也没有计算 precision、recall 和 F1。
- 样本由单人标注，尚未进行多人一致性检查。
- 当前报告保存在终端或可选 JSON 文件，尚未接入持续集成趋势图。

## Day 20 完成情况

- [x] 20 条人工标注意图与风险样本
- [x] 七类意图和四级风险覆盖
- [x] 独立基线预测快照
- [x] JSONL 严格加载与 id 对齐
- [x] 完全正确率、意图准确率和风险准确率
- [x] 意图混淆矩阵
- [x] 错误样本与原因输出
- [x] 自动化测试覆盖数据和统计逻辑
- [x] Docker 镜像升级为 Day20
- [x] 全量测试、Ruff、依赖和 Compose 检查通过

# Day 18：SSE 流式输出与聊天演示页面

## 今日目标

1. 使用 OpenAI Responses API 获取增量文本。
2. 使用 FastAPI `StreamingResponse` 暴露 SSE 接口。
3. 定义稳定的流式事件协议和结束信号。
4. 创建不依赖前端框架的简单聊天页面。
5. 在没有真实 API Key 时仍可验证完整流式链路。

## 完成内容

### 1. Responses API 流式客户端

扩展 `LLMClient`，新增 `stream_text()`：

- 请求参数使用 `stream=True`
- 只消费 `response.output_text.delta` 文本增量事件
- 忽略与文本无关的生命周期事件
- 将流建立阶段和迭代阶段的 SDK 异常映射为项目统一异常
- 拒绝没有任何有效文本的空流
- 未配置 API Key 时抛出稳定的 `LLM_NOT_CONFIGURED` 错误

### 2. SSE 事件协议

新增聊天 Service，并统一生成以下事件：

```text
start -> delta -> ... -> done
                 \-> error
```

- `start`：说明流已开始以及当前运行模式
- `delta`：携带一段新增文本
- `done`：表示本次回复正常完成
- `error`：携带稳定错误码与安全错误信息并终止流

所有 SSE 数据使用 JSON 编码和 UTF-8 中文，事件之间使用空行分隔。

### 3. FastAPI 流式接口

新增：

```http
POST /chat/stream
```

接口使用 `StreamingResponse` 和 `text/event-stream`，并设置：

- `Cache-Control: no-cache`
- `X-Accel-Buffering: no`

OpenAPI 同步声明 `text/event-stream` 响应类型。

### 4. 原生聊天页面

新增：

```http
GET /chat
```

页面只使用原生 HTML、CSS 和 JavaScript，不引入 Streamlit 或额外前端依赖。浏览器通过 `fetch()` 和 `ReadableStream` 读取响应，使用缓冲区处理网络分块可能从任意位置断开的情况，再按 SSE 空行边界解析事件。

模型文本通过 `textContent` 追加显示，不作为 HTML 执行，降低脚本注入风险。页面显示连接状态、流式光标、错误信息和完成状态。

### 5. 无密钥演示模式

聊天请求支持显式的 `demo=true`。该模式不调用外部模型、不消耗 Token，用固定分段文本验证：

- HTTP 流式传输
- SSE 事件解析
- 浏览器增量渲染
- `done` 结束信号

网页会明确显示“无 API Key 演示模式”，避免把演示内容误认为真实模型回答。取消勾选后才会使用真实 LLM 配置。

### 6. 自动化测试与容器验证

新增测试覆盖：

- LLM 文本增量流
- 无密钥流式调用
- 空流拒绝
- SSE JSON 编码
- 聊天 Service 正常流、错误流和演示流
- SSE 响应头与事件顺序
- 空消息 422 校验
- OpenAPI 流式响应描述
- 聊天 HTML 页面可访问性

Docker 镜像升级为：

```text
servicemind-api:day18
```

API 与 PostgreSQL 容器均通过健康检查，容器内 `/chat` 页面和 `/chat/stream` 接口完成验证。

最终检查结果：

```text
88 passed
All checks passed!
No broken requirements found.
```

## 今日遇到的问题

### 1. 流式测试不能直接读取 `response.text`

HTTPX 流式响应在读取前没有完整 `_content`，直接访问 `response.text` 会触发 `ResponseNotRead`。测试改为先调用 `response.read()`，再使用 UTF-8 解码。

### 2. Docker Hub 临时返回 EOF

构建阶段读取 `python:3.14-slim` 元数据时，Docker Hub 连接临时中断。该问题与 Dockerfile 语法无关，重新拉取基础镜像后构建成功。

## 今日收获

1. 理解普通 HTTP 响应与流式响应的差异。
2. 学会使用 Responses API 的语义化流事件。
3. 学会设计 `start`、`delta`、`done`、`error` 生命周期。
4. 学会使用 FastAPI `StreamingResponse` 返回 SSE。
5. 学会在浏览器中处理跨网络分块的 SSE 文本。
6. 学会在没有 API Key 时建立可验证、明确标识的演示路径。
7. 理解流式内容在生产环境中需要额外考虑审核、断线和取消请求。

## 面试表达

我在 ServiceMind 中基于 OpenAI Responses API 和 FastAPI `StreamingResponse` 实现了 SSE 流式聊天链路。LLM 客户端只消费文本增量事件，Service 层把模型输出转换为稳定的 `start`、`delta`、`done` 和 `error` 协议，浏览器使用 `ReadableStream` 处理任意网络分块并实时追加内容。为了让项目在没有真实 API Key 时仍可验收，我增加了明确标识、不会调用外部模型的演示模式。整条链路通过 Mock、接口测试和 Docker 容器验证，不依赖真实 Token。

## 当前边界

- 当前没有配置真实 API Key，因此只完成协议、Mock 和本地演示流验证。
- 当前聊天接口没有保存多轮会话历史。
- 当前没有实现客户端取消请求和服务端断线检测。
- 当前没有统计首个 Token 延迟、总生成时间和 Token 用量。
- 流式输出在生产环境中还需要补充内容审核、限流和身份认证。

## Day 18 完成情况

- [x] Responses API 流式文本客户端
- [x] 统一流式异常映射
- [x] SSE 事件编码
- [x] `POST /chat/stream`
- [x] `start`、`delta`、`done`、`error` 事件协议
- [x] `GET /chat` 原生演示页面
- [x] 无 API Key 演示模式
- [x] 流式接口与页面自动化测试
- [x] Docker 镜像升级为 Day18
- [x] 全项目 88 项测试通过
- [x] Ruff、依赖和 Compose 配置检查通过
