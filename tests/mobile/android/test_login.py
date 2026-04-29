import pytest
from screens.android.otp_screen import OtpScreen
from screens.android.home_screen import HomeScreen


@pytest.mark.smoke
@pytest.mark.mobile
def test_rider_login_with_valid_otp(android_driver, db_client):
    """Rider can log in with a valid phone + OTP."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 AND onboarding_status = 1 LIMIT 1"
    )
    otp_screen = OtpScreen(android_driver)
    otp_screen.enter_phone(rider["phone_number"])
    otp_screen.tap_send_otp()
    otp_screen.enter_otp(rider["otp"])
    otp_screen.tap_verify()

    home = HomeScreen(android_driver)
    assert home.is_visible(home._HOME_CONTAINER), "Home screen did not load after login"


@pytest.mark.sanity
@pytest.mark.mobile
def test_blocked_rider_cannot_login(android_driver, db_client):
    """Blocked rider should see an error and not reach home screen."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE is_blocked = 1 LIMIT 1"
    )
    if not rider:
        pytest.skip("No blocked rider found in DB")

    otp_screen = OtpScreen(android_driver)
    otp_screen.login(rider["phone_number"], rider["otp"])
    assert otp_screen.is_error_visible(), "Expected error for blocked rider"


@pytest.mark.sanity
@pytest.mark.mobile
def test_login_with_invalid_otp_shows_error(android_driver, db_client):
    """Invalid OTP should show an error message."""
    rider = db_client.fetch_one(
        "SELECT phone_number FROM zippeeriderapp_rider WHERE is_active = 1 LIMIT 1"
    )
    otp_screen = OtpScreen(android_driver)
    otp_screen.login(rider["phone_number"], "000000")
    assert otp_screen.is_error_visible(), "Expected error for invalid OTP"
