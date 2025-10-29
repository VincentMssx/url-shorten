FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get -y install gcc libpq-dev

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api /app/api

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn api.app.main:app --host 0.0.0.0 --port 8000"]