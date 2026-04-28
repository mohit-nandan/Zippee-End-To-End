from utils.config_loader import get_config

def test_config_loads_base_urls():
    cfg = get_config()
    assert "internal_api_url" in cfg
    assert cfg["internal_api_url"].startswith("http")

def test_config_loads_dashboard_url():
    cfg = get_config()
    assert "dashboard_url" in cfg
