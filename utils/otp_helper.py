import time
import logging
from utils.db_client import DatabaseClient

logger = logging.getLogger(__name__)

_STAGING_DB = dict(
    host="staging-db.cnaoy1kocghu.ap-south-1.rds.amazonaws.com",
    port=3306,
    user="dev",
    password="DfTfEc5n0GkEVWN",
    database="staging",
)


def wait_for_otp(
    phone: str,
    db: DatabaseClient = None,
    timeout: int = 30,
    poll_interval: int = 2,
) -> str:
    """Poll staging DB until a fresh OTP appears for the given phone number.

    Phone may be passed as '9140151251' or '+919140151251'.
    Returns the OTP string.
    Raises TimeoutError if OTP does not arrive within `timeout` seconds.
    """
    if not phone.startswith("+"):
        phone = f"+91{phone}"

    own_db = db is None
    if own_db:
        db = DatabaseClient(**_STAGING_DB)

    try:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            row = db.fetch_one(
                "SELECT otp FROM zippeeriderapp_rider WHERE phone_number = %s",
                (phone,),
            )
            otp = row["otp"] if row else None
            if otp and otp != "0":
                logger.info("OTP received for %s: %s", phone, otp)
                return otp
            time.sleep(poll_interval)

        raise TimeoutError(
            f"OTP not received for {phone} within {timeout}s"
        )
    finally:
        if own_db:
            db.close()


def fetch_rider(phone: str, db: DatabaseClient = None) -> dict:
    """Return the full rider row for the given phone number."""
    if not phone.startswith("+"):
        phone = f"+91{phone}"

    own_db = db is None
    if own_db:
        db = DatabaseClient(**_STAGING_DB)

    try:
        return db.fetch_one(
            "SELECT id, phone_number, otp, is_active, is_blocked, onboarding_status "
            "FROM zippeeriderapp_rider WHERE phone_number = %s",
            (phone,),
        )
    finally:
        if own_db:
            db.close()
