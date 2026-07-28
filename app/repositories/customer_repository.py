from sqlalchemy.orm import Session

from app.models import Customer


def get_customer_by_id(
    session: Session,
    customer_id: int,
) -> Customer | None:
    """按数据库编号查询客户。"""
    return session.get(Customer, customer_id)