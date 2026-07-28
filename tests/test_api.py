from fastapi.testclient import TestClient


def _create_ticket(
    api_client: TestClient,
    *,
    issue_type: str = "物流",
    wait_minutes: int = 15,
) -> dict[str, object]:
    """通过 API 创建一张测试工单。"""
    response = api_client.post(
        "/tickets",
        json={
            "customer_id": 1,
            "order_id": 1,
            "issue_type": issue_type,
            "message": f"测试工单：{issue_type}",
            "wait_minutes": wait_minutes,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_health_check(
    api_client: TestClient,
) -> None:
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ServiceMind",
    }


def test_create_ticket_runs_vip_rule(
    api_client: TestClient,
) -> None:
    ticket = _create_ticket(api_client)

    assert ticket["ticket_id"] == 1
    assert ticket["customer_id"] == 1
    assert ticket["order_id"] == 1
    assert ticket["priority"] == "P1"
    assert ticket["assigned_team"] == "VIP 客服组"
    assert ticket["sla_minutes"] == 30
    assert ticket["status"] == "received"
    assert ticket["created_at"] is not None


def test_get_ticket_returns_persisted_ticket(
    api_client: TestClient,
) -> None:
    created = _create_ticket(api_client)

    response = api_client.get(
        f"/tickets/{created['ticket_id']}",
    )

    assert response.status_code == 200
    assert response.json() == created


def test_list_tickets_supports_pagination_and_filters(
    api_client: TestClient,
) -> None:
    _create_ticket(
        api_client,
        issue_type="物流",
    )
    payment_ticket = _create_ticket(
        api_client,
        issue_type="支付",
    )

    response = api_client.get(
        "/tickets",
        params={
            "page": 1,
            "page_size": 1,
            "status": "received",
            "priority": "P0",
            "issue_type": "支付",
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["items"] == [payment_ticket]
    assert result["page"] == 1
    assert result["page_size"] == 1
    assert result["total"] == 1
    assert result["pages"] == 1


def test_patch_ticket_recalculates_rule(
    api_client: TestClient,
) -> None:
    created = _create_ticket(api_client)

    response = api_client.patch(
        f"/tickets/{created['ticket_id']}",
        json={
            "wait_minutes": 180,
            "status": "processing",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["wait_minutes"] == 180
    assert updated["status"] == "processing"
    assert updated["priority"] == "P1"
    assert updated["assigned_team"] == "综合客服组"
    assert "等待时间" in updated["reason"]


def test_create_ticket_returns_404_for_unknown_customer(
    api_client: TestClient,
) -> None:
    response = api_client.post(
        "/tickets",
        json={
            "customer_id": 999,
            "issue_type": "物流",
            "message": "不存在的客户",
            "wait_minutes": 0,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "CUSTOMER_NOT_FOUND",
            "message": "客户 999 不存在。",
            "resource": "customer",
            "resource_id": 999,
        },
    }


def test_create_ticket_rejects_unrelated_order(
    api_client: TestClient,
) -> None:
    response = api_client.post(
        "/tickets",
        json={
            "customer_id": 1,
            "order_id": 999,
            "issue_type": "物流",
            "message": "不存在的订单",
            "wait_minutes": 0,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "ORDER_NOT_FOUND",
            "message": "订单 999 不存在或不属于客户 1。",
            "resource": "order",
            "resource_id": 999,
        },
    }


def test_invalid_ticket_returns_422(
    api_client: TestClient,
) -> None:
    response = api_client.post(
        "/tickets",
        json={
            "customer_id": 0,
            "issue_type": "售后",
            "message": "",
            "wait_minutes": -10,
        },
    )

    assert response.status_code == 422

    error_fields = {
        error["loc"][-1]
        for error in response.json()["detail"]
    }

    assert error_fields == {
        "customer_id",
        "issue_type",
        "message",
        "wait_minutes",
    }


def test_missing_ticket_returns_404(
    api_client: TestClient,
) -> None:
    get_response = api_client.get("/tickets/999")
    patch_response = api_client.patch(
        "/tickets/999",
        json={
            "status": "closed",
        },
    )

    assert get_response.status_code == 404
    assert patch_response.status_code == 404
    expected_error = {
        "error": {
            "code": "TICKET_NOT_FOUND",
            "message": "工单 999 不存在。",
            "resource": "ticket",
            "resource_id": 999,
        },
    }
    assert get_response.json() == expected_error
    assert patch_response.json() == expected_error


def test_empty_patch_returns_400(
    api_client: TestClient,
) -> None:
    created = _create_ticket(api_client)

    response = api_client.patch(
        f"/tickets/{created['ticket_id']}",
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "至少需要提供一个要更新的字段。"
    )


def test_get_customer_returns_details(
    api_client: TestClient,
) -> None:
    response = api_client.get("/customers/1")

    assert response.status_code == 200

    customer = response.json()

    assert customer["customer_id"] == 1
    assert customer["name"] == "测试 VIP 客户"
    assert customer["email"] == "vip@example.com"
    assert customer["level"] == "VIP"
    assert customer["is_vip"] is True
    assert customer["created_at"] is not None


def test_get_order_returns_details(
    api_client: TestClient,
) -> None:
    response = api_client.get("/orders/1")

    assert response.status_code == 200

    order = response.json()

    assert order["order_id"] == 1
    assert order["order_number"] == "TEST-ORDER-001"
    assert order["customer_id"] == 1
    assert order["status"] == "paid"
    assert order["total_amount"] == "299.00"
    assert order["created_at"] is not None


def test_missing_customer_returns_unified_404(
    api_client: TestClient,
) -> None:
    response = api_client.get("/customers/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "CUSTOMER_NOT_FOUND",
            "message": "客户 999 不存在。",
            "resource": "customer",
            "resource_id": 999,
        },
    }


def test_missing_order_returns_unified_404(
    api_client: TestClient,
) -> None:
    response = api_client.get("/orders/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "ORDER_NOT_FOUND",
            "message": "订单 999 不存在。",
            "resource": "order",
            "resource_id": 999,
        },
    }


def test_openapi_describes_resource_responses(
    api_client: TestClient,
) -> None:
    openapi = api_client.get("/openapi.json").json()
    schemas = openapi["components"]["schemas"]

    customer_fields = schemas["CustomerResponse"]["properties"]
    order_fields = schemas["OrderResponse"]["properties"]
    error_fields = schemas["ErrorDetail"]["properties"]

    assert all(
        "description" in field
        for field in customer_fields.values()
    )
    assert all(
        "description" in field
        for field in order_fields.values()
    )
    assert all(
        "description" in field
        for field in error_fields.values()
    )

    customer_404 = openapi["paths"][
        "/customers/{customer_id}"
    ]["get"]["responses"]["404"]
    order_404 = openapi["paths"][
        "/orders/{order_id}"
    ]["get"]["responses"]["404"]

    assert customer_404["description"] == "客户不存在。"
    assert order_404["description"] == "订单不存在。"
