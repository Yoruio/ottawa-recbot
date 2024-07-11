import imaplib
import email
import signal
import sys
import re
import requests
import os
from dotenv import load_dotenv

from lib.utils import Email

def main():
    seen_emails = set()
    with Email(os.getenv('EMAIL_SERVER'), os.getenv('EMAIL_USERNAME'), os.getenv('EMAIL_PASSWORD')) as mail:
        mail.select('inbox')
        status, data = mail.search(None, '(FROM "noreply@frontdesksuite.com")')
        seen_emails = set(data[0].split())

        while True:
            mail.select('inbox')
            status, data = mail.search(None, '(FROM "noreply@frontdesksuite.com")')

            # Iterate through each email message and print its contents
            for num in [id for id in reversed(data[0].split()) if id not in seen_emails]:
                seen_emails.add(num)
                status, data = mail.fetch(num, '(RFC822)')
                email_message = email.message_from_bytes(data[0][1])
                print('From:', email_message['From'])
                print('Subject:', email_message['Subject'])
                print('Date:', email_message['Date'])
                body = email_message.get_payload()
                print('Body:', body)
                code = body.split('Your verification code is:')[1].strip()
                code = result = re.sub('[^0-9]','', code)
                verification_pattern = re.compile("https://ca.fdesk.click/r/[a-zA-Z0-9]+")
                url = verification_pattern.search(body).group()
                print(f'code: [{code}] url: [{url}]')
                print()
                
                requests.get(url)


if __name__ == "__main__":
    load_dotenv()
    main()
    
