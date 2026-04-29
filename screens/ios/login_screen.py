from appium.webdriver.common.appiumby import AppiumBy
from screens.base_screen import BaseScreen


class IOSLoginScreen(BaseScreen):
    PHONE_INPUT  = (AppiumBy.ACCESSIBILITY_ID, "phone_input")
    OTP_INPUT    = (AppiumBy.ACCESSIBILITY_ID, "otp_input")
    SEND_OTP_BTN = (AppiumBy.ACCESSIBILITY_ID, "send_otp_button")
    VERIFY_BTN   = (AppiumBy.ACCESSIBILITY_ID, "verify_otp_button")

    def enter_phone(self, phone: str):
        self.fill(self.PHONE_INPUT, phone)

    def request_otp(self):
        self.tap(self.SEND_OTP_BTN)

    def enter_otp(self, otp: str):
        self.fill(self.OTP_INPUT, otp)

    def verify(self):
        self.tap(self.VERIFY_BTN)

    def login(self, phone: str, otp: str):
        self.enter_phone(phone)
        self.request_otp()
        self.enter_otp(otp)
        self.verify()
