from bs4 import BeautifulSoup as bs
import re

from lib.utils import page_actions, PageRequest, PageHandler

@page_actions.add_handler("Home")
class HomeHandler(PageHandler):
    def handle_page(self, page_text, activity, **kwargs) -> PageRequest:
        print("In home page handler")
        print('Parsing page')
        soup = bs(page_text, 'html.parser')
        links = soup.find_all('a')
        next_page = ""
        for link in links:
            if link.find(string=re.compile(activity)):
                next_page = link['href']
                break
        else:
            # TODO: logging instead of print
            print(f"Activity [{activity}] link not found on main page")
            return None
        next_page_request = PageRequest(next_page, "GET")

        return next_page_request