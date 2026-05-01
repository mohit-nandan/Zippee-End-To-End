from pages.base_page import BasePage


class NavPage(BasePage):
    SIDEBAR = "div.sidebar"

    NAV = {
        "home":             "/",
        "brands":           "/brand",
        "analytics":        "/analytics",
        "emergency_comms":  "/emergency-comms",
        "billing":          "/billing",
        "rules":            "/rules",
        "stores":           "/stores",
        "ds_profile":       "/ds-profile",
        "shipments":        "/shipments",
        "orders":           "/orders",
        "settlement":       "/settlement",
        "attendance":       "/attendenceDashboard",
        "payouts":          "/payoutConsole",
        "payroll_template": "/createNewPayroll",
        "rider_payroll":    "/riderPayroll",
        "deactivated":      "/deactivatedRider",
        "riders_kyc":       "/kyc",
        "redo_logs":        "/redoLogs",
        "manual_upload":    "/manualUpload",
        "deliveries":       "/pnd",
        "print_waybills":   "/pick-and-del/print-waybills",
        "express_hub":      "/pnd/express-hub",
        "store_transfer":   "/store-transfer",
    }

    def go_to(self, section: str, base_url: str):
        path = self.NAV[section]
        self.navigate(f"{base_url}{path}")

    def expand_middleware(self):
        self.page.get_by_role("button").filter(has_text="Middleware").click()

    def expand_cod(self):
        self.page.get_by_role("button").filter(has_text="COD").click()

    def expand_pickup_delivery(self):
        self.page.get_by_role("button").filter(has_text="Pickup Delivery").click()

    def is_sidebar_visible(self) -> bool:
        return self.is_visible(self.SIDEBAR)
