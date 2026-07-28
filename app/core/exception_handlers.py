from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import ResourceNotFoundError
from app.schemas.errors import ErrorDetail, ErrorResponse


async def resource_not_found_handler(
    request: Request,
    error: ResourceNotFoundError,
) -> JSONResponse:
    """将所有资源不存在异常转换为统一 404 JSON。"""
    response = ErrorResponse(
        error=ErrorDetail(
            code=error.code,
            message=error.message,
            resource=error.resource,
            resource_id=error.resource_id,
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response.model_dump(),
    )


def register_exception_handlers(
    app: FastAPI,
) -> None:
    """注册项目级异常处理器。"""
    app.add_exception_handler(
        ResourceNotFoundError,
        resource_not_found_handler,
    )