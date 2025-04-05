FROM python:3.12-slim

WORKDIR /mailbot
COPY requirements.txt .
COPY .env.example .env
RUN pip install --no-cache-dir -r requirements.txt
COPY script.py .
CMD ["python", "-u", "script.py"]