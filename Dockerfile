FROM python:3.12-slim

WORKDIR /mailbot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements
COPY .env.example .env
CMD ["python", "script.py"]