import os
import time
import sys
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class InstagramBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError("❌ Instagram credentials not found in environment variables")
        
        print(f"🔑 Using username: {self.username[:3]}***")

    def setup_driver(self):
        """Initialize Appium driver with proper capabilities"""
        desired_caps = {
            "platformName": "Android",
            "platformVersion": "11",
            "deviceName": "emulator-5554",
            "automationName": "UiAutomator2",
            "appPackage": "com.instagram.android",
            "appActivity": ".activity.MainTabActivity",
            "noReset": True,
            "fullReset": False,
            "newCommandTimeout": 300,
            "androidInstallTimeout": 90000,
            "adbExecTimeout": 60000,
            "autoGrantPermissions": True,
            "ignoreHiddenApiPolicyError": True,
            "disableWindowAnimation": True,
        }
        
        try:
            print("🔌 Connecting to Appium server...")
            self.driver = webdriver.Remote("http://localhost:4723", desired_caps)
            self.wait = WebDriverWait(self.driver, 30)
            print("✅ Connected to Appium successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Appium: {e}")
            return False

    def wait_for_element(self, by_type, selector, timeout=30):
        """Wait for element to be present and return it"""
        try:
            if by_type == "uiautomator":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, selector))
                )
            elif by_type == "id":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((AppiumBy.ID, selector))
                )
            else:
                raise ValueError(f"Unsupported by_type: {by_type}")
            return element
        except TimeoutException:
            print(f"⏰ Timeout waiting for element: {selector}")
            return None

    def safe_find_element(self, by_type, selector):
        """Safely find element without waiting"""
        try:
            if by_type == "uiautomator":
                return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, selector)
            elif by_type == "id":
                return self.driver.find_element(AppiumBy.ID, selector)
            else:
                raise ValueError(f"Unsupported by_type: {by_type}")
        except NoSuchElementException:
            return None

    def safe_click(self, element, description="element"):
        """Safely click an element with error handling"""
        try:
            if element:
                element.click()
                print(f"👆 Clicked {description}")
                time.sleep(2)  # Short delay after click
                return True
            else:
                print(f"❌ Cannot click {description} - element not found")
                return False
        except Exception as e:
            print(f"❌ Error clicking {description}: {e}")
            return False

    def safe_send_keys(self, element, text, description="input"):
        """Safely send keys to an element"""
        try:
            if element:
                element.clear()
                element.send_keys(text)
                print(f"⌨️ Entered text in {description}")
                time.sleep(1)
                return True
            else:
                print(f"❌ Cannot enter text in {description} - element not found")
                return False
        except Exception as e:
            print(f"❌ Error entering text in {description}: {e}")
            return False

    def handle_initial_screens(self):
        """Handle initial Instagram screens (permissions, intro, etc.)"""
        print("🎬 Handling initial screens...")
        
        # Wait for app to load
        time.sleep(10)
        
        # Handle potential permission dialogs
        try:
            # Allow permissions if prompted
            allow_btn = self.safe_find_element("uiautomator", 'new UiSelector().textContains("Allow")')
            if allow_btn:
                self.safe_click(allow_btn, "Allow permission")
            
            # Skip intro screens if present
            skip_btn = self.safe_find_element("uiautomator", 'new UiSelector().textContains("Skip")')
            if skip_btn:
                self.safe_click(skip_btn, "Skip intro")
                
        except Exception as e:
            print(f"⚠️ Error handling initial screens: {e}")

    def navigate_to_login(self):
        """Navigate to login screen"""
        print("🚪 Navigating to login screen...")
        
        # Look for "Log in" button on welcome screen
        login_selectors = [
            'new UiSelector().textContains("Log in")',
            'new UiSelector().textContains("Log In")',
            'new UiSelector().resourceId("com.instagram.android:id/log_in_button")',
            'new UiSelector().className("android.widget.Button").textContains("Log")'
        ]
        
        for selector in login_selectors:
            login_btn = self.safe_find_element("uiautomator", selector)
            if login_btn:
                if self.safe_click(login_btn, "Log in button"):
                    time.sleep(3)
                    return True
        
        print("ℹ️ No login button found - might already be on login screen")
        return True

    def perform_login(self):
        """Perform the actual login process"""
        print("🔐 Starting login process...")
        
        # Wait for login form to appear
        time.sleep(5)
        
        # Try different selectors for username field
        username_selectors = [
            "com.instagram.android:id/login_username",
            "com.instagram.android:id/username",
            'new UiSelector().resourceId("com.instagram.android:id/login_username")',
            'new UiSelector().className("android.widget.EditText").instance(0)'
        ]
        
        username_field = None
        for selector in username_selectors:
            if selector.startswith("com.instagram"):
                username_field = self.safe_find_element("id", selector)
            else:
                username_field = self.wait_for_element("uiautomator", selector, timeout=15)
            
            if username_field:
                print(f"✅ Found username field with selector: {selector}")
                break
        
        if not username_field:
            raise Exception("❌ Username field not found")
        
        # Try different selectors for password field
        password_selectors = [
            "com.instagram.android:id/password",
            "com.instagram.android:id/login_password",
            'new UiSelector().resourceId("com.instagram.android:id/password")',
            'new UiSelector().className("android.widget.EditText").instance(1)'
        ]
        
        password_field = None
        for selector in password_selectors:
            if selector.startswith("com.instagram"):
                password_field = self.safe_find_element("id", selector)
            else:
                password_field = self.safe_find_element("uiautomator", selector)
            
            if password_field:
                print(f"✅ Found password field with selector: {selector}")
                break
        
        if not password_field:
            raise Exception("❌ Password field not found")
        
        # Enter credentials
        if not self.safe_send_keys(username_field, self.username, "username field"):
            raise Exception("❌ Failed to enter username")
        
        if not self.safe_send_keys(password_field, self.password, "password field"):
            raise Exception("❌ Failed to enter password")
        
        # Find and click login button
        login_button_selectors = [
            'new UiSelector().resourceId("com.instagram.android:id/button_text")',
            'new UiSelector().textContains("Log in")',
            'new UiSelector().textContains("Log In")',
            'new UiSelector().className("android.widget.Button").enabled(true)'
        ]
        
        login_button = None
        for selector in login_button_selectors:
            login_button = self.safe_find_element("uiautomator", selector)
            if login_button:
                print(f"✅ Found login button with selector: {selector}")
                break
        
        if not login_button:
            raise Exception("❌ Login submit button not found")
        
        if not self.safe_click(login_button, "login submit button"):
            raise Exception("❌ Failed to click login button")
        
        print("📤 Login form submitted, waiting for response...")
        time.sleep(15)  # Wait for login to process

    def verify_login_success(self):
        """Verify if login was successful"""
        print("🔍 Verifying login status...")
        
        # Wait a bit more for potential loading
        time.sleep(10)
        
        # Check for various indicators of successful login
        success_indicators = [
            'new UiSelector().descriptionContains("Home")',
            'new UiSelector().resourceId("com.instagram.android:id/tab_bar")',
            'new UiSelector().textContains("Home")',
            'new UiSelector().resourceId("com.instagram.android:id/bottom_navigation")',
            'new UiSelector().descriptionContains("Feed")'
        ]
        
        for indicator in success_indicators:
            element = self.safe_find_element("uiautomator", indicator)
            if element:
                print(f"✅ Login successful! Found: {indicator}")
                return True
        
        # Check for error messages
        error_indicators = [
            'new UiSelector().textContains("incorrect")',
            'new UiSelector().textContains("wrong")',
            'new UiSelector().textContains("error")',
            'new UiSelector().textContains("try again")',
            'new UiSelector().textContains("Sorry")'
        ]
        
        for indicator in error_indicators:
            element = self.safe_find_element("uiautomator", indicator)
            if element:
                error_text = element.text if hasattr(element, 'text') else "Unknown error"
                print(f"❌ Login failed! Error: {error_text}")
                return False
        
        print("⚠️ Login status unclear - no clear success or error indicators found")
        return None

    def take_screenshot(self, filename="debug_screenshot.png"):
        """Take a screenshot for debugging"""
        try:
            if self.driver:
                self.driver.save_screenshot(filename)
                print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")

    def run(self):
        """Main execution flow"""
        try:
            print("🤖 Starting Instagram Bot...")
            
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Handle initial screens
            self.handle_initial_screens()
            
            # Navigate to login
            if not self.navigate_to_login():
                raise Exception("Failed to navigate to login")
            
            # Perform login
            self.perform_login()
            
            # Verify login
            login_result = self.verify_login_success()
            
            if login_result is True:
                print("🎉 Instagram bot login completed successfully!")
                self.take_screenshot("success_screenshot.png")
                return True
            elif login_result is False:
                print("❌ Instagram bot login failed!")
                self.take_screenshot("error_screenshot.png")
                return False
            else:
                print("⚠️ Instagram bot login status unclear")
                self.take_screenshot("unclear_screenshot.png")
                return False
                
        except Exception as e:
            print(f"💥 Critical error in bot execution: {e}")
            self.take_screenshot("critical_error_screenshot.png")
            return False
        finally:
            if self.driver:
                print("🔚 Closing driver...")
                try:
                    self.driver.quit()
                    print("✅ Driver closed successfully")
                except Exception as e:
                    print(f"⚠️ Error closing driver: {e}")

def main():
    """Main entry point"""
    try:
        bot = InstagramBot()
        success = bot.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
