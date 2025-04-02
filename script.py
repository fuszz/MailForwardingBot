import os
from time import sleep
from dotenv import load_dotenv
from imaplib import IMAP4_SSL
load_dotenv()

CREDENTIALS = (os.environ.get("ADDR"), os.environ.get("PASSWD"), os.environ.get("URL"))

def mailserverConnect():
    try:
        connection = IMAP4_SSL(host=CREDENTIALS[2])
        connection.login(CREDENTIALS[0], CREDENTIALS[1])
        print("Successfully logged to mail server")
        
    except Exception as e:
        print(f"Connecting or login error: {e}")
        return None
    return connection

def readMails(connection: IMAP4_SSL):
    
    try:
        connection.select()
        connection.recent()
        status, messages = connection.search(None, 'SINCE', '01-Mar-2025')
        print(f"status {status}")
        print()
        print(f"Messages {messages}")
        
        for m in messages[0].decode().split():
            print(m)
            _, data = connection.fetch(m, "(RFC822)")
            print(data)
    except Exception as e:
        print(f"An error occured while reading mails: {e}")
        
        
    
        
def main():
    
    while True:
        connection = mailserverConnect()
        readMails(connection)
        connection.close()
        connection.logout()
        sleep(5)  
        

if __name__ == "__main__":
    main()
