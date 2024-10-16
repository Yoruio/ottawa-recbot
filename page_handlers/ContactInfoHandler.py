from lib.utils import page_actions, PageHandler, HandlerResponse
import lib.utils as utils

import string
import random

UNIQUE_TO_EMAIL = True
FALLBACK_NAME_INPUT_NAME = "field2021"

@page_actions.add_handler("ContactInfo")
class ContactInfoHandler(PageHandler):
    def handle_page(self, driver, phone_number, email_address, name, **kwargs) -> HandlerResponse:
        if UNIQUE_TO_EMAIL:
            rand_str = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))
            split_email = email_address.split('@')
            split_email[0] += f"+{rand_str}"
            to_email = '@'.join(split_email)
        else:
            to_email = email_address

        inputs = []
        input_values = {
            "PhoneNumber": phone_number,
            "Email": to_email
        }
        auto_find_input_names = ["PhoneNumber", "Email"]

        name_input = driver.find_elements("xpath", f"//span[contains(text(),'Name')]/ancestor::label/child::input")
        if len(name_input) == 0:
            auto_find_input_names.append(FALLBACK_NAME_INPUT_NAME)
            input_values[FALLBACK_NAME_INPUT_NAME] = name
        else:
            inputs.append(name_input[0])
            input_values[name_input[0].get_attribute("name")] = name

        input_xpath_filters = ' or '.join([f"@name = '{name}'" for name in auto_find_input_names])
        
        inputs = driver.find_elements("xpath", f"//input[{input_xpath_filters}]") + inputs
        utils.fill_inputs(inputs, input_values)

        button = driver.find_element("xpath", f"//button[@id='submit-btn']")
        button.click()

        return HandlerResponse(False, {'to_email': to_email})