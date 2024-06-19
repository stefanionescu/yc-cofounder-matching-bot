import os
from time import time 
from scout.scout import Scout
import constants as CONSTANTS
from selenium import webdriver
from dotenv import load_dotenv
import chromedriver_autoinstaller
from sign_in.sign_in import SignIn
from proxy.extension import proxies
from utils.utils import Utils as utils
from my_profile.my_profile import MyProfile
from founder_messages import founder_messages
from selenium.webdriver.chrome.options import Options

def setup_chrome_driver():
    """
    Sets up and returns a Chrome WebDriver with configured options and potential proxy.
    """
    chromedriver_autoinstaller.install()
    chrome_options = Options()
    add_chrome_options(chrome_options)
    configure_proxy_if_needed(chrome_options)
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def add_chrome_options(chrome_options):
    """
    Adds necessary Chrome options for the browser.
    """
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--v=1')
    chrome_options.add_argument('--log-level=0')

def configure_proxy_if_needed(chrome_options):
    """
    Configures a proxy for Chrome if the relevant environment variable is set.
    """
    use_proxy = os.getenv('USE_PROXY', '').lower() == 'true'
    if use_proxy:
        proxy_details = get_proxy_details()
        if None not in proxy_details.values():
            proxy_extension = proxies(**proxy_details)
            chrome_options.add_extension(proxy_extension)
            print("Proxy setup complete.")
        else:
            print("Incomplete proxy configuration. Check environment variables.")

def get_proxy_details():
    """
    Retrieves proxy configuration details from environment variables.
    """
    return {
        'username': os.getenv("SMART_PROXY_USERNAME"),
        'password': os.getenv("SMART_PROXY_PASSWORD"),
        'endpoint': os.getenv("SMART_PROXY_ENDPOINT"),
        'port': os.getenv("SMART_PROXY_PORT")
    }

def check_yc_creds():
    """
    Checks YC credentials availability.
    """
    return all(os.getenv(key) for key in ["YC_USERNAME", "YC_PASSWORD"])

def check_general_vars():
    """
    Validate general bot settings from environment variables.
    """
    max_runtime = os.getenv("BOT_MAX_RUN_TIME", 1)
    use_gpt = os.getenv("ANALYZE_PROFILES_WITH_GPT", "false").lower() == "true"
    gpt_key = os.getenv("CHAT_GPT_API_KEY", "")
    gpt_org = os.getenv("CHAT_GPT_ORGANIZATION", "")
    gpt_project_id = os.getenv("CHAT_GPT_PROJECT_ID", "")
    city_to_return_to = os.getenv("CITY_TO_RETURN_TO", "")
    contact_founders = os.getenv("CONTACT_FOUNDERS", "false").lower() == "true"
    max_founders_to_contact = os.getenv("MAX_FOUNDERS_TO_CONTACT", 0)
    shared_interests = os.getenv("IMPORTANT_SHARED_INTERESTS", "").split(";")

    if city_to_return_to == "" or len(city_to_return_to) <= 2:
        return False
    if not max_runtime or not 600 <= int(max_runtime) <= 1500:
        return False
    if use_gpt and (not gpt_key or gpt_key != "") and (not gpt_org or gpt_org != "") and (not gpt_project_id or gpt_project_id != ""):
        return False
    if contact_founders and not 0 < int(max_founders_to_contact) or contact_founders and len(founder_messages) == 0:
        return False
    if shared_interests[0] == "" or (len(shared_interests) != len(founder_messages)):
        return False

    return True

def log_into_account(driver):
    """
    Log into a YC account using provided WebDriver. Returns True if login successful, else False.
    """
    sign_in = SignIn(driver)
    if not sign_in.go_to_sign_in() or not sign_in.sign_in():
        print("Failed to navigate to sign-in page or log in.")
        return False

    my_profile = MyProfile(driver)
    return my_profile.check_dashboard_weekly_limit_reached()

def find_cofounders(driver, bot_start_time):
    """
    Search and contact cofounders.
    """
    cofounder_scout = Scout(driver, bot_start_time)
    cofounder_scout.find_cofounders()

def main():
    """
    Main execution routine.
    """
    bot_start_time = int(time())

    if not check_yc_creds():
        print("Invalid YC credentials. Please check environment variables.")
        return
    
    if not check_general_vars():
        print("Invalid bot vars. Please check environment variables.")
        return

    driver = setup_chrome_driver()
    try:
        driver.get(CONSTANTS.BASE_URL)
        utils.random_normal_sleep()

        if not log_into_account(driver):
            return

        # find_cofounders(driver, bot_start_time)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    load_dotenv()
    main()