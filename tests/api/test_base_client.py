import responses as resp_mock
import pytest
from api_clients.base_client import BaseClient


@pytest.mark.api
@resp_mock.activate
def test_get_returns_json():
    resp_mock.add(resp_mock.GET, "https://api.test/orders", json={"orders": []}, status=200)
    client = BaseClient(base_url="https://api.test", token="test-token")
    data = client.get("/orders")
    assert data == {"orders": []}


@pytest.mark.api
@resp_mock.activate
def test_post_sends_json_body():
    resp_mock.add(resp_mock.POST, "https://api.test/orders", json={"id": "123"}, status=201)
    client = BaseClient(base_url="https://api.test", token="test-token")
    data = client.post("/orders", json={"order_ref": "AUTO_TEST_001"})
    assert data["id"] == "123"


@pytest.mark.api
@resp_mock.activate
def test_assert_status_raises_on_mismatch():
    resp_mock.add(resp_mock.GET, "https://api.test/bad", json={}, status=404)
    client = BaseClient(base_url="https://api.test", token="test-token")
    with pytest.raises(AssertionError, match="Expected 200"):
        client.get("/bad", expected_status=200)


@pytest.mark.api
@resp_mock.activate
def test_put_sends_correct_method():
    resp_mock.add(resp_mock.PUT, "https://api.test/orders/1", json={"updated": True}, status=200)
    client = BaseClient(base_url="https://api.test", token="test-token")
    data = client.put("/orders/1", json={"status": "delivered"})
    assert data["updated"] is True


@pytest.mark.api
@resp_mock.activate
def test_patch_sends_correct_method():
    resp_mock.add(resp_mock.PATCH, "https://api.test/orders/1/cancel", json={"cancelled": True}, status=200)
    client = BaseClient(base_url="https://api.test", token="test-token")
    data = client.patch("/orders/1/cancel")
    assert data["cancelled"] is True


@pytest.mark.api
@resp_mock.activate
def test_bearer_token_sent_in_header():
    resp_mock.add(resp_mock.GET, "https://api.test/me", json={"user": "test"}, status=200)
    client = BaseClient(base_url="https://api.test", token="secret-token")
    client.get("/me")
    assert resp_mock.calls[0].request.headers["Authorization"] == "Bearer secret-token"
