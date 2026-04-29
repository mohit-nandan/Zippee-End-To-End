from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


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

    def swipe_up(self):
        size = self.driver.get_window_size()
        x = size["width"] // 2
        self.driver.swipe(x, int(size["height"] * 0.8), x, int(size["height"] * 0.2), 500)
