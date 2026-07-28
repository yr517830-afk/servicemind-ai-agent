from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.customers import CustomerResponse
from app.schemas.errors import ErrorResponse
from app.services.customer_service import get_customer


router = APIRouter(
    prefix="/customers",
    tags=["客户"],
)

SessionDependency = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "客户不存在。",
        },
    },
)
def get_customer_detail(
    customer_id: Annotated[
        int,
        Path(
            ge=1,
            description="需要查询的客户编号。",
        ),
    ],
    session: SessionDependency,
) -> CustomerResponse:
    """查询一名客户的详细信息。"""
    customer = get_customer(
        session,
        customer_id,
    )

    return CustomerResponse.model_validate(customer)