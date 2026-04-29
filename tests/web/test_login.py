import pytest
from unittest.mock import MagicMock
from pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.web
def test_login_page_enter_email_calls_fill():
    mock_page = MagicMock()
    lp = LoginPage(mock_page)
    lp.enter_email("rider@zippee.in")
    mock_page.locator.assert_called_with(LoginPage.EMAIL_INPUT)
    mock_page.locator().fill.assert_called_with("rider@zippee.in")


@pytest.mark.web
def test_login_page_enter_password_calls_fill():
    mock_page = MagicMock()
    lp = LoginPage(mock_page)
    lp.enter_password("secret123")
    mock_page.locator.assert_called_with(LoginPage.PASSWORD_INPUT)
    mock_page.locator().fill.assert_called_with("secret123")


@pytest.mark.sanity
@pytest.mark.web
def test_login_page_submit_clicks_and_waits():
    mock_page = MagicMock()
    lp = LoginPage(mock_page)
    lp.submit()
    mock_page.locator.assert_called_with(LoginPage.SUBMIT_BUTTON)
    mock_page.locator().click.assert_called_once()
    mock_page.wait_for_load_state.assert_called_with("networkidle")


@pytest.mark.web
def test_login_page_is_error_visible_true():
    mock_page = MagicMock()
    mock_page.locator.return_value.is_visible.return_value = True
    lp = LoginPage(mock_page)
    assert lp.is_error_visible() is True


@pytest.mark.web
def test_login_page_is_error_visible_false():
    mock_page = MagicMock()
    mock_page.locator.return_value.is_visible.return_value = False
    lp = LoginPage(mock_page)
    assert lp.is_error_visible() is False
