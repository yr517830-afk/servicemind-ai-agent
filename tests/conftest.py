from collections.abc import Callable, Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import Customer, Order
from ticket_core.models import (
    CustomerProfile,
    IssueType,
    TicketInput,
)


@pytest.fixture
def normal_customer() -> CustomerProfile:
    """创建一个普通客户，供规则测试重复使用。"""
    return CustomerProfile(
        customer_id=1001,
        name="普通客户",
        level="普通",
        is_vip=False,
    )


@pytest.fixture
def vip_customer() -> CustomerProfile:
    """创建一个 VIP 客户，供规则测试重复使用。"""
    return CustomerProfile(
        customer_id=1002,
        name="VIP 客户",
        level="VIP",
        is_vip=True,
    )


@pytest.fixture
def ticket_factory() -> Callable[..., TicketInput]:
    """返回一个可以快速创建测试工单的函数。"""

    def make_ticket(
        issue_type: IssueType = IssueType.OTHER,
        customer_name: str = "测试客户",
        message: str = "测试工单信息",
        wait_minutes: int = 0,
    ) -> TicketInput:
        return TicketInput(
            customer_name=customer_name,
            issue_type=issue_type,
            message=message,
            wait_minutes=wait_minutes,
        )

    return make_ticket


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    """为整套 API 测试提供共享的 SQLite 内存数据库结构。"""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def api_client(
    test_engine: Engine,
) -> Generator[TestClient, None, None]:
    """提供测试结束后自动回滚数据库事务的 API 客户端。"""
    connection = test_engine.connect()
    transaction = connection.begin()

    testing_session_local = sessionmaker(
        bind=connection,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="rollback_only",
    )

    with testing_session_local() as seed_session:
        customer = Customer(
            name="测试 VIP 客户",
            email="vip@example.com",
            level="VIP",
            is_vip=True,
        )
        seed_session.add(customer)
        seed_session.flush()

        order = Order(
            order_number="TEST-ORDER-001",
            customer_id=customer.id,
            status="paid",
            total_amount=Decimal("299.00"),
        )
        seed_session.add(order)
        seed_session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        with testing_session_local() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)

        if transaction.is_active:
            transaction.rollback()

        connection.close()