import pytest
from unittest.mock import MagicMock, patch
from pages.base_page import BasePage


@pytest.mark.web
def test_navigate_calls_goto_and_waits():
    mock_page = MagicMock()
    bp = BasePage(mock_page)
    bp.navigate("https://example.com")
    mock_page.goto.assert_called_once_with("https://example.com")
    mock_page.wait_for_load_state.assert_called_once_with("networkidle")


@pytest.mark.web
def test_fill_calls_locator_fill():
    mock_page = MagicMock()
    bp = BasePage(mock_page)
    bp.fill("input[name='email']", "test@test.com")
    mock_page.locator.assert_called_with("input[name='email']")
    mock_page.locator().fill.assert_called_with("test@test.com")


@pytest.mark.web
def test_is_visible_returns_bool():
    mock_page = MagicMock()
    mock_page.locator.return_value.is_visible.return_value = True
    bp = BasePage(mock_page)
    assert bp.is_visible(".some-element") is True


@pytest.mark.web
def test_get_text_returns_inner_text():
    mock_page = MagicMock()
    mock_page.locator.return_value.inner_text.return_value = "Order #123"
    bp = BasePage(mock_page)
    assert bp.get_text(".order-id") == "Order #123"
