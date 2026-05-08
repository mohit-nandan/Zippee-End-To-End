"""
DB tests — zorms_shipment_extention matview sync (preprod)
===========================================================
Verifies that zorms_shipment_extention stays in sync with zorms_shipment
after rider app / admin actions on the preprod environment.

Table note: the table is named 'zorms_shipment_extention' (typo — missing 's').

Sync fields verified:
  - brand_display_name    : populated from brand record
  - order_reference_code  : matches the WMS reference
  - item_count            : count of shipment items
  - delivered_date        : set by rider app on delivery
  - current_rider_name    : populated when trip is assigned
  - current_rider_id      : populated when trip is assigned
  - current_trip_id       : set on rider assignment
  - attempt_count         : incremented on delivery attempts

Run:
    $env:ENV="preprod"; pytest tests/db/test_matview_sync_preprod.py -v
"""
import pytest
from utils.db_client import DatabaseClient
from utils.config_loader import get_config
from dotenv import load_dotenv

load_dotenv()

# AWBs delivered via rider app (have delivered_date + rider info)
AWBS_RIDER_DELIVERED = [
    "ZPEDETMAQWDW0FN",   # Clickpost Prepaid — DELIVERED
    "ZPEKAKE9Z9WPX0V",   # Clickpost COD    — DELIVERED
    "ZPENZE8RYZDFGVV",   # Uniware Prepaid  — DELIVERED
    "ZPERM6V4LOVDCZT",   # Uniware COD      — DELIVERED
    "ZPE0QZX6D4ILO6D",   # Easycom Prepaid  — DELIVERED
    "ZPEDKVA8XUHVR57",   # Easycom COD      — DELIVERED
]

# AWBs where delivery was attempted but not completed:
#   - rider / trip NOT assigned (current_rider_id=null, current_trip_id=null)
#   - attempt_count >= 1
AWBS_DELIVERY_ATTEMPTED = [
    "FBX8KCATF4D8B47",   # attempt_count=1, no rider/trip assigned
]

ALL_AWBS = AWBS_RIDER_DELIVERED + AWBS_DELIVERY_ATTEMPTED


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


# ─────────────────────────────────────────────────────────────────
# Coverage: every shipment must have an ext row
# ─────────────────────────────────────────────────────────────────

