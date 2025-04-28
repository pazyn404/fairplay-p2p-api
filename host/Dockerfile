FROM python:3.11-slim

WORKDIR /app

COPY dev/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001
CMD ["flask", "run"]
