from lib.utils import page_actions, PageHandler, HandlerResponse

@page_actions.add_handler("Home")
class HomeHandler(PageHandler):
    def handle_page(self, driver, activity, **kwargs) -> HandlerResponse:
        button = driver.find_element("xpath",f"//a[@class='button no-img']/div[normalize-space()='{activity}']/..")
        button.click()

        return HandlerResponse(False, None)