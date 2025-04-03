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
        
def new_emails_uids(connection: MailBox) -> List[str]:
    new_mail_uids = []
    
    try:
        for msg in connection.fetch():
            new_mail_uids.append(msg.uid)
            print(f"New email UID: {msg.uid}")
        return new_mail_uids
    
    except Exception as e:
        print(f"Error checking for new emails: {e}")
        return []
    
def pull_emails(connection: MailBox, uids: List[str]) -> Mapping | None:
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
        print(markdowned_msg)
    return markdowned
    
def send_to_discord(markdowned: List[str]) -> bool:
    for mail in markdowned:
        webhook = DiscordWebhook(os.environ.get("WEBHOOK_URL"), content=mail)
        response = webhook.execute()

    
def main():
    connection = establish_connection()
    uids = new_emails_uids(connection)
    if not uids:
        print("No new emails found.")
        close_connection(connection)
        return
    emails = pull_emails(connection, uids)
    close_connection(connection)
    markdowned = parse_email(emails)
    send_to_discord(markdowned)
        

if __name__ == "__main__":
    main()
