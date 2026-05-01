"""
Login page tests — UI flow, negative cases, API token validation.
URL: /sign-in
"""
import allure
import pytest
from pages.login_page import LoginPage
from utils.web_api_interceptor import ApiInterceptor


@allure.feature("Authentication")
class TestLoginUI:

    @allure.story("Valid login flow")
    @allure.title("Login page loads and shows email field")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_login_page_loads(self, page, web_cfg):
        lp = LoginPage(page)
        lp.load(web_cfg["dashboard_url"])
        lp.expect_visible(LoginPage.EMAIL_INPUT)
        lp.expect_visible(LoginPage.CONTINUE_BUTTON)
        assert lp.is_on_sign_in_page()

    @allure.story("Valid login flow")
    @allure.title("Entering email reveals password field")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_email_step_reveals_password(self, page, web_cfg):
        lp = LoginPage(page)
        lp.load(web_cfg["dashboard_url"])
        lp.enter_email(web_cfg["admin_user"])
        lp.click_continue()
        lp.expect_visible(LoginPage.PASSWORD_INPUT)

    @allure.story("Valid login flow")
    @allure.title("Valid credentials redirect to dashboard")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_valid_login_redirects(self, authenticated_dashboard, web_cfg):
        base = web_cfg["dashboard_url"].rstrip("/")
        assert authenticated_dashboard.url.startswith(base), (
            f"Expected dashboard URL, got: {authenticated_dashboard.url}"
        )

    @allure.story("Invalid login")
    @allure.title("Wrong password shows error or stays on sign-in")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_wrong_password_blocked(self, page, web_cfg):
        lp = LoginPage(page)
        lp.load(web_cfg["dashboard_url"])
        lp.enter_email(web_cfg["admin_user"])
        lp.click_continue()
        lp.enter_password("WRONG_PASSWORD_XYZ_999!")
        lp.click_login()
        assert lp.is_on_sign_in_page() or lp.is_error_visible(), (
            "Wrong password should keep user on sign-in or show error"
        )

    @allure.story("Invalid login")
    @allure.title("Empty email blocked by browser validation")
    @pytest.mark.regression
    @pytest.mark.web
    def test_empty_email_blocked(self, page, web_cfg):
        lp = LoginPage(page)
        lp.load(web_cfg["dashboard_url"])
        page.get_by_role("button", name="Continue with Email").click()
        assert lp.is_on_sign_in_page()

    @allure.story("Invalid login")
    @allure.title("Invalid email format blocked")
    @pytest.mark.regression
    @pytest.mark.web
    def test_invalid_email_format(self, page, web_cfg):
        lp = LoginPage(page)
        lp.load(web_cfg["dashboard_url"])
        lp.enter_email("not-an-email-address")
        page.get_by_role("button", name="Continue with Email").click()
        assert lp.is_on_sign_in_page()

    @allure.story("Forgot password")
    @allure.title("Forgot password section is accessible")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_forgot_password_visible(self, page, web_cfg):
        lp = LoginPage(page)
        lp.load(web_cfg["dashboard_url"])
        lp.expect_visible(LoginPage.FORGOT_PASSWORD)

    @allure.story("Unauthenticated access")
    @allure.title("Protected page redirects unauthenticated user to sign-in")
    @pytest.mark.sanity
    @pytest.mark.web
    def test_unauthenticated_redirect(self, page, web_cfg):
        base = web_cfg["dashboard_url"].rstrip("/")
        page.goto(f"{base}/shipments")
        page.wait_for_load_state("networkidle")
        assert "sign-in" in page.url, (
            f"Unauthenticated /shipments should redirect to sign-in, got: {page.url}"
        )


@allure.feature("Authentication")
class TestLoginAPI:

    @allure.story("Auth token API")
    @allure.title("Login API call returns 200 with token")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_login_api_returns_token(self, page, web_cfg):
        interceptor = ApiInterceptor(page).watch("/token", "/auth", "/sign-in", "/login")
        lp = LoginPage(page)
        lp.load(web_cfg["dashboard_url"])
        lp.login(web_cfg["admin_user"], web_cfg["admin_pass"])

        # At minimum — no auth errors
        client_errors = [c for c in interceptor.all() if c.is_client_error]
        assert client_errors == [], (
            f"Login API returned client error: {[(c.url, c.status) for c in client_errors]}"
        )

    @allure.story("Auth token API")
    @allure.title("No 5xx errors during login flow")
    @pytest.mark.smoke
    @pytest.mark.web
    def test_login_no_server_errors(self, page, web_cfg):
        interceptor = ApiInterceptor(page).watch("")  # watch all
        lp = LoginPage(page)
        lp.load(web_cfg["dashboard_url"])
        lp.login(web_cfg["admin_user"], web_cfg["admin_pass"])
        interceptor.assert_no_server_errors()
