class InvalidTicketError(ValueError):
    """工单数据不合法时抛出的异常。"""


class UnknownIssueTypeError(ValueError):
    """工单问题类型不被系统支持时抛出的异常。"""


if __name__ == "__main__":
    try:
        raise InvalidTicketError("客户名称不能为空。")
    except InvalidTicketError as error:
        print(f"捕获到工单错误：{error}")