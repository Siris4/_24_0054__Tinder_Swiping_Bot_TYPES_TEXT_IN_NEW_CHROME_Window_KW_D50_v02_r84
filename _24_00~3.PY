from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os
import time

# Constants
EMAIL = os.environ.get('email', 'Email does not exist')
GMAIL_PASSWORD = os.environ.get('gmail_password', 'Password does not exist')

# Function to log messages
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{timestamp} - {message}")

def init_driver():
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    log_message("WebDriver initialized.")
    return driver

def click_element(driver, by, value, description):
    try:
        element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((by, value)))
        log_message(f"Attempting to click {description}.")
        element.click()
        log_message(f"{description} clicked successfully.")
        return True
    except TimeoutException:
        log_message(f"{description} not clickable or not found.")
        return False
    except StaleElementReferenceException:
        log_message(f"{description} was stale, trying to click again.")
        return click_element(driver, by, value, description)  # Recursively try to click again
    except Exception as e:
        log_message(f"An error occurred while clicking {description}: {e}")
        return False

def switch_to_new_window(driver):
    main_window = driver.current_window_handle
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
    new_window = [window for window in driver.window_handles if window != main_window][0]
    driver.switch_to.window(new_window)
    log_message("Switched to new window.")
    return main_window

def enter_email_at_cursor(driver, email, gmail_password):
    try:
        main_window = switch_to_new_window(driver)

        log_message("Locating the email input field...")
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        log_message(f"Email field located, attempting to enter email: {email}")
        email_input.clear()
        email_input.send_keys(email)
        email_input.send_keys(Keys.ENTER)

        # Wait for the transition to the password input field
        time.sleep(2)  # Wait for the UI to potentially update to the password field

        log_message("Locating the password input field...")
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))  # Ensure this is the correct selector for the password field
        )
        log_message("Password field located, attempting to enter password.")
        password_input.clear()
        password_input.send_keys(gmail_password)
        password_input.send_keys(Keys.ENTER)

        driver.switch_to.window(main_window)
        log_message("Switched back to the main window.")

        return True
    except Exception as e:
        driver.switch_to.window(main_window)
        log_message(f"Failed to enter email or password: {e}")
        return False

def login_sequence(driver):
    if click_element(driver, By.XPATH, "//div[contains(text(), 'I decline')]", "Decline button"):
        log_message("Decline button found and clicked.")
    else:
        log_message("Decline button not found, proceeding with login.")

    if click_element(driver, By.CLASS_NAME, "l17p5q9z", "Main login button"):
        if click_element(driver, By.XPATH, "//span[contains(text(), 'English')]", "English language option"):
            click_element(driver, By.CSS_SELECTOR, "a[href*='tinder.onelink.me'] div.l17p5q9z",
                          "Additional login button")
            if click_element(driver, By.CSS_SELECTOR, "span.nsm7Bb-HzV7m-LgbsSe-BPrWId", "Continue with Google button"):
                enter_email_at_cursor(driver, EMAIL, GMAIL_PASSWORD)

    # Wait for a few seconds after login
    time.sleep(5)

    # Click the "Not Interested" button
    click_element(driver, By.XPATH, "//button[contains(text(), 'Not Interested')]", "Not Interested button")

def main():
    driver = init_driver()
    driver.get("https://tinder.com/")
    log_message("Navigated to Tinder's login page.")

    login_sequence(driver)

    input("Press Enter to exit...\n")
    driver.quit()

if __name__ == "__main__":
    main()
