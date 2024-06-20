import os
import sys
from yagmail import SMTP
import constants as CONSTANTS
from dotenv import load_dotenv

class Logging():
    def __init__(self):
        load_dotenv()

    def log_report_to_email(self, report):
        if not report:
            print("LOGGING: Cannot email a null report.")
            return
        yag = SMTP(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_FROM_PASSWORD"))
        yag.send(to = os.getenv("EMAIL_TO"), subject = CONSTANTS.REPORT_TITLE, contents = report.strip())

    def log_report_to_email_and_quit(
            self, 
            hit_weekly_limit, 
            bot_error, 
            skipped_cities, 
            contacted_founders, 
            contacted_founders_breakdown, 
            saved_founders, 
            saved_founders_breakdown,
            skipped_founders
        ):
        report = self.create_scraping_report(
            hit_weekly_limit, 
            bot_error, 
            skipped_cities, 
            contacted_founders, 
            contacted_founders_breakdown, 
            saved_founders, 
            saved_founders_breakdown, 
            skipped_founders
        )
        self.log_report_to_email(report)
        sys.quit("Quitting...")

    def create_scraping_report(
            self, 
            hit_weekly_limit, 
            bot_error, 
            skipped_cities, 
            contacted_founders, 
            contacted_founders_breakdown, 
            saved_founders,
            saved_founders_breakdown,
            skipped_founders
        ):
        if not isinstance(skipped_cities, list):
            print("LOGGING: Invalid skipped_cities var.")
            sys.quit("Quitting...")

        report = CONSTANTS.REPORT_INTRO

        if hit_weekly_limit:
            report += CONSTANTS.REPORT_WEEKLY_LIMIT_REACHED
            report += CONSTANTS.REPORT_END
            return report
        
        if bot_error:
            report += CONSTANTS.REPORT_BOT_ERROR.format(bot_error=bot_error)
            report += CONSTANTS.REPORT_END
            return report
        
        if skipped_cities:
            all_cities = ", ".join(skipped_cities)
            report += CONSTANTS.REPORT_CITIES_SKIPPED.format(skipped_cities=all_cities)

        if contacted_founders and contacted_founders_breakdown:
            if not isinstance(contacted_founders_breakdown, dict):
                print("LOGGING: Invalid contacted_founders_breakdown var.")
                sys.quit("Quitting...")
            
            formatted_breakdown = [f"{key}: {value}" for key, value in contacted_founders_breakdown.items()]
            all_contacted_founders = ", ".join(formatted_breakdown)

            report += CONSTANTS.REPORT_PROFILES_CONTACTED(contacted_founders=contacted_founders, contacted_founders_breakdown=all_contacted_founders)

        if saved_founders and saved_founders_breakdown:
            if not isinstance(saved_founders_breakdown, dict):
                print("LOGGING: Invalid saved_founders_breakdown var.")
                sys.quit("Quitting...")
            
            formatted_breakdown = [f"{key}: {value}" for key, value in saved_founders_breakdown.items()]
            all_saved_founders = ", ".join(formatted_breakdown)

            report += CONSTANTS.REPORT_PROFILES_SAVED(saved_founders=saved_founders, saved_founders_breakdown=all_saved_founders)

        if skipped_founders:
            report += CONSTANTS.REPORT_PROFILES_SKIPPED.format(skipped_founders=skipped_founders)

        report += CONSTANTS.REPORT_END
        return report