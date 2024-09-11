# Ottawa Recbot
This is a simple but extensible python script to reserve drop-in spots in City of Ottawa
recreation centers.

## Features
 - Fully configurable
 - Automatic checking of email for confirmation codes
 - Reloads page until time slots are available
 - Saves screenshots of reservation confirmations available after reservation is created
 - Handles multiple reservations in parallel
 - Easily handle new pages with extensible page handler system

## Usage
1. Clone locally: ```git clone git@github.com:Yoruio/ottawa-recbot.git```
2. Enter repo: ```cd ottawa-recbot```
3. Copy activities.example.json and .env.example to activities.json and .env respectively
4. Fill in newly copied files
5. (Optional) Create python venv:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```
6. Install requirements: ```pip install -r requirements.txt```
7. Run bot: ```python bot.py```

### Filling in data files
#### activities.json
activities.json is a json file containing a list of objects with the following fields:
| Field name | Description |
| ---------- | ----------- |
|   domain   | Main domain name for reservation system. This is used as the `domain` variable in main_page. Should not need to be changed. |
|  main_page | Full URL to reservation page of specific location. Can use `domain` and `location_id` variables. |
|  location  | Location ID of specific location. This is used as the `location_id` variable in main_page. |
|  activity  | Activity, exactly as written on the reservation page. (case sensitive) |
| num_people | Number of people to reserve for. This must be over 0 and under the maximum amount of people allowed by the reservation system. |
|   weekday  | Weekday of requested timeslot. Weekdays start on Monday as 0, Tuesday as 1, etc. |
|  time_hour | Hour of requested timeslot, in 24 hr time format |
| time_minute | Minute of requested timeslot. Only put 1 digit if value is between 0 and 9. |
| phone_number | Phone number to make reservation under. |
| email_address | Email address to make reservation under. |
|    name    | Name to make reservation under. |

#### .env
The .env file contains the required information to access and check emails.
| Field name | Description |
| ---------- | ----------- |
| 