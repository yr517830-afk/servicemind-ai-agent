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