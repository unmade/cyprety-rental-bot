FROM python:3.7-alpine

ENV APP_HOME="/cyprety-rental-bot"

COPY Pipfile /
COPY Pipfile.lock /

RUN pip3 install --upgrade pip \
    && pip3 install pipenv

RUN apk add --virtual .build-deps gcc libc-dev \
    && pipenv install --system --ignore-pipfile --deploy \
    && apk del .build-deps gcc libc-dev

WORKDIR ${APP_HOME}
COPY . ${APP_HOME}

CMD ["python", "-m", "app"]
