import os
from typing import List, Mapping
from time import sleep
from dotenv import load_dotenv
from imap_tools import MailBox, AND
from discord_webhook import DiscordWebhook

load_dotenv()

CREDENTIALS = (os.environ.get("ADDR"), os.environ.get("PASSWD"), os.environ.get("URL"))

def establish_connection() -> MailBox | None: 
    try:
        connection = MailBox(CREDENTIALS[2]).login(CREDENTIALS[0], CREDENTIALS[1])
        return connection
    except Exception as e:
        print(f"Error establishing connection: {e}")
        return None
    
def close_connection(connection: MailBox) -> bool:
    try:
        connection.logout()
        return True
    except Exception as e:
        print(f"Error closing connection: {e}")
        return False
        
def new_emails_uids(connection: MailBox, last_received_uid: str) -> List[str]:
    new_mail_uids = []
           
    
    try:
        if last_received_uid:
            connection.select("INBOX")
            connection.search(AND(seen=False, int(uid)>int(last_received_uid)))
        for msg in connection.fetch():
            new_mail_uids.append(msg.uid)
            print(f"New email UID: {msg.uid}")
        return new_mail_uids
    
    except Exception as e:
        print(f"Error checking for new emails: {e}")
        return []
    
def pull_emails(connection: MailBox, uids: List[str]) -> Mapping:
    pulled_emails = {}
    print(uids)
    try:
        for msg in connection.fetch(AND(uid=uids)):
            pulled_emails[msg.uid] = {
                "subject": msg.subject,
                "from": msg.from_,
                "to": msg.to,
                "cc": msg.cc,
                "bcc": msg.bcc,
                "date": msg.date,
                "body": msg.text,
                "attachments": msg.attachments,
            }
        return pulled_emails
    
    except Exception as e:
        print(f"Error pulling emails: {e}")
        return None

def parse_email(email: Mapping) -> List[str]:
    markdowned = []
    
    for m in email.keys():
        markdowned_msg = "# Nowa wiadomość e-mail \n"
        markdowned_msg += f"## Temat: {email[m]['subject']}\n"
        markdowned_msg += f"## Od: {email[m]['from']}\n"
        markdowned_msg += f"## Do: {email[m]['to']}\n"
        if 'CC' in email[m].keys(): markdowned_msg += f"## DW: {email[m]['cc']}\n"
        if 'BCC' in email[m].keys(): markdowned_msg += f"## Ukryte DW: {email[m]['bcc']}\n"
        markdowned_msg += f"## Data: {email[m]['date']}\n"
        markdowned_msg += f"## Treść:\n {email[m]['body']}\n"
        if len(email[m]['attachments']) > 0:
            markdowned_msg += f"### Ten email zawiera załączniki.\n"
            
        markdowned.append(markdowned_msg)
        #print(markdowned_msg)
    return markdowned
    
def send_to_discord(markdowned: List[str]) -> bool:
    for mail in markdowned:
        try:
            webhook = DiscordWebhook(os.environ.get("WEBHOOK_URL"), content=mail)
            response = webhook.execute()
            print(f"Messages sent to Discord: {response.status_code}")
            return True
        
        except Exception as e:
            print(f"Error sending to Discord: {e}")
            return False

    
def main():
    last_received_uid = None
    while True:
        connection = establish_connection()
        if not connection:
            print("Failed to establish connection.")
            continue
        
        uids = new_emails_uids(connection, last_received_uid)
        if not uids:
            print("No new emails found.")
            close_connection(connection)
            continue
        
        emails = pull_emails(connection, uids)
        close_connection(connection)
        if len(emails) == 0:
            print("No emails to process.")
            continue
        markdowned = parse_email(emails)

        if not send_to_discord(markdowned):
            print("Failed to send emails to Discord.")
            continue
        last_received_uid = uids[-1]

if __name__ == "__main__":
    main()
