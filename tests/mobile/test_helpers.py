import pytest
from unittest.mock import MagicMock
from utils.helpers import get_login_screen, get_home_screen, get_delivery_screen, get_onboarding_screen
from screens.android.login_screen import AndroidLoginScreen
from screens.android.home_screen import AndroidHomeScreen
from screens.android.delivery_screen import AndroidDeliveryScreen
from screens.android.onboarding_screen import AndroidOnboardingScreen
from screens.ios.login_screen import IOSLoginScreen
from screens.ios.home_screen import IOSHomeScreen
from screens.ios.delivery_screen import IOSDeliveryScreen
from screens.ios.onboarding_screen import IOSOnboardingScreen


def android_driver():
    d = MagicMock()
    d.capabilities = {"platformName": "Android"}
    return d


def ios_driver():
    d = MagicMock()
    d.capabilities = {"platformName": "iOS"}
    return d


@pytest.mark.mobile
def test_get_login_screen_android():
    assert isinstance(get_login_screen(android_driver()), AndroidLoginScreen)

@pytest.mark.mobile
def test_get_login_screen_ios():
    assert isinstance(get_login_screen(ios_driver()), IOSLoginScreen)

@pytest.mark.mobile
def test_get_home_screen_android():
    assert isinstance(get_home_screen(android_driver()), AndroidHomeScreen)

@pytest.mark.mobile
def test_get_home_screen_ios():
    assert isinstance(get_home_screen(ios_driver()), IOSHomeScreen)

@pytest.mark.mobile
def test_get_delivery_screen_android():
    assert isinstance(get_delivery_screen(android_driver()), AndroidDeliveryScreen)

@pytest.mark.mobile
def test_get_delivery_screen_ios():
    assert isinstance(get_delivery_screen(ios_driver()), IOSDeliveryScreen)

@pytest.mark.mobile
def test_get_onboarding_screen_android():
    assert isinstance(get_onboarding_screen(android_driver()), AndroidOnboardingScreen)

@pytest.mark.mobile
def test_get_onboarding_screen_ios():
    assert isinstance(get_onboarding_screen(ios_driver()), IOSOnboardingScreen)
