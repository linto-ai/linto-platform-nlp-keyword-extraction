FROM python:3.11
LABEL maintainer="iharrando@linagora.com"
ENV PYTHONUNBUFFERED TRUE
# ENV IMAGE_NAME <----- TBR Repository name

# Common dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    ca-certificates \
    g++ \
#     openjdk-11-jre-headless \
    curl \
    wget

WORKDIR /usr/src/app

# Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    python3 -m spacy download fr_core_news_md
#    python3 -m spacy download fr_core_news_md && \
#    python3 -m spacy download en_core_web_md

# Modules
COPY celery_app /usr/src/app/celery_app
COPY http_server /usr/src/app/http_server
COPY document /usr/src/app/document
COPY keyword_extraction /usr/src/app/keyword_extraction
# COPY nlp /usr/src/app/nlp
COPY RELEASE.md ./
COPY docker-entrypoint.sh wait-for-it.sh healthcheck.sh ./

# Grep CURRENT VERSION
RUN export VERSION=$(awk -v RS='' '/#/ {print; exit}' RELEASE.md | head -1 | sed 's/#//' | sed 's/ //')

HEALTHCHECK CMD ./healthcheck.sh

ENV TEMP=/usr/src/app/tmp
ENTRYPOINT ["./docker-entrypoint.sh"]
