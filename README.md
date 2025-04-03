# Mail to Discord messages forwarding

Simple script written due to n8n problems.

## Installation
### Clone this repository
1. Clone this repo and open it in console
2. Modify `.env.example` as specified below
3. Ensure requirements are satisfied via executing 
```
pip install -r requirements.txt
```

### Pull docker image from Dockerhub
Docker image will be provided later

## `.env` file

To use this script, you need to provide the following environment variables:

- `MAILBOX_NUMBER` – number of mailboxes to forward  
  > Note: Mailbox IDs should be in the range `[0 .. MAILBOX_NUMBER - 1]` instead of `<id>` placeholder.  

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

