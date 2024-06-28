from bs4 import BeautifulSoup as bs
import re
import datetime

from lib.utils import page_actions, PageRequest, PageHandler

@page_actions.add_handler("TimeSelection")
class TimeSelectionHandler(PageHandler):
    def handle_page(self, page_text, weekday, time_minute, time_hour, num_people, **kwargs) -> PageRequest:
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
        # TODO: handle if full: Currently full days will trigger else statement. (not reliably, sometimes there are greyed out times, sometimes there are not.)
        for link in links:
            if link.find(string=re.compile(next_date.strftime("%A %B %d, %Y"))):
                ul = link.parent.find('ul', {'class': 'times-list'})
                break
        else:
            print(f"Could not find times for day {next_date.strftime('%A %B %d, %Y')}")
            # TODO: refresh until times are available
            return None # TODO: throw error
        
        times = ul.find_all('li', {'class': 'time'})
        time_a = None
        for time in times:
            if time.find(string=re.compile(next_date.strftime("%I:%M %p"))):
                time_a = time.find("a")
                break
        else:
            print(f"Could not find {next_date.strftime('%I:%M %p')} slot on date {next_date.strftime('%A %B %d, %Y')}")
            return None #TODO: throw error

        select_time_exec = time_a['onclick'].split(';')[0]
        null = None                 # JS compatibility bs... this was a mistake... never do tihs again.
        exec(select_time_exec)      # The most convoluted weakness ever. richcraft can really screw us with this

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