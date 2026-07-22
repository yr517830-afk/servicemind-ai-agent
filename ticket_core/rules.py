import logging

from ticket_core.config_loader import (
    DEFAULT_CONFIG_PATH,
    load_routing_rules,
)
from ticket_core.logging_config import configure_logging
from ticket_core.models import (
    CustomerProfile,
    IssueType,
    Priority,
    TicketDecision,
    TicketInput,
)


configure_logging()

logger = logging.getLogger(__name__)

ROUTING_RULES = load_routing_rules()

logger.info(
    "路由配置加载成功：%s",
    DEFAULT_CONFIG_PATH,
)

def _build_decision(rule_name: str) -> TicketDecision:
    """根据配置中的规则名称创建工单决策。"""

    rule = ROUTING_RULES[rule_name]

    decision = TicketDecision(
        priority=Priority(rule["priority"]),
        assigned_team=rule["assigned_team"],
        sla_minutes=rule["sla_minutes"],
        reason=rule["reason"],
    )

    logger.info(
        "命中规则=%s，优先级=%s，团队=%s，SLA=%s分钟",
        rule_name,
        decision.priority.value,
        decision.assigned_team,
        decision.sla_minutes,
    )

    return decision

def decide_ticket(
    ticket: TicketInput,
    customer: CustomerProfile,
) -> TicketDecision:
    """根据工单、客户资料和 JSON 配置生成处理决策。"""

    security_rule = ROUTING_RULES["security"]

    if ticket.issue_type.value in security_rule["issue_types"]:
        return _build_decision("security")

    overdue_rule = ROUTING_RULES["overdue"]

    if ticket.wait_minutes >= overdue_rule["wait_minutes_threshold"]:
        return _build_decision("overdue")

    if customer.is_vip:
        return _build_decision("vip")

    refund_rule = ROUTING_RULES["refund"]

    if ticket.issue_type.value in refund_rule["issue_types"]:
        return _build_decision("refund")

    return _build_decision("default")


if __name__ == "__main__":
    demo_ticket = TicketInput(
        customer_name="配置测试客户",
        issue_type=IssueType.LOGISTICS,
        message="查询物流",
        wait_minutes=0,
    )

    demo_customer = CustomerProfile(
        customer_id=2001,
        name="配置测试客户",
        level="VIP",
        is_vip=True,
    )

    demo_decision = decide_ticket(
        demo_ticket,
        demo_customer,
    )

    print(f"VIP 优先级：{demo_decision.priority.value}")
    print(f"VIP 处理团队：{demo_decision.assigned_team}")
    print(f"VIP SLA：{demo_decision.sla_minutes} 分钟")
    print(f"判断原因：{demo_decision.reason}")

    vip_customer = CustomerProfile(
        customer_id=1001,
        name="小王",
        level="VIP",
        is_vip=True,
    )

    normal_customer = CustomerProfile(
        customer_id=1002,
        name="小李",
        level="普通",
        is_vip=False,
    )

    payment_ticket = TicketInput(
        customer_name="小王",
        issue_type=IssueType.PAYMENT,
        message="我的支付异常。",
        wait_minutes=10,
    )
    assert decide_ticket(payment_ticket, vip_customer).priority == Priority.P0

    delayed_ticket = TicketInput(
        customer_name="小李",
        issue_type=IssueType.LOGISTICS,
        message="我的订单还没到。",
        wait_minutes=120,
    )
    assert decide_ticket(delayed_ticket, normal_customer).priority == Priority.P1

    vip_ticket = TicketInput(
        customer_name="小王",
        issue_type=IssueType.LOGISTICS,
        message="我要查询订单。",
        wait_minutes=10,
    )
    assert decide_ticket(vip_ticket, vip_customer).priority == Priority.P1

    refund_ticket = TicketInput(
        customer_name="小李",
        issue_type=IssueType.REFUND,
        message="我要退款。",
        wait_minutes=10,
    )
    assert decide_ticket(refund_ticket, normal_customer).priority == Priority.P2

    normal_ticket = TicketInput(
        customer_name="小李",
        issue_type=IssueType.OTHER,
        message="我想咨询活动规则。",
        wait_minutes=10,
    )
    assert decide_ticket(normal_ticket, normal_customer).priority == Priority.P3

    account_ticket = TicketInput(
        customer_name="小李",
        issue_type=IssueType.ACCOUNT,
        message="我的账号无法登录。",
        wait_minutes=5,
    )
    assert decide_ticket(account_ticket, normal_customer).priority == Priority.P0

    near_timeout_ticket = TicketInput(
        customer_name="小李",
        issue_type=IssueType.LOGISTICS,
        message="我在等待物流信息。",
        wait_minutes=119,
    )
    assert decide_ticket(near_timeout_ticket, normal_customer).priority == Priority.P3

    vip_refund_ticket = TicketInput(
        customer_name="小王",
        issue_type=IssueType.REFUND,
        message="我要退款。",
        wait_minutes=10,
    )
    assert decide_ticket(vip_refund_ticket, vip_customer).priority == Priority.P1
    # 9. 支付问题，即使不是 VIP，也必须是 P0
    assert (
        decide_ticket(
            TicketInput("小李", IssueType.PAYMENT, "支付失败", 0),
            CustomerProfile(1009, "小李"),
        ).priority
        == Priority.P0
    )

    # 10. 账号问题，即使等待很久，也必须优先判为 P0
    assert (
        decide_ticket(
            TicketInput("小张", IssueType.ACCOUNT, "账号被盗", 999),
            CustomerProfile(1010, "小张"),
        ).priority
        == Priority.P0
    )

    # 11. 物流工单等待满 120 分钟，应进入 P1
    assert (
        decide_ticket(
            TicketInput("小赵", IssueType.LOGISTICS, "订单未到", 120),
            CustomerProfile(1011, "小赵", level="VIP", is_vip=True),
        ).priority
        == Priority.P1
    )

    # 12. 退款工单等待很久时，等待超时规则优先于普通退款规则
    assert (
        decide_ticket(
            TicketInput("小孙", IssueType.REFUND, "退款未到账", 180),
            CustomerProfile(1012, "小孙"),
        ).priority
        == Priority.P1
    )
    
    print("12条工单规则测试全部通过！")