import pytest
import responses as resp_mock
from api_clients.uniware import UniwareClient
from utils.data_factory import generate_order_payload

BASE = "http://localhost:8001"

def make_client():
    return UniwareClient(base_url=BASE, token="test-token")

@pytest.mark.smoke
@pytest.mark.api
@resp_mock.activate
def test_uniware_order_push_succeeds():
    resp_mock.add(resp_mock.POST, f"{BASE}/uniware/v1/orders/push", json={"success": True, "ref": "UNI001"}, status=201)
    result = make_client().push_order(generate_order_payload(warehouse="uniware"))
    assert result is not None

@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_uniware_push_sends_warehouse_field():
    resp_mock.add(resp_mock.POST, f"{BASE}/uniware/v1/orders/push", json={"ref": "UNI002"}, status=201)
    payload = generate_order_payload(warehouse="uniware")
    make_client().push_order(payload)
    import json
    sent = json.loads(resp_mock.calls[0].request.body)
    assert sent["warehouse"] == "uniware"

@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_uniware_order_status_check():
    resp_mock.add(resp_mock.GET, f"{BASE}/uniware/v1/orders/UNI001/status", json={"ref": "UNI001", "status": "synced"}, status=200)
    result = make_client().get_order_sync_status("UNI001")
    assert result["status"] == "synced"
