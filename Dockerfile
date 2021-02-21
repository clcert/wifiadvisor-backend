FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10
EXPOSE 8000
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt