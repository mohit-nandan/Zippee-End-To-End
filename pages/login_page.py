from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Update selectors to match your actual dashboard login page HTML.
    Inspect elements in browser DevTools to find correct selectors.
    """
    EMAIL_INPUT    = "input[name='email']"
    PASSWORD_INPUT = "input[name='password']"
    SUBMIT_BUTTON  = "button[type='submit']"
    ERROR_MESSAGE  = ".error-message, .alert-danger, [data-testid='login-error']"

    def enter_email(self, email: str):
        self.fill(self.EMAIL_INPUT, email)

    def enter_password(self, password: str):
        self.fill(self.PASSWORD_INPUT, password)

    def submit(self):
        self.click(self.SUBMIT_BUTTON)
        self.page.wait_for_load_state("networkidle")

    def is_error_visible(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)
