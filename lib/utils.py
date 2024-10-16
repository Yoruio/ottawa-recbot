from typing import Callable, Type
from dataclasses import dataclass
import re
from abc import ABC, abstractmethod
import imaplib
import time
import email
import functools
from selenium import webdriver


@dataclass
class HandlerResponse():
    is_terminal: bool = False
    new_kwargs: dict = None
    restart_flow: bool = False

class PageHandler(ABC):
    @abstractmethod
    def handle_page(self, driver: webdriver.Chrome, **kwargs) -> HandlerResponse:
        """Function to handle page.
            Any required kwargs should be explicitly defined, with 
            **kwargs as a catchall at the end.
        """
        pass

class PageActions:
    """
    Class to register actions to take based on page URL
    """
    def __init__(self) -> None:
        self.page_actions = dict()

    def add_handler(self, url_substring: str) -> Callable[[PageHandler], PageHandler]:
        """Decorator to register a page handler.

        Args:
            url_substring (str): url section to match (must be between /'s in url)

        Returns:
            Callable[[PageHandler], PageHandler]: Decorator to register URL
        
        Usage:
            @page_actions.add_handler("example")
            class ExampleHandler(PageHandler):
                def handle_page(self, **kwargs):
                    pass
        """
        def decorator(handler: Type[PageHandler]) -> Type[PageHandler]:
            self.page_actions[url_substring] = handler
            return handler
        return decorator
    
    def get_handler(self, url: str) -> Type[PageHandler]:
        """Get corresponding handler for given URL

        Args:
            url (str): URL of page to match handlers to

        Raises:
            NotImplementedError: If no matching handlers have been registered
            ValueError: If multiple matching handlers have been registered

        Returns:
            Type[PageHandler]: Corresponding handler for given URL
        """
        # Get longest matching page substring from page_actions
        longest_matching_page = functools.reduce(
            lambda a, b: a if len(a) > len(b) else b, 
            filter(
                lambda page_substr: page_substr in url, self.page_actions.keys()
            ),
            ""
        )
        if not longest_matching_page:
            return NotImplementedError(f"No handlers match for url: {url}")
        return self.page_actions[longest_matching_page]

page_actions = PageActions()

class Email:
    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
    
    def __enter__(self):
        self.mail = imaplib.IMAP4_SSL(self.server)
        self.mail.login(self.username, self.password)
        return self.mail

    def __exit__(self, exc_type, exc_value, traceback):
        self.mail.close()
        self.mail.logout()

def get_confirmation_email(mail: Email, to_email: str, timeout=60) -> tuple[str, str]:
    timeout = time.time() + timeout

    while True:
        mail.select('inbox')
        _, data = mail.search(None, f'((FROM "noreply@frontdesksuite.com") (TO "{to_email}"))')

        ids = reversed(data[0].split())

        id = next(ids, None)

        if id is None:
            if time.time() > timeout:
                return None
            time.sleep(1)
        else:
            num = id
            _, data = mail.fetch(num, '(RFC822)')
            email_message = email.message_from_bytes(data[0][1])
            body = email_message.get_payload()

            code_pattern = re.compile(r"Your verification code is:\s*([0-9]+)")
            code = code_pattern.search(body).group(1)
            verification_pattern = re.compile(r"https://ca.fdesk.click/r/[a-zA-Z0-9]+")
            url = verification_pattern.search(body).group()
            print(f'code: [{code}] url: [{url}]')
            return code, url
        
def fill_inputs(inputs: list, values: dict) -> int:
    filled_fields = 0
    for input in inputs:
        input_name = input.get_attribute("name")
        if input_name in values:
            if input.get_attribute("value"):
                input.clear()
            input.send_keys(str(values[input_name]))
            filled_fields += 1

class ActivityNotAvailable(Exception):
    pass

class TimeSlotNotAvailable(Exception):
    pass

