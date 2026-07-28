from sqlalchemy.orm import Session

from app.core.exceptions import OrderNotFoundError
from app.models import Order
from app.repositories.order_repository import get_order_by_id


def get_order(
    session: Session,
    order_id: int,
) -> Order:
    """查询订单，不存在时抛出统一资源异常。"""
    order = get_order_by_id(
        session,
        order_id,
    )
    if order is None:
        raise OrderNotFoundError(order_id)

    return order