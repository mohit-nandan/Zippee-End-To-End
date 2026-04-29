import pytest
import responses as resp_mock
from api_clients.clickpost import ClickpostClient
from utils.data_factory import generate_order_payload

BASE = "http://localhost:8003"

def make_client():
    return ClickpostClient(base_url=BASE, api_key="test-api-key", shipment_username="test-user", shipment_password="test-pass")

@pytest.mark.smoke
@pytest.mark.api
@resp_mock.activate
def test_clickpost_order_push_succeeds():
    resp_mock.add(resp_mock.POST, f"{BASE}/clickpost/v1/orders", json={"waybill": "CP001"}, status=201)
    result = make_client().push_order(generate_order_payload(warehouse="clickpost"))
    assert result is not None

@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_clickpost_push_sends_correct_payload():
    resp_mock.add(resp_mock.POST, f"{BASE}/clickpost/v1/orders", json={"waybill": "CP002"}, status=201)
    payload = generate_order_payload(warehouse="clickpost")
    make_client().push_order(payload)
    import json
    sent = json.loads(resp_mock.calls[0].request.body)
    assert sent["warehouse"] == "clickpost"

@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_clickpost_tracking_status():
    resp_mock.add(resp_mock.GET, f"{BASE}/clickpost/v1/track/CP001", json={"waybill": "CP001", "status": "in_transit"}, status=200)
    result = make_client().get_tracking_status("CP001")
    assert result["status"] == "in_transit"
