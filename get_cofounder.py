import os
import zipfile
import tempfile
from scout.scout import Scout
import constants as CONSTANTS
from dotenv import load_dotenv
from sign_in.sign_in import SignIn
from proxy.extension import proxies
import undetected_chromedriver as uc
from utils.utils import Utils as utils
from my_profile.my_profile import MyProfile
from founder_messages import founder_messages
from datetime import datetime, timedelta, timezone
from email_logging.email_logging import EmailLogging

def setup_chrome_driver():
    """
    Sets up and returns a Chrome WebDriver with configured options and potential proxy.
    """
    uc.TARGET_VERSION = CONSTANTS.CHROME_DRIVER_VERSION
    chrome_options = uc.ChromeOptions()

    add_chrome_options(chrome_options)
    configure_proxy_if_needed(chrome_options)

    driver = uc.Chrome(options=chrome_options, suppress_welcome=True)
    return driver

def add_chrome_options(chrome_options):
    """
    Adds necessary Chrome options for the browser.
    """
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--v=1')
    chrome_options.add_argument('--log-level=0')

def configure_proxy_if_needed(chrome_options):
    """
    Configures a proxy for Chrome if the relevant environment variable is set.
    """
    temp_dir = None
    use_proxy = os.getenv('USE_PROXY', '').lower() == 'true'
    if use_proxy:
        proxy_details = get_proxy_details()
        if None not in proxy_details.values():
            proxy_extension = proxies(**proxy_details)

            # Create a temporary directory to extract the extension
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(proxy_extension, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            chrome_options.add_argument(f'--load-extension={temp_dir}')
            print("GET_COFOUNDER: Proxy setup complete.")
        else:
            log_message(None, "Incomplete proxy configuration.")
            print("GET_COFOUNDER: Incomplete proxy configuration. Check environment variables.")

def get_proxy_details():
    """
    Retrieves proxy configuration details from environment variables.
    """
    return {
        'username': os.getenv("PROXY_USERNAME"),
        'password': os.getenv("PROXY_PASSWORD"),
        'endpoint': os.getenv("PROXY_ENDPOINT"),
        'port': os.getenv("PROXY_PORT")
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
    search_after_limit = os.getenv("SEARCH_WHEN_LIMIT_REACHED", "false").lower() == "true"
    use_gpt = os.getenv("ANALYZE_PROFILES_WITH_GPT", "false").lower() == "true"
    gpt_key = os.getenv("OPENAI_API_KEY", "")
    gpt_org = os.getenv("CHAT_GPT_ORGANIZATION", "")
    gpt_project_id = os.getenv("CHAT_GPT_PROJECT", "")
    city_to_return_to = os.getenv("CITY_TO_RETURN_TO", "")
    contact_founders = os.getenv("CONTACT_FOUNDERS", "false").lower() == "true"
    max_founders_to_contact = os.getenv("MAX_FOUNDERS_TO_CONTACT", 0)
    shared_interests = os.getenv("IMPORTANT_SHARED_INTERESTS", "").split(";")

    email_from = os.getenv("EMAIL_FROM", "")
    email_to = os.getenv("EMAIL_TO", "")
    email_from_password = os.getenv("EMAIL_FROM_PASSWORD", "")

    if city_to_return_to == "" or len(city_to_return_to) <= 2:
        print("GET_COFOUNDER: Invalid city to return to.")
        return False
    if not max_runtime or not 600 <= int(max_runtime) <= 3600:
        print("GET_COFOUNDER: Invalid max runtime.")
        return False
    if not search_after_limit:
        print("GET_COFOUNDER: Search after weekly limit is invalid.")
        return False
    if use_gpt and (gpt_key == "" or gpt_org == "" or gpt_project_id == ""):
        print("GET_COFOUNDER: Invalid GPT params.")
        return False
    if (contact_founders and not 0 < int(max_founders_to_contact)) or (contact_founders and len(founder_messages)) == 0:
        print("GET_COFOUNDER: Invalid founders contact setup.")
        return False
    if len(shared_interests) == 0 or shared_interests[0] == "" or (len(shared_interests) != len(founder_messages)):
        print("GET_COFOUNDER: Invalid shared interests.")
        return False
    if email_from == "" or email_from_password == "" or email_to == "":
        print("GET_COFOUNDER: Invalid email setup.")
        return False

    return True

def log_into_account(driver):
    """
    Log into a YC account using provided WebDriver. Returns True if login successful, else False.
    """
    sign_in = SignIn(driver)

    if not sign_in.go_to_sign_in() or not sign_in.sign_in():
        print("GET_COFOUNDER: Failed to navigate to sign-in page or log in.")
        log_message(None, "Failed to navigate to sign-in page or log in.")
        return False

    my_profile = MyProfile(driver)
    hit_limit = my_profile.check_dashboard_weekly_limit_reached()
    search_after_limit = os.getenv("SEARCH_WHEN_LIMIT_REACHED", "false").lower() == "true"

    if hit_limit and not search_after_limit: 
        print("GET_COFOUNDER: Hit the weekly limit for cofounder matching.")
        log_message(True, None)
        return False
    return True

def find_cofounders(driver):
    """
    Search and contact cofounders.
    """
    cofounder_scout = Scout(driver)
    cofounder_scout.find_cofounders()

def log_message(hit_weekly_limit, bot_error):
    email_logging = EmailLogging() 
    email_logging.log_report_to_email(hit_weekly_limit, bot_error, None, None, None, None)

def correct_execution_time():
    # Get the target time from the environment variable
    target_time_str = os.getenv('TARGET_TIME_UTC', '')
    if not target_time_str or target_time_str == '':
        return True

    target_time = datetime.strptime(target_time_str, '%H:%M').time()

    # Get the wiggle room from the environment variable (default to 0 if not set)
    wiggle_room_minutes = int(os.getenv('TARGET_TIME_WIGGLE_ROOM', '0'))

    # Get the current UTC time
    current_time_utc = datetime.now(timezone.utc)

    # Calculate the time window
    start_time = (datetime.combine(current_time_utc.date(), target_time) - timedelta(minutes=wiggle_room_minutes)).time()
    end_time = (datetime.combine(current_time_utc.date(), target_time) + timedelta(minutes=wiggle_room_minutes)).time()

    # Check if the current time is within the wiggle room window
    if start_time <= current_time_utc.time() <= end_time:
        return True
    
    return False

def main():
    """
    Main execution routine.
    """
    if not correct_execution_time():
        print("Cannot run at this time.")
        return

    if not check_yc_creds():
        return
    
    if not check_general_vars():
        return

    print("GET_COFOUNDER: Setting up the Chrome driver...")
    driver = setup_chrome_driver()
    try:
        driver.maximize_window() 
        print("GET_COFOUNDER: Navigating to YC's website...")
        driver.get(CONSTANTS.BASE_URL)
        utils.random_long_sleep()

        print("GET_COFOUNDER: Logging in...")
        login_output = log_into_account(driver)
        if not login_output:
            return

        print("GET_COFOUNDER: Starting the cofounder search...")
        find_cofounders(driver)
    except SystemExit as e:
        print("GET_COFOUNDER: Exited peacefully.")
    except Exception as e:
        print(f"GET_COFOUNDER: An error occurred: {e}")
        log_message(None, str(e))
    finally:
        driver.quit()

if __name__ == '__main__':
    load_dotenv()
    main()