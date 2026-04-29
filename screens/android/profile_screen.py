from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class ProfileScreen(BaseScreen):
    _NAME_TEXT        = (AppiumBy.XPATH, '//*[@content-desc="rider-name" or contains(@text,"Rider")]')
    _PHONE_TEXT       = (AppiumBy.XPATH, '//*[@content-desc="rider-phone"]')
    _KYC_STATUS       = (AppiumBy.XPATH, '//*[contains(@text,"KYC") or @content-desc="kyc-status"]')
    _BANK_DETAILS_BTN = (AppiumBy.XPATH, '//*[@text="Bank Details" or @content-desc="Bank Details"]')
    _LOGOUT_BTN       = (AppiumBy.XPATH, '//*[@text="Logout" or @content-desc="Logout"]')
    _CONFIRM_LOGOUT   = (AppiumBy.XPATH, '//*[@text="Yes" or @text="Confirm"]')

    def get_rider_name(self) -> str:
        return self.get_text(self._NAME_TEXT)

    def get_kyc_status(self) -> str:
        return self.get_text(self._KYC_STATUS)

    def tap_bank_details(self):
        self.tap(self._BANK_DETAILS_BTN)

    def logout(self):
        self.tap(self._LOGOUT_BTN)
        if self.is_visible(self._CONFIRM_LOGOUT):
            self.tap(self._CONFIRM_LOGOUT)
