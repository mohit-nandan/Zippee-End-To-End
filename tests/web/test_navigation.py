"""
Navigation smoke tests — every route loads without errors.
Parametrized so adding a new route = one line in test_data/web_test_data.py.
"""
import allure
import pytest
from pages.nav_page import NavPage
from pages.base_page import BasePage
from utils.web_api_interceptor import ApiInterceptor
from test_data.web_test_data import ALL_ROUTES


@allure.feature("Navigation")
class TestNavigationSmoke:

    @allure.story("Page routing")
    @allure.title("Page loads without 5xx — {section}")
    @pytest.mark.smoke
    @pytest.mark.web
    @pytest.mark.parametrize("section,path", list(ALL_ROUTES.items()))
    def test_no_server_errors(self, authenticated_dashboard, web_cfg, section, path):
        interceptor = ApiInterceptor(authenticated_dashboard).watch("")
        nav = NavPage(authenticated_dashboard)
        with allure.step(f"Navigate to {section} ({path})"):
            nav.go_to(section, web_cfg["dashboard_url"])
            nav.wait_for_spinner_gone()
        interceptor.assert_no_server_errors()

    @allure.story("Page routing")
    @allure.title("URL contains expected path — {section}")
    @pytest.mark.smoke
    @pytest.mark.web
    @pytest.mark.parametrize("section,path", list(ALL_ROUTES.items()))
    def test_url_correct(self, authenticated_dashboard, web_cfg, section, path):
        nav = NavPage(authenticated_dashboard)
        nav.go_to(section, web_cfg["dashboard_url"])
        nav.wait_for_spinner_gone()
        assert path in nav.current_url(), (
            f"Expected URL to contain '{path}', got: {nav.current_url()}"
        )

    @allure.story("Page routing")
    @allure.title("Sidebar persists on every page — {section}")
    @pytest.mark.smoke
    @pytest.mark.web
    @pytest.mark.parametrize("section,path", list(ALL_ROUTES.items()))
    def test_sidebar_persists(self, authenticated_dashboard, web_cfg, section, path):
        nav = NavPage(authenticated_dashboard)
        nav.go_to(section, web_cfg["dashboard_url"])
        assert nav.is_sidebar_visible(), f"Sidebar missing on {path}"

    @allure.story("Auth guard")
    @allure.title("Unauthenticated access is redirected to sign-in")
    @pytest.mark.sanity
    @pytest.mark.web
    @pytest.mark.parametrize("section,path", [
        ("shipments", "/shipments"),
        ("brands",    "/brand"),
        ("orders",    "/orders"),
    ])
    def test_unauth_redirect(self, page, web_cfg, section, path):
        base = web_cfg["dashboard_url"].rstrip("/")
        page.goto(f"{base}{path}")
        page.wait_for_load_state("networkidle")
        assert "sign-in" in page.url, (
            f"Expected redirect to sign-in for {path}, got: {page.url}"
        )
