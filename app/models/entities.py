from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Customer(Base):
    """客户 ORM 模型。"""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    level: Mapped[str] = mapped_column(
        String(20),
        default="普通",
        nullable=False,
    )
    is_vip: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Order(Base):
    """订单 ORM 模型。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="orders",
    )
    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="order",
    )


class Ticket(Base):
    """工单 ORM 模型。"""

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        index=True,
        nullable=False,
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id"),
        index=True,
        nullable=True,
    )
    issue_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    wait_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    priority: Mapped[str] = mapped_column(
        String(10),
        default="P3",
        nullable=False,
    )
    assigned_team: Mapped[str] = mapped_column(
        String(100),
        default="客服组",
        nullable=False,
    )
    sla_minutes: Mapped[int] = mapped_column(
        Integer,
        default=240,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        default="待规则引擎处理",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="received",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="tickets",
    )
    order: Mapped["Order | None"] = relationship(
        back_populates="tickets",
    )