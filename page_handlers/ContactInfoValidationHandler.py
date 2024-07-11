from lib.utils import page_actions, PageHandler, Email, HandlerResponse
import lib.utils as utils
import time
import os
from dotenv import load_dotenv

EMAIL_BOT = False

@page_actions.add_handler("ContactInfoValidation")
class ContactInfoValidationHandler(PageHandler):
    def handle_page(self, driver, to_email, **kwargs) -> HandlerResponse:
        if not EMAIL_BOT:
            load_dotenv()
            with Email(os.getenv('EMAIL_SERVER'), os.getenv('EMAIL_USERNAME'), os.getenv('EMAIL_PASSWORD')) as mail:
                code, url = utils.get_confirmation_email(mail, to_email, 120)
                print(f'code: {code}')
                utils.fill_inputs(driver.find_elements("xpath", f"//input"), {'code': code})
                button = driver.find_element("xpath", f"//button[normalize-space()='Confirm']")
                button.click()
        else:
            # Just wait for email bot to verify
            time.sleep(5)
            return HandlerResponse(False, None)

        return HandlerResponse(True, None)