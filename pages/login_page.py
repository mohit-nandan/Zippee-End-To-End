from pages.base_page import BasePage


class LoginPage(BasePage):
    EMAIL_INPUT      = "#email"
    CONTINUE_BUTTON  = "button:has-text('Continue with Email')"
    PASSWORD_INPUT   = "input[type='password']"
    LOGIN_BUTTON     = "button[type='submit']:has-text('Login')"
    ERROR_MESSAGE    = ".error-message, .alert-danger, [class*='error'], [class*='toast-error']"
    FORGOT_PASSWORD  = "[class*='Forgot'], :text('Forgot Password')"

    def load(self, base_url: str):
        self.navigate(f"{base_url}/sign-in")

    def enter_email(self, email: str):
        self.page.locator(self.EMAIL_INPUT).fill(email)

    def click_continue(self):
        self.page.locator(self.CONTINUE_BUTTON).click()
        self.page.locator(self.PASSWORD_INPUT).wait_for(state="visible", timeout=5000)

    def enter_password(self, password: str):
        self.page.locator(self.PASSWORD_INPUT).fill(password)

    def click_login(self):
        self.page.get_by_role("button", name="Login", exact=True).click()
        self.page.wait_for_load_state("networkidle")

    def login(self, email: str, password: str):
        self.enter_email(email)
        self.click_continue()
        self.enter_password(password)
        self.click_login()

    def is_error_visible(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)

    def is_on_sign_in_page(self) -> bool:
        return "sign-in" in self.current_url()
