FROM python:3.12-slim

WORKDIR /src

COPY .env /

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \ 
    pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["main:app", "--host", "localhost", "--port", "8000"]

