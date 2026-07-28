from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.errors import ErrorResponse
from app.schemas.orders import OrderResponse
from app.services.order_service import get_order


router = APIRouter(
    prefix="/orders",
    tags=["订单"],
)

SessionDependency = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "订单不存在。",
        },
    },
)
def get_order_detail(
    order_id: Annotated[
        int,
        Path(
            ge=1,
            description="需要查询的订单编号。",
        ),
    ],
    session: SessionDependency,
) -> OrderResponse:
    """查询一张订单的详细信息。"""
    order = get_order(
        session,
        order_id,
    )

    return OrderResponse.model_validate(order)