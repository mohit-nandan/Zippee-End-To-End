import pytest
from screens.android.otp_screen import OtpScreen
from screens.android.onboarding_screen import OnboardingScreen
from screens.android.home_screen import HomeScreen


@pytest.mark.regression
@pytest.mark.mobile
def test_new_rider_sees_onboarding(android_driver, db_client):
    """Rider with onboarding_status=0 is redirected to onboarding after login."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE onboarding_status = 0 AND is_active = 1 LIMIT 1"
    )
    if not rider:
        pytest.skip("No unboarded rider found in DB")

    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    onboarding = OnboardingScreen(android_driver)
    assert onboarding.is_visible(onboarding._WELCOME_TEXT), "Onboarding screen not shown for new rider"


@pytest.mark.regression
@pytest.mark.mobile
def test_completed_onboarding_rider_goes_to_home(android_driver, db_client):
    """Rider with onboarding_status=1 goes directly to home after login."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE onboarding_status = 1 AND is_active = 1 AND is_blocked = 0 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    assert home.is_visible(home._HOME_CONTAINER), "Home screen not shown for onboarded rider"


@pytest.mark.regression
@pytest.mark.mobile
def test_terms_acceptance_required_on_first_login(android_driver, db_client):
    """Rider who hasn't accepted terms sees T&C screen."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE terms_accepted = 0 AND is_active = 1 LIMIT 1"
    )
    if not rider:
        pytest.skip("No rider with pending T&C found in DB")

    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    onboarding = OnboardingScreen(android_driver)
    assert onboarding.is_terms_visible(), "T&C screen not shown for rider with terms_accepted=0"
