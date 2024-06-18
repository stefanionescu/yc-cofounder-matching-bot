import os
from time import time
from openai import OpenAI
from bs4 import BeautifulSoup
import constants as CONSTANTS
from dotenv import load_dotenv
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
        profile_info = {}
        # Get intro
        profile_info.intro = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_INTRO).text.rstrip()
        # Get life story
        profile_info.life_story = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_LIFE_STORY).text.rstrip()
        # Get free time
        profile_info.free_time = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_FREE_TIME).text.rstrip()
        # Get other info
        profile_info.other = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_OTHER_INFO).text.rstrip()
        # Get equity expectations
        profile_info.equity_expectations = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_EQUITY_EXPECTATIONS).text.rstrip()
        # Get impressive accomplishments
        profile_info.accomplishments = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_IMPRESSIVE_ACCOMPLISHMENT).text.rstrip()
        # Get potential ideas
        profile_info.potential_ideas = ""
        potential_ideas = self.driver.find_elements(By.CSS_SELECTOR, CONSTANTS.FOUNDER_POTENTIAL_IDEAS)
        if potential_ideas is not None and len(potential_ideas) == 1:
            profile_info.potential_ideas = potential_ideas[0].text.rstrip()
        # Get shared interests
        profile_info.shared_interests = set()
        shared_interests_span = self.driver.find_element(By.XPATH, CONSTANTS.FOUNDER_SHARED_INTERESTS_SPAN).find_elements(By.TAG_NAME, "div")
        interests_array = []
        for interest in shared_interests_span:
            interests_array.append(interest.text)
        if len(interests_array) > 0:
            profile_info.shared_interests = set(interests_array)
        return profile_info
            
    def analyze_with_gpt(self, profile_info):
        if profile_info is None: 
            # TODO: log to email
            return (False, None)

        gpt = OpenAI(
            organization= os.getenv("CHAT_GPT_ORGANIZATION"),
            project=os.getenv("CHAT_GPT_API_KEY")
        )

        prompt_text = self.generate_gpt_prompt(profile_info)
        if prompt_text is None or prompt_text == "": return (CONSTANTS.GPT_PROMPT_CREATION_FAILED, True)

        try:
            gpt_response = gpt.chat.completions.create(
                model=CONSTANTS.GPT_MODEL,
                messages=[
                    {"role": "system", "content": CONSTANTS.CHAT_GPT_SYSTEM_PERSONA},
                    {"role": "user", "content": prompt_text}
                ],
                max_tokens=CONSTANTS.GPT_MAX_TOKENS,
                temperature=CONSTANTS.GPT_TEMPERATURE
            )

            if 'choices' not in gpt_response or gpt_response['choices'] is None:
                # TODO: log to email
                return (CONSTANTS.NO_ANSWER_FROM_GPT, True)
            
            gpt_likes_founder = False
            if CONSTANTS.GPT_ANSWER_PASS in gpt_response.choices[0].message:
                gpt_likes_founder = True
            
            return ("", gpt_likes_founder)
        except Exception as e:
            # TODO: log to email
            return (CONSTANTS.CANNOT_CALL_GPT, True)

    def generate_gpt_prompt(self, profile_info):
        gpt_prompt = CONSTANTS.CHAT_GPT_PROMPT_ONE.format(founder_intro=profile_info.intro) + \
                     " " + \
                     CONSTANTS.CHAT_GPT_PROMPT_TWO.format(free_time=profile_info.life_story) + \
                     " " + \
                     CONSTANTS.CHAT_GPT_PROMPT_THREE.format(other_info=profile_info.free_time) + \
                     " " + \
                     CONSTANTS.CHAT_GPT_PROMPT_FOUR.format(impressive_accomplishment=profile_info.other) + \
                     " " + \
                     CONSTANTS.CHAT_GPR_PROMPT_FIVE.format(impressive_accomplishment=profile_info.accomplishments) + \
                     " " + \
                     CONSTANTS.CHAT_GPT_PROMPT_SIX.format(potential_ideas=profile_info.potential_ideas) + \
                     " " + \
                     CONSTANTS.PROMPT_ENDING
        
        return gpt_prompt


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
        return self.my_profile.go_to_profile_and_change_city(self.city_to_return_to)

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