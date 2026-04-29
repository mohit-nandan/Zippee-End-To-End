import pytest
import responses as resp_mock
from api_clients.internal import InternalClient
from utils.data_factory import generate_order_payload, PREFIX


BASE = "http://localhost:8000"


def make_client():
    return InternalClient(base_url=BASE, token="test-token")


@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_create_order_returns_id():
    resp_mock.add(resp_mock.POST, f"{BASE}/api/v1/orders", json={"id": "ORD001", "status": "pending"}, status=201)
    client = make_client()
    payload = generate_order_payload()
    order = client.create_order(payload)
    assert "id" in order
    assert order["id"] == "ORD001"


@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_created_order_is_retrievable():
    resp_mock.add(resp_mock.POST, f"{BASE}/api/v1/orders", json={"id": "ORD002", "status": "pending"}, status=201)
    resp_mock.add(resp_mock.GET, f"{BASE}/api/v1/orders/ORD002", json={"id": "ORD002", "status": "pending"}, status=200)
    client = make_client()
    created = client.create_order(generate_order_payload())
    fetched = client.get_order(created["id"])
    assert fetched["id"] == created["id"]


@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_created_order_has_pending_status():
    resp_mock.add(resp_mock.POST, f"{BASE}/api/v1/orders", json={"id": "ORD003", "status": "pending"}, status=201)
    resp_mock.add(resp_mock.GET, f"{BASE}/api/v1/orders/ORD003", json={"id": "ORD003", "status": "pending"}, status=200)
    client = make_client()
    order = client.create_order(generate_order_payload())
    assert client.get_order_status(order["id"]) in ("pending", "created")


@pytest.mark.regression
@pytest.mark.api
@resp_mock.activate
def test_cancel_order_changes_status():
    resp_mock.add(resp_mock.POST, f"{BASE}/api/v1/orders", json={"id": "ORD004", "status": "pending"}, status=201)
    resp_mock.add(resp_mock.PATCH, f"{BASE}/api/v1/orders/ORD004/cancel", json={"id": "ORD004", "status": "cancelled"}, status=200)
    resp_mock.add(resp_mock.GET, f"{BASE}/api/v1/orders/ORD004", json={"id": "ORD004", "status": "cancelled"}, status=200)
    client = make_client()
    order = client.create_order(generate_order_payload())
    client.cancel_order(order["id"])
    assert client.get_order_status(order["id"]) == "cancelled"


@pytest.mark.regression
@pytest.mark.api
@resp_mock.activate
def test_order_payload_contains_auto_test_prefix():
    resp_mock.add(resp_mock.POST, f"{BASE}/api/v1/orders", json={"id": "ORD005"}, status=201)
    client = make_client()
    payload = generate_order_payload()
    assert payload["order_ref"].startswith(PREFIX)
    client.create_order(payload)
    import json
    sent = json.loads(resp_mock.calls[0].request.body)
    assert sent["order_ref"].startswith(PREFIX)
