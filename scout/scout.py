# import os
# import sys
# from time import time
# from openai import OpenAI
# from bs4 import BeautifulSoup
# import constants as CONSTANTS
# from dotenv import load_dotenv
# from utils.utils import Utils as utils
# from selenium.webdriver.common.by import By
# from my_profile.my_profile import MyProfile
# from founder_messages import founder_messages

# class Scout():
#     def __init__(self, driver, start_time):
#         self.driver = driver
#         self.bot_start_time = start_time

#         load_dotenv() # Load environment variables once during initialization

#         self.contacted_founders = 0
#         self.skipped_founders = 0
#         self.saved_founders = 0
#         self.skipped_cities = 0

#         self.cities = os.getenv("YC_CITIES").split(";")
#         self.city_to_return_to = os.getenv("CITY_TO_RETURN_TO")
#         self.bot_max_run_time = os.getenv("BOT_MAX_RUN_TIME", 600)
#         self.contact_founders_flag = os.getenv("CONTACT_FOUNDERS", "false")
#         self.max_founders_to_contact = os.getenv("MAX_FOUNDERS_TO_CONTACT", 1)
#         self.analyze_profile_with_gpt = os.getenv("ANALYZE_PROFILES_WITH_GPT", "false")
#         self.gpt_organization = os.getenv("CHAT_GPT_ORGANIZATION", "")
#         self.gpt_project = os.getenv("CHAT_GPT_PROJECT", "")
#         self.skip_yc_alumni = os.getenv("SKIP_YC_ALUMNI", "false")
#         self.gpt_questions = os.getenv("CHAT_GPT_QUESTIONS", "")

#         interest_groups = os.getenv("IMPORTANT_SHARED_INTERESTS").split(";")
#         self.important_interests = []
#         for group in interest_groups:
#             group_interests = group.split(",")
#             self.important_interests.append(group_interests)

#         self.my_profile = MyProfile(self.driver)

#     def check_elapsed_time(self, time_limit):
#         return (int(time()) - self.bot_start_time < time_limit)
    
#     def can_form_group(group, category_set):
#         return all(item in category_set for item in group)
    
#     def still_have_time(self):
#         return (self.check_elapsed_time(self.bot_max_run_time) and self.check_elapsed_time(CONSTANTS.MAX_POSSIBLE_ELAPSED_TIME))

#     def search_profiles(self):
#         # If not on discover page, increment skipped cities and return
#         if not self.driver.current_url.startswith(CONSTANTS.DISCOVER_PROFILES_URL): 
#             self.skipped_cities += 1
#             return False
#         # While time did not elapse and while there are still profiles to see in the current city, loop through profiles
#         while self.still_have_time() and self.driver.current_url.startswith(CONSTANTS.DISCOVER_PROFILES_URL):
#             # See if we need to check if they are a YC alum. If we check and they are, skip. If we check and they aren't, continue to analyze the profile
#             if self.skip_yc_alumni == "true" and self.is_yc_alumn():
#                 skip_result = self.skip_founder()
#                 if not skip_result: return False
#                 continue
#             # Get profile info
#             profile_info = self.get_profile_info()
#             if profile_info is None: return False
#             # Check if your preferences match. If not, skip. If yes, continue
#             interest_group = self.important_interests_match(profile_info.shared_interests)
#             if interest_group == -1:
#                 skip_result = self.skip_founder()
#                 if not skip_result: return False
#                 continue
#             # See if we need to get GPT's opinion and if self.gpt_questions is not null. Depending on opinion, decide if we skip or save/contact the founder
#             gpt_outcome = "failed"
#             if self.gpt_questions != "" and self.analyze_profile_with_gpt == "true":
#                 gpt_analysis = self.analyze_with_gpt(profile_info)
#                 # If there was an error with GPT, skip this section
#                 if gpt_analysis[0] == "":
#                     # If we need to contact and we contacted less profiles than the max, send message to founder
#                     if self.contacted_founders < self.max_founders_to_contact and self.contact_founders_flag == "true":
#                         contact_founder_result = self.contact_founder(interest_group)
#                         if contact_founder_result == False: return False
#                         gpt_outcome = "succeeded"
#                     # Otherwise just save the profile
#                     else:
#                         save_founder_result = self.save_founder()
#                         if save_founder_result == False: return False
#                         gpt_outcome = "succeeded"
                        
