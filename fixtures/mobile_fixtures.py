import os
import pytest
from appium import webdriver as appium_webdriver
from utils.config_loader import get_device_caps


@pytest.fixture(params=["android", "ios"])
def driver(request):
    """
    Parametrized fixture — runs each test on both Android and iOS.
    Requires Appium server at APPIUM_SERVER_URL and builds in ./builds/.
    """
    platform = request.param
    caps = get_device_caps(platform)
    server_url = os.environ.get("APPIUM_SERVER_URL", "http://localhost:4723")
    drv = appium_webdriver.Remote(server_url, caps)
    yield drv
    drv.quit()


@pytest.fixture(params=["android"])
def android_driver(request):
    caps = get_device_caps("android")
    server_url = os.environ.get("APPIUM_SERVER_URL", "http://localhost:4723")
    drv = appium_webdriver.Remote(server_url, caps)
    yield drv
    drv.quit()


@pytest.fixture(params=["ios"])
def ios_driver(request):
    caps = get_device_caps("ios")
    server_url = os.environ.get("APPIUM_SERVER_URL", "http://localhost:4723")
    drv = appium_webdriver.Remote(server_url, caps)
    yield drv
    drv.quit()
