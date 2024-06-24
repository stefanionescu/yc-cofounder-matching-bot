import os
import sys
import sendgrid
import constants as CONSTANTS
from dotenv import load_dotenv
from sendgrid.helpers.mail import Mail, Email, To, Content

class EmailLogging():
    def __init__(self):
        load_dotenv()

    def send_email(self, report):
        if not report:
            print("LOGGING: Cannot email a null report.")
            sys.exit(0)

        sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        from_email = Email(os.getenv("EMAIL_FROM"))
        to_email = To(os.getenv("EMAIL_TO"))
        subject = CONSTANTS.REPORT_TITLE
        content = Content("text/plain", str(report))
        mail = Mail(from_email, to_email, subject, content)

        # Get a JSON-ready representation of the Mail object
        mail_json = mail.get()

        # Send an HTTP POST request to /mail/send
        response = sg.client.mail.send.post(request_body=mail_json)

        if response.status_code and (str(response.status_code) == "200" or str(response.status_code) == "202"):
            print("LOGGING: Report sent!")
        else:
            print("LOGING: Failed to send the report")

    def log_report_to_email(
            self, 
            hit_weekly_limit, 
            bot_error, 
            skipped_cities, 
            contacted_founders,
            saved_founders,
            skipped_founders
        ):
        print("LOGGING: Creating the report...")

        report = self.create_scraping_report(
            hit_weekly_limit, 
            bot_error, 
            skipped_cities, 
            contacted_founders,
            saved_founders,
            skipped_founders
        )

        self.send_email(report)

    def create_scraping_report(
            self, 
            hit_weekly_limit, 
            bot_error, 
            skipped_cities, 
            contacted_founders,
            saved_founders,
            skipped_founders
        ):
        if skipped_cities is not None and not isinstance(skipped_cities, list):
            print("LOGGING: Invalid skipped_cities var.")
            sys.exit(0)

        report = CONSTANTS.REPORT_INTRO

        if hit_weekly_limit:
            report += CONSTANTS.REPORT_WEEKLY_LIMIT_REACHED
        
        if bot_error and bot_error != "":
            report += CONSTANTS.REPORT_BOT_ERROR.format(bot_error=bot_error)
        
        if skipped_cities and len(skipped_cities) > 0:
            all_cities = ""
            if len(skipped_cities) == 1:
                all_cities = skipped_cities[0]
            else:
                all_cities = "; ".join(skipped_cities)
            report += CONSTANTS.REPORT_CITIES_SKIPPED.format(skipped_cities=all_cities)

        if contacted_founders:
            report += CONSTANTS.REPORT_PROFILES_CONTACTED.format(contacted_founders=contacted_founders)

        if saved_founders:
            report += CONSTANTS.REPORT_PROFILES_SAVED.format(saved_founders=saved_founders)

        if skipped_founders:
            report += CONSTANTS.REPORT_PROFILES_SKIPPED.format(skipped_founders=skipped_founders)

        if len(report) == len(CONSTANTS.REPORT_INTRO):
            report += CONSTANTS.REPORT_NO_DATA

        report += CONSTANTS.REPORT_END
        return report