"""
Home / Dashboard page tests.
URL: /
"""
import pytest
from pages.home_page import HomePage
from pages.nav_page import NavPage


@pytest.mark.smoke
@pytest.mark.web
def test_home_page_loads(authenticated_dashboard, web_cfg):
    home = HomePage(authenticated_dashboard)
    home.go_to("home", web_cfg["dashboard_url"])
    assert home.is_loaded(), "Home page stats should be visible after login"


@pytest.mark.smoke
@pytest.mark.web
def test_home_new_orders_card_visible(authenticated_dashboard, web_cfg):
    home = HomePage(authenticated_dashboard)
    home.go_to("home", web_cfg["dashboard_url"])
    home.expect_visible(HomePage.NEW_ORDERS_CARD)


@pytest.mark.smoke
@pytest.mark.web
def test_home_prepaid_card_visible(authenticated_dashboard, web_cfg):
    home = HomePage(authenticated_dashboard)
    home.go_to("home", web_cfg["dashboard_url"])
    home.expect_visible(HomePage.PREPAID_CARD)


@pytest.mark.smoke
@pytest.mark.web
def test_home_delivered_card_visible(authenticated_dashboard, web_cfg):
    home = HomePage(authenticated_dashboard)
    home.go_to("home", web_cfg["dashboard_url"])
    home.expect_visible(HomePage.DELIVERED_CARD)


@pytest.mark.sanity
@pytest.mark.web
def test_home_coverage_map_visible(authenticated_dashboard, web_cfg):
    home = HomePage(authenticated_dashboard)
    home.go_to("home", web_cfg["dashboard_url"])
    assert home.is_coverage_section_visible(), "Zippee Coverage section should be visible"


@pytest.mark.sanity
@pytest.mark.web
def test_home_brand_dropdown_visible(authenticated_dashboard, web_cfg):
    home = HomePage(authenticated_dashboard)
    home.go_to("home", web_cfg["dashboard_url"])
    home.expect_visible(HomePage.BRAND_DROPDOWN)


@pytest.mark.sanity
@pytest.mark.web
def test_sidebar_is_visible_on_home(authenticated_dashboard, web_cfg):
    nav = NavPage(authenticated_dashboard)
    nav.go_to("home", web_cfg["dashboard_url"])
    assert nav.is_sidebar_visible(), "Sidebar must be visible on every authenticated page"
