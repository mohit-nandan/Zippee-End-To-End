import pytest
from unittest.mock import MagicMock, patch
from utils.helpers import get_delivery_screen


@pytest.mark.sanity
@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_delivery_attempted_taps_attempt_button_android(mock_wait):
    mock_el = MagicMock()
    mock_wait.return_value.until.return_value = mock_el
    driver = MagicMock()
    driver.capabilities = {"platformName": "Android"}
    screen = get_delivery_screen(driver)
    screen.tap(screen.ATTEMPT_BTN)
    mock_el.click.assert_called_once()


@pytest.mark.sanity
@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_delivery_attempted_taps_attempt_button_ios(mock_wait):
    mock_el = MagicMock()
    mock_wait.return_value.until.return_value = mock_el
    driver = MagicMock()
    driver.capabilities = {"platformName": "iOS"}
    screen = get_delivery_screen(driver)
    screen.tap(screen.ATTEMPT_BTN)
    mock_el.click.assert_called_once()
