from selenium.common.exceptions import NoSuchElementException

from lib.utils import page_actions, PageHandler, HandlerResponse, ActivityNotAvailable

@page_actions.add_handler("Home")
class HomeHandler(PageHandler):
    def handle_page(self, driver, activity, **kwargs) -> HandlerResponse:
        try:
            button = driver.find_element("xpath",f"//a[@class='button no-img']/div[normalize-space()='{activity}']/..")
        except NoSuchElementException as e:
            raise(ActivityNotAvailable(f"Could not find {activity} in selected location"))
        button.click()

        return HandlerResponse(False, None)