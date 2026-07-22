import logging
import sqlite3
from pathlib import Path

from ticket_core.models import (
    TicketDecision,
    TicketInput,
)


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "servicemind.db"


def initialize_database(
    database_path: Path = DATABASE_PATH,
) -> None:
    """创建数据库目录和工单表。"""

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                message TEXT NOT NULL,
                wait_minutes INTEGER NOT NULL,
                priority TEXT NOT NULL,
                assigned_team TEXT NOT NULL,
                sla_minutes INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    logger.info(
        "数据库初始化完成：%s",
        database_path,
    )


def save_ticket(
    ticket: TicketInput,
    decision: TicketDecision,
    database_path: Path = DATABASE_PATH,
) -> int:
    """保存工单及其决策，并返回数据库编号。"""

    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                customer_name,
                issue_type,
                message,
                wait_minutes,
                priority,
                assigned_team,
                sla_minutes,
                reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket.customer_name,
                ticket.issue_type.value,
                ticket.message,
                ticket.wait_minutes,
                decision.priority.value,
                decision.assigned_team,
                decision.sla_minutes,
                decision.reason,
            ),
        )

        ticket_id = cursor.lastrowid

    logger.info(
        "工单保存成功：ticket_id=%s",
        ticket_id,
    )

    return ticket_id


def ticket_exists(
    ticket: TicketInput,
    database_path: Path = DATABASE_PATH,
) -> bool:
    """判断数据库中是否已经存在相同工单。"""

    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        existing_ticket = connection.execute(
            """
            SELECT 1
            FROM tickets
            WHERE customer_name = ?
              AND issue_type = ?
              AND message = ?
            LIMIT 1
            """,
            (
                ticket.customer_name,
                ticket.issue_type.value,
                ticket.message,
            ),
        ).fetchone()

    return existing_ticket is not None

def list_tickets(
    database_path: Path = DATABASE_PATH,
) -> list[sqlite3.Row]:
    """查询最近保存的工单。"""

    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT
                id,
                customer_name,
                issue_type,
                priority,
                assigned_team,
                sla_minutes,
                created_at
            FROM tickets
            ORDER BY id DESC
            LIMIT 10
            """
        ).fetchall()

    return rows

if __name__ == "__main__":
    from ticket_core.models import (
        CustomerProfile,
        IssueType,
    )
    from ticket_core.rules import decide_ticket

    demo_ticket = TicketInput(
        customer_name="小王",
        issue_type=IssueType.REFUND,
        message="退款一直没有到账",
        wait_minutes=30,
    )

    demo_customer = CustomerProfile(
        customer_id=3001,
        name="小王",
        level="普通",
        is_vip=False,
    )

    demo_decision = decide_ticket(
        demo_ticket,
        demo_customer,
    )

    saved_ticket_id = save_ticket(
        demo_ticket,
        demo_decision,
    )

    print(f"工单保存成功，编号：{saved_ticket_id}")
    print("数据库中的最近工单：")

    for saved_ticket in list_tickets():
        print(dict(saved_ticket))