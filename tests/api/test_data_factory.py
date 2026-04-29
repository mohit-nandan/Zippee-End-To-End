import pytest
from utils.data_factory import generate_order_payload, generate_rider_payload, PREFIX, order_id


@pytest.mark.api
def test_order_id_has_prefix():
    oid = order_id()
    assert oid.startswith(PREFIX)


@pytest.mark.api
def test_order_ids_are_unique():
    ids = {order_id() for _ in range(100)}
    assert len(ids) == 100


@pytest.mark.api
def test_generate_order_payload_has_required_keys():
    payload = generate_order_payload()
    for key in ("order_ref", "warehouse", "customer_name", "customer_phone", "delivery_address", "items"):
        assert key in payload, f"Missing key: {key}"


@pytest.mark.api
def test_generate_order_payload_ref_has_prefix():
    payload = generate_order_payload()
    assert payload["order_ref"].startswith(PREFIX)


@pytest.mark.api
def test_generate_order_payload_overrides_work():
    payload = generate_order_payload(warehouse="uniware", customer_name="Test User")
    assert payload["warehouse"] == "uniware"
    assert payload["customer_name"] == "Test User"


@pytest.mark.api
def test_generate_rider_payload_has_required_keys():
    payload = generate_rider_payload()
    for key in ("name", "phone", "email"):
        assert key in payload, f"Missing key: {key}"


@pytest.mark.api
def test_generate_rider_payload_name_has_prefix():
    payload = generate_rider_payload()
    assert payload["name"].startswith(PREFIX)
