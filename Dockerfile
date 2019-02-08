FROM python:3.7-alpine

ENV APP_HOME="/cyprety-rental-bot"

COPY Pipfile /
COPY Pipfile.lock /

RUN pip3 install --upgrade pip && \
    pip3 install pipenv

RUN pipenv install --system --ignore-pipfile --deploy

WORKDIR ${APP_HOME}
COPY . ${APP_HOME}

CMD ["python", "-m", "app"]
