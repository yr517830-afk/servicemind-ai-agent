def normalize_message(messgae: str) -> str:
    """清理用户消息，去掉多余空格并转换成小写。"""
    return" ".join(messgae.strip().lower().split())

assert normalize_message("  Hello  World  ") == "hello world"

print("第一个函数运行成功!")


def unique_preserve_order(items: list[str]) -> list[str]:
    """去除重复元素，但保留他们第一次出现的顺序。"""
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result

assert unique_preserve_order(["苹果","香蕉","苹果","橙子","香蕉"]) == ["苹果","香蕉","橙子"]

print("第二个函数运行成功！")


def word_frequency(text:str) -> dict[str,int]:
    """统计一段文本中，每个单词出现的次数"""
    frequencies = {}

    for word in text.lower().split():
        frequencies[word] = frequencies.get(word,0) + 1

    return frequencies

assert word_frequency("Apple apple banana apple") == {"apple":3,"banana":1}

print("第三个函数运行成功！")


def is_high_risk(message:str) -> bool:
    """消息包含高风险关键词时返回True"""
    risk_keywords = ("退款","取消订单","修改地址","支付")

    return any(keyword in message for keyword in risk_keywords)

assert is_high_risk("我要申请退款") is True
assert is_high_risk("物流什么时候到") is False

print("第四个函数输出成功！")


def average_wait_minutes(wait_times: list[int]) -> float:
    """计算平均等待分钟数；空列表返回 0。"""
    if not wait_times:
        return 0.0
    return sum(wait_times)/len(wait_times)

assert average_wait_minutes([10,20,30]) == 20.0
assert average_wait_minutes([]) == 0.0

print("第五个函数输出成功！")


def find_longest_message(messages: list[str]) -> str:
    """返回最长的一条消息；空列表返回空字符串。"""
    return max(messages,key=len,default="")

assert find_longest_message(["你好", "我要查询订单", "退款"]) == "我要查询订单"
assert find_longest_message([]) == ""

print("第六个函数输出成功！")


def group_by_issue_type(tickets: list[dict]) -> dict[str,list[dict]]:
    """按 issue_type 字段分组工单。"""
    grouped = {}

    for ticket in tickets:
        issue_type = ticket.get("issue_type","unknow")
        grouped.setdefault(issue_type,[]).append(ticket)

    return grouped

tickets = [
    {"id": 1, "issue_type": "物流"},
    {"id": 2, "issue_type": "退款"},
    {"id": 3, "issue_type": "物流"},
]
assert len(group_by_issue_type(tickets)["物流"]) == 2

print("第七个函数运行成功！")


def filter_priority_customers(customers: list[dict]) -> list[dict]:
    """筛选level为VIP的客户"""
    return[customer for customer in customers if customer.get("level") == "VIP"]

customers = [
    {"name": "小王", "level": "VIP"},
    {"name": "小李", "level": "普通"},
    {"name": "小张", "level": "VIP"},
]

assert len(filter_priority_customers(customers)) == 2

print("第八个函数运行成功！")


def safe_get_order_total(order:list) -> float:
    """安全读取订单金额；缺失或非法时返回 0。"""
    total = order.get("total",0)

    if isinstance(total,(int,float)) and not isinstance(total,bool):
        return float(total)

    return 0.0

assert safe_get_order_total({"total": 99.9}) == 99.9
assert safe_get_order_total({"total": "免费"}) == 0.0
assert safe_get_order_total({}) == 0.0

print("第九个函数运行成功！")


def ticket_summary(ticket:dict) -> str:
    """生成一条可读的工单摘要。"""
    customer_name = ticket.get("customer_name", "未知客户")
    issue_type = ticket.get("issue_type", "未知问题")
    wait_minutes = ticket.get("wait_minutes", 0)

    return f"{customer_name} - {issue_type} - 等待 {wait_minutes} 分钟"


assert ticket_summary(
    {
        "customer_name": "小王",
        "issue_type": "物流",
        "wait_minutes": 15,
    }
) == "小王 - 物流 - 等待 15 分钟"

print("第十个函数运行成功！")