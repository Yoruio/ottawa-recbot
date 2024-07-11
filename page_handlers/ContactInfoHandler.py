from lib.utils import page_actions, PageHandler, HandlerResponse, timer
import lib.utils as utils

import string
import random

UNIQUE_TO_EMAIL = True

@page_actions.add_handler("ContactInfo")
class ContactInfoHandler(PageHandler):
    def handle_page(self, driver, phone_number, email_address, name, **kwargs) -> HandlerResponse:
        timer.set_start()
        if UNIQUE_TO_EMAIL:
            rand_str = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))
            split_email = email_address.split('@')
            split_email[0] += f"+{rand_str}"
            to_email = '@'.join(split_email)
        else:
            to_email = email_address
        
        input_values = {
            "PhoneNumber": phone_number,
            "Email": to_email,
            "field2021": name
        }

        input_xpath_filters = ' or '.join([f"@name = '{name}'" for name in input_values.keys()])
        
        inputs = driver.find_elements("xpath", f"//input[{input_xpath_filters}]")
        utils.fill_inputs(inputs, input_values)

        button = driver.find_element("xpath", f"//button[@id='submit-btn']")
        button.click()

        return HandlerResponse(False, {'to_email': to_email})