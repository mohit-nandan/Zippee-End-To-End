from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class AndroidDrawerScreen(BaseScreen):
    # Profile row — content-desc is dynamic ("Name, # RIDER_ID"), so match by partial text
    PROFILE_ROW     = (AppiumBy.XPATH, '//android.view.ViewGroup[contains(@content-desc, "#")]')

    # Menu items
    HELP_SUPPORT    = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Help & Support"]')
    BEST_PRACTICES  = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Rider\'s Best Practices"]')
    TERMS           = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Terms & Conditions"]')
    LOG_OUT         = (AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Log Out"]')

    # Confirmation dialog
    LOGOUT_CONFIRM  = (AppiumBy.XPATH, '//android.widget.TextView[@text="Confirm"]')
    LOGOUT_CANCEL   = (AppiumBy.XPATH, '//android.widget.TextView[@text="Cancel"]')
    LOGOUT_DIALOG   = (AppiumBy.XPATH, '//android.widget.TextView[@text="Log Out?"]')

    # ------------------------------------------------------------------ #

    def is_loaded(self, timeout: int = 10) -> bool:
        return self.is_visible(self.LOG_OUT, timeout=timeout)

    def get_rider_name(self) -> str:
        text = self.get_text(self.PROFILE_ROW)
        return text.split(",")[0].strip() if "," in text else text

    def tap_profile(self):
        self.tap(self.PROFILE_ROW)

    def tap_help_support(self):
        self.tap(self.HELP_SUPPORT)

    def tap_best_practices(self):
        self.tap(self.BEST_PRACTICES)

    def tap_terms(self):
        self.tap(self.TERMS)

    def tap_log_out(self):
        self.tap(self.LOG_OUT)

    def confirm_logout(self):
        self.tap(self.LOGOUT_CONFIRM)

    def cancel_logout(self):
        self.tap(self.LOGOUT_CANCEL)

    def is_logout_dialog_visible(self, timeout: int = 5) -> bool:
        return self.is_visible(self.LOGOUT_DIALOG, timeout=timeout)

    def logout(self):
        """Full logout: tap Log Out → confirm dialog."""
        self.tap_log_out()
        assert self.is_logout_dialog_visible(), "Log Out confirmation dialog did not appear"
        self.confirm_logout()
