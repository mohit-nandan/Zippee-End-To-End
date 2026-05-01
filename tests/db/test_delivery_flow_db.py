"""
DB tests for end-to-end delivery flow verification.
Checks zorms_shipment, zfw_webhook_history, zorcs_brand_webhook_logs,
and zorcs_order_event on the preprod DB after rider actions in the app.
"""
import pytest
from utils.db_client import DatabaseClient
from utils.config_loader import get_config
from dotenv import load_dotenv

load_dotenv()

AWBS = [
    "ZPEDETMAQWDW0FN",   # Clickpost Prepaid
    "ZPEKAKE9Z9WPX0V",   # Clickpost COD
    "ZPENZE8RYZDFGVV",   # Uniware Prepaid
    "ZPERM6V4LOVDCZT",   # Uniware COD
    "ZPE0QZX6D4ILO6D",   # Easycom Prepaid
    "ZPEDKVA8XUHVR57",   # Easycom COD
]

# Full delivery event sequence expected per channel_type
CLICKPOST_EVENTS = [
    "OPENED", "PROCESSED",
    "ALLOCATION_PENDINGNOTIFICATION",
    "PICKUP_PENDINGNOTIFICATION",
    "PICKUP_IN_PROGRESSNOTIFICATION",
    "PICKUP_COMPLETEDNOTIFICATION",
    "OUT_FOR_DELIVERYNOTIFICATION",
    "REACHED_DELIVERYNOTIFICATION",
    "DELIVERY_IN_PROGRESSNOTIFICATION",
    "DELIVEREDNOTIFICATION",
]

UNIWARE_EVENTS = [
    "OPENED", "PROCESSED",
    "PICKEDUPNOTIFICATION",
    "DELIVEREDNOTIFICATION",
]

WEBHOOK_SEQUENCE = [
    "ALLOCATION_PENDING",
    "PICKUP_IN_PROGRESS",
    "PICKUP_COMPLETED",
    "OUT_FOR_DELIVERY",
    "REACHED_DELIVERY",
    "DELIVERY_IN_PROGRESS",
    "DELIVERED",
]


@pytest.fixture(scope="module")
def db():
    cfg = get_config("preprod")
    client = DatabaseClient(
        host=cfg["db_host"], port=cfg["db_port"],
        user=cfg["db_user"], password=cfg["db_password"],
        database=cfg["db_name"],
    )
    yield client
    client.close()


def _ph(awbs):
    return ",".join(["%s"] * len(awbs))


# ─────────────────────────────────────────────
# zorms_shipment
# ─────────────────────────────────────────────

class TestZormsShipment:

    def test_all_awbs_exist(self, db):
        rows = db.fetch_all(
            f"SELECT zippee_awb FROM zorms_shipment WHERE zippee_awb IN ({_ph(AWBS)})",
            AWBS,
        )
        found = {r["zippee_awb"] for r in rows}
        assert found == set(AWBS), f"Missing AWBs in zorms_shipment: {set(AWBS) - found}"

    @pytest.mark.parametrize("awb", AWBS)
    def test_shipment_status_is_delivered(self, db, awb):
        row = db.fetch_one(
            "SELECT shipment_status FROM zorms_shipment WHERE zippee_awb = %s", (awb,)
        )
        assert row is not None, f"AWB {awb} not found in zorms_shipment"
        assert row["shipment_status"] == "DELIVERED", (
            f"AWB {awb} expected DELIVERED, got {row['shipment_status']}"
        )

    @pytest.mark.parametrize("awb", AWBS)
    def test_order_status_is_active(self, db, awb):
        row = db.fetch_one(
            "SELECT order_status FROM zorms_shipment WHERE zippee_awb = %s", (awb,)
        )
        assert row is not None
        assert row["order_status"] == 1, (
            f"AWB {awb} order_status expected 1, got {row['order_status']}"
        )

    @pytest.mark.parametrize("awb,expected_pm", [
        ("ZPEDETMAQWDW0FN", 5),   # Clickpost Prepaid
        ("ZPEKAKE9Z9WPX0V", 2),   # Clickpost COD
        ("ZPERM6V4LOVDCZT", 2),   # Uniware COD
        ("ZPE0QZX6D4ILO6D", 5),   # Easycom Prepaid
        ("ZPEDKVA8XUHVR57", 2),   # Easycom COD
    ])
    def test_payment_mode_id(self, db, awb, expected_pm):
        row = db.fetch_one(
            "SELECT payment_mode_id FROM zorms_shipment WHERE zippee_awb = %s", (awb,)
        )
        assert row is not None
        assert row["payment_mode_id"] == expected_pm, (
            f"AWB {awb} payment_mode_id expected {expected_pm}, got {row['payment_mode_id']}"
        )

    @pytest.mark.parametrize("awb", AWBS)
    def test_delivery_pincode_is_122008(self, db, awb):
        row = db.fetch_one(
            "SELECT pin_code FROM zorms_shipment WHERE zippee_awb = %s", (awb,)
        )
        assert row is not None
        assert row["pin_code"] == "122008", (
            f"AWB {awb} pin_code expected 122008, got {row['pin_code']}"
        )


