import pymysql
import pymysql.cursors

_ALLOWED_PREFIXES = ("select", "show", "describe", "explain")


class DatabaseClient:
    def __init__(self, host: str, port, user: str, password: str, database: str):
        self._conn = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
        )

    def _guard_readonly(self, sql: str):
        stripped = sql.strip().lower()
        if not any(stripped.startswith(p) for p in _ALLOWED_PREFIXES):
            raise ValueError(f"Only read-only queries are allowed. Got: {sql[:80]!r}")
        if ";" in sql:
            raise ValueError("Multi-statement queries are not allowed.")

    def fetch_one(self, sql: str, params=None) -> dict | None:
        self._guard_readonly(sql)
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    def fetch_all(self, sql: str, params=None) -> list[dict]:
        self._guard_readonly(sql)
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

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
