import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "routing_rules.json"

def load_routing_rules(config_path:Path = DEFAULT_CONFIG_PATH,) -> dict:
    """读取并返回工单路由规则"""
    with config_path.open("r",encoding="utf-8") as  file:
        rules = json.load(file)

    return rules

if __name__ == "__main__":
    routing_rules = load_routing_rules()
    print(f"配置文件位置：{DEFAULT_CONFIG_PATH}")
    print("路由规则加载成功！")

    for rule_name,rule in routing_rules.items():
        print(f"{rule_name}: "
            f"{rule['priority']} -> "
            f"{rule['assigned_team']}")
