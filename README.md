# Mail to Discord messages forwarding

Simple script written due to n8n problems that monitors your mailboxes using the IMAP protocol. It connects to the mailbox, checks for new messages, and, if any are found, forwards them to a specified Discord webhook.
By default, the interval between checks is 10 minutes, but this can be manually adjusted in the script.

## Manual installation
### Clone this repository
1. Clone this repo and open it in console
2. Modify `.env.example` as specified below
3. Ensure requirements are satisfied via executing 
```
pip install -r requirements.txt
```

## `.env` file

To use this script, you need to provide the following environment variables:

- `MAILBOX_NUMBER` – number of mailboxes to forward  

For each mailbox (replace `<id>` with the actual mailbox index):  
- `ADDRESS_<id>` – your mailbox address  
- `PASSWORD_<id>` – your mailbox password  
- `MAIL_URL_<id>` – your mailbox server URL  
- `WEBHOOK_URL_<id>` – your Discord Webhook URL (copied from Discord Server settings)  


## Usage
Execute the following command
``` 
python3 script.py
```

## Docker compose installation
1. Copy [docker-compose.yml](docker-compose.yml) file
2. Create new directory for script, i. e. `mailbot` and enter it
``` bash
mkdir mailbot && cd mailbot
```
3. Copy [`.env.example`](.env.example) file and edit it.
4. Save edited file as `.env`
5. Start container using
``` bash
docker compose up -d
```
