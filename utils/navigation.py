import constants as CONSTANTS
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class Navigation:
    def page_has_loaded(self, driver):
        return driver.execute_script("return document.readyState") == "complete"

    def navigate_with_refresh(self, driver, url, max_attempts=CONSTANTS.MAX_PAGE_RELOAD_TRIES, timeout=CONSTANTS.PAGE_LOAD_RETRY_SESSION):
        for attempt in range(max_attempts):
            try:
                print(f"NAVIGATION: Attempting to navigate to {url} (Attempt #{attempt + 1})")
                driver.get(url)
                WebDriverWait(driver, timeout).until(lambda x: self.page_has_loaded(x))
                print("NAVIGATION: Page loaded successfully.")
                return True
            except TimeoutException:
                if attempt < max_attempts - 1:
                    print(f"NAVIGATION: Page load timed out. Refreshing...")
                    driver.refresh()
                else:
                    print(f"NAVIGATION: Page at {url} failed to load after {max_attempts} attempts.")
                    return False