FROM python:3.7-alpine

ENV APP_HOME="/cyprety-rental-bot"

COPY requirements/ /requirements/

RUN pip3 install --upgrade pip

RUN apk add --virtual .build-deps gcc libc-dev \
    && pip install -r requirements/requirements.txt \
    && apk del .build-deps gcc libc-dev

WORKDIR ${APP_HOME}
COPY . ${APP_HOME}

CMD ["python", "-m", "app"]
