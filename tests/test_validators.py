import pytest

from ticket_core.exceptions import (
    InvalidTicketError,
    UnknownIssueTypeError,
)
from ticket_core.models import IssueType
from ticket_core.validators import validate_ticket_input

def test_valid_ticket_passes(ticket_factory) -> None:
    """合法工单应该顺利通过校验。"""

    ticket = ticket_factory(
        issue_type=IssueType.LOGISTICS,
        customer_name="小王",
        message="查询物流信息",
        wait_minutes=0,
    )

    validate_ticket_input(ticket)

@pytest.mark.parametrize(
    "customer_name",
    [
        "",
        "   ",
    ]
)
def test_blank_customer_name_raises(
        ticket_factory,
        customer_name,
) -> None:
    """客户名称为空或只有空格时应该报错。"""

    ticket = ticket_factory(customer_name=customer_name)

    with pytest.raises(
        InvalidTicketError,
        match="客户名称不能为空",
    ):
        validate_ticket_input(ticket)

@pytest.mark.parametrize(
    "message",
    [
        "",
        "   ",
    ]
)
def test_blank_message_raises(
        ticket_factory,
        message,
) -> None:
    """问题描述为空或只有空格时应该报错。"""

    ticket = ticket_factory(message=message)

    with pytest.raises(
        InvalidTicketError,
        match="工单消息不能为空",
    ):
        validate_ticket_input(ticket)

def test_negative_wait_minutes_raises(ticket_factory) -> None:
    """等待时间小于零时应该报错。"""

    ticket = ticket_factory(wait_minutes= -1)
    with pytest.raises(
        InvalidTicketError,
        match="等待时间不能小于 0",
    ):
        validate_ticket_input(ticket)

def test_unknown_issue_type_raises(ticket_factory) -> None:
    """问题类型不是 IssueType 枚举时应该报错。"""

    ticket = ticket_factory(issue_type="退款")

    with pytest.raises(
        UnknownIssueTypeError,
        match="不支持的工单问题类型",
    ):
        validate_ticket_input(ticket)