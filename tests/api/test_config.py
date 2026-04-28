import pytest
from utils.config_loader import get_config, get_device_caps


@pytest.mark.smoke
@pytest.mark.api
def test_config_loads_base_urls():
    cfg = get_config()
    assert "internal_api_url" in cfg
    assert cfg["internal_api_url"].startswith("http"), (
        f"internal_api_url should be a URL, got: {cfg['internal_api_url']!r}"
    )


@pytest.mark.smoke
@pytest.mark.api
def test_config_loads_dashboard_url():
    cfg = get_config()
    assert "dashboard_url" in cfg
    assert cfg["dashboard_url"].startswith("http"), (
        f"dashboard_url should be a URL, got: {cfg['dashboard_url']!r}"
    )


@pytest.mark.smoke
@pytest.mark.api
def test_device_caps_android():
    caps = get_device_caps("android")
    assert caps["platformName"] == "Android"
    assert caps["automationName"] == "UIAutomator2"
    assert "app" in caps


@pytest.mark.smoke
@pytest.mark.api
def test_device_caps_ios():
    caps = get_device_caps("ios")
    assert caps["platformName"] == "iOS"
    assert caps["automationName"] == "XCUITest"
    assert "app" in caps
