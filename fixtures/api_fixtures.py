import os
import pytest
from api_clients.internal import InternalClient
from api_clients.uniware import UniwareClient
from api_clients.easycom import EasycomClient
from api_clients.clickpost import ClickpostClient
from utils.config_loader import get_config
from utils.data_factory import generate_order_payload


@pytest.fixture(scope="session")
def cfg():
    return get_config()


@pytest.fixture(scope="session")
def internal_client(cfg):
    return InternalClient(
        base_url=cfg["internal_api_url"],
        token=os.environ["INTERNAL_API_TOKEN"],
    )


@pytest.fixture(scope="session")
def uniware_client(cfg):
    return UniwareClient(
        base_url=cfg["uniware_api_url"],
        token=os.environ["UNIWARE_API_TOKEN"],
    )


@pytest.fixture(scope="session")
def easycom_client(cfg):
    return EasycomClient(
        base_url=cfg["easycom_api_url"],
        token=os.environ["EASYCOM_API_TOKEN"],
    )


@pytest.fixture(scope="session")
def clickpost_client(cfg):
    return ClickpostClient(
        base_url=cfg["clickpost_api_url"],
        token=os.environ["CLICKPOST_API_TOKEN"],
    )


@pytest.fixture
def test_order(internal_client):
    """Creates a test order before the test, cancels it after."""
    payload = generate_order_payload()
    order = internal_client.create_order(payload)
    yield order
    try:
        internal_client.cancel_order(order["id"])
    except Exception:
        pass  # best-effort cleanup
