import pytest
import responses as resp_mock
from api_clients.easycom import EasycomClient
from utils.data_factory import generate_order_payload

BASE = "http://localhost:8002"

def make_client():
    return EasycomClient(base_url=BASE, token="test-token")

@pytest.mark.smoke
@pytest.mark.api
@resp_mock.activate
def test_easycom_order_push_succeeds():
    resp_mock.add(resp_mock.POST, f"{BASE}/easycom/api/orders", json={"id": "EASY001"}, status=201)
    result = make_client().push_order(generate_order_payload(warehouse="easycom"))
    assert result is not None

@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_easycom_push_sends_correct_payload():
    resp_mock.add(resp_mock.POST, f"{BASE}/easycom/api/orders", json={"id": "EASY002"}, status=201)
    payload = generate_order_payload(warehouse="easycom")
    make_client().push_order(payload)
    import json
    sent = json.loads(resp_mock.calls[0].request.body)
    assert sent["warehouse"] == "easycom"

@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_easycom_order_sync_status():
    resp_mock.add(resp_mock.GET, f"{BASE}/easycom/api/orders/EASY001", json={"id": "EASY001", "status": "received"}, status=200)
    result = make_client().get_order_sync_status("EASY001")
    assert "status" in result