# ─────────────────────────────────────────────
# zfw_webhook_history
# ─────────────────────────────────────────────

class TestWebhookHistory:

    @pytest.mark.parametrize("awb", AWBS)
    def test_delivered_webhook_fired(self, db, awb):
        row = db.fetch_one(
            "SELECT id FROM zfw_webhook_history WHERE reference_code = %s AND webhook_type = 'DELIVERED'",
            (awb,),
        )
        assert row is not None, f"No DELIVERED webhook found for AWB {awb}"

    @pytest.mark.parametrize("awb", AWBS)
    def test_webhook_sequence_is_ordered(self, db, awb):
        rows = db.fetch_all(
            "SELECT webhook_type, added_on FROM zfw_webhook_history "
            "WHERE reference_code = %s ORDER BY added_on",
            (awb,),
        )
        types = [r["webhook_type"] for r in rows]
        # DELIVERED must be the last unique event
        assert types[-1] == "DELIVERED", (
            f"AWB {awb} last webhook is '{types[-1]}', expected 'DELIVERED'"
        )

    @pytest.mark.parametrize("awb", AWBS)
    def test_out_for_delivery_before_delivered(self, db, awb):
        ofd = db.fetch_one(
            "SELECT added_on FROM zfw_webhook_history "
            "WHERE reference_code = %s AND webhook_type = 'OUT_FOR_DELIVERY'",
            (awb,),
        )
        dlv = db.fetch_one(
            "SELECT added_on FROM zfw_webhook_history "
            "WHERE reference_code = %s AND webhook_type = 'DELIVERED'",
            (awb,),
        )
        assert ofd is not None, f"No OUT_FOR_DELIVERY webhook for {awb}"
        assert dlv is not None, f"No DELIVERED webhook for {awb}"
        assert ofd["added_on"] < dlv["added_on"], (
            f"AWB {awb}: OUT_FOR_DELIVERY not before DELIVERED"
        )

    @pytest.mark.parametrize("awb", AWBS)
    def test_pickup_completed_before_out_for_delivery(self, db, awb):
        pc = db.fetch_one(
            "SELECT added_on FROM zfw_webhook_history "
            "WHERE reference_code = %s AND webhook_type = 'PICKUP_COMPLETED'",
            (awb,),
        )
        ofd = db.fetch_one(
            "SELECT added_on FROM zfw_webhook_history "
            "WHERE reference_code = %s AND webhook_type = 'OUT_FOR_DELIVERY'",
            (awb,),
        )
        assert pc is not None, f"No PICKUP_COMPLETED webhook for {awb}"
        assert ofd is not None, f"No OUT_FOR_DELIVERY webhook for {awb}"
        assert pc["added_on"] < ofd["added_on"], (
            f"AWB {awb}: PICKUP_COMPLETED not before OUT_FOR_DELIVERY"
        )


# ─────────────────────────────────────────────
# zorcs_brand_webhook_logs
# ─────────────────────────────────────────────

class TestBrandWebhookLogs:

    @pytest.mark.parametrize("awb", [
        "ZPEDETMAQWDW0FN", "ZPEKAKE9Z9WPX0V",   # Clickpost
        "ZPE0QZX6D4ILO6D", "ZPEDKVA8XUHVR57",   # Easycom
    ])
    def test_brand_webhook_logs_exist(self, db, awb):
        """Clickpost and Easycom AWBs generate brand webhook logs; Uniware does not."""
        rows = db.fetch_all(
            "SELECT id FROM zorcs_brand_webhook_logs WHERE reference_code = %s",
            (awb,),
        )
        assert len(rows) > 0, f"No brand webhook logs found for AWB {awb}"

    @pytest.mark.parametrize("awb", ["ZPEDETMAQWDW0FN", "ZPEKAKE9Z9WPX0V"])
    def test_clickpost_brand_webhooks_all_succeeded(self, db, awb):
        """Clickpost AWBs have a svix URL configured — all should return 200."""
        failed = db.fetch_all(
            "SELECT id, response_status FROM zorcs_brand_webhook_logs "
            "WHERE reference_code = %s AND response_status != 0",
            (awb,),
        )
        assert len(failed) == 0, (
            f"AWB {awb} has failed brand webhooks: {failed}"
        )

    @pytest.mark.parametrize("awb", ["ZPEDETMAQWDW0FN", "ZPEKAKE9Z9WPX0V"])
    def test_clickpost_brand_webhook_url_is_set(self, db, awb):
        row = db.fetch_one(
            "SELECT url FROM zorcs_brand_webhook_logs WHERE reference_code = %s LIMIT 1",
            (awb,),
        )
        assert row and row["url"], f"AWB {awb} brand webhook URL is empty"


