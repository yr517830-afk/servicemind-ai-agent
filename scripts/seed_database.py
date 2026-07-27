from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Customer, Order, Ticket


SEED_EMAIL = "xiaowang@example.com"


def seed_database() -> None:
    """插入一组可重复验证的客户、订单和工单数据。"""

    with SessionLocal() as session:
        existing_customer = session.scalar(
            select(Customer).where(
                Customer.email == SEED_EMAIL,
            )
        )

        if existing_customer is not None:
            print("Seed data already exists")
            return

        customer = Customer(
            name="小王",
            email=SEED_EMAIL,
            level="VIP",
            is_vip=True,
        )

        order = Order(
            order_number="SM-20260727-001",
            status="shipped",
            total_amount=Decimal("299.00"),
            customer=customer,
        )

        ticket = Ticket(
            issue_type="物流",
            message="我的订单什么时候送到？",
            wait_minutes=15,
            priority="P2",
            assigned_team="物流组",
            sla_minutes=60,
            reason="VIP 客户咨询物流进度",
            status="received",
            customer=customer,
            order=order,
        )

        session.add_all(
            [
                customer,
                order,
                ticket,
            ]
        )
        session.commit()

        print(
            "Seed data created:",
            f"customer_id={customer.id}",
            f"order_id={order.id}",
            f"ticket_id={ticket.id}",
        )


if __name__ == "__main__":
    seed_database()