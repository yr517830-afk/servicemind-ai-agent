from ticket_core.models import (
    CustomerProfile,
    IssueType,
    Priority,
    TicketDecision,
    TicketInput,
)


def decide_ticket(
    ticket: TicketInput,
    customer: CustomerProfile,
) -> TicketDecision:
    """根据工单和客户信息，生成处理决策。"""

    if ticket.issue_type in (IssueType.PAYMENT, IssueType.ACCOUNT):
        return TicketDecision(
            priority=Priority.P0,
            assigned_team="账号与支付安全组",
            sla_minutes=15,
            reason="涉及支付或账号安全，需要最高优先级处理。",
        )

    if ticket.wait_minutes >= 120:
        return TicketDecision(
            priority=Priority.P1,
            assigned_team="综合客服组",
            sla_minutes=30,
            reason="用户等待时间超过 120 分钟。",
        )

    if customer.is_vip:
        return TicketDecision(
            priority=Priority.P1,
            assigned_team="VIP 客服组",
            sla_minutes=30,
            reason="VIP 客户需要优先响应。",
        )

    if ticket.issue_type == IssueType.REFUND:
        return TicketDecision(
            priority=Priority.P2,
            assigned_team="退款售后组",
            sla_minutes=60,
            reason="普通退款咨询。",
        )

    return TicketDecision(
        priority=Priority.P3,
        assigned_team="综合客服组",
        sla_minutes=120,
        reason="普通咨询工单。",
    )


if __name__ == "__main__":
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

    print("8条工单规则测试全部通过！")