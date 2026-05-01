"""
Static test data for web UI tests.
Keeps test logic clean — tests import constants from here, never hardcode values.
"""

# ── Known preprod fixtures ────────────────────────────────────────────────────

KNOWN_BRAND      = "testing_fabbox"
KNOWN_DARKSTORE  = "express_warehouse"
KNOWN_RIDER_NAME = "Test"          # partial match, exists in KYC table
KNOWN_CITY       = "Delhi"
KNOWN_RULE_NAME  = "express_warehouse"

# ── Search inputs that should produce zero results ────────────────────────────

NO_MATCH_STRING  = "ZZZNOTEXIST_99999"

# ── Payment modes ────────────────────────────────────────────────────────────

PAYMENT_MODES    = ["COD", "Prepaid", "Online"]

# ── Shipment statuses (as shown in UI dropdowns) ──────────────────────────────

SHIPMENT_STATUSES = ["PROCESSED", "OPEN", "FAILED"]

# ── PND delivery sub-tabs ────────────────────────────────────────────────────

PND_TABS = ["assign_now", "assign_later", "assigned", "completed", "return", "all_shipments"]

# ── Settlement tabs ───────────────────────────────────────────────────────────

SETTLEMENT_TABS = ["rider", "dark_store", "company", "brand"]

# ── Analytics tabs ────────────────────────────────────────────────────────────

ANALYTICS_TABS = ["operations", "business", "brands"]

# ── All navigable pages (section_key → expected_url_fragment) ────────────────

ALL_ROUTES = {
    "home":            "/",
    "brands":          "/brand",
    "analytics":       "/analytics",
    "emergency_comms": "/emergency-comms",
    "billing":         "/billing",
    "rules":           "/rules",
    "shipments":       "/shipments",
    "orders":          "/orders",
    "settlement":      "/settlement",
    "riders_kyc":      "/kyc",
    "manual_upload":   "/manualUpload",
    "deliveries":      "/pnd",
    "express_hub":     "/pnd/express-hub",
    "store_transfer":  "/store-transfer",
    "print_waybills":  "/pick-and-del/print-waybills",
}

# ── API URL patterns (fragments matched against full URL) ─────────────────────

API = {
    "brands":      "/brand",
    "shipments":   "/shipment",
    "orders":      "/order",
    "deliveries":  "/pnd",
    "settlement":  "/settlement",
    "riders":      "/kyc",
    "billing":     "/billing",
    "analytics":   "/analytics",
    "rules":       "/rules",
    "auth":        "/token",
}