# ─────────────────────────────────────────────
# zorcs_order_event
# ─────────────────────────────────────────────

class TestOrderEvents:

    @pytest.mark.parametrize("awb", AWBS)
    def test_order_events_exist(self, db, awb):
        rows = db.fetch_all(
            "SELECT id FROM zorcs_order_event WHERE awb_number = %s", (awb,)
        )
        assert len(rows) > 0, f"No order events found for AWB {awb}"

    @pytest.mark.parametrize("awb", AWBS)
    def test_delivered_event_present(self, db, awb):
        row = db.fetch_one(
            "SELECT id FROM zorcs_order_event "
            "WHERE awb_number = %s AND notification_type = 'DELIVEREDNOTIFICATION'",
            (awb,),
        )
        assert row is not None, f"No DELIVEREDNOTIFICATION event for AWB {awb}"

    @pytest.mark.parametrize("awb", AWBS)
    def test_opened_event_is_first(self, db, awb):
        row = db.fetch_one(
            "SELECT notification_type FROM zorcs_order_event "
            "WHERE awb_number = %s ORDER BY added_on ASC LIMIT 1",
            (awb,),
        )
        assert row is not None
        assert row["notification_type"] == "OPENED", (
            f"AWB {awb} first event is '{row['notification_type']}', expected 'OPENED'"
        )

    @pytest.mark.parametrize("awb", AWBS)
    def test_delivered_event_is_last(self, db, awb):
        row = db.fetch_one(
            "SELECT notification_type FROM zorcs_order_event "
            "WHERE awb_number = %s ORDER BY added_on DESC LIMIT 1",
            (awb,),
        )
        assert row is not None
        assert row["notification_type"] == "DELIVEREDNOTIFICATION", (
            f"AWB {awb} last event is '{row['notification_type']}', expected 'DELIVEREDNOTIFICATION'"
        )

    @pytest.mark.parametrize("awb", AWBS)
    def test_brand_id_is_318(self, db, awb):
        row = db.fetch_one(
            "SELECT DISTINCT brand_id FROM zorcs_order_event WHERE awb_number = %s",
            (awb,),
        )
        assert row is not None
        assert row["brand_id"] == 318, (
            f"AWB {awb} brand_id expected 318, got {row['brand_id']}"
        )

    @pytest.mark.parametrize("awb", [
        "ZPEDETMAQWDW0FN", "ZPEKAKE9Z9WPX0V",
        "ZPE0QZX6D4ILO6D", "ZPEDKVA8XUHVR57",
    ])
    def test_clickpost_easycom_full_event_chain(self, db, awb):
        """Clickpost & Easycom AWBs have granular events including pickup steps."""
        required = ["PICKUP_IN_PROGRESSNOTIFICATION", "PICKUP_COMPLETEDNOTIFICATION",
                    "OUT_FOR_DELIVERYNOTIFICATION", "DELIVEREDNOTIFICATION"]
        rows = db.fetch_all(
            "SELECT notification_type FROM zorcs_order_event WHERE awb_number = %s",
            (awb,),
        )
        found = {r["notification_type"] for r in rows}
        missing = [e for e in required if e not in found]
        assert not missing, f"AWB {awb} missing events: {missing}"

    @pytest.mark.parametrize("awb", ["ZPENZE8RYZDFGVV", "ZPERM6V4LOVDCZT"])
    def test_uniware_has_pickedup_and_delivered(self, db, awb):
        """Uniware AWBs emit PICKEDUPNOTIFICATION directly (no step-by-step pickup)."""
        for event in ["PICKEDUPNOTIFICATION", "DELIVEREDNOTIFICATION"]:
            row = db.fetch_one(
                "SELECT id FROM zorcs_order_event WHERE awb_number = %s AND notification_type = %s",
                (awb, event),
            )
            assert row is not None, f"AWB {awb} missing event: {event}"
