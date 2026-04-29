import socket
import pytest
import pymysql.err
from unittest.mock import MagicMock, patch
from utils.db_client import DatabaseClient
from utils.config_loader import get_config


def _host_reachable(host: str, port: int = 3306, timeout: int = 3) -> bool:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


# ------------------------------------------------------------------ #
# Live connectivity — SELECT 1 against each environment              #
# ------------------------------------------------------------------ #

@pytest.mark.smoke
@pytest.mark.parametrize("env", ["staging", "preprod", "prod"])
def test_db_connectivity(env):
    cfg = get_config(env)
    if not _host_reachable(cfg["db_host"], cfg["db_port"]):
        pytest.skip(f"{env} DB not reachable from this network — skipping live check")
    with DatabaseClient(
        host=cfg["db_host"],
        port=cfg["db_port"],
        user=cfg["db_user"],
        password=cfg["db_password"],
        database=cfg["db_name"],
    ) as db:
        result = db.fetch_value("SELECT 1")
        assert result == 1, f"DB ping failed for {env}"


# ------------------------------------------------------------------ #
# Read-only guard                                                     #
# ------------------------------------------------------------------ #

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


# ------------------------------------------------------------------ #
# Retry mechanism                                                     #
# ------------------------------------------------------------------ #

@pytest.mark.smoke
def test_db_retries_on_transient_error_then_succeeds():
    """Client retries up to 3 times on MySQL gone-away (2006) and succeeds."""
    transient = pymysql.err.OperationalError(2006, "MySQL server has gone away")

    mock_cursor = MagicMock()
    mock_cursor.__enter__ = lambda s: s
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchall.return_value = [{"1": 1}]

    mock_conn = MagicMock()
    mock_conn.cursor.side_effect = [transient, transient, mock_cursor]
    mock_conn.ping = MagicMock()

    with patch("utils.db_client.pymysql.connect", return_value=mock_conn), \
         patch("utils.db_client.time.sleep"):
        client = DatabaseClient(host="h", port=3306, user="u", password="p", database="d")
        result = client.fetch_value("SELECT 1")

    assert result == 1
    assert mock_conn.cursor.call_count == 3


@pytest.mark.smoke
def test_db_raises_after_all_retries_exhausted():
    """Client raises OperationalError after all retry attempts fail."""
    transient = pymysql.err.OperationalError(2006, "MySQL server has gone away")

    mock_conn = MagicMock()
    mock_conn.cursor.side_effect = transient
    mock_conn.ping = MagicMock()

    with patch("utils.db_client.pymysql.connect", return_value=mock_conn), \
         patch("utils.db_client.time.sleep"):
        client = DatabaseClient(host="h", port=3306, user="u", password="p", database="d")
        with pytest.raises(pymysql.err.OperationalError):
            client.fetch_value("SELECT 1")


# ------------------------------------------------------------------ #
# Auto-reconnect                                                      #
# ------------------------------------------------------------------ #

@pytest.mark.smoke
def test_db_ping_reconnects_on_stale_connection():
    """If ping raises, client reconnects before executing the query."""
    mock_cursor = MagicMock()
    mock_cursor.__enter__ = lambda s: s
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchall.return_value = [{"1": 1}]

    fresh_conn = MagicMock()
    fresh_conn.ping = MagicMock()
    fresh_conn.cursor.return_value = mock_cursor

    stale_conn = MagicMock()
    stale_conn.ping.side_effect = Exception("gone away")

    with patch("utils.db_client.pymysql.connect", side_effect=[stale_conn, fresh_conn]):
        client = DatabaseClient(host="h", port=3306, user="u", password="p", database="d")
        result = client.fetch_value("SELECT 1")

    assert result == 1
    assert fresh_conn.cursor.called


# ------------------------------------------------------------------ #
# Timeout configuration                                               #
# ------------------------------------------------------------------ #

@pytest.mark.smoke
def test_db_custom_timeouts_passed_to_pymysql():
    """read_timeout and write_timeout are forwarded to pymysql.connect."""
    with patch("utils.db_client.pymysql.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        DatabaseClient(
            host="h", port=3306, user="u", password="p", database="d",
            read_timeout=60, write_timeout=60,
        )
    _, kwargs = mock_connect.call_args
    assert kwargs["read_timeout"] == 60
    assert kwargs["write_timeout"] == 60
    assert kwargs["autocommit"] is True
