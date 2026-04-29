from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class AttendanceScreen(BaseScreen):
    _MARK_BTN        = (AppiumBy.XPATH, '//*[@text="Mark Attendance" or @content-desc="Mark Attendance"]')
    _STATUS_TEXT     = (AppiumBy.XPATH, '//*[contains(@text,"Present") or contains(@text,"Absent")]')
    _CONFIRM_BTN     = (AppiumBy.XPATH, '//*[@text="Confirm" or @content-desc="Confirm"]')
    _SUCCESS_TOAST   = (AppiumBy.XPATH, '//*[contains(@text,"marked") or contains(@text,"success")]')

    def mark_attendance(self):
        self.tap(self._MARK_BTN)
        if self.is_visible(self._CONFIRM_BTN):
            self.tap(self._CONFIRM_BTN)

    def get_status(self) -> str:
        return self.get_text(self._STATUS_TEXT)

    def is_success_shown(self) -> bool:
        return self.is_visible(self._SUCCESS_TOAST)
