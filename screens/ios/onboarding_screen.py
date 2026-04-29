from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class IOSOnboardingScreen(BaseScreen):
    NAME_INPUT   = (AppiumBy.ACCESSIBILITY_ID, "name_input")
    VEHICLE_BTN  = (AppiumBy.ACCESSIBILITY_ID, "vehicle_type")
    SUBMIT_BTN   = (AppiumBy.ACCESSIBILITY_ID, "onboarding_submit")
    SUCCESS_TEXT = (AppiumBy.ACCESSIBILITY_ID, "onboarding_success")

    def complete_onboarding(self, name: str, vehicle: str):
        self.fill(self.NAME_INPUT, name)
        self.tap(self.VEHICLE_BTN)
        self.driver.find_element(
            AppiumBy.XPATH,
            f"//XCUIElementTypeStaticText[@name='{vehicle}']"
        ).click()
        self.tap(self.SUBMIT_BTN)

    def is_success_shown(self) -> bool:
        return self.is_visible(self.SUCCESS_TEXT)
