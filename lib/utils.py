from typing import NamedTuple, Callable
import re
from abc import ABC, abstractmethod

class PageRequest(NamedTuple):
    url: str = None
    method: str = None
    files: dict = None
    data: dict = None

class PageHandler(ABC):
    @abstractmethod
    def handle_page(self, **kwargs) -> PageRequest:
        """Function to handle page.
            Any required kwargs should be explicitly defined, with 
            **kwargs as a catchall at the end.

        Returns:
            PageRequest: Request for next page to retrieve
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
        def decorator(handler: PageHandler) -> PageHandler:
            self.page_actions[url_substring] = handler()
            return handler
        return decorator
    
    def get_handler(self, url: str) -> Callable:
        """Get corresponding handler for given URL

        Args:
            url (str): URL of page to match handlers to

        Raises:
            NotImplementedError: If no matching handlers have been registered
            ValueError: If multiple matching handlers have been registered

        Returns:
            Callable: Corresponding handler for given URL
        """
        matching_pages = [page_substr for page_substr in self.page_actions.keys() if page_substr in re.split('/|\?', url)]

        if len(matching_pages) == 1:
            return self.page_actions[matching_pages[0]]
        elif len(matching_pages) == 0:
            print("No matches found")
            raise NotImplementedError(f"No handlers match for url: {url}")
        else:
            raise ValueError(f"Multiple matching handlers: {matching_pages} for url: {url}")

page_actions = PageActions()

