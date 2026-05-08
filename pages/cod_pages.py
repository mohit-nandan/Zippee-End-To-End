import re
from playwright.sync_api import Page, expect


def _ensure_cod_visible(page, item_locator):
    """
    Check if the sidebar item is VISIBLE (not just attached).
    Hidden accordion items pass "attached" but fail "visible" — switching
    to visible correctly detects collapsed accordion state.
    If not visible, expand the COD accordion via its role=button element,
    then wait for the item to become visible before returning.
    """
    try:
        item_locator.wait_for(state="visible", timeout=2000)
    except Exception:
        # COD accordion is collapsed — expand it via its button role
        page.locator(".sidebar").get_by_role("button").filter(
            has_text=re.compile(r"COD", re.IGNORECASE)
        ).first.click()
        # Wait for item to be visible after animation
        item_locator.wait_for(state="visible", timeout=8000)


class CODAttendancePage:
    def __init__(self, page: Page):
        self.page = page

    def click_attendance_tab(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/global-filter/" in r.url
                      and "source=attendance" in r.url
                      and r.request.method == "POST",
            timeout=timeout,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Attendance\s*$", re.IGNORECASE)
            ).last
            _ensure_cod_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp


class CODDeactivatedRidersPage:
    def __init__(self, page: Page):
        self.page = page

    def click_deactivated_riders_tab(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/riders/deactivated/" in r.url and r.request.method == "GET",
            timeout=timeout,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Deactivated Riders\s*$", re.IGNORECASE)
            ).last
            _ensure_cod_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp


class CODPayoutsPage:
    def __init__(self, page: Page):
        self.page = page

    def click_payouts_tab(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/rider/payout/tracking/" in r.url and r.request.method == "GET",
            timeout=timeout,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Payouts\s*$", re.IGNORECASE)
            ).last
            _ensure_cod_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp


class CODPayrollPage:
    def __init__(self, page: Page):
        self.page = page

    def click_payroll_tab(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/payroll/" in r.url and r.request.method == "GET",
            timeout=timeout,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Rider Payroll\s*$", re.IGNORECASE)
            ).last
            _ensure_cod_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        # preprod returns total=0 / results=[] — no table-row assertion
        return resp


class CODRedoLogsPage:
    def __init__(self, page: Page):
        self.page = page

    def click_redo_logs_tab(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/redo-logs/" in r.url and r.request.method == "GET",
            timeout=timeout,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Redo Logs\s*$", re.IGNORECASE)
            ).last
            _ensure_cod_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp


class CODRidersKYCPage:
    def __init__(self, page: Page):
        self.page = page

    def click_riders_kyc_tab(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/riders/kyc/status/" in r.url and r.request.method == "GET",
            timeout=timeout,
        ) as resp_info:
            # Scope to <a> to avoid matching "Deactivated Riders" — mirrors Cypress: cy.contains('a', /^Riders$/)
            item = self.page.locator(".sidebar a").filter(
                has_text=re.compile(r"^\s*Riders\s*$", re.IGNORECASE)
            ).last
            _ensure_cod_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp


class CODSettlementsPage:
    def __init__(self, page: Page):
        self.page = page

    def click_settlements_tab(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/riders/kpi/" in r.url and r.request.method == "GET",
            timeout=timeout,
        ) as resp_info:
            item = self.page.locator(".sidebar").get_by_text(
                re.compile(r"^\s*Settlements\s*$", re.IGNORECASE)
            ).last
            _ensure_cod_visible(self.page, item)
            item.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        # riders/kpi returns KPI cards, not a table — no table-row assertion
        return resp

    def click_darkstores_kpi(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/settlements/darkstore/" in r.url and r.request.method == "GET",
            timeout=timeout,
        ) as resp_info:
            # mirrors Cypress: cy.contains('h2', 'Dark Store').closest('button').click()
            self.page.locator("button:has(h2:has-text('Dark Store'))").first.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp

    def click_company_kpi(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/settlements/company/" in r.url and r.request.method == "GET",
            timeout=timeout,
        ) as resp_info:
            # mirrors Cypress: cy.contains('h2', 'Company').closest('button').click()
            self.page.locator("button:has(h2:has-text('Company'))").first.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp

    def click_brands_kpi(self):
        timeout = 30000
        with self.page.expect_response(
            lambda r: "/app/api/settlements/brand/" in r.url and r.request.method == "GET",
            timeout=timeout,
        ) as resp_info:
            # mirrors Cypress: cy.contains('h2', 'Brand').closest('button').click()
            self.page.locator("button:has(h2:has-text('Brand'))").first.click()
        resp = resp_info.value
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        expect(self.page.locator("table tbody tr").first).to_be_visible(timeout=15000)
        return resp


class CODTemplatesPage:
    def __init__(self, page: Page):
        self.page = page

    def click_templates_tab(self):
        # mirrors Cypress: cy.contains("Create New Template").click(); cy.url().should('include','createNewPayroll')
        # React SPAs never reach networkidle — use wait_for_url instead
        item = self.page.locator(".sidebar").get_by_text(
            re.compile(r"^\s*Create New Template\s*$", re.IGNORECASE)
        ).last
        _ensure_cod_visible(self.page, item)
        item.click()
        self.page.wait_for_url("**/createNewPayroll**", timeout=20000)
        return None
