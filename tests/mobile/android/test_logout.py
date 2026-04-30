import pytest
from screens.android.login_screen import AndroidLoginScreen
from screens.android.home_screen import AndroidHomeScreen
from screens.android.drawer_screen import AndroidDrawerScreen
from utils.otp_helper import wait_for_otp


STAGING_PHONE = "9140151251"


def _login(driver, db_client):
    """Shared helper: performs a full login and returns a loaded HomeScreen."""
    login = AndroidLoginScreen(driver)
    login.tap_login()
    login.enter_phone(STAGING_PHONE)
    login.tap_proceed()
    assert login.wait_for_otp_screen(), "OTP screen did not appear"
    otp = wait_for_otp(STAGING_PHONE, db=db_client)
    login.enter_otp(otp)
    login.tap_submit()
    home = AndroidHomeScreen(driver)
    assert home.is_loaded(), "Home screen did not load after login"
    return home


@pytest.mark.smoke
@pytest.mark.mobile
def test_logout_returns_to_splash(android_driver, db_client):
    """Rider can log out via hamburger drawer and lands back on the splash/login screen."""
    home = _login(android_driver, db_client)

    home.open_drawer()
    drawer = AndroidDrawerScreen(android_driver)
    assert drawer.is_loaded(), "Drawer did not open"

    drawer.logout()

    login = AndroidLoginScreen(android_driver)
    assert login.is_visible(login.LOGIN_BTN, timeout=15), (
        "Expected to land on splash/login screen after logout"
    )


@pytest.mark.sanity
@pytest.mark.mobile
def test_logout_dialog_cancel_keeps_session(android_driver, db_client):
    """Cancelling the logout dialog leaves the rider logged in on the home screen."""
    home = _login(android_driver, db_client)

    home.open_drawer()
    drawer = AndroidDrawerScreen(android_driver)
    assert drawer.is_loaded(), "Drawer did not open"

    drawer.tap_log_out()
    assert drawer.is_logout_dialog_visible(), "Log Out confirmation dialog did not appear"
    drawer.cancel_logout()

    assert home.is_loaded(timeout=10), (
        "Expected to stay on home screen after cancelling logout"
    )
