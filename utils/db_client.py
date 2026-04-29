import logging
import time

import pymysql
import pymysql.cursors
import pymysql.err

logger = logging.getLogger(__name__)

_ALLOWED_PREFIXES = ("select", "show", "describe", "explain")

# MySQL error codes that are safe to retry (transient network/server blips)
_RETRIABLE_CODES = {
    2003,  # Can't connect to MySQL server
    2006,  # MySQL server has gone away
    2013,  # Lost connection to MySQL server during query
}

_RETRY_DELAYS = (1, 2, 4)  # seconds — exponential backoff, 3 attempts total


class DatabaseClient:
    def __init__(
        self,
        host: str,
        port,
        user: str,
        password: str,
        database: str,
        connect_timeout: int = 10,
        read_timeout: int = 30,
        write_timeout: int = 30,
    ):
        self._connect_kwargs = dict(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            autocommit=True,
        )
        self._conn = self._connect()

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _connect(self) -> pymysql.connections.Connection:
        logger.debug("Opening DB connection to %s", self._connect_kwargs["host"])
        return pymysql.connect(**self._connect_kwargs)

    def _ensure_connected(self):
        """Ping the server and transparently reconnect if the connection is stale."""
        try:
            self._conn.ping(reconnect=True)
        except Exception:
            logger.warning("DB ping failed — reconnecting")
            self._conn = self._connect()

    def _guard_readonly(self, sql: str):
        stripped = sql.strip().lower()
        if not any(stripped.startswith(p) for p in _ALLOWED_PREFIXES):
            raise ValueError(f"Only read-only queries are allowed. Got: {sql[:80]!r}")
        if ";" in sql:
            raise ValueError("Multi-statement queries are not allowed.")

    def _execute(self, sql: str, params=None) -> list[dict]:
        """Single execution path with retry and timing log."""
        self._guard_readonly(sql)
        self._ensure_connected()

        last_exc: Exception | None = None
        delays = list(_RETRY_DELAYS)

        for attempt in range(1, len(delays) + 2):  # attempts 1..4
            try:
                t0 = time.monotonic()
                with self._conn.cursor() as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()
                elapsed = time.monotonic() - t0
                logger.debug(
                    "Query OK | %.3fs | %d row(s) | %s",
                    elapsed,
                    len(rows),
                    sql[:120],
                )
                return rows

            except pymysql.err.OperationalError as exc:
                code = exc.args[0]
                if code in _RETRIABLE_CODES and attempt <= len(delays):
                    delay = delays[attempt - 1]
                    logger.warning(
                        "Transient DB error %s on attempt %d/%d — retrying in %ss",
                        code,
                        attempt,
                        len(delays) + 1,
                        delay,
                    )
                    time.sleep(delay)
                    try:
                        self._conn = self._connect()
                    except Exception:
                        pass
                    last_exc = exc
                    continue
                raise

        raise last_exc  # exhausted all retries

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def fetch_all(self, sql: str, params=None) -> list[dict]:
        return self._execute(sql, params)

    def fetch_one(self, sql: str, params=None) -> dict | None:
        rows = self._execute(sql, params)
        return rows[0] if rows else None

    def fetch_value(self, sql: str, params=None):
        row = self.fetch_one(sql, params)
        if row is None:
            return None
        return next(iter(row.values()))

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
