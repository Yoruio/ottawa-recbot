import datetime
from selenium.common.exceptions import NoSuchElementException
import time
from sys import platform

from lib.utils import TimeSlotNotAvailable
from lib.utils import page_actions, PageHandler, HandlerResponse

REFRESH_IF_NOT_FOUND = False
RESTART_FLOW_IF_NOT_FOUND = True

REFRESH_IF_FULL = False
RESTART_FLOW_IF_FULL = True

SLEEP_BETWEEN_REFRESH = 0.5

@page_actions.add_handler("TimeSelection")
class TimeSelectionHandler(PageHandler):
    def handle_page(self, driver, weekday, time_minute, time_hour, **kwargs) -> HandlerResponse:
        now = datetime.datetime.now()
        date_diff = (weekday - now.weekday() + 7) % 7
        next_date = now + datetime.timedelta(days=date_diff)
        next_date = next_date.replace(second=00, minute=time_minute, hour=time_hour)

        if platform == "win32":
            strip_zeros_char = "#"
        else:
            strip_zeros_char = "-"
        date_str = next_date.strftime(f"%A %B %{strip_zeros_char}d, %Y")
        time_str = next_date.strftime(f'%{strip_zeros_char}I:%M %p')

        try:
            times_list_expander = driver.find_element("xpath", f"//a/div[@class='date-text']/span[normalize-space()='{date_str}']/../..")
        except NoSuchElementException:
            # Could not find date dropdown
            if REFRESH_IF_NOT_FOUND:
                # Refresh page and exit if time not available yet
                driver.refresh()
                time.sleep(SLEEP_BETWEEN_REFRESH)
                return HandlerResponse(False, None)
            elif RESTART_FLOW_IF_NOT_FOUND:
                return HandlerResponse(restart_flow=True)
            else:
                raise TimeSlotNotAvailable(f"No time slots found for {date_str}.")
        times_list_expander.click()

        try:
            button = driver.find_element("xpath", f"//a/div[@class='date-text']/span[normalize-space()='{date_str}']/../../following-sibling::ul[normalize-space(@class)='times-list']//span[normalize-space()='{time_str}']/..")
        except NoSuchElementException:
            # Could not find timeslot within date dropdown
            if REFRESH_IF_NOT_FOUND:
                driver.refresh()
                time.sleep(SLEEP_BETWEEN_REFRESH)
                return HandlerResponse(False, None)
            elif RESTART_FLOW_IF_NOT_FOUND:
                return HandlerResponse(restart_flow=True)
            else:
                raise TimeSlotNotAvailable(f"No time slots found for {time_str} on {date_str}")
        
        # Check if time is full
        if "reserved" in button.find_element("xpath", "ancestor::li").get_attribute("class"):
            if REFRESH_IF_FULL:
                driver.refresh()
                time.sleep(SLEEP_BETWEEN_REFRESH)
                return HandlerResponse(False, None)
            elif RESTART_FLOW_IF_FULL:
                return HandlerResponse(restart_flow=True)
            else:
                raise TimeSlotNotAvailable(f"Time slot for {time_str} on {date_str} is full.")

        button.click()
        
        return HandlerResponse(False, None)