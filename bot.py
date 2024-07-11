import os
import pkgutil
from selenium import webdriver
from selenium_stealth import stealth
import time
import json
import threading
import traceback

from lib.utils import page_actions, TimeSlotNotAvailable
import importlib

# Dynamically import all page handlers
page_handlers_dir = 'page_handlers'
page_handlers_path = f"{os.path.dirname(os.path.realpath(__file__))}/{page_handlers_dir}"
for loader, module_name, _ in pkgutil.walk_packages([page_handlers_path]):
    importlib.import_module(f"page_handlers.{module_name}")

# TODO: use logging module instead of print statements
def register(
        location: str,
        activity: str,
        num_people: str,
        weekday: int,
        time_hour: int,
        time_minute: int,
        phone_number: str,
        email_address: str,
        name: str,
        domain = "https://reservation.frontdesksuite.ca",
        main_page = "{domain}/rcfs/{location_id}/",
        task_id = 0
    ):
    local_kwargs = locals()

    options = webdriver.ChromeOptions()
    # options.add_argument("start-maximized")
    # options.add_argument("--headless")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    
    driver.get(main_page.format(domain = domain, location_id = location))
    time.sleep(0.5)
    while True:
        current_url = driver.current_url
        try:
            page_handler = page_actions.get_handler(current_url)
        except NotImplementedError as e:
            print(e)
            break
        
        try:
            resp = page_handler().handle_page(
                driver = driver,
                **local_kwargs
            )
        except TimeSlotNotAvailable as e:
            print(e)
            break
        except Exception:
            print(traceback.format_exc())
            break

        if resp.is_terminal:
            print("Terminal page reached.")
            break
        if resp.new_kwargs is not None:
            local_kwargs.update(resp.new_kwargs)

    time.sleep(1)
    driver.get_screenshot_as_file(f'./result-{task_id}.png')

        
def main():
    with open('./activities.json', 'r') as activities:
        activities_list = json.loads(activities.read())
    
    tasks = []
    task_id = 0
    if type(activities_list) != list:
        print("JSON is not formatted as a list")
        return
    for activity in activities_list:
        if type(activity) != dict:
            print("JSON activity list items must all be objects")
            return
        activity['task_id'] = task_id
        task_id += 1
        tasks.append(threading.Thread(target=register, kwargs=activity))

    for task in tasks:
        task.start()
    for task in tasks:
        task.join()

if __name__ == "__main__":
   main()