from app.core.database import Base
from app.models import Customer, Order, Ticket


def test_orm_models_register_expected_tables() -> None:
    """ORM 应注册客户、订单和工单三张表。"""

    assert set(Base.metadata.tables) == {
        "customers",
        "orders",
        "tickets",
    }

    assert Customer.__table__ is Base.metadata.tables["customers"]
    assert Order.__table__ is Base.metadata.tables["orders"]
    assert Ticket.__table__ is Base.metadata.tables["tickets"]


def test_orm_models_define_expected_foreign_keys() -> None:
    """订单与工单应包含正确的实体关联。"""

    foreign_keys = {
        (
            table.name,
            foreign_key.parent.name,
            foreign_key.target_fullname,
        )
        for table in Base.metadata.tables.values()
        for foreign_key in table.foreign_keys
    }

    assert foreign_keys == {
        (
            "orders",
            "customer_id",
            "customers.id",
        ),
        (
            "tickets",
            "customer_id",
            "customers.id",
        ),
        (
            "tickets",
            "order_id",
            "orders.id",
        ),
    }