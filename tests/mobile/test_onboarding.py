import pytest
from unittest.mock import MagicMock, patch
from utils.helpers import get_onboarding_screen


RIDER_PHONE = "9800000001"
RIDER_OTP   = "1234"


@pytest.mark.smoke
@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_onboarding_flow_calls_correct_methods(mock_wait):
    mock_el = MagicMock()
    mock_wait.return_value.until.return_value = mock_el
    driver = MagicMock()
    driver.capabilities = {"platformName": "Android"}
    screen = get_onboarding_screen(driver)
    screen.fill(screen.NAME_INPUT, "Test Rider")
    screen.tap(screen.SUBMIT_BTN)
    mock_el.clear.assert_called()
    mock_el.click.assert_called()


@pytest.mark.smoke
@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_onboarding_success_check(mock_wait):
    mock_wait.return_value.until.return_value = MagicMock()
    driver = MagicMock()
    driver.capabilities = {"platformName": "iOS"}
    screen = get_onboarding_screen(driver)
    assert screen.is_success_shown() is True
