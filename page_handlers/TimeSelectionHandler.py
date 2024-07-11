import datetime
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
import time

from lib.utils import TimeSlotNotAvailable
from lib.utils import page_actions, PageHandler, HandlerResponse

import asyncio

REFRESH_IF_NOT_FOUND = True
REFRESH_IF_FULL = True
SLEEP_BETWEEN_REFRESH = 0.5

@page_actions.add_handler("TimeSelection")
class TimeSelectionHandler(PageHandler):
    def handle_page(self, driver, weekday, time_minute, time_hour, **kwargs) -> HandlerResponse:
        now = datetime.datetime.now()
        date_diff = (weekday - now.weekday() + 7) % 7
        next_date = now + datetime.timedelta(days=date_diff)
        next_date = next_date.replace(second=00, minute=time_minute, hour=time_hour)

        date_str = next_date.strftime("%A %B %-d, %Y")
        time_str = next_date.strftime('%-I:%M %p')

        try:
            times_list_expander = driver.find_element("xpath", f"//a/div[@class='date-text']/span[normalize-space()='{date_str}']/../..")
        except NoSuchElementException:
            if REFRESH_IF_NOT_FOUND:
                # Refresh page and exit if time not available yet
                driver.refresh()
                time.sleep(SLEEP_BETWEEN_REFRESH)
                return HandlerResponse(False, None)
            else:
                raise TimeSlotNotAvailable(f"No time slots found for {date_str}.")
        times_list_expander.click()

        try:
            button = driver.find_element("xpath", f"//a/div[@class='date-text']/span[normalize-space()='{date_str}']/../../following-sibling::ul[normalize-space(@class)='times-list']//span[normalize-space()='{time_str}']/..")
        except NoSuchElementException:
            if REFRESH_IF_NOT_FOUND:
                driver.refresh()
                time.sleep(SLEEP_BETWEEN_REFRESH)
                return HandlerResponse(False, None)
            else:
                raise TimeSlotNotAvailable(f"No time slots found for {time_str} on {date_str}")
        
        # Check if time is full
        if "reserved" in button.find_element("xpath", "ancestor::li").get_attribute("class"):
            if REFRESH_IF_FULL:
                driver.refresh()
                time.sleep(SLEEP_BETWEEN_REFRESH)
                return HandlerResponse(False, None)
            else:
                raise TimeSlotNotAvailable(f"Time slot for {time_str} on {date_str} is full.")

        button.click()
        
        return HandlerResponse(False, None)