#             if gpt_outcome == "failed":
#                 # If we need to contact and we contacted less profiles than the max, send message to founder
#                 if self.contacted_founders < self.max_founders_to_contact and self.contact_founders_flag == "true":
#                     contact_founder_result = self.contact_founder(interest_group)
#                     if contact_founder_result == False: return False
#                 # Otherwise just save the profile
#                 else:
#                     save_founder_result = self.save_founder()
#                     if save_founder_result == False: return False

#         # Return True when we don't have any more profiles to see
#         return True

#     def change_cities_and_search_profiles(self):
#         for city in self.cities:
#             if (not self.still_have_time()): break
#             if not self.my_profile.go_to_profile_and_change_city(city):
#                 self.skipped_cities += 1
#                 continue
            
#             if not self.go_to_discover():
#                 # TODO: log to email
#                 self.skipped_cities += 1
#                 continue

#             search_result = self.search_profiles()
#             if not search_result: 
#                 # TODO: log to email
#                 break
            
#     def go_to_discover(self):
#         discover = self.driver.find_elements(By.XPATH, CONSTANTS.DASHBOARD_DISCOVER_MENU_OPTION)
#         if len(discover) == 1:
#             discover[0].click()
#             utils.random_long_sleep()
#             return self.driver.current_url.startswith(CONSTANTS.DISCOVER_PROFILES_URL)
#         return False

#     def is_yc_alumn(self):
#         soup = BeautifulSoup(self.driver.page_source, 'html.parser')
#         yc_alum_tag = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_YC_ALUM_TAG_FIELD)
#         if CONSTANTS.FOUNDER_YC_ALUM_TAG_TEXT in soup.get_text() or len(yc_alum_tag) > 0:
#             return True
#         return False
    
#     def important_interests_match(self, interests_set):
#         if len(interests_set) == 0: return -1
#         for index, interests in enumerate(self.important_interests):
#             if self.can_form_group(interests, interests_set):
#                 return index

#         return -1

#     def get_profile_info(self):
#         profile_info = {}
#         # Get intro
#         intro = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_INTRO)
#         if intro is None or len(intro) != 1: return None
#         profile_info.intro = intro[0].text.rstrip()
#         # Get life story
#         life_story = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_LIFE_STORY)
#         if life_story is None or len(life_story) != 1: return None
#         profile_info.life_story = life_story[0].text.rstrip()
#         # Get free time
#         free_time = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_FREE_TIME)
#         if free_time is None or len(free_time) != 1: return None
#         profile_info.free_time = free_time[0].text.rstrip()
#         # Get other info
#         other = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_OTHER_INFO)
#         if other is None or len(other) != 1: return None
#         profile_info.other = other[0].text.rstrip()
#         # Get equity expectations
#         equity_expectations = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_EQUITY_EXPECTATIONS)
#         if equity_expectations is None or len(equity_expectations) != 1: return None
#         profile_info.equity_expectations = equity_expectations[0].text.rstrip()
#         # Get impressive accomplishments
#         accomplishments = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_IMPRESSIVE_ACCOMPLISHMENT)
#         if accomplishments is None or len(accomplishments) != 1: return None
#         profile_info.accomplishments = accomplishments[0].text.rstrip()
#         # Get potential ideas
#         profile_info.potential_ideas = ""
#         potential_ideas = self.driver.find_elements(By.CSS_SELECTOR, CONSTANTS.FOUNDER_POTENTIAL_IDEAS)
#         if potential_ideas is not None and len(potential_ideas) == 1:
#             profile_info.potential_ideas = potential_ideas[0].text.rstrip()
#         # Get shared interests
#         profile_info.shared_interests = set()
#         shared_interests_span = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_SHARED_INTERESTS_SPAN)
#         if shared_interests_span is None or len(shared_interests_span) != 1: return profile_info
#         shared_interests_divs = shared_interests_span[0].find_elements(By.TAG_NAME, "div")
#         interests_array = []
#         for interest in shared_interests_divs:
#             interests_array.append(interest.text)
#         if len(interests_array) > 0:
#             profile_info.shared_interests = set(interests_array)
#         return profile_info
            
#     def analyze_with_gpt(self, profile_info):
#         if profile_info is None: 
#             # TODO: log to email
#             return (CONSTANTS.EMPTY_PROFILE_INFO, False)

#         gpt = OpenAI(
#             organization=self.gpt_organization,
#             project=self.gpt_project
#         )

