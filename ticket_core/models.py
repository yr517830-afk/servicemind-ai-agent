from dataclasses import dataclass
from enum import Enum

class IssueType(str,Enum):
    LOGISTICS = "物流"
    REFUND = "退款"
    ACCOUNT = "账号"
    PAYMENT = "支付"
    OTHER = "其他"

class Priority(str,Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

@dataclass
class TicketInput:
    customer_name: str
    issue_type: IssueType
    message: str
    wait_minutes: int = 0

@dataclass
class CustomerProfile:
    customer_id: int
    name: str
    level: str="普通"
    is_vip: bool=False

@dataclass
class TicketDecision:
    priority: Priority
    assigned_team: str
    sla_minutes: int
    reason: str

if __name__ == "__main__":
    ticket = TicketInput(
        customer_name="小王",
        issue_type=IssueType.LOGISTICS,
        message="我的订单什么时候到?",
        wait_minutes=15,
    )
    customer = CustomerProfile(
        customer_id=1001,
        name="小王",
        level="VIP",
        is_vip=True,
    )
    decision = TicketDecision(
        priority=Priority.P2,
        assigned_team="物流组",
        sla_minutes=60,
        reason="普通物流，未超过等待阈值.",
    )

    print(ticket)
    print(customer)
    print(decision)

