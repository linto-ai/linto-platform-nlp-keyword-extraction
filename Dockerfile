FROM python:3.10
LABEL maintainer="iharrando@linagora.com"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        nano \
        git \
        zlib1g-dev \
        libtool \
        pkg-config \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# Install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    python3 -m spacy download en_core_web_sm

WORKDIR /usr/src/app

COPY keyword_extraction /usr/src/app/keyword_extraction
COPY celery_app /usr/src/app/celery_app
COPY http_server /usr/src/app/http_server
COPY document /usr/src/app/document
COPY docker-entrypoint.sh wait-for-it.sh healthcheck.sh ./

ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app/keyword_extraction"

HEALTHCHECK CMD ./healthcheck.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
