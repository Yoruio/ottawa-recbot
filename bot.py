from bs4 import BeautifulSoup as bs
import requests
import re
import urllib
from typing import NamedTuple
import datetime

# TODO: use argparse
domain = "https://reservation.frontdesksuite.ca"
main_page = "{domain}/rcfs/{location_id}/"
location = "richcraftkanata"
activity = "Basketball - adult"
num_people = "1"
weekday = 3
time_hour = 11
time_minute = 00


page_actions = dict()

class PageRequest(NamedTuple):
    url: str = None
    method: str = None
    files: dict = None
    data: dict = None


def page_action(url_substring: str):
    def decorator(func):
        page_actions[url_substring] = func
        return func
    return decorator

def main():
    session = requests.Session()
    print(f"Parsing page: {main_page.format(domain = domain, location_id = location)}")
    response = session.request('GET', main_page.format(domain = domain, location_id = location))
    main_page_soup = bs(response.text, 'html.parser')

    # Find activity link
    links = main_page_soup.find_all('a')
    next_page = ""
    for link in links:
        if link.find(string=re.compile(activity)):
            next_page = link['href']
            break
    else:
        print(f"Activity [{activity}] link not found on main page")
        return
    
    next_page_url = urllib.parse.urljoin(domain, next_page)
    next_page_request = PageRequest(next_page_url, "GET")
    
    while True:
        # Parse next page
        next_page_request_dict = next_page_request._asdict()
        next_page_request_dict['url'] = urllib.parse.urljoin(domain, next_page_request_dict['url'])

        print(f"\nGetting page: {next_page_request_dict['url']}")
        response = session.request(**next_page_request_dict)   # TODO: handle post requests
        breakpoint()
        if response.history:
            for resp in response.history:
                if resp.is_redirect:
                    print(f"redir: {resp.status_code} | {resp.headers['location']}")
        page_url = response.url

        matching_pages = [page_substr for page_substr in page_actions.keys() if page_substr in re.split('/|\?', page_url)]

        if len(matching_pages) == 1:
            next_page_request = page_actions[matching_pages[0]](response.text)
            if next_page_request is None:
                print("Success")
                break
        elif len(matching_pages) == 0:
            print("No matches found")
            print(response.text)
            return
        else:
            print("Multiple matches found")
            return

@page_action("SlotCountSelection")
# Return next_page pageRequest
def slot_count_selection_handler(page_text):
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

@page_action("TimeSelection")
def time_selection_handler(page_text):

    # This 
    filled_form = dict()
    def selectTime(queueId, categoryId, dateTime, timeHash):
        nonlocal filled_form
        filled_form['queueId'] = queueId
        filled_form['categoryId'] = categoryId
        filled_form['dateTime'] = dateTime
        filled_form['timeHash'] = timeHash

    print("In time selection handler")
    now = datetime.datetime.now()
    date_diff = (weekday - now.weekday() + 7) % 7
    next_date = now + datetime.timedelta(days=date_diff)
    next_date = next_date.replace(second=00, minute=time_minute, hour=time_hour)
    # print(f"time = {next_date.strftime("%I:%M %p %A %B %d, %Y")}")

    # Get date expansion link
    print('Parsing page')
    soup = bs(page_text, 'html.parser')

    links = soup.find_all('a')
    ul = None
    for link in links:
        if link.find(string=re.compile(next_date.strftime("%A %B %d, %Y"))):
            ul = link.parent.find('ul', {'class': 'times-list'})
            break
    else:
        return None #TODO: throw error
    
    times = ul.find_all('li', {'class': 'time'})
    time_a = None
    for time in times:
        if time.find(string=re.compile(next_date.strftime("%I:%M %p"))):
            time_a = time.find("a")
            break
    else:
        return None #TODO: throw error

    select_time_exec = time_a['onclick'].split(';')[0]
    null = None                 # JS compatibility bs... this was a mistake... never do tihs again.
    exec(select_time_exec)      #The most convoluted weakness ever. richcraft can really screw us with this

    form = soup.find('form')
    form_inputs = form.find_all('input')
    for form_input in form_inputs:
        if form_input.has_attr('value'):
            filled_form[form_input['name']] = form_input['value']
    
    filled_form['reservationCount'] = num_people
    # kill me

    print(filled_form)
    command_to_send = 'SubmitTimeSelection'
    return PageRequest(f'/rcfs/richcraftkanata/ReserveTime/{command_to_send}?culture=en', 'POST', data = filled_form)

if __name__ == "__main__":
    main()