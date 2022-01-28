FROM python:3.9
LABEL maintainer="rbaraglia@linagora.com"

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
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app

COPY disfluency /usr/src/app/disfluency
COPY celery_app /usr/src/app/celery_app
COPY http_server /usr/src/app/http_server
COPY document /usr/src/app/document
COPY docker-entrypoint.sh wait-for-it.sh healthcheck.sh ./

ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app/disfluency"

HEALTHCHECK CMD ./healthcheck.sh

ENTRYPOINT ["./docker-entrypoint.sh"]