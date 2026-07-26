from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ServiceMind",
    }


def test_create_ticket() -> None:
    response = client.post(
        "/tickets",
        json={
            "customer_name": "小王",
            "issue_type": "物流",
            "message": "我的订单什么时候送到？",
            "wait_minutes": 15,
            "is_vip": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["ticket_id"] == 1
    assert response.json()["status"] == "received"
    assert response.json()["customer_name"] == "小王"


def test_invalid_ticket_returns_422() -> None:
    response = client.post(
        "/tickets",
        json={
            "customer_name": "",
            "issue_type": "售后",
            "message": "",
            "wait_minutes": -10,
            "is_vip": False,
        },
    )

    assert response.status_code == 422

    error_fields = {
        error["loc"][-1]
        for error in response.json()["detail"]
    }

    assert error_fields == {
        "customer_name",
        "issue_type",
        "message",
        "wait_minutes",
    }