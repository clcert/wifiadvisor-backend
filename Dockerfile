FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10
EXPOSE 8000
COPY . /app
WORKDIR /app
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps