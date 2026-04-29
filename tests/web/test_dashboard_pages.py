import pytest
from unittest.mock import MagicMock
from pages.dashboard_page import DashboardPage
from pages.order_list_page import OrderListPage
from pages.order_detail_page import OrderDetailPage


@pytest.mark.smoke
@pytest.mark.web
def test_dashboard_is_loaded_via_stats_card():
    mock_page = MagicMock()
    mock_page.locator.return_value.is_visible.return_value = True
    mock_page.url = "https://dashboard.zippee.in/dashboard"
    dp = DashboardPage(mock_page)
    assert dp.is_loaded() is True


@pytest.mark.web
def test_dashboard_go_to_orders_returns_order_list_page():
    mock_page = MagicMock()
    dp = DashboardPage(mock_page)
    result = dp.go_to_orders()
    assert isinstance(result, OrderListPage)
    mock_page.locator.assert_called_with(DashboardPage.NAV_ORDERS)
    mock_page.locator().click.assert_called_once()


@pytest.mark.web
def test_order_list_search_fills_and_presses_enter():
    mock_page = MagicMock()
    olp = OrderListPage(mock_page)
    olp.search_order("AUTO_TEST_ABC123")
    mock_page.locator.assert_called_with(OrderListPage.SEARCH_INPUT)
    mock_page.locator().fill.assert_called_with("AUTO_TEST_ABC123")
    mock_page.keyboard.press.assert_called_with("Enter")


@pytest.mark.web
def test_order_list_order_count_uses_locator():
    mock_page = MagicMock()
    mock_page.locator.return_value.count.return_value = 5
    olp = OrderListPage(mock_page)
    assert olp.order_count() == 5


@pytest.mark.web
def test_order_list_open_first_order_returns_detail_page():
    mock_page = MagicMock()
    olp = OrderListPage(mock_page)
    result = olp.open_first_order()
    assert isinstance(result, OrderDetailPage)


@pytest.mark.sanity
@pytest.mark.web
def test_order_detail_get_status_returns_text():
    mock_page = MagicMock()
    mock_page.locator.return_value.inner_text.return_value = "delivered"
    odp = OrderDetailPage(mock_page)
    assert odp.get_status() == "delivered"


@pytest.mark.sanity
@pytest.mark.web
def test_order_detail_get_order_id_returns_text():
    mock_page = MagicMock()
    mock_page.locator.return_value.inner_text.return_value = "ORD-001"
    odp = OrderDetailPage(mock_page)
    assert odp.get_order_id() == "ORD-001"
