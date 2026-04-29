import pytest
from utils.db_client import DatabaseClient


@pytest.fixture(scope="session")
def db_client(cfg):
    client = DatabaseClient(
        host=cfg["db_host"],
        port=cfg["db_port"],
        user=cfg["db_user"],
        password=cfg["db_password"],
        database=cfg["db_name"],
    )
    yield client
    client.close()
