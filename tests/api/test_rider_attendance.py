import pytest
import responses as resp_mock
from datetime import date
from api_clients.internal import InternalClient


BASE = "http://localhost:8000"
RIDER_ID = "TEST_RIDER_001"


def make_client():
    return InternalClient(base_url=BASE, token="test-token")


@pytest.mark.smoke
@pytest.mark.api
@resp_mock.activate
def test_mark_attendance_succeeds():
    resp_mock.add(
        resp_mock.POST,
        f"{BASE}/api/v1/riders/{RIDER_ID}/attendance",
        json={"success": True, "id": "ATT001"},
        status=201,
    )
    client = make_client()
    result = client.mark_attendance(RIDER_ID, {"date": str(date.today()), "status": "present"})
    assert result.get("success") is True or "id" in result


@pytest.mark.sanity
@pytest.mark.api
@resp_mock.activate
def test_attendance_payload_sent_correctly():
    resp_mock.add(
        resp_mock.POST,
        f"{BASE}/api/v1/riders/{RIDER_ID}/attendance",
        json={"success": True},
        status=201,
    )
    client = make_client()
    today = str(date.today())
    client.mark_attendance(RIDER_ID, {"date": today, "status": "present"})
    import json
    sent = json.loads(resp_mock.calls[0].request.body)
    assert sent["date"] == today
    assert sent["status"] == "present"


@pytest.mark.regression
@pytest.mark.api
@resp_mock.activate
def test_get_rider_returns_rider_data():
    resp_mock.add(
        resp_mock.GET,
        f"{BASE}/api/v1/riders/{RIDER_ID}",
        json={"id": RIDER_ID, "name": "Test Rider", "phone": "9800000001"},
        status=200,
    )
    client = make_client()
    rider = client.get_rider(RIDER_ID)
    assert rider["id"] == RIDER_ID
