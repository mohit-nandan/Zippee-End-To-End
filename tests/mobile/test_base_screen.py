import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import TimeoutException
from screens.base_screen import BaseScreen


def make_screen():
    mock_driver = MagicMock()
    return BaseScreen(mock_driver), mock_driver


@pytest.mark.mobile
def test_base_screen_stores_driver():
    screen, driver = make_screen()
    assert screen.driver is driver


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_tap_waits_for_clickable_and_clicks(mock_wait):
    mock_el = MagicMock()
    mock_wait.return_value.until.return_value = mock_el
    screen, driver = make_screen()
    screen.tap(("id", "some-button"))
    mock_el.click.assert_called_once()


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_fill_clears_then_sends_keys(mock_wait):
    mock_el = MagicMock()
    mock_wait.return_value.until.return_value = mock_el
    screen, driver = make_screen()
    screen.fill(("id", "some-input"), "test text")
    mock_el.clear.assert_called_once()
    mock_el.send_keys.assert_called_once_with("test text")


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_get_text_returns_element_text(mock_wait):
    mock_el = MagicMock()
    mock_el.text = "Delivered"
    mock_wait.return_value.until.return_value = mock_el
    screen, driver = make_screen()
    assert screen.get_text(("id", "status-label")) == "Delivered"


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_is_visible_returns_true_when_found(mock_wait):
    mock_wait.return_value.until.return_value = MagicMock()
    screen, driver = make_screen()
    assert screen.is_visible(("id", "some-el")) is True


@pytest.mark.mobile
@patch("screens.base_screen.WebDriverWait")
def test_is_visible_returns_false_on_timeout(mock_wait):
    mock_wait.return_value.until.side_effect = TimeoutException()
    screen, driver = make_screen()
    assert screen.is_visible(("id", "missing-el")) is False


@pytest.mark.mobile
def test_swipe_up_calls_driver_swipe():
    screen, driver = make_screen()
    driver.get_window_size.return_value = {"width": 400, "height": 800}
    screen.swipe_up()
    driver.swipe.assert_called_once_with(200, 640, 200, 160, 500)
