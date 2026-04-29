import pytest
from screens.android.otp_screen import OtpScreen
from screens.android.home_screen import HomeScreen
from screens.android.attendance_screen import AttendanceScreen


@pytest.mark.smoke
@pytest.mark.mobile
def test_rider_can_mark_attendance(android_driver, db_client):
    """Rider can mark attendance from the home screen."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 AND onboarding_status = 1 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    home.go_to_attendance()

    attendance = AttendanceScreen(android_driver)
    attendance.mark_attendance()
    assert attendance.is_success_shown(), "Attendance success message not shown"


@pytest.mark.sanity
@pytest.mark.mobile
def test_attendance_status_matches_db(android_driver, db_client):
    """is_logged_in flag in DB matches attendance status shown in app."""
    rider = db_client.fetch_one(
        "SELECT phone_number, otp, is_logged_in FROM zippeeriderapp_rider "
        "WHERE is_active = 1 AND is_blocked = 0 LIMIT 1"
    )
    OtpScreen(android_driver).login(rider["phone_number"], rider["otp"])

    home = HomeScreen(android_driver)
    home.go_to_attendance()

    attendance = AttendanceScreen(android_driver)
    status = attendance.get_status()
    expected = "Present" if rider["is_logged_in"] else "Absent"
    assert expected.lower() in status.lower(), f"Expected {expected}, got {status}"
