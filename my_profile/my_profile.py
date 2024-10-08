from bs4 import BeautifulSoup
import constants as CONSTANTS
from utils.utils import Utils as utils
from selenium.webdriver.common.by import By

class MyProfile():
    def __init__(self, driver):
        self.driver = driver

    def change_city(self, city_name):
        city_name = city_name.strip()
        current_location_field = self.driver.find_elements(By.NAME, CONSTANTS.MY_PROFILE_CURRENT_LOCATION)
        submit_button = self.driver.find_elements(By.XPATH, CONSTANTS.MY_PROFILE_SUBMIT_BUTTON)

        if not current_location_field or len(current_location_field) != 1 or len(submit_button) != 3:
            print("MY_PROFILE: Location input field or submit button could not be found")
            return False
        
        if current_location_field[0].get_attribute('value') == city_name:
            return True # No change needed

        print("MY_PROFILE: Updating the city field to " + city_name + "...")
        self.update_city_field(city_name)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        utils.random_short_sleep()
        print("MY_PROFILE: Clicking on the save button...")
        submit_button[0].click()
        utils.random_long_sleep()

        return self.check_city_update_success(city_name)

    def update_city_field(self, city_name):
        field = self.driver.find_element(By.NAME, CONSTANTS.MY_PROFILE_CURRENT_LOCATION)
        field.clear()
        field.send_keys(city_name)
        utils.random_short_sleep()

    def check_city_update_success(self, city_name):
        print("MY_PROFILE: Checking if the city update was successful...")
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        if CONSTANTS.FIX_ERRORS_STRING not in soup.get_text():
            return True
        print(f"MY_PROFILE: Probably tried to set a weird city name: {city_name}")
        return False

    def go_to_first_profile_tab(self):
        print("MY_PROFILE: Going to the first profile tab...")
        basics_button = self.driver.find_elements(By.XPATH, CONSTANTS.MY_PROFILE_BASICS_BUTTON)
        if len(basics_button) == 1:
            basics_button[0].click()
            utils.random_normal_sleep()
            return True
        print("MY_PROFILE: Failed to find the Basics tab button.")
        return False

    def go_to_profile_and_change_city(self, city_name):
        if not city_name or not city_name.strip() or len(city_name) > CONSTANTS.MAX_CITY_LENGTH:
            print("MY_PROFILE: Invalid city name or city name is too long.")
            return False

        if not self.navigate_to_profile():
            print("MY_PROFILE: Failed to navigate to profile.")
            return False

        if self.driver.current_url.endswith(CONSTANTS.MY_PROFILE_PAGE_URL_PAGE_ONE):
            return self.change_city(city_name)

        if self.go_to_first_profile_tab():
            return self.change_city(city_name)
        
        return False

    def navigate_to_profile(self):
        print("MY_PROFILE: Navigating to the profile section...")
        my_profile = self.driver.find_elements(By.XPATH, CONSTANTS.DASHBOARD_MY_ACCOUNT_MENU_OPTION)

        if len(my_profile) == 1:
            my_profile[0].click()
            utils.random_long_sleep()
            return self.driver.current_url.startswith(CONSTANTS.MY_PROFILE_URL)
        print("MY_PROFILE: My profile button is not found or multiple instances found.")
        return False
    
    def check_dashboard_weekly_limit_reached(self):
        if self.driver.current_url != CONSTANTS.STARTUP_SCHOOL_DASHBOARD_URL:
            return True

        weekly_limit_box = self.driver.find_elements(By.XPATH, CONSTANTS.DASHBOARD_LIMIT_NOTICE_BOX)

        if len(weekly_limit_box) != 1: 
            return True
        if CONSTANTS.DASHBOARD_WEEKLY_LIMIT_NOTICE in weekly_limit_box[0].text:
            return True
        
        return False