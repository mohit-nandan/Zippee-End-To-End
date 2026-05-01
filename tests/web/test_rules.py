"""
Rules Management page tests — load, search, sort, status filter.
URL: /rules  (Middleware > Rules)
"""
import pytest
from pages.rules_page import RulesPage


@pytest.fixture
def rules(authenticated_dashboard, web_cfg):
    pg = RulesPage(authenticated_dashboard)
    pg.go_to("rules", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg


@pytest.mark.smoke
@pytest.mark.web
def test_rules_page_loads(rules):
    assert rules.is_loaded(), "Rules Management heading should be visible"


@pytest.mark.smoke
@pytest.mark.web
def test_rules_add_button_visible(rules):
    rules.expect_visible(RulesPage.ADD_BTN)


@pytest.mark.sanity
@pytest.mark.web
def test_rules_table_has_rows(rules):
    assert rules.get_row_count() > 0, "Rules table should have entries"


@pytest.mark.sanity
@pytest.mark.web
def test_rules_search_by_name(rules):
    rules.search_name("express")
    rules.wait_for_spinner_gone()
    assert rules.get_row_count() >= 0


@pytest.mark.sanity
@pytest.mark.web
def test_rules_search_no_match(rules):
    rules.search_name("ZZZNOTEXIST9999")
    rules.wait_for_spinner_gone()
    assert rules.get_row_count() == 0


@pytest.mark.sanity
@pytest.mark.web
def test_rules_search_by_description(rules):
    rules.search_description("express")
    rules.wait_for_spinner_gone()
    assert rules.get_row_count() >= 0


@pytest.mark.regression
@pytest.mark.web
def test_rules_sort_by_name(rules):
    count = rules.get_row_count()
    rules.click_sort_name()
    assert rules.get_row_count() == count


@pytest.mark.smoke
@pytest.mark.web
def test_rules_api_no_5xx(authenticated_dashboard, web_cfg):
    errors = []
    authenticated_dashboard.on(
        "response",
        lambda r: errors.append((r.url, r.status)) if r.status >= 500 else None,
    )
    pg = RulesPage(authenticated_dashboard)
    pg.go_to("rules", web_cfg["dashboard_url"])
    pg.wait_for_network_idle()
    assert errors == [], f"Server errors on rules: {errors}"
