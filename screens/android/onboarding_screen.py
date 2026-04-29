from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class AndroidOnboardingScreen(BaseScreen):
    NAME_INPUT    = (AppiumBy.ID, "com.zippee.rider:id/name_input")
    VEHICLE_DROPDOWN = (AppiumBy.ID, "com.zippee.rider:id/vehicle_type")
    SUBMIT_BTN    = (AppiumBy.ID, "com.zippee.rider:id/onboarding_submit")
    SUCCESS_TEXT  = (AppiumBy.ID, "com.zippee.rider:id/onboarding_success")

    def complete_onboarding(self, name: str, vehicle: str):
        self.fill(self.NAME_INPUT, name)
        self.tap(self.VEHICLE_DROPDOWN)
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{vehicle}")'
        ).click()
        self.tap(self.SUBMIT_BTN)

    def is_success_shown(self) -> bool:
        return self.is_visible(self.SUCCESS_TEXT)
