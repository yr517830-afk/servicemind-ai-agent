from sqlalchemy.orm import Session

from app.core.exceptions import CustomerNotFoundError
from app.models import Customer
from app.repositories.customer_repository import get_customer_by_id


def get_customer(
    session: Session,
    customer_id: int,
) -> Customer:
    """查询客户，不存在时抛出统一资源异常。"""
    customer = get_customer_by_id(
        session,
        customer_id,
    )
    if customer is None:
        raise CustomerNotFoundError(customer_id)

    return customer