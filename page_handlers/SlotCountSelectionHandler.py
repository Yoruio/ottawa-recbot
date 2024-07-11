from lib.utils import page_actions, PageHandler, HandlerResponse
import lib.utils as utils

@page_actions.add_handler("SlotCountSelection")
class SlotCountSelectionHandler(PageHandler):
    def handle_page(self, driver, num_people, **kwargs) -> HandlerResponse:
        input_values = {
            "ReservationCount": num_people
        }

        utils.fill_inputs(driver.find_elements("xpath", f"//input"), input_values)

        button = driver.find_element("xpath", f"//button[@id='submit-btn']")
        button.click()

        return HandlerResponse(False, None)