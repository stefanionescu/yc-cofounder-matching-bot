import os
import sys
from time import time
from bs4 import BeautifulSoup
import constants as CONSTANTS
from dotenv import load_dotenv
from selenium import webdriver
from utils.utils import Utils as utils
from selenium.webdriver.common.by import By
from my_profile.my_profile import MyProfile
from founder_messages import founder_messages

class Scout():
    def __init__(self, driver, start_time):
        self.driver = driver
        self.bot_start_time = start_time

        load_dotenv()  # Load environment variables once during initialization

        self.contacted_founders = 0
        self.skipped_founders = 0
        self.saved_founders = 0
        self.saved_founder_profiles = []
        self.contacted_founders_profiles = []

        self.cities = os.getenv("YC_CITIES").split(";")
        self.city_to_return_to = os.getenv("CITY_TO_RETURN_TO")
        self.bot_max_run_time = os.getenv("BOT_MAX_RUN_TIME", 600)
        self.contact_founders = os.getenv("CONTACT_FOUNDERS", "false")
        self.max_founders_to_contact = os.getenv("MAX_FOUNDERS_TO_CONTACT", 1)
        self.analyze_profile_with_gpt = os.getenv("ANALYZE_PROFILES_WITH_GPT", "false")
        self.gpt_api_key = os.getenv("CHAT_GPT_API_KEY", "")
        self.skip_yc_alumni = os.getenv("SKIP_YC_ALUMNI", "false")
        self.gpt_questions = os.getenv("CHAT_GPT_QUESTIONS", "")

        interest_groups = os.getenv("IMPORTANT_SHARED_INTERESTS").split(";")
        self.important_interests = []
        for group in interest_groups:
            group_interests = group.split(",")
            self.important_interests.append(group_interests)

        self.my_profile = MyProfile(self.driver)

    def check_elapsed_time(self):
        return (int(time()) - self.bot_start_time < os.getenv("BOT_MAX_RUN_TIME"))
    
    def can_form_group(group, category_set):
        return all(item in category_set for item in group)

    def search_profiles(self):
        pass

    def change_cities_and_search_profiles(self):
        for city in self.cities:
            if not self.my_profile.go_to_profile_and_change_city(city):
                next
            
            if not self.go_to_discover():
                # TODO: log to email
                return
            
            search_result = self.search_profiles()
            if not search_result: break
            
    def go_to_discover(self):
        discover = self.driver.find_elements(By.XPATH, CONSTANTS.DASHBOARD_DISCOVER_MENU_OPTION)
        if len(discover) == 1:
            discover[0].click()
            utils.random_long_sleep()
            return self.driver.current_url.startswith(CONSTANTS.DISCOVER_PROFILES_URL)
        print("Discover Profiles button is not found or multiple instances found.")
        return False

    def is_yc_alumn(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        yc_alum_tag = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_YC_ALUM_TAG_FIELD)
        if CONSTANTS.FOUNDER_YC_ALUM_TAG_TEXT in soup.get_text() or len(yc_alum_tag) > 0:
            return True
        return False
    
    def important_interests_match(self, interests_set):
        for index, interests in enumerate(self.important_interests):
            if self.can_form_group(interests, interests_set):
                return index

        return -1

    def get_profile_info(self):
        # TODO: make sure the array of shared interests is converted into a set
        pass

    def analyze_with_gpt(self, profile_info):
        pass

    def contact_founder(self, interest_group):
        if self.contact_founders.lower() != "true": return
        if interest_group >= len(founder_messages):
            # TODO: log to email
            return False
        
        message_field = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_MESSAGE_FIELD)
        send_message_button = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_INVITE_TO_CONNECT_BUTTON)
        if len(message_field) != 1 or len(send_message_button) != 2: return False

        message_field.clear()
        message_field.send_keys(founder_messages[interest_group])
        utils.random_short_sleep()

        send_message_button.click()
        utils.random_normal_sleep()

        self.contact_founders += 1
        return True

    def skip_founder(self):
        skip_button = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_SKIP_PROFILE_BUTTON)
        if len(skip_button) != 4: return False

        skip_button.click()
        utils.random_normal_sleep()
        return True

    def save_founder(self):
        save_button = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_SAVE_TO_FAVORITES)
        next_founder_button = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_SEE_NEXT_PROFILE_BUTTON)
        if len(save_button) != 1: return False
        if len(next_founder_button) != 4: return False

        save_button.click()
        utils.random_short_sleep()
        next_founder_button.click()
        utils.random_normal_sleep()
        return True

    def go_back_to_preferred_city(self):
        if not self.my_profile.go_to_profile_and_change_city(self.city_to_return_to):
            # TODO: log to email
            return False
        
        return True

    def find_cofounders(self):
        try:
            if len(self.cities) == 0 or self.cities[0] == "":
                if not self.go_to_discover():
                    # TODO: log to email
                    return
                self.search_profiles()
            else:
                self.change_cities_and_search_profiles()
            pass
        except Exception as e:
            # TODO: log to email
            print(e)
            pass