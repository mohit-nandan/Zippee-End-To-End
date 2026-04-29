import pytest
from utils.db_client import DatabaseClient
from utils.config_loader import get_config


@pytest.mark.smoke
@pytest.mark.parametrize("env", ["staging", "preprod", "prod"])
def test_db_connectivity(env):
    cfg = get_config(env)
    with DatabaseClient(
        host=cfg["db_host"],
        port=cfg["db_port"],
        user=cfg["db_user"],
        password=cfg["db_password"],
        database=cfg["db_name"],
    ) as db:
        result = db.fetch_value("SELECT 1")
        assert result == 1, f"DB ping failed for {env}"


@pytest.mark.smoke
def test_db_readonly_guard_blocks_insert(db_client):
    with pytest.raises(ValueError, match="read-only"):
        db_client.fetch_one("INSERT INTO orders (id) VALUES (99999)")


@pytest.mark.smoke
def test_db_readonly_guard_blocks_update(db_client):
    with pytest.raises(ValueError, match="read-only"):
        db_client.fetch_one("UPDATE orders SET status='cancelled' WHERE id=99999")


@pytest.mark.smoke
def test_db_readonly_guard_blocks_semicolon(db_client):
    with pytest.raises(ValueError, match="Multi-statement"):
        db_client.fetch_one("SELECT 1; DROP TABLE orders")
