import  pytest

from ticket_core.models import (
    CustomerProfile,
    IssueType,
    TicketInput,
)

@pytest.fixture
def normal_customer() -> CustomerProfile:
    """创建一个普通客户，供测试重复使用。"""

    return  CustomerProfile(
        customer_id=1001,
        name="普通客户",
        level="普通",
        is_vip=False,
    )

@pytest.fixture
def vip_customer() -> CustomerProfile:
    """创建一个VIP客户，供测试重复使用。"""

    return  CustomerProfile(
        customer_id=1002,
        name="VIP客户",
        level="VIP",
        is_vip=True,
    )

@pytest.fixture
def ticket_factory():
    """返回一个可以快速创建测试工单的函数。"""

    def make_ticket(
            issue_type: IssueType = IssueType.OTHER,
            customer_name: str = "测试客户",
            message: str = "测试工单信息",
            wait_minutes: int = 0,
    ) -> TicketInput:
        return TicketInput(
            customer_name = customer_name,
            issue_type = issue_type,
            message = message,
            wait_minutes = wait_minutes,
        )

    return make_ticket
