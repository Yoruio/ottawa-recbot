from lib.utils import page_actions, PageHandler, Email, HandlerResponse

@page_actions.add_handler("ConfirmationPage")
class ConfirmationPageHandler(PageHandler):
    def handle_page(self, **kwargs) -> HandlerResponse:
        return HandlerResponse(True, None)