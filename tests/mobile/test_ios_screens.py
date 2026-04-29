import pytest
from unittest.mock import MagicMock, patch
from screens.ios.login_screen import IOSLoginScreen
from screens.ios.home_screen import IOSHomeScreen
from screens.ios.delivery_screen import IOSDeliveryScreen
from screens.ios.onboarding_screen import IOSOnboardingScreen


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_ios_login_calls_fill_and_tap_in_order(mock_wait):
    mock_el = MagicMock()
    mock_wait.return_value.until.return_value = mock_el
    driver = MagicMock()
    screen = IOSLoginScreen(driver)
    screen.login(phone="9800000001", otp="1234")
    assert mock_el.clear.call_count >= 2
    assert mock_el.click.call_count >= 2


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_ios_home_is_loaded_checks_welcome_text(mock_wait):
    mock_wait.return_value.until.return_value = MagicMock()
    driver = MagicMock()
    screen = IOSHomeScreen(driver)
    assert screen.is_loaded() is True


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_ios_delivery_confirm_fills_otp_and_taps(mock_wait):
    mock_el = MagicMock()
    mock_wait.return_value.until.return_value = mock_el
    driver = MagicMock()
    screen = IOSDeliveryScreen(driver)
    screen.confirm_delivery("4321")
    mock_el.clear.assert_called()
    mock_el.send_keys.assert_called_with("4321")
    assert mock_el.click.called


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_ios_onboarding_is_success_shown(mock_wait):
    mock_wait.return_value.until.return_value = MagicMock()
    driver = MagicMock()
    screen = IOSOnboardingScreen(driver)
    assert screen.is_success_shown() is True


@pytest.mark.mobile
def test_ios_uses_accessibility_id_locators():
    from appium.webdriver.common.appiumby import AppiumBy
    assert IOSLoginScreen.PHONE_INPUT[0] == AppiumBy.ACCESSIBILITY_ID
    assert IOSDeliveryScreen.CONFIRM_BTN[0] == AppiumBy.ACCESSIBILITY_ID


@pytest.mark.mobile
def test_android_uses_resource_id_locators():
    from appium.webdriver.common.appiumby import AppiumBy
    from screens.android.login_screen import AndroidLoginScreen
    from screens.android.delivery_screen import AndroidDeliveryScreen
    assert AndroidLoginScreen.PHONE_INPUT[0] == AppiumBy.ID
    assert AndroidDeliveryScreen.CONFIRM_BTN[0] == AppiumBy.ID
