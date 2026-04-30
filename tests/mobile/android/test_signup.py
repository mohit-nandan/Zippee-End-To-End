import pytest
from screens.android.login_screen import AndroidLoginScreen
from screens.android.signup_screen import AndroidSignupScreen
from screens.android.verified_screen import AndroidVerifiedScreen
from utils.otp_helper import wait_for_otp
from utils.phone_factory import generate_unique_phone


@pytest.mark.smoke
@pytest.mark.mobile
def test_new_rider_signup_reaches_verified_screen(android_driver, db_client):
    """New rider can complete signup (form + OTP) and land on the verified screen."""
    phone = generate_unique_phone(db=db_client)

    login = AndroidLoginScreen(android_driver)
    login.tap_signup()

    signup = AndroidSignupScreen(android_driver)
    signup.enter_first_name("TestRider")
    signup.enter_last_name("Auto")
    signup.enter_phone(phone)
    signup.tap_submit()

    assert signup.wait_for_otp_screen(), "OTP screen did not appear after signup form submission"

    otp = wait_for_otp(phone, db=db_client)
    signup.enter_otp(otp)
    signup.tap_submit_otp()

    verified = AndroidVerifiedScreen(android_driver)
    assert verified.is_visible(), "Verified screen did not appear after OTP entry"


@pytest.mark.sanity
@pytest.mark.mobile
def test_signup_with_duplicate_phone_shows_error(android_driver):
    """Attempting to sign up with a phone already registered should surface an error."""
    existing_phone = "9140151251"

    login = AndroidLoginScreen(android_driver)
    login.tap_signup()

    signup = AndroidSignupScreen(android_driver)
    signup.enter_first_name("TestRider")
    signup.enter_last_name("Auto")
    signup.enter_phone(existing_phone)
    signup.tap_submit()

    assert signup.is_error_visible(timeout=8), (
        "Expected an error message when registering with an already-used phone number"
    )


@pytest.mark.sanity
@pytest.mark.mobile
def test_signup_with_invalid_otp_shows_error(android_driver, db_client):
    """Entering a wrong OTP during signup should show an error."""
    phone = generate_unique_phone(db=db_client)

    login = AndroidLoginScreen(android_driver)
    login.tap_signup()

    signup = AndroidSignupScreen(android_driver)
    signup.enter_first_name("TestRider")
    signup.enter_last_name("Auto")
    signup.enter_phone(phone)
    signup.tap_submit()

    assert signup.wait_for_otp_screen(), "OTP screen did not appear"

    signup.enter_otp("0000")
    signup.tap_submit_otp()

    assert signup.is_error_visible(), "Expected error for invalid OTP during signup"
