from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.core.database import SessionLocal
from app.models import Customer, Order, Ticket


def query_database() -> None:
    """查询客户、订单、工单及其关联关系。"""

    with SessionLocal() as session:
        customer = session.scalar(
            select(Customer)
            .options(
                selectinload(Customer.orders),
                selectinload(Customer.tickets),
            )
            .where(
                Customer.email == "xiaowang@example.com",
            )
        )

        order = session.scalar(
            select(Order)
            .options(
                joinedload(Order.customer),
            )
            .where(
                Order.order_number == "SM-20260727-001",
            )
        )

        ticket = session.scalar(
            select(Ticket)
            .options(
                joinedload(Ticket.customer),
                joinedload(Ticket.order),
            )
            .where(
                Ticket.id == 1,
            )
        )

        if customer is None:
            raise RuntimeError("Customer seed data not found")

        if order is None:
            raise RuntimeError("Order seed data not found")

        if ticket is None:
            raise RuntimeError("Ticket seed data not found")

        print(
            "Customer:",
            customer.id,
            customer.name,
            customer.level,
            f"orders={len(customer.orders)}",
            f"tickets={len(customer.tickets)}",
        )
        print(
            "Order:",
            order.id,
            order.order_number,
            order.total_amount,
            f"customer={order.customer.name}",
        )
        print(
            "Ticket:",
            ticket.id,
            ticket.issue_type,
            ticket.priority,
            f"customer={ticket.customer.name}",
            f"order={ticket.order.order_number if ticket.order else None}",
        )


if __name__ == "__main__":
    query_database()