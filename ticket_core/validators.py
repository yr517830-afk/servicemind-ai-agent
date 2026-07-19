from ticket_core.exceptions import InvalidTicketError, UnknownIssueTypeError
from ticket_core.models import IssueType, TicketInput


def validate_ticket_input(ticket: TicketInput) -> None:
    """检查工单输入是否符合基本要求。"""

    if not ticket.customer_name.strip():
        raise InvalidTicketError("客户名称不能为空。")

    if not ticket.message.strip():
        raise InvalidTicketError("工单消息不能为空。")

    if ticket.wait_minutes < 0:
        raise InvalidTicketError("等待时间不能小于 0。")

    if not isinstance(ticket.issue_type, IssueType):
        raise UnknownIssueTypeError("不支持的工单问题类型。")


if __name__ == "__main__":
    valid_ticket = TicketInput(
        customer_name="小王",
        issue_type=IssueType.LOGISTICS,
        message="我的订单什么时候到？",
        wait_minutes=15,
    )

    validate_ticket_input(valid_ticket)
    print("合法工单校验通过。")

    try:
        invalid_ticket = TicketInput(
            customer_name="",
            issue_type=IssueType.OTHER,
            message="我要咨询订单。",
            wait_minutes=5,
        )

        validate_ticket_input(invalid_ticket)
    except InvalidTicketError as error:
        print(f"捕获到校验错误：{error}")