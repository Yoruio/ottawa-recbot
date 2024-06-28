from bs4 import BeautifulSoup as bs

from lib.utils import page_actions, PageRequest

@page_actions.add_handler("SlotCountSelection")
# Return next_page pageRequest
def slot_count_selection_handler(page_text, num_people, **kwargs) -> PageRequest:
    print("In slot count selection handler")
    print('Parsing page')
    soup = bs(page_text, 'html.parser')
    form = soup.find('form')
    form_inputs = form.find_all('input')
    filled_form = dict()
    for form_input in form_inputs:
        filled_form[form_input['name']] = form_input['value']
    filled_form['ReservationCount'] = num_people
    print(filled_form)
    command_to_send = 'SubmitSlotCount'
    return PageRequest(f'/rcfs/richcraftkanata/ReserveTime/{command_to_send}?culture=en', 'POST', filled_form)