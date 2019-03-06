From python:3.7.2-alpine3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update
RUN apk add python3-dev postgresql-dev gcc linux-headers libc-dev

WORKDIR /usr/src/app/

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]