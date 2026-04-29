def get_login_screen(driver):
    platform = driver.capabilities.get("platformName", "").lower()
    if platform == "android":
        from screens.android.login_screen import AndroidLoginScreen
        return AndroidLoginScreen(driver)
    from screens.ios.login_screen import IOSLoginScreen
    return IOSLoginScreen(driver)


def get_home_screen(driver):
    platform = driver.capabilities.get("platformName", "").lower()
    if platform == "android":
        from screens.android.home_screen import AndroidHomeScreen
        return AndroidHomeScreen(driver)
    from screens.ios.home_screen import IOSHomeScreen
    return IOSHomeScreen(driver)


def get_delivery_screen(driver):
    platform = driver.capabilities.get("platformName", "").lower()
    if platform == "android":
        from screens.android.delivery_screen import AndroidDeliveryScreen
        return AndroidDeliveryScreen(driver)
    from screens.ios.delivery_screen import IOSDeliveryScreen
    return IOSDeliveryScreen(driver)


def get_onboarding_screen(driver):
    platform = driver.capabilities.get("platformName", "").lower()
    if platform == "android":
        from screens.android.onboarding_screen import AndroidOnboardingScreen
        return AndroidOnboardingScreen(driver)
    from screens.ios.onboarding_screen import IOSOnboardingScreen
    return IOSOnboardingScreen(driver)
