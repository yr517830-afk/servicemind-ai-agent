from ticket_core.models import (CustomerProfile,
    IssueType,
    TicketInput,
)
from ticket_core.repository import (
    list_tickets,
    save_ticket,
    ticket_exists,
)
from ticket_core.rules import decide_ticket
from ticket_core.validators import validate_ticket_input

def show_menu() -> None:
    """显示 ServiceMind 系统主菜单。"""
    print("\n============================")
    print(" ServiceMind 智能工单系统")
    print("============================")
    print("1. 创建新工单")
    print("2. 查询历史工单")
    print("0. 退出系统")

def input_issue_type() -> IssueType:
    """让用户输入问题类型，并返回对应的枚举对象。"""

    while True:
        print("\n支持的问题类型：物流、退款、账号、支付、其他")
        issue_type_text = input("请输入问题类型：").strip()

        try:
            return IssueType(issue_type_text)
        except ValueError:
            print("问题类型错误，请重新输入。")

def input_required_text(prompt:str) -> str:
    """接收不能为空的文本输入。"""

    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("输入不能为空请重新输入")

def input_wait_minutes() -> int:
    """接收大于或等于零的等待分钟数。"""

    while True:
        wait_text = input("请输入等待的分钟数：").strip()

        try:
            wait_minutes = int(wait_text)
        except ValueError:
            print("等待时间必须是整数，请重新输入。")
            continue

        if wait_minutes < 0:
            print("等待时间不能小于0，请重新输入。")
            continue

        return wait_minutes


def input_is_vip() ->bool:
    """接收客户是否为 VIP 的输入。"""
    while True:
        vip_text = input("客户是否为 VIP？（y/n）：").strip().lower()

        if vip_text == "y":
            return True

        if vip_text == "n":
            return False

        print("输入错误，请输入 y 或 n。")

def confirm_save() -> bool:
    """询问用户是否确认保存工单。"""

    while True:
        confirm_text = input("\n是否确认保存？（y/n）：").strip().lower()

        if confirm_text == "y":
            return True

        if confirm_text == "n":
            return False

        print("输入错误，请输入 y 或 n。")

def show_ticket_history() -> None:
    """查询并显示最近保存的工单。"""

    tickets = list_tickets()

    if not tickets:
        print("\n目前还没有保存任何工单。")
        return

    print("\n========== 最近工单 ==========")

    for ticket in tickets:
        print(
            f"编号：{ticket['id']} | "
            f"客户：{ticket['customer_name']} | "
            f"类型：{ticket['issue_type']} | "
            f"优先级：{ticket['priority']} | "
            f"团队：{ticket['assigned_team']} | "
            f"SLA：{ticket['sla_minutes']} 分钟 | "
            f"时间：{ticket['created_at']}"
        )

def main() -> None:
    """运行命令行主菜单。"""

    while True:
        show_menu()
        choice = input("请选择操作: ").strip()

        if choice == "1":
            print("你选择了：创建新工单")

            customer_name = input_required_text("请输入客户名称：")
            issue_type = input_issue_type()
            message = input_required_text("请输入问题描述：")
            wait_minutes = input_wait_minutes()
            is_vip = input_is_vip()
            
            ticket = TicketInput(
                customer_name=customer_name,
                issue_type=issue_type,
                message=message,
                wait_minutes=wait_minutes,
            )

            customer = CustomerProfile(
                customer_id=0,
                name=customer_name,
                level="VIP" if is_vip else "普通",
                is_vip=is_vip,
            )

            validate_ticket_input(ticket)

            decision = decide_ticket(ticket,customer)

            print("\n工单基础信息：")
            print(f"客户名称: {customer_name}")
            print(f"问题类型: {issue_type.value}")
            print(f"问题描述: {message}")
            print(f"等待时间: {wait_minutes}分钟")
            print(f"VIP客户: {'是' if is_vip else '否'}")
            print("工单对象创建并校验成功。")
            print("\n处理决策：")
            print(f"优先级：{decision.priority.value}")
            print(f"处理团队：{decision.assigned_team}")
            print(f"SLA：{decision.sla_minutes} 分钟")
            print(f"判断原因：{decision.reason}")

            if ticket_exists(ticket):
                print("\n发现相同工单，请勿重复提交。")
                continue
                
            if confirm_save():
                ticket_id = save_ticket(ticket, decision)
                print(f"工单保存成功，编号：{ticket_id}")
            else:
                print("已取消保存，本次工单没有写入数据库。")

        elif choice == "2":
            print("你选择了：查询历史工单")
            show_ticket_history()

        elif choice == "0":
            print("已退出 ServiceMind 系统。")
            break
        else:
            print("输出错误，请输入0、1或2。")

if __name__ == "__main__":
   main()