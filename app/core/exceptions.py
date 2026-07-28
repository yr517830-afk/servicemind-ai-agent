class ResourceNotFoundError(LookupError):
    """所有资源不存在异常的基类。"""

    def __init__(
        self,
        *,
        code: str,
        resource: str,
        resource_id: int,
        message: str,
    ) -> None:
        self.code = code
        self.resource = resource
        self.resource_id = resource_id
        self.message = message
        super().__init__(message)


class CustomerNotFoundError(ResourceNotFoundError):
    """客户不存在。"""

    def __init__(self, customer_id: int) -> None:
        super().__init__(
            code="CUSTOMER_NOT_FOUND",
            resource="customer",
            resource_id=customer_id,
            message=f"客户 {customer_id} 不存在。",
        )


class OrderNotFoundError(ResourceNotFoundError):
    """订单不存在或不属于指定客户。"""

    def __init__(
        self,
        order_id: int,
        customer_id: int | None = None,
    ) -> None:
        if customer_id is None:
            message = f"订单 {order_id} 不存在。"
        else:
            message = (
                f"订单 {order_id} 不存在或不属于"
                f"客户 {customer_id}。"
            )

        super().__init__(
            code="ORDER_NOT_FOUND",
            resource="order",
            resource_id=order_id,
            message=message,
        )


class TicketNotFoundError(ResourceNotFoundError):
    """工单不存在。"""

    def __init__(self, ticket_id: int) -> None:
        super().__init__(
            code="TICKET_NOT_FOUND",
            resource="ticket",
            resource_id=ticket_id,
            message=f"工单 {ticket_id} 不存在。",
        )