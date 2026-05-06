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

    # ── Brands ───────────────────────────────────────────────────────────
    "brands": [
        {
            "path": "/api/1/brands/",
            "expected_keys": _ENVELOPE,
            "schema": {"data": dict, "status": str, "result": bool},
        },
    ],

    # ── Remaining pages — fill in paths from DevTools as you capture them ──
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

# ── Home nested field specs ───────────────────────────────────────────────────
HOME_KPI_FIELDS        = ["today_orders", "delivered_orders", "prepaid_orders"]
HOME_USER_FIELDS       = ["name", "user_id", "email", "user_type", "permissions"]
HOME_BRAND_ITEM_FIELDS = ["id", "brand_display_name", "status", "brand_type"]

# ── Brands nested field specs ─────────────────────────────────────────────────
BRANDS_PAGINATION_FIELDS = ["next", "previous", "total", "total_pages", "page", "page_size", "results"]
BRANDS_ITEM_FIELDS       = ["id", "brand_display_name", "status", "whatsapp_basic_notif",
                             "wa_re_a_notif", "wa_cod_notif", "category", "wallet_balance"]
