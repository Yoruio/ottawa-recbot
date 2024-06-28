from bs4 import BeautifulSoup as bs
import requests
import re
import urllib
import os
import pkgutil

from lib.utils import page_actions, PageRequest
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
        domain = "https://reservation.frontdesksuite.ca",
        main_page = "{domain}/rcfs/{location_id}/"
    ):
    local_kwargs = locals()
    session = requests.Session()

    # Start at landing page for rec location
    next_page_request = PageRequest(
        main_page.format(domain = domain, location_id = location),
        'GET'
    )
    while True:
        # Parse next page
        next_page_request_dict = next_page_request._asdict()
        next_page_request_dict['url'] = urllib.parse.urljoin(domain, next_page_request_dict['url'])

        print(f"\nGetting page: {next_page_request_dict['url']}")
        response = session.request(**next_page_request_dict)   # TODO: handle post requests
        if response.history:
            for resp in response.history:
                if resp.is_redirect:
                    print(f"redir: {resp.status_code} | {resp.headers['location']}")
        page_url = response.url

        page_handler = page_actions.get_handler(page_url)
        next_page_request = page_handler.handle_page(
            response.text,
            **local_kwargs
        )

        if next_page_request is None:
            print("Finsihed")
            return
        
def main():
    # TODO: Multiprocessing
    register(
        domain = "https://reservation.frontdesksuite.ca",
        main_page = "{domain}/rcfs/{location_id}/",
        location = "richcraftkanata",
        activity = "Volleyball - adult",
        num_people = "1",
        weekday = 5,
        time_hour = 11,
        time_minute = 00
    )


if __name__ == "__main__":
    main()