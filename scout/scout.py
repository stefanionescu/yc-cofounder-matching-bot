import os
import sys
from time import time
import constants as CONSTANTS
from dotenv import load_dotenv
from utils.utils import Utils as utils
from selenium.webdriver.common.by import By
from my_profile.my_profile import MyProfile
from founder_messages import founder_messages

class Scout:
    def __init__(self, driver):
        load_dotenv()  # Load environment variables
        self.driver = driver
        self.bot_start_time = time()
        self.initialize_environment()

    def initialize_environment(self):
        """ Initialize environment variables and set default values. """
        self.cities = os.getenv("YC_CITIES", "").split(";")
        self.city_to_return_to = os.getenv("CITY_TO_RETURN_TO", "")
        self.bot_max_run_time = int(os.getenv("BOT_MAX_RUN_TIME", 600))
        self.contact_founders_flag = os.getenv("CONTACT_FOUNDERS", "false") == "true"
        self.max_founders_to_contact = int(os.getenv("MAX_FOUNDERS_TO_CONTACT", 1))
        self.analyze_profile_with_gpt = os.getenv("ANALYZE_PROFILES_WITH_GPT", "false") == "true"
        self.gpt_organization = os.getenv("CHAT_GPT_ORGANIZATION", "")
        self.gpt_project = os.getenv("CHAT_GPT_PROJECT", "")
        self.skip_yc_alumni = os.getenv("SKIP_YC_ALUMNI", "false") == "true"
        self.gpt_questions = os.getenv("CHAT_GPT_QUESTIONS", "")
        self.important_interests = [group.split(",") for group in os.getenv("IMPORTANT_SHARED_INTERESTS", "").split(";")]
        self.my_profile = MyProfile(self.driver)
        self.initialize_counters()

    def initialize_counters(self):
        """ Initialize counters for tracked activities. """
        self.contacted_founders = 0
        self.skipped_founders = 0
        self.saved_founders = 0
        self.skipped_cities = 0

    def check_elapsed_time(self, time_limit):
        """ Check if the current time is within the allowed time limit. """
        return (time() - self.bot_start_time) < time_limit

    def can_form_group(self, group, category_set):
        """ Check if all items in a group are present in a category set. """
        return all(item in category_set for item in group)

    def still_have_time(self):
        """ Check if there is still time to perform operations based on max run time. """
        return self.check_elapsed_time(self.bot_max_run_time) and self.check_elapsed_time(CONSTANTS.MAX_POSSIBLE_ELAPSED_TIME)
    
    def go_to_discover(self):
        """ Navigate to the Discover page and verify if navigation was successful. """
        try:
            discover = self.driver.find_element(By.XPATH, CONSTANTS.DASHBOARD_DISCOVER_MENU_OPTION)
            discover.click()
            utils.random_long_sleep()
            return self.driver.current_url.startswith(CONSTANTS.DISCOVER_PROFILES_URL)
        except Exception as e:
            print(f"Failed to navigate to Discover: {e}")
            return False

    def is_yc_alumn(self):
        """ Check if the profile belongs to a YC alumnus by looking for specific markers. """
        try:
            # Directly search for the specific text or markers
            yc_alum_tag = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_YC_ALUM_TAG_FIELD)
            if any(CONSTANTS.FOUNDER_YC_ALUM_TAG_TEXT in elem.text for elem in yc_alum_tag):
                return True
            return False
        except Exception as e:
            print(f"Error checking YC alumni status: {e}")
            return False

    def important_interests_match(self, interests_set):
        """ Determine if any important interest groups match the given interests set. """
        if not interests_set:
            return -1
        for index, interests in enumerate(self.important_interests):
            if self.can_form_group(interests, interests_set):
                return index
        return -1

    def get_profile_info(self):
        """ Extracts all relevant information from a founder's profile page. """
        try:
            profile_info = {
                'intro': self.extract_text(By.XPATH, CONSTANTS.FOUNDER_INTRO),
                'life_story': self.extract_text(By.XPATH, CONSTANTS.FOUNDER_LIFE_STORY),
                'free_time': self.extract_text(By.XPATH, CONSTANTS.FOUNDER_FREE_TIME),
                'other_info': self.extract_text(By.XPATH, CONSTANTS.FOUNDER_OTHER_INFO),
                'equity_expectations': self.extract_text(By.XPATH, CONSTANTS.FOUNDER_EQUITY_EXPECTATIONS),
                'accomplishments': self.extract_text(By.XPATH, CONSTANTS.FOUNDER_IMPRESSIVE_ACCOMPLISHMENT),
                'potential_ideas': self.extract_text(By.CSS_SELECTOR, CONSTANTS.FOUNDER_POTENTIAL_IDEAS),
                'shared_interests': self.extract_interests(By.XPATH, CONSTANTS.FOUNDER_SHARED_INTERESTS_SPAN)
            }
            return profile_info if all(profile_info.values()) else None
        except Exception as e:
            print(f"Error extracting profile information: {e}")
            return None

    def extract_text(self, by, locator):
        """ Helper function to safely extract text from a single element. """
        element = self.driver.find_element(by, locator)
        return element.text.strip() if element else None

    def extract_interests(self, by, locator):
        """ Helper function to extract interests from profile, assumes they are in div tags. """
        interests_span = self.driver.find_elements(by, locator)
        return {div.text for div in interests_span[0].find_elements(By.TAG_NAME, 'div')} if interests_span else set()

    def analyze_with_gpt(self, profile_info):
        """ Analyze the founder's profile using GPT and determine interest. """
        if not profile_info:
            print("Profile information is incomplete.")
            return None, False
        
        prompt_text = self.generate_gpt_prompt(profile_info)
        if not prompt_text:
            print("Failed to generate a valid GPT prompt.")
            return None, False
        
        try:
            response = self.call_gpt_api(prompt_text)
            print("the GPT response is:")
            print(response)
            return self.interpret_gpt_response(response)
        except Exception as e:
            print(f"Failed to call GPT API: {e}")
            return None, False
    
    def call_gpt_api(self, prompt):
        """ Send a prompt to the GPT API and return the response. """
        from openai import Completion
        return Completion.create(
            engine=CONSTANTS.GPT_MODEL,
            prompt=prompt,
            max_tokens=CONSTANTS.GPT_MAX_TOKENS,
            temperature=CONSTANTS.GPT_TEMPERATURE,
            top_p=1
        )
    
    def interpret_gpt_response(self, response):
        """ Interpret GPT's response to determine the next step. """
        if 'choices' not in response or not response['choices']:
            print("No valid response from GPT.")
            return None, False
        answer = response['choices'][0].text.strip()
        return answer, CONSTANTS.GPT_ANSWER_PASS in answer

    def generate_gpt_prompt(self, profile_info):
        """ Generate a detailed prompt for GPT based on the founder's profile. """
        if not profile_info:
            return ""
        parts = [
            CONSTANTS.CHAT_GPT_PROMPT_ONE.format(founder_intro=profile_info['intro']),
            CONSTANTS.CHAT_GPT_PROMPT_TWO.format(life_story=profile_info['life_story']),
            CONSTANTS.CHAT_GPT_PROMPT_THREE.format(free_time=profile_info['free_time']),
            CONSTANTS.CHAT_GPT_PROMPT_FOUR.format(other_info=profile_info['other_info']),
            CONSTANTS.CHAT_GPT_PROMPT_FIVE.format(impressive_accomplishment=profile_info['accomplishments']),
            CONSTANTS.CHAT_GPT_PROMPT_SIX.format(potential_ideas=profile_info['potential_ideas']),
            CONSTANTS.PROMPT_ENDING,
            self.gpt_questions
        ]
        return " ".join(filter(None, parts))

    def contact_founder(self, interest_group):
        """ Contact a founder based on a specific interest group. """
        if not self.contact_founders_flag:
            print("Contacting founders is disabled.")
            return False
        if interest_group >= len(founder_messages):
            print("Interest group index out of range.")
            return False

        try:
            message_field = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_MESSAGE_FIELD)
            send_button = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_INVITE_TO_CONNECT_BUTTON)
            message_field.clear()
            message_field.send_keys(founder_messages[interest_group])
            utils.random_short_sleep()
            send_button.click()
            utils.random_normal_sleep()
            self.contacted_founders += 1
            return True
        except Exception as e:
            print(f"Failed to contact founder: {e}")
            return False
        
    def skip_founder(self):
        """ Skip the current founder profile. """
        try:
            skip_button = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_SKIP_PROFILE_BUTTON)
            skip_button.click()
            utils.random_normal_sleep()
            self.skipped_founders += 1
            return True
        except Exception as e:
            print(f"Failed to skip founder: {e}")
            return False

    def save_founder(self):
        """ Save the current founder profile to favorites. """
        try:
            save_button = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_SAVE_TO_FAVORITES)
            next_button = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_SEE_NEXT_PROFILE_BUTTON)
            save_button.click()
            utils.random_short_sleep()
            next_button.click()
            utils.random_normal_sleep()
            self.saved_founders += 1
            return True
        except Exception as e:
            print(f"Failed to save founder: {e}")
            return False

    def go_back_to_preferred_city(self):
        """ Navigate back to the preferred city in the profile settings. """
        return self.my_profile.go_to_profile_and_change_city(self.city_to_return_to)

    def find_cofounders(self):
        """ Initiate the process of finding and handling cofounder profiles across cities. """
        try:
            self.setup_discovery()
            self.handle_city_profiles()
            self.wrap_up_search()
        except Exception as e:
            print(f"Exception during cofounder search: {e}")

    def setup_discovery(self):
        """ Prepare for profile discovery by navigating to the discover page if necessary. """
        if len(self.cities) == 0 or self.cities[0] == "":
            if not self.go_to_discover():
                print("Failed to navigate to Discover page.")
                return

    def handle_city_profiles(self):
        """ Process profiles for each city in the list. """
        for city in self.cities:
            if not self.still_have_time():
                break
            if not self.change_city_and_search(city):
                print(f"Failed to process profiles for city: {city}")

    def change_city_and_search(self, city):
        """ Change to a specific city and search for profiles. """
        if not self.my_profile.go_to_profile_and_change_city(city):
            self.skipped_cities += 1
            return False
        if not self.go_to_discover():
            self.skipped_cities += 1
            return False
        return self.search_profiles()

    def wrap_up_search(self):
        """ Complete the search process by returning to the preferred city. """
        if not self.go_back_to_preferred_city():
            print("Failed to return to preferred city.")

    def search_profiles(self):
        """ Navigate and process profiles on the Discover page. """
        if not self.driver.current_url.startswith(CONSTANTS.DISCOVER_PROFILES_URL):
            self.skipped_cities += 1
            return False

        while self.still_have_time() and self.driver.current_url.startswith(CONSTANTS.DISCOVER_PROFILES_URL):
            if not self.process_current_profile():
                continue  # Skip to next profile if current one is not processed
        return True

    def process_current_profile(self):
        """ Process an individual founder's profile and determine actions based on profile data. """
        if self.skip_yc_alumni and self.is_yc_alumn():
            return self.skip_founder()

        profile_info = self.get_profile_info()
        if not profile_info:
            return False  # Skip profile if no info is extracted

        interest_group = self.important_interests_match(profile_info['shared_interests'])
        if interest_group == -1:
            return self.skip_founder()

        return self.evaluate_and_act_on_profile(profile_info, interest_group)

    def evaluate_and_act_on_profile(self, profile_info, interest_group):
        """ Evaluate profile with or without GPT and act accordingly (contact/save). """
        if self.analyze_profile_with_gpt and self.gpt_questions:
            return self.handle_profile_with_gpt(profile_info, interest_group)
        return self.default_profile_handling(interest_group)

    def handle_profile_with_gpt(self, profile_info, interest_group):
        """ Use GPT to analyze the profile and decide on further actions. """
        gpt_analysis = self.analyze_with_gpt(profile_info)
        if not gpt_analysis[1]:  # GPT does not recommend contacting
            return False
        return self.contact_or_save_founder(interest_group)

    def default_profile_handling(self, interest_group):
        """ Handle profile based on the system settings without GPT analysis. """
        if self.contact_founders_flag and self.contacted_founders < self.max_founders_to_contact:
            return self.contact_founder(interest_group)
        return self.save_founder()

    def change_cities_and_search_profiles(self):
        """ Iterate through cities to search for cofounders. """
        for city in self.cities:
            if not self.still_have_time():
                break
            if not self.change_city_and_search(city):
                print(f"Failed to process profiles in city: {city}")

    def change_city_and_search(self, city):
        """ Change to the specified city and perform profile searching. """
        if not self.my_profile.go_to_profile_and_change_city(city):
            self.skipped_cities += 1
            return False
        return self.search_profiles_in_city()

    def search_profiles_in_city(self):
        """ Check and manage profiles searching in the current city. """
        if not self.go_to_discover():
            self.skipped_cities += 1
            return False
        return self.search_profiles()