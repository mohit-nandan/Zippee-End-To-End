import pytest
from screens.android.otp_screen import OtpScreen
from screens.android.home_screen import HomeScreen
from screens.android.profile_screen import ProfileScreen
from screens.android.otp_screen import OtpScreen


@pytest.mark.sanity
@pytest.mark.mobile
def test_profile_shows_correct_rider_name(android_driver, db_client):
    """Profile screen shows rider name matching the DB record."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp, rider_name FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 AND onboarding_status = 1 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    home.go_to_profile()

    profile = ProfileScreen(android_driver)
    displayed_name = profile.get_rider_name()
    assert rider["rider_name"].lower() in displayed_name.lower(), \
        f"Expected '{rider['rider_name']}' in profile, got '{displayed_name}'"


@pytest.mark.sanity
@pytest.mark.mobile
def test_profile_kyc_status_matches_db(android_driver, db_client):
    """KYC status shown in app matches the kyc_status field in DB."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp, kyc_status FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 AND onboarding_status = 1 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    home.go_to_profile()

    profile = ProfileScreen(android_driver)
    displayed_kyc = profile.get_kyc_status()
    assert rider["kyc_status"].lower() in displayed_kyc.lower(), \
        f"KYC mismatch: DB={rider['kyc_status']}, App={displayed_kyc}"


@pytest.mark.sanity
@pytest.mark.mobile
def test_rider_can_logout(android_driver, db_client):
    """Rider can log out and is returned to the login screen."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 AND onboarding_status = 1 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    home.go_to_profile()

    profile = ProfileScreen(android_driver)
    profile.logout()

    otp_screen = OtpScreen(android_driver)
    assert otp_screen.is_visible(otp_screen._PHONE_INPUT), "Login screen not shown after logout"
