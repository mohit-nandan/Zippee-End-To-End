import pytest
from unittest.mock import MagicMock, patch
from utils.helpers import get_delivery_screen, get_home_screen


@pytest.mark.smoke
@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_delivery_confirm_otp_flow_android(mock_wait):
    mock_el = MagicMock()
    mock_el.text = "Delivered"
    mock_wait.return_value.until.return_value = mock_el
    driver = MagicMock()
    driver.capabilities = {"platformName": "Android"}
    screen = get_delivery_screen(driver)
    screen.confirm_delivery("4321")
    mock_el.send_keys.assert_called_with("4321")
    assert mock_el.click.called


@pytest.mark.smoke
@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_delivery_confirm_otp_flow_ios(mock_wait):
    mock_el = MagicMock()
    mock_el.text = "Delivered"
    mock_wait.return_value.until.return_value = mock_el
    driver = MagicMock()
    driver.capabilities = {"platformName": "iOS"}
    screen = get_delivery_screen(driver)
    screen.confirm_delivery("4321")
    mock_el.send_keys.assert_called_with("4321")
    assert mock_el.click.called


@pytest.mark.sanity
@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_home_screen_go_to_orders(mock_wait):
    mock_wait.return_value.until.return_value = MagicMock()
    driver = MagicMock()
    driver.capabilities = {"platformName": "Android"}
    home = get_home_screen(driver)
    home.go_to_orders()
    assert mock_wait.return_value.until.called
