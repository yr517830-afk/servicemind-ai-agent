from fastapi import APIRouter

from app.clients.llm_client import llm_client


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """检查 ServiceMind API 是否正常运行。"""
    return {
        "status": "ok",
        "service": "ServiceMind",
    }


@router.get("/health/llm")
def llm_health_check() -> dict[str, object]:
    """检查 LLM 客户端的本地配置状态。"""
    return llm_client.health()