import random
from utils.db_client import DatabaseClient

_STAGING_DB = dict(
    host="staging-db.cnaoy1kocghu.ap-south-1.rds.amazonaws.com",
    port=3306,
    user="dev",
    password="DfTfEc5n0GkEVWN",
    database="staging",
)


def generate_unique_phone(db: DatabaseClient = None) -> str:
    """Return a 10-digit Indian mobile number (no +91 prefix) absent from the staging DB.

    Generates random candidates starting with 9 and rejects any that already
    have a rider row, so every test run gets a fresh, unused number.
    Raises RuntimeError if 50 candidates are all taken (extremely unlikely).
    """
    own_db = db is None
    if own_db:
        db = DatabaseClient(**_STAGING_DB)

    try:
        for _ in range(50):
            candidate = "9" + str(random.randint(100_000_000, 999_999_999))
            row = db.fetch_one(
                "SELECT id FROM zippeeriderapp_rider WHERE phone_number = %s",
                (f"+91{candidate}",),
            )
            if not row:
                return candidate
        raise RuntimeError("Could not generate a unique phone number after 50 attempts")
    finally:
        if own_db:
            db.close()
