import logging

import pytest
from ticket_core.models import (
    IssueType,
    Priority,
)
from ticket_core.rules import decide_ticket

@pytest.mark.parametrize(
    (
        "issue_type",
        "wait_minutes",
        "use_vip",
        "expected_priority",
        "expected_team"
    ),
    [
        (
            IssueType.PAYMENT,
            0,
            False,
            Priority.P0,
            "账号与支付安全组"
        ),
        (
            IssueType.ACCOUNT,
            0,
            False,
            Priority.P0,
            "账号与支付安全组",
        ),
        (
            IssueType.LOGISTICS,
            120,
            False,
            Priority.P1,
            "综合客服组",
        ),
        (
            IssueType.LOGISTICS,
            10,
            True,
            Priority.P1,
            "VIP 客服组",
        ),
        (
            IssueType.REFUND,
            10,
            False,
            Priority.P2,
            "退款售后组",
        ),
        (
            IssueType.OTHER,
            10,
            False,
            Priority.P3,
            "综合客服组",
        ),
        (
            IssueType.PAYMENT,
            999,
            True,
            Priority.P0,
            "账号与支付安全组",
        ),
        (
            IssueType.REFUND,
            180,
            True,
            Priority.P1,
            "综合客服组",
        ),
    ],
    ids=[
        "payment-security",
        "account-security",
        "overdue-logistics",
        "vip-logistics",
        "normal-refund",
        "normal-other",
        "security-before-vip-and-overdue",
        "overdue-before-vip-and-refund",
    ],
)
def test_ticket_routing_rules(
        ticket_factory,
        normal_customer,
        vip_customer,
        issue_type,
        wait_minutes,
        use_vip,
        expected_priority,
        expected_team,
) -> None:
    """不同工单场景应该得到正确的优先级和处理团队。"""

    customer = vip_customer if use_vip else normal_customer

    ticket =ticket_factory(
        issue_type = issue_type,
        customer_name = customer.name,
        message = "规则测试工单",
        wait_minutes = wait_minutes,
    )

    decision = decide_ticket(ticket,customer)

    assert decision.priority == expected_priority
    assert decision.assigned_team == expected_team
    assert decision.sla_minutes > 0
    assert decision.reason

def test_ticket_routing_writes_decision_log(
    caplog: pytest.LogCaptureFixture,
    ticket_factory,
    vip_customer,
) -> None:
    """规则执行后应该记录命中的规则和路由结果。"""
    ticket = ticket_factory(
        issue_type=IssueType.LOGISTICS,
        customer_name=vip_customer.name,
        message="查询物流进度",
        wait_minutes=10,
    )

    with caplog.at_level(
        logging.INFO,
        logger="ticket_core.rules",
    ):
        decision = decide_ticket(
            ticket,
            vip_customer,
        )

    assert decision.priority == Priority.P1
    assert "命中规则=vip" in caplog.text
    assert f"优先级={decision.priority.value}" in caplog.text
    assert f"团队={decision.assigned_team}" in caplog.text
    assert f"SLA={decision.sla_minutes}分钟" in caplog.text