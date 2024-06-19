# URLs and Endpoint Definitions
BASE_URL = "https://www.ycombinator.com/cofounder-matching"
MY_PROFILE_URL = "https://www.startupschool.org/cofounder-matching/profile"
STARTUP_SCHOOL_DASHBOARD_URL = "https://www.startupschool.org/cofounder-matching"
DISCOVER_PROFILES_URL = "https://www.startupschool.org/cofounder-matching/candidate"

# XPaths for Dynamic Elements on Pages
LANDING_PAGE_SIGN_IN_BUTTON = "//div/a[starts-with(@href, 'http://startupschool.org/users/sign_in?continue_url')]"
DASHBOARD_MY_ACCOUNT_MENU_OPTION = "//a//div[text()='My Account']"
DASHBOARD_DISCOVER_MENU_OPTION = "//a//div[text()='Discover Profiles']"
MY_PROFILE_BASICS_BUTTON = "//span[text()='Basics']"
MY_PROFILE_SUBMIT_BUTTON = "//button[@type='submit'][@disabled='']"

FOUNDER_MESSAGE_FIELD = "//div//div//textarea"
FOUNDER_INVITE_TO_CONNECT_BUTTON = "//div//div//button[text()='Invite to connect']"
FOUNDER_SKIP_PROFILE_BUTTON = "//div//button[text()='Skip for now']"
FOUNDER_SEE_NEXT_PROFILE_BUTTON = "//div//button[text()='See next profile']"
FOUNDER_SAVE_TO_FAVORITES = "//div[text()='Save to favorites']"
FOUNDER_YC_ALUM_TAG_TEXT = "YC Alum ("
FOUNDER_YC_ALUM_TAG_FIELD = "//p//div//span[starts-with(., 'YC Alum (')]"
FOUNDER_SHARED_INTERESTS_SPAN = "//span[text()='Our shared interests']/following-sibling::div[1]/span"
FOUNDER_IMPRESSIVE_ACCOMPLISHMENT = "//span[text()='Impressive accomplishment']/following-sibling::div[1]"
FOUNDER_EQUITY_EXPECTATIONS = "//span[text()='Equity expectations']/following-sibling::div[1]"
FOUNDER_INTRO = "//span[text()='Intro']/following-sibling::div[1]"
FOUNDER_LIFE_STORY = "//span[text()='Life Story']/following-sibling::div[1]"
FOUNDER_FREE_TIME = "//span[text()='Free Time']/following-sibling::div[1]"
FOUNDER_OTHER_INFO = "//span[text()='Other']/following-sibling::div[1]"

# CSS Paths for Text Element
DASHBOARD_LIMIT_NOTICE_BOX = "div[class='css-1czqf2r e13d1soq2'] div div"
FOUNDER_POTENTIAL_IDEAS = "body > div:nth-child(1) > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(6) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1)"

# IDs and Class Names for Form Elements
SIGN_IN_USER_FIELD = "ycid-input"
SIGN_IN_PASS_FIELD = "password-input"
MY_PROFILE_CURRENT_LOCATION = "currentUser.location"
SIGN_IN_PAGE_LOGIN_BUTTON = "div.actions button[type='submit']"

# Page-Specific Query Parameters or Paths
MY_PROFILE_PAGE_URL_PAGE_ONE = "?page=1"

# Text Constants for Validation and Errors
FIX_ERRORS_STRING = "Please fix the errors below before continuing."
COULD_NOT_FIND_CITY_STRING = "Could not identify this location"
DASHBOARD_WEEKLY_LIMIT_NOTICE = "You can keep skipping or hiding profiles, but cannot send any more invites"
FOUNDER_PROFILE_WEEKLY_LIMIT_NOTICE = "You can keep skipping or hiding profiles, but cannot send any more invites. Check back on Monday when invites refresh!"

# GPT Instructions
CHAT_GPT_SYSTEM_PERSONA = "You answer all queries either with {'output': 'Pass'} or {'output': 'Fail'} depending on how you are prompted"
CHAT_GPT_PROMPT_ONE = "I'm analyzing the profile of a potential startup cofounder. Here is the founder's intro: {founder_intro}."
CHAT_GPT_PROMPT_TWO = "Here is the founder's life story: {life_story}."
CHAT_GPT_PROMPT_THREE = "Here's what the founder does in their free time: {free_time}."
CHAT_GPT_PROMPT_FOUR = "Here's some other information about the founder: {other_info}."
CHAT_GPT_PROMPT_FIVE = "Here are the founder's notable accomplishments: {impressive_accomplishment}."
CHAT_GPT_PROMPT_SIX = "Here are some potential startup ideas the founder has: {potential_ideas}."
PROMPT_QUESTIONS_SECTION = "My Questions: "
PROMPT_ENDING = "Your answer must be formatted exactly like this: {'output': 'Pass'} or {'output': 'Fail'}. You say {'output': 'Pass'} if the answer for at least one of the questions I asked is Yes. You say {'output': 'Fail'} if the answer for at least one of the questions I asked is No."
GPT_MODEL = "gpt-4o-2024-05-13"
GPT_MAX_TOKENS = 25
GPT_TEMPERATURE = 0
GPT_ANSWER_PASS = "'output': 'Pass'"
GPT_ANSWER_FAIL = "'output': 'Fail'"

# Error Messages
GPT_PROMPT_CREATION_FAILED = "Could not create GPT prompt"
NO_ANSWER_FROM_GPT = "GPT couldn't answer"
CANNOT_CALL_GPT = "Could not call GPT API"
EMPTY_PROFILE_INFO = "Profile info is empty"

# Input Validation Constants
MAX_CITY_LENGTH = 30
MAX_POSSIBLE_ELAPSED_TIME = 1500

# Time Delays and Wait Periods
SHORT_MIN_SECONDS_TO_WAIT = 4
SHORT_MAX_SECONDS_TO_WAIT = 7
NORMAL_MIN_SECONDS_TO_WAIT = 10
NORMAL_MAX_SECONDS_TO_WAIT = 15
LONG_MIN_SECONDS_TO_WAIT = 20
LONG_MAX_SECONDS_TO_WAIT = 25
DEFAULT_IMPLICIT_WAIT = 5