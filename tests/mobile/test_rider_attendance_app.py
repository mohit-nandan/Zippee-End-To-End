import pytest
from unittest.mock import MagicMock, patch
from utils.helpers import get_home_screen


@pytest.mark.smoke
@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_mark_attendance_android(mock_wait):
    mock_wait.return_value.until.return_value = MagicMock()
    driver = MagicMock()
    driver.capabilities = {"platformName": "Android"}
    home = get_home_screen(driver)
    home.mark_attendance()
    assert mock_wait.return_value.until.called


@pytest.mark.smoke
@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_mark_attendance_ios(mock_wait):
    mock_wait.return_value.until.return_value = MagicMock()
    driver = MagicMock()
    driver.capabilities = {"platformName": "iOS"}
    home = get_home_screen(driver)
    home.mark_attendance()
    assert mock_wait.return_value.until.called