class TestMatviewCoverage:

    def test_no_recent_shipments_missing_from_extention(self, db):
        """Shipments created in the last 30 days must all have an ext row."""
        rows = db.fetch_all(
            "SELECT s.id, s.zippee_awb, s.shipment_status "
            "FROM zorms_shipment s "
            "LEFT JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE e.id IS NULL "
            "AND s.added_on >= NOW() - INTERVAL 30 DAY "
            "ORDER BY s.id DESC",
            (),
        )
        assert not rows, (
            f"Recent shipments missing from zorms_shipment_extention ({len(rows)}): "
            + ", ".join(r["zippee_awb"] for r in rows)
        )

    @pytest.mark.parametrize("awb", ALL_AWBS)
    def test_ext_row_exists_for_awb(self, db, awb):
        row = db.fetch_one(
            "SELECT e.id FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb} has no row in zorms_shipment_extention"

    def test_ext_total_count_matches_shipment_count(self, db):
        """Row count in ext must equal row count in zorms_shipment."""
        result = db.fetch_one(
            "SELECT "
            "  (SELECT COUNT(*) FROM zorms_shipment) AS shipment_count, "
            "  (SELECT COUNT(*) FROM zorms_shipment_extention) AS ext_count",
            (),
        )
        diff = result["shipment_count"] - result["ext_count"]
        assert diff == 0, (
            f"zorms_shipment has {result['shipment_count']} rows but "
            f"zorms_shipment_extention has {result['ext_count']} "
            f"({abs(diff)} {'missing' if diff > 0 else 'extra'})"
        )


# ─────────────────────────────────────────────────────────────────
# Field sync checks
# ─────────────────────────────────────────────────────────────────

class TestMatviewFieldSync:

    @pytest.mark.parametrize("awb", ALL_AWBS)
    def test_brand_display_name_not_empty(self, db, awb):
        row = db.fetch_one(
            "SELECT e.brand_display_name FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no ext row"
        assert row["brand_display_name"], (
            f"AWB {awb}: brand_display_name is empty/null in ext"
        )

    @pytest.mark.parametrize("awb", ALL_AWBS)
    def test_order_reference_code_not_empty(self, db, awb):
        row = db.fetch_one(
            "SELECT e.order_reference_code FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no ext row"
        assert row["order_reference_code"], (
            f"AWB {awb}: order_reference_code is empty/null in ext"
        )

    @pytest.mark.parametrize("awb", ALL_AWBS)
    def test_item_count_is_positive(self, db, awb):
        row = db.fetch_one(
            "SELECT e.item_count FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no ext row"
        assert row["item_count"] and row["item_count"] > 0, (
            f"AWB {awb}: item_count is {row['item_count']} (expected > 0)"
        )


# ─────────────────────────────────────────────────────────────────
# Rider app delivery sync
# ─────────────────────────────────────────────────────────────────

class TestRiderDeliverySync:
    """Verify ext fields populated by the rider app after delivery."""

    @pytest.mark.parametrize("awb", AWBS_RIDER_DELIVERED)
    def test_delivered_date_is_set(self, db, awb):
        """delivered_date must be populated after rider marks delivery."""
        row = db.fetch_one(
            "SELECT e.delivered_date, s.shipment_status FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no ext row"
        assert row["shipment_status"] == "DELIVERED", (
            f"AWB {awb}: expected DELIVERED, got {row['shipment_status']}"
        )
        assert row["delivered_date"] is not None, (
            f"AWB {awb}: delivered_date is null in ext — rider delivery not synced"
        )

    @pytest.mark.parametrize("awb", AWBS_RIDER_DELIVERED)
    def test_rider_info_is_populated(self, db, awb):
        """current_rider_name and current_rider_id must be set for rider deliveries."""
        row = db.fetch_one(
            "SELECT e.current_rider_name, e.current_rider_id, e.current_trip_id "
            "FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no ext row"
        assert row["current_rider_name"], (
            f"AWB {awb}: current_rider_name is empty in ext"
        )
        assert row["current_rider_id"] is not None, (
            f"AWB {awb}: current_rider_id is null in ext"
        )
        assert row["current_trip_id"] is not None, (
            f"AWB {awb}: current_trip_id is null in ext"
        )

    def test_all_trip_assigned_awbs_have_rider_info(self, db):
        """Any ext row with current_trip_id must also have rider name and id."""
        rows = db.fetch_all(
            "SELECT s.zippee_awb, e.current_trip_id, "
            "       e.current_rider_name, e.current_rider_id "
            "FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE e.current_trip_id IS NOT NULL "
            "AND (e.current_rider_name = '' OR e.current_rider_id IS NULL)",
            (),
        )
        assert not rows, (
            f"AWBs with trip_id but missing rider info ({len(rows)}): "
            + ", ".join(r["zippee_awb"] for r in rows)
        )

    def test_rider_delivered_awbs_have_delivered_date(self, db):
        """DELIVERED shipments with a rider assigned must have delivered_date set."""
        rows = db.fetch_all(
            "SELECT s.zippee_awb "
            "FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.shipment_status = 'DELIVERED' "
            "AND e.current_rider_id IS NOT NULL "
            "AND e.delivered_date IS NULL "
            "ORDER BY s.updated_on DESC LIMIT 10",
            (),
        )
        assert not rows, (
            f"Rider-delivered shipments missing delivered_date ({len(rows)}): "
            + ", ".join(r["zippee_awb"] for r in rows)
        )


# ─────────────────────────────────────────────────────────────────
# Consistency between zorms_shipment and ext
# ─────────────────────────────────────────────────────────────────

class TestMatviewConsistency:

    def test_no_orphan_rows_in_ext(self, db):
        """ext rows without a parent in zorms_shipment must not exist."""
        rows = db.fetch_all(
            "SELECT e.id FROM zorms_shipment_extention e "
            "LEFT JOIN zorms_shipment s ON s.id = e.id "
            "WHERE s.id IS NULL LIMIT 10",
            (),
        )
        assert not rows, (
            f"zorms_shipment_extention has {len(rows)} orphan rows with no matching shipment"
        )

    @pytest.mark.parametrize("awb", ALL_AWBS)
    def test_non_delivered_has_no_delivered_date(self, db, awb):
        """If shipment is not DELIVERED, delivered_date must be null."""
        row = db.fetch_one(
            "SELECT s.shipment_status, e.delivered_date FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no ext row"
        if row["shipment_status"] != "DELIVERED":
            assert row["delivered_date"] is None, (
                f"AWB {awb}: status is {row['shipment_status']} but "
                f"delivered_date is set to {row['delivered_date']}"
            )


# ─────────────────────────────────────────────────────────────────
# Delivery attempted — no rider/trip assigned, attempt_count synced
# ─────────────────────────────────────────────────────────────────

class TestDeliveryAttemptedSync:
    """
    Verify ext sync for AWBs where delivery was attempted but not completed.
    Expected state: attempt_count >= 1, rider/trip fields are null/empty.
    """

    @pytest.mark.parametrize("awb", AWBS_DELIVERY_ATTEMPTED)
    def test_ext_row_exists(self, db, awb):
        row = db.fetch_one(
            "SELECT e.id FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no row in zorms_shipment_extention"

    @pytest.mark.parametrize("awb", AWBS_DELIVERY_ATTEMPTED)
    def test_attempt_count_is_synced(self, db, awb):
        """attempt_count in ext must be >= 1 after a delivery attempt."""
        row = db.fetch_one(
            "SELECT e.attempt_count FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no ext row"
        assert row["attempt_count"] is not None and row["attempt_count"] >= 1, (
            f"AWB {awb}: attempt_count is {row['attempt_count']} "
            f"(expected >= 1 after delivery attempt)"
        )

    @pytest.mark.parametrize("awb", AWBS_DELIVERY_ATTEMPTED)
    def test_no_rider_or_trip_assigned(self, db, awb):
        """After a failed attempt with no current assignment, rider/trip must be null."""
        row = db.fetch_one(
            "SELECT e.current_rider_id, e.current_trip_id, e.current_rider_name "
            "FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no ext row"
        assert row["current_rider_id"] is None, (
            f"AWB {awb}: current_rider_id should be null but got {row['current_rider_id']}"
        )
        assert row["current_trip_id"] is None, (
            f"AWB {awb}: current_trip_id should be null but got {row['current_trip_id']}"
        )
        assert not row["current_rider_name"], (
            f"AWB {awb}: current_rider_name should be empty but got '{row['current_rider_name']}'"
        )

    @pytest.mark.parametrize("awb", AWBS_DELIVERY_ATTEMPTED)
    def test_delivered_date_is_null(self, db, awb):
        """No delivered_date for an attempted-but-not-delivered shipment."""
        row = db.fetch_one(
            "SELECT e.delivered_date FROM zorms_shipment s "
            "JOIN zorms_shipment_extention e ON s.id = e.id "
            "WHERE s.zippee_awb = %s",
            (awb,),
        )
        assert row, f"AWB {awb}: no ext row"
        assert row["delivered_date"] is None, (
            f"AWB {awb}: delivered_date should be null for attempted-not-delivered, "
            f"got {row['delivered_date']}"
        )
