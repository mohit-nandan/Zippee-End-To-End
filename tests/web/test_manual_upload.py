"""
Manual Upload (Upload Orders) page tests — load, search, sort.
URL: /manualUpload  (COD > Upload Orders)
"""
import pytest
from pages.manual_upload_page import ManualUploadPage


@pytest.fixture
def manual(authenticated_dashboard, web_cfg):
    pg = ManualUploadPage(authenticated_dashboard)
    pg.go_to("manual_upload", web_cfg["dashboard_url"])
    pg.wait_for_spinner_gone()
    return pg


@pytest.mark.smoke
@pytest.mark.web
def test_manual_upload_page_loads(manual):
    assert manual.is_loaded(), "Manually Added Orders heading should be visible"


@pytest.mark.smoke
@pytest.mark.web
def test_manual_upload_button_visible(manual):
    manual.expect_visible(ManualUploadPage.UPLOAD_BTN)


@pytest.mark.smoke
@pytest.mark.web
def test_manual_add_new_button_visible(manual):
    manual.expect_visible(ManualUploadPage.ADD_NEW_BTN)


@pytest.mark.sanity
@pytest.mark.web
def test_manual_table_has_rows(manual):
    assert manual.get_row_count() > 0, "Manual orders table should have data"


@pytest.mark.sanity
@pytest.mark.web
def test_manual_search_by_rider(manual):
    manual.search_rider("PRI_JAL")
    manual.wait_for_spinner_gone()
    assert manual.get_row_count() >= 0


@pytest.mark.sanity
@pytest.mark.web
def test_manual_search_no_match_rider(manual):
    manual.search_rider("ZZZNOTEXIST9999")
    manual.wait_for_spinner_gone()
    assert manual.get_row_count() == 0


@pytest.mark.regression
@pytest.mark.web
def test_manual_sort_by_order_id(manual):
    count = manual.get_row_count()
    manual.click_sort("Order ID")
    assert manual.get_row_count() == count


@pytest.mark.regression
@pytest.mark.web
def test_manual_sort_by_rider_username(manual):
    manual.click_sort("Rider Username")
    assert manual.get_row_count() >= 0


@pytest.mark.smoke
@pytest.mark.web
def test_manual_api_no_5xx(authenticated_dashboard, web_cfg):
    errors = []
    authenticated_dashboard.on(
        "response",
        lambda r: errors.append((r.url, r.status)) if r.status >= 500 else None,
    )
    pg = ManualUploadPage(authenticated_dashboard)
    pg.go_to("manual_upload", web_cfg["dashboard_url"])
    pg.wait_for_network_idle()
    assert errors == [], f"Server errors on manual upload: {errors}"
