import os
import time
import subprocess
import pytest
import requests
from appium import webdriver as appium_webdriver
from utils.config_loader import get_device_caps

APPIUM_URL = os.environ.get("APPIUM_SERVER_URL", "http://localhost:4723")


def _appium_is_running() -> bool:
    try:
        r = requests.get(f"{APPIUM_URL}/status", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=False)
def appium_server():
    """Start Appium server if not already running; stop it after the session."""
    started_here = False
    if not _appium_is_running():
        proc = subprocess.Popen(
            ["appium", "--log-level", "warn"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        started_here = True
        for _ in range(15):
            if _appium_is_running():
                break
            time.sleep(1)
        else:
            proc.terminate()
            pytest.fail("Appium server did not start within 15 seconds")

    yield

    if started_here:
        proc.terminate()


@pytest.fixture
def android_driver(appium_server):
    """Android driver — auto-launches Pixel_8 AVD and installs the APK."""
    caps = get_device_caps("android")
    drv = appium_webdriver.Remote(APPIUM_URL, options=_make_options(caps))
    yield drv
    drv.quit()


@pytest.fixture
def ios_driver(appium_server):
    """iOS driver — requires a connected device or booted simulator."""
    caps = get_device_caps("ios")
    drv = appium_webdriver.Remote(APPIUM_URL, options=_make_options(caps))
    yield drv
    drv.quit()


def _make_options(caps: dict):
    from appium.options import AppiumOptions
    options = AppiumOptions()
    for key, value in caps.items():
        options.set_capability(key, value)
    return options
