FROM python:3.10-alpine
LABEL authors="kalishevgeniy"

COPY . /var/lib/TaskBot
WORKDIR /var/lib/TaskBot

RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3", "main.py"]
