from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """检查 ServiceMind API 是否正常运行。"""
    return {
        "status": "ok",
        "service": "ServiceMind",
    }