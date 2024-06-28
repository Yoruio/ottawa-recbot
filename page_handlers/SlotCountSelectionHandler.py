from bs4 import BeautifulSoup as bs

from lib.utils import page_actions, PageRequest, PageHandler

@page_actions.add_handler("SlotCountSelection")
class SlotCountSelectionHandler(PageHandler):
    def handle_page(self, page_text, num_people, **kwargs) -> PageRequest:
        soup = bs(page_text, 'html.parser')

        form = soup.find('form')
        form_inputs = form.find_all('input')
        
        filled_form = dict()
        for form_input in form_inputs:
            filled_form[form_input['name']] = form_input['value']
        filled_form['ReservationCount'] = num_people

        print(f"SlotCountSelection form: {filled_form}")

        command_to_send = 'SubmitSlotCount'
        return PageRequest(f'/rcfs/richcraftkanata/ReserveTime/{command_to_send}?culture=en', 'POST', filled_form)