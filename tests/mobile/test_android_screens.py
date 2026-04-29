import pytest
from unittest.mock import MagicMock, patch
from screens.android.login_screen import AndroidLoginScreen
from screens.android.home_screen import AndroidHomeScreen
from screens.android.delivery_screen import AndroidDeliveryScreen
from screens.android.onboarding_screen import AndroidOnboardingScreen


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_android_login_calls_fill_and_tap_in_order(mock_wait):
    mock_el = MagicMock()
    mock_wait.return_value.until.return_value = mock_el
    driver = MagicMock()
    screen = AndroidLoginScreen(driver)
    screen.login(phone="9800000001", otp="1234")
    assert mock_el.clear.call_count >= 2
    assert mock_el.click.call_count >= 2


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_android_home_is_loaded_checks_welcome_text(mock_wait):
    mock_wait.return_value.until.return_value = MagicMock()
    driver = MagicMock()
    screen = AndroidHomeScreen(driver)
    result = screen.is_loaded()
    assert result is True


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_android_delivery_confirm_fills_otp_and_taps(mock_wait):
    mock_el = MagicMock()
    mock_wait.return_value.until.return_value = mock_el
    driver = MagicMock()
    screen = AndroidDeliveryScreen(driver)
    screen.confirm_delivery("4321")
    mock_el.clear.assert_called()
    mock_el.send_keys.assert_called_with("4321")
    assert mock_el.click.called


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_android_onboarding_is_success_shown(mock_wait):
    mock_wait.return_value.until.return_value = MagicMock()
    driver = MagicMock()
    screen = AndroidOnboardingScreen(driver)
    result = screen.is_success_shown()
    assert result is True
