"""
API endpoint specs for network interception tests.

Structure per page: list of endpoint dicts, each with:
  path          — URL substring to match (interceptor uses substring matching)
  expected_keys — top-level keys that must exist in the JSON response body
  schema        — optional deeper schema: {key: type} validated via schema_validator

Add entries for remaining pages as you capture them from DevTools.
"""

# Common envelope present on every Zippee API response
_ENVELOPE = ["data", "status", "result"]

DASHBOARD_ENDPOINTS = {

    # ── Home Dashboard ────────────────────────────────────────────────────
    "home": [
        {
            "path": "/api/1/home/",
            "expected_keys": _ENVELOPE,
            "schema": {"data": dict, "status": str, "result": bool},
        },
        {
            "path": "/api/1/auth/user/",
            "expected_keys": _ENVELOPE,
            "schema": {"data": dict, "status": str, "result": bool},
        },
        {
            "path": "/api/1/brands/options/",
            "expected_keys": _ENVELOPE,
            "schema": {"data": list, "status": str, "result": bool},
        },
    ],

    # ── Remaining pages — fill in paths from DevTools as you capture them ──
    "brands":       [],
    "orders":       [],
    "shipments":    [],
    "deliveries":   [],
    "settlement":   [],
    "riders_kyc":   [],
    "billing":      [],
    "analytics":    [],
    "rules":        [],
    "manual_upload": [],
}

# Nested field specs used for deeper home KPI validation
HOME_KPI_FIELDS     = ["today_orders", "delivered_orders", "prepaid_orders"]
HOME_USER_FIELDS    = ["name", "user_id", "email", "user_type", "permissions"]
HOME_BRAND_ITEM_FIELDS = ["id", "brand_display_name", "status", "brand_type"]
