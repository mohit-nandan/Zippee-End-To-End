import pytest
from screens.android.otp_screen import OtpScreen
from screens.android.home_screen import HomeScreen
from screens.android.delivery_screen import DeliveryScreen


@pytest.mark.smoke
@pytest.mark.mobile
def test_delivery_order_visible_on_home(android_driver, db_client):
    """Active rider with assigned orders sees orders on home screen."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 AND onboarding_status = 1 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    assert home.is_visible(home._ORDER_LIST), "Order list not visible on home screen"


@pytest.mark.sanity
@pytest.mark.mobile
def test_rider_can_accept_order(android_driver, db_client):
    """Rider can accept an available delivery order."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 AND onboarding_status = 1 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    home.open_first_order()

    delivery = DeliveryScreen(android_driver)
    delivery.accept_order()
    assert delivery.is_order_accepted(), "Order was not accepted successfully"


@pytest.mark.regression
@pytest.mark.mobile
def test_rider_can_complete_delivery(android_driver, db_client):
    """Rider can mark an order as delivered end to end."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 AND onboarding_status = 1 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    home.open_first_order()

    delivery = DeliveryScreen(android_driver)
    delivery.accept_order()
    delivery.navigate_to_pickup()
    delivery.confirm_pickup()
    delivery.navigate_to_customer()
    delivery.confirm_delivery()
    assert delivery.is_delivery_complete(), "Delivery was not marked as complete"


@pytest.mark.sanity
@pytest.mark.mobile
def test_delivery_attempted_flow(android_driver, db_client):
    """Rider can mark delivery as attempted when customer is unavailable."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 AND onboarding_status = 1 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    home.open_first_order()

    delivery = DeliveryScreen(android_driver)
    delivery.accept_order()
    delivery.navigate_to_customer()
    delivery.mark_attempted()
    assert delivery.is_attempted_marked(), "Delivery attempted state not confirmed"
