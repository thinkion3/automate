import os
import time
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.common.exceptions import NoSuchElementException

username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")

desired_caps = {
    "platformName": "Android",
    "platformVersion": "11",
    "deviceName": "Android Emulator",
    "automationName": "UiAutomator2",
    "appPackage": "com.instagram.android",
    "appActivity": ".activity.MainTabActivity",
    "noReset": False,
}

driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
time.sleep(20)  # Let app fully load

def safe_find(selector):
    try:
        return driver.find_element(MobileBy.ANDROID_UIAUTOMATOR, selector)
    except NoSuchElementException:
        return None

try:
    print("📲 Looking for login screen...")

    login_button = safe_find('new UiSelector().textContains("Log in")')
    if login_button:
        login_button.click()
        time.sleep(3)

    # Enter credentials
    user_input = safe_find('new UiSelector().resourceId("com.instagram.android:id/login_username")')
    pass_input = safe_find('new UiSelector().resourceId("com.instagram.android:id/password")')

    if user_input and pass_input:
        user_input.send_keys(username)
        time.sleep(1)
        pass_input.send_keys(password)
        time.sleep(1)

        login_submit = safe_find('new UiSelector().resourceId("com.instagram.android:id/button_text")')
        if login_submit:
            login_submit.click()
            print("🔐 Submitted login form.")
            time.sleep(10)
        else:
            raise Exception("❌ Login button not found")

    else:
        raise Exception("❌ Username/password input not found")

    # ✅ Check for home feed to confirm login
    print("✅ Checking login status...")
    home_icon = safe_find('new UiSelector().descriptionContains("Home")')
    if home_icon:
        print("✅ Login successful. Home icon detected.")
    else:
        raise Exception("❌ Login likely failed — Home icon not detected")

except Exception as e:
    print("⚠️ Exception:", e)

finally:
    driver.quit()
