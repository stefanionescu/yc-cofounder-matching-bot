import os
import constants as CONSTANTS
from dotenv import load_dotenv
from utils.utils import Utils as utils
from selenium.webdriver.common.by import By

class SignIn():
    def __init__(self, driver):
        self.driver = driver
        load_dotenv()  # Load environment variables once during initialization

    def sign_in(self):
        # Attempt to retrieve necessary elements
        userid_field = self.find_element(By.ID, CONSTANTS.SIGN_IN_USER_FIELD)
        pass_field = self.find_element(By.ID, CONSTANTS.SIGN_IN_PASS_FIELD)
        sign_in_btn = self.find_element(By.CSS_SELECTOR, CONSTANTS.SIGN_IN_PAGE_LOGIN_BUTTON)

        if not userid_field or not pass_field or not sign_in_btn:
            # Log error or send email
            self.log_error("Sign-in fields are missing on the page.")
            return False

        # Fill in credentials and submit form
        self.fill_and_submit_form(userid_field, pass_field, sign_in_btn)
        print("url after sign in: " + self.driver.current_url)
        return True

    def fill_and_submit_form(self, userid_field, pass_field, sign_in_btn):
        userid_field.send_keys(os.getenv("YC_USERNAME"))
        pass_field.send_keys(os.getenv("YC_PASSWORD"))
        sign_in_btn.click()
        utils.random_long_sleep()

    def go_to_sign_in(self):
        sign_in_button = self.find_element(By.XPATH, CONSTANTS.LANDING_PAGE_SIGN_IN_BUTTON)
        if not sign_in_button:
            self.log_error("Sign-in button not found on landing page.")
            return False

        sign_in_button.click()
        utils.random_short_sleep()
        return True

    def find_element(self, by_method, identifier):
        elements = self.driver.find_elements(by_method, identifier)
        if len(elements) == 1:
            return elements[0]
        return None

    def log_error(self, message):
        # TODO: Log this error to a file or send an email alert
        print(message)