#         prompt_text = self.generate_gpt_prompt(profile_info)
#         if prompt_text is None or prompt_text == "": return (CONSTANTS.GPT_PROMPT_CREATION_FAILED, False)

#         try:
#             gpt_response = gpt.chat.completions.create(
#                 model=CONSTANTS.GPT_MODEL,
#                 messages=[
#                     {"role": "system", "content": CONSTANTS.CHAT_GPT_SYSTEM_PERSONA},
#                     {"role": "user", "content": prompt_text}
#                 ],
#                 max_tokens=CONSTANTS.GPT_MAX_TOKENS,
#                 temperature=CONSTANTS.GPT_TEMPERATURE
#             )

#             if 'choices' not in gpt_response or gpt_response['choices'] is None:
#                 # TODO: log to email
#                 return (CONSTANTS.NO_ANSWER_FROM_GPT, False)
            
#             gpt_likes_founder = False
#             if CONSTANTS.GPT_ANSWER_PASS in gpt_response.choices[0].message:
#                 gpt_likes_founder = True
            
#             return ("", gpt_likes_founder)
#         except Exception as e:
#             # TODO: log to email
#             return (CONSTANTS.CANNOT_CALL_GPT, False)

#     def generate_gpt_prompt(self, profile_info):
#         gpt_prompt = CONSTANTS.CHAT_GPT_PROMPT_ONE.format(founder_intro=profile_info.intro) + \
#                      " " + \
#                      CONSTANTS.CHAT_GPT_PROMPT_TWO.format(free_time=profile_info.life_story) + \
#                      " " + \
#                      CONSTANTS.CHAT_GPT_PROMPT_THREE.format(other_info=profile_info.free_time) + \
#                      " " + \
#                      CONSTANTS.CHAT_GPT_PROMPT_FOUR.format(impressive_accomplishment=profile_info.other) + \
#                      " " + \
#                      CONSTANTS.CHAT_GPR_PROMPT_FIVE.format(impressive_accomplishment=profile_info.accomplishments) + \
#                      " " + \
#                      CONSTANTS.CHAT_GPT_PROMPT_SIX.format(potential_ideas=profile_info.potential_ideas) + \
#                      " " + \
#                      CONSTANTS.PROMPT_ENDING + \
#                      " " + \
#                      self.gpt_questions
        
#         return gpt_prompt


#     def contact_founder(self, interest_group):
#         if self.contact_founders.lower() != "true": return
#         if interest_group >= len(founder_messages):
#             # TODO: log to email
#             return False
        
#         message_field = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_MESSAGE_FIELD)
#         send_message_button = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_INVITE_TO_CONNECT_BUTTON)
#         if len(message_field) != 1 or len(send_message_button) != 2: 
#             # TODO: log to email
#             return False

#         message_field.clear()
#         message_field.send_keys(founder_messages[interest_group])
#         utils.random_short_sleep()

#         send_message_button.click()
#         utils.random_normal_sleep()

#         self.contact_founders += 1
#         return True

#     def skip_founder(self):
#         skip_button = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_SKIP_PROFILE_BUTTON)
#         if len(skip_button) != 4: return False

#         skip_button.click()
#         utils.random_normal_sleep()

#         self.skipped_founders += 1
#         return True

#     def save_founder(self):
#         save_button = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_SAVE_TO_FAVORITES)
#         next_founder_button = self.driver.find_elements(By.XPATH, CONSTANTS.FOUNDER_SEE_NEXT_PROFILE_BUTTON)
#         if len(save_button) != 1: return False
#         if len(next_founder_button) != 4: return False

#         save_button.click()
#         utils.random_short_sleep()
#         next_founder_button.click()
#         utils.random_normal_sleep()

#         self.saved_founders += 1
#         return True

#     def go_back_to_preferred_city(self):
#         return self.my_profile.go_to_profile_and_change_city(self.city_to_return_to)

#     def find_cofounders(self):
#         try:
#             if len(self.cities) == 0 or self.cities[0] == "":
#                 if not self.go_to_discover():
#                     # TODO: log to email
#                     return
#                 self.search_profiles()
#                 self.go_back_to_preferred_city()
#             else:
#                 self.change_cities_and_search_profiles()
#                 self.go_back_to_preferred_city()
#             pass
#         except Exception as e:
#             # TODO: log to email
#             print(e)
#             pass

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