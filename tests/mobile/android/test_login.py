import pytest
from screens.android.login_screen import AndroidLoginScreen
from screens.android.home_screen import AndroidHomeScreen
from utils.otp_helper import wait_for_otp, fetch_rider


STAGING_PHONE = "9140151251"


@pytest.mark.smoke
@pytest.mark.mobile
def test_rider_login_with_valid_otp(android_driver, db_client):
    """Rider can log in with a valid phone + OTP fetched live from staging DB."""
    login = AndroidLoginScreen(android_driver)
    login.tap_login()
    login.enter_phone(STAGING_PHONE)
    login.tap_proceed()

    assert login.wait_for_otp_screen(), "OTP screen did not appear"

    otp = wait_for_otp(STAGING_PHONE, db=db_client)
    login.enter_otp(otp)
    login.tap_submit()

    home = AndroidHomeScreen(android_driver)
    assert home.is_visible(home._HOME_CONTAINER), "Home screen did not load after login"


@pytest.mark.sanity
@pytest.mark.mobile
def test_blocked_rider_cannot_login(android_driver, db_client):
    """Blocked rider should not be able to log in."""
    rider = db_client.fetch_one(
        "SELECT phone_number FROM zippeeriderapp_rider "
        "WHERE is_blocked = 1 AND phone_number LIKE '+91%' LIMIT 1"
    )
    if not rider:
        pytest.skip("No blocked rider found in staging DB")

    phone = rider["phone_number"].replace("+91", "")
    login = AndroidLoginScreen(android_driver)
    login.tap_login()
    login.enter_phone(phone)
    login.tap_proceed()

    assert login.wait_for_otp_screen(), "OTP screen did not appear"
    otp = wait_for_otp(phone, db=db_client)
    login.enter_otp(otp)
    login.tap_submit()

    assert login.is_error_visible(), "Expected error for blocked rider"


@pytest.mark.sanity
@pytest.mark.mobile
def test_login_with_invalid_otp_shows_error(android_driver):
    """Entering a wrong OTP should show an error message."""
    login = AndroidLoginScreen(android_driver)
    login.tap_login()
    login.enter_phone(STAGING_PHONE)
    login.tap_proceed()

    assert login.wait_for_otp_screen(), "OTP screen did not appear"
    login.enter_otp("0000")
    login.tap_submit()

    assert login.is_error_visible(), "Expected error for invalid OTP"
