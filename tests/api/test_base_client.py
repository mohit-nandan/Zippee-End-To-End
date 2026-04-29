import json
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
def test_get_does_not_send_content_type():
    resp_mock.add(resp_mock.GET, "https://api.test/orders", json={}, status=200)
    client = BaseClient(base_url="https://api.test", token="test-token")
    client.get("/orders")
    assert "Content-Type" not in resp_mock.calls[0].request.headers


@pytest.mark.api
@resp_mock.activate
def test_post_sends_json_body():
    resp_mock.add(resp_mock.POST, "https://api.test/orders", json={"id": "123"}, status=201)
    client = BaseClient(base_url="https://api.test", token="test-token")
    data = client.post("/orders", json={"order_ref": "AUTO_TEST_001"})
    assert data["id"] == "123"
    sent = json.loads(resp_mock.calls[0].request.body)
    assert sent["order_ref"] == "AUTO_TEST_001"


@pytest.mark.api
@resp_mock.activate
def test_assert_status_raises_on_mismatch():
    resp_mock.add(resp_mock.GET, "https://api.test/bad", json={}, status=404)
    client = BaseClient(base_url="https://api.test", token="test-token")
    with pytest.raises(AssertionError, match=r"Expected 200.*404.*https://api.test/bad"):
        client.get("/bad", expected_status=200)


@pytest.mark.api
@resp_mock.activate
def test_put_sends_correct_method():
    resp_mock.add(resp_mock.PUT, "https://api.test/orders/1", json={"updated": True}, status=200)
    client = BaseClient(base_url="https://api.test", token="test-token")
    data = client.put("/orders/1", json={"status": "delivered"})
    assert data["updated"] is True
    sent = json.loads(resp_mock.calls[0].request.body)
    assert sent["status"] == "delivered"


@pytest.mark.api
@resp_mock.activate
def test_patch_sends_correct_method():
    resp_mock.add(resp_mock.PATCH, "https://api.test/orders/1/cancel", json={"cancelled": True}, status=200)
    client = BaseClient(base_url="https://api.test", token="test-token")
    data = client.patch("/orders/1/cancel")
    assert data["cancelled"] is True


@pytest.mark.api
@resp_mock.activate
def test_delete_returns_none_on_204():
    resp_mock.add(resp_mock.DELETE, "https://api.test/orders/1", body=b"", status=204)
    client = BaseClient(base_url="https://api.test", token="test-token")
    result = client.delete("/orders/1")
    assert result is None


@pytest.mark.api
@resp_mock.activate
def test_bearer_token_sent_in_header():
    resp_mock.add(resp_mock.GET, "https://api.test/me", json={"user": "test"}, status=200)
    client = BaseClient(base_url="https://api.test", token="secret-token")
    client.get("/me")
    assert resp_mock.calls[0].request.headers["Authorization"] == "Bearer secret-token"


@pytest.mark.api
@resp_mock.activate
def test_no_auth_header_when_token_is_none():
    resp_mock.add(resp_mock.GET, "https://api.test/public", json={}, status=200)
    client = BaseClient(base_url="https://api.test")
    client.get("/public")
    assert "Authorization" not in resp_mock.calls[0].request.headers


@pytest.mark.api
@resp_mock.activate
def test_parse_response_raises_on_non_json():
    resp_mock.add(resp_mock.GET, "https://api.test/html", body=b"<html>error</html>", status=200)
    client = BaseClient(base_url="https://api.test", token="test-token")
    with pytest.raises(ValueError, match="Non-JSON response"):
        client.get("/html")
