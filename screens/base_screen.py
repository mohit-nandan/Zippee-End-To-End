import subprocess
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Android keycode for each digit 0-9
_DIGIT_KEYCODE = {str(i): 7 + i for i in range(10)}


class BaseScreen:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def tap(self, locator: tuple, timeout: int = 10):
        by, value = locator
        el = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        el.click()

    def fill(self, locator: tuple, text: str, timeout: int = 10):
        by, value = locator
        el = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        el.clear()
        el.send_keys(text)

    def get_text(self, locator: tuple, timeout: int = 10) -> str:
        by, value = locator
        el = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return el.text

    def is_visible(self, locator: tuple, timeout: int = 5) -> bool:
        by, value = locator
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    def type_via_keyevent(self, text: str):
        """Type digits using adb key events — required for ViewGroup-based OTP boxes."""
        udid = self.driver.capabilities.get("udid", "emulator-5554")
        for char in str(text):
            code = _DIGIT_KEYCODE.get(char)
            if code is not None:
                subprocess.run(
                    ["adb", "-s", udid, "shell", "input", "keyevent", str(code)],
                    check=True,
                )

    def swipe_up(self):
        size = self.driver.get_window_size()
        x = size["width"] // 2
        self.driver.swipe(x, int(size["height"] * 0.8), x, int(size["height"] * 0.2), 500)
