from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order


def get_order_by_id(
    session: Session,
    order_id: int,
) -> Order | None:
    """按数据库编号查询订单。"""
    return session.get(Order, order_id)


def get_order_for_customer(
    session: Session,
    order_id: int,
    customer_id: int,
) -> Order | None:
    """查询属于指定客户的订单。"""
    statement = select(Order).where(
        Order.id == order_id,
        Order.customer_id == customer_id,
    )
    return session.scalar(statement)
