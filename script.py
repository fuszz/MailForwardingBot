import os
from typing import List, Mapping
from time import sleep
from datetime import datetime
from html2text import HTML2Text
from dotenv import load_dotenv
from imap_tools import MailBox, AND, MailMessageFlags
from discord_webhook import DiscordWebhook


def establish_connection(credentials: map) -> MailBox | None: 
    try:
        connection = MailBox(credentials["mail_url"]).login(credentials["address"], credentials["password"])
        return connection
    except Exception as e:
        print(f"{datetime.now()} Error establishing connection: {e}")
        return None
 
    
def close_connection(connection) -> bool:
    try:
        connection.logout()
        return True
    except Exception as e:
        print(f"{datetime.now()} Error closing connection: {e}")
        return False
 
        
def new_emails_uids(connection: MailBox) -> List[str]:
    new_mail_uids = []
    
    try:
        for msg in connection.fetch(AND(seen=False)):
            new_mail_uids.append(msg.uid)
            print(f"{datetime.now()} New email UID: {msg.uid}")
        return new_mail_uids
    
    except Exception as e:
        print(f"{datetime.now()} Error checking for new emails: {e}")
        return []

    
def pull_emails(connection: MailBox, uids: List[str]) -> Mapping:
    pulled_emails = {}
    try:
        for msg in connection.fetch(AND(uid=uids)):
            pulled_emails[msg.uid] = {
                "subject": msg.subject,
                "from": msg.from_,
                "to": msg.to,
                "cc": msg.cc,
                "bcc": msg.bcc,
                "date": msg.date,
                "body": msg.html,
                "attachments": msg.attachments,
            }
        return pulled_emails
    
    except Exception as e:
        print(f"{datetime.now()} Error pulling emails: {e}")
        return None

def parse_html_to_md(html: str) -> str:
    html_to_md = HTML2Text()
    html_to_md.body_width = 0
    html_to_md.single_line_break = True
    return html_to_md.handle(html)

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
        markdowned_msg += f"## Treść:\n" + parse_html_to_md(str(email[m]['body']))
        if len(email[m]['attachments']) > 0:
            markdowned_msg += f"### Ten email zawiera załączniki.\n"
            for a in email[m]['attachments']:
                markdowned_msg += " - " + a.filename + " size: " + str(round(a.size / 1024, 2)) + "kB \n"
        markdowned.append(markdowned_msg)
    return markdowned

    
def send_to_discord(markdowned: List[str], uids: List[str], webhook_url: str) -> List[str]:
    sent_uids = []
    try:
        for (uid, mail) in zip(uids, markdowned):
            print("SEND: ",mail)
            webhook = DiscordWebhook(webhook_url, content=mail)
            response = webhook.execute()
            sent_uids.append(uid)
            print(f"{datetime.now()} Message {uid} sent to Discord: status code {response.status_code}")
                
    except Exception as e:
        print(f"{datetime.now()} Error sending to Discord: {e}")
    return sent_uids


def refresh_mailbox(credentials: map) -> None:
        print(f"{datetime.now()} Start processing mailbox {credentials["address"]}")
        connection = establish_connection(credentials)
        if not connection:
            print(f"{datetime.now()} Failed to establish connection.")
            print(f"{datetime.now()} Stop processing mailbox {credentials["address"]}")
            return
        
        uids = new_emails_uids(connection)
        if not uids:
            print(f"{datetime.now()} No new emails found.")
            close_connection(connection)
            print(f"{datetime.now()} Stop processing mailbox {credentials["address"]}")
            return
        
        emails = pull_emails(connection, uids)
        if len(emails) == 0:
            print(f"{datetime.now()} No emails to process.")
            close_connection(connection)
            print(f"{datetime.now()} Stop processing mailbox {credentials["address"]}")
            return
        
        markdowned = parse_email(emails)
        sent_uids = send_to_discord(markdowned, uids, credentials["webhook_url"])
    
        
        for uid in uids:
            if uid not in sent_uids:
                print(f"{datetime.now()} Email with UID {uid} was not sent.")
                connection.flag(uid, [MailMessageFlags.SEEN], False)
        close_connection(connection)
        print(f"{datetime.now()} Stop processing mailbox {credentials["address"]}")
        return
               
def main():
    print(f"{datetime.now()} Starting the script.")
    print(f"{datetime.now()} Loading environment variables.")
    if not load_dotenv():
        print(f"{datetime.now()} Failed to load environment variables.")
        print(f"{datetime.now()} Exting the script.")
        return   

    mailbox_number = int(os.environ.get("MAILBOX_NUMBER"))
    if mailbox_number is None or mailbox_number <= 0:
        print(f"{datetime.now()} Invalid mailbox number.")
        return
    
    credentials = []
                    
    for i in range(mailbox_number):
        mail_creds = {}
        mail_creds["address"] = os.environ.get(f"ADDRESS_{i}")
        mail_creds["password"] = os.environ.get(f"PASSWORD_{i}")
        mail_creds["mail_url"] = os.environ.get(f"MAIL_URL_{i}")
        mail_creds["webhook_url"] = os.environ.get(f"WEBHOOK_URL_{i}")
        credentials.append(mail_creds)    
    print(f"{datetime.now()} Loaded environment variables.")

    while True:
        for id in range(mailbox_number):
            refresh_mailbox(credentials[id])
        print(f"{datetime.now()} Sleeping for 10 minutes.")
        sleep(600)
                  

if __name__ == "__main__":
    main()
