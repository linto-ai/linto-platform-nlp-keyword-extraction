# LINTO-PLATFORM-DISFLUENCY
[Description générale]

## Pre-requisites

[Si il y a des pré-requis genre model / hardware]

### Docker
The transcription service requires docker up and running.

### (micro-service) Service broker and shared folder
The STT only entry point in job mode are tasks posted on a message broker. Supported message broker are RabbitMQ, Redis, Amazon SQS.
On addition, as to prevent large audio from transiting through the message broker, STT-Worker use a shared storage folder.

## Deploy linto-platform-disfluency
linto-platform-disfluency can be deployed three ways:
* As a standalone disfluency reduction service through an HTTP API.
* As a micro-service connected to a message broker.

```bash
git clone https://github.com/linto-ai/linto-platform-disfluency.git
cd linto-platform-disfluency
docker build . -t linto-platform-disfluency:latest
```

### HTTP API

```bash
docker run --rm \
-p HOST_SERVING_PORT:80 \
--env LANGUAGE=en_US \
--env SERVICE_MODE=http \
--env CONCURRENCY=10 \
linto-platform-disfluency:latest
```

This will run a container providing an http API binded on the host HOST_SERVING_PORT port.

**Parameters:**
| Variables | Description | Example |
|:-|:-|:-|
| HOST_SERVING_PORT | Host serving port | 80 |
| LANGUAGE | Language code as a BCP-47 code  | en-US, fr_FR, ... |
| CONCURRENCY | Number of worker | 4 |

### Micro-service within LinTO-Platform stack
>LinTO-platform-disfluency can be deployed within the linto-platform-stack through the use of linto-platform-services-manager. Used this way, the container spawn celery worker waiting for disfluency task on a message broker.
>LinTO-platform-disfluency in task mode is not intended to be launch manually.
>However, if you intent to connect it to your custom message's broker here are the parameters:

You need a message broker up and running at MY_SERVICE_BROKER.

```bash
docker run --rm \
--env SERVICES_BROKER=MY_SERVICE_BROKER \
--env BROKER_PASS=MY_BROKER_PASS \
--env LANGUAGE=en_US \
--env SERVICE_MODE=task \
--env CONCURRENCY=10 \
linto-platform-disfluency:dev
```

**Parameters:**
| Variables | Description | Example |
|:-|:-|:-|
| AM_PATH | Path to the acoustic model | /my/path/to/models/AM_fr-FR_v2.2.0 |
| LM_PATH | Path to the language model | /my/path/to/models/AM_fr-FR_v2.2.0 |
| SERVICES_BROKER | Service broker uri | redis://my_redis_broker:6379 |
| BROKER_PASS | Service broker password (Leave empty if there is no password) | my_password |
| LANGUAGE | Transcription language | en-US |
| CONCURRENCY | Number of worker (1 worker = 1 cpu) | [ 1 -> numberOfCPU] |

## Usages

### HTTP API

#### /healthcheck

Returns the state of the API

Method: GET

Returns "1" if healthcheck passes.

#### /disfluency

Transcription API

* Method: POST
* Response content: text/plain
* Text: The text to process
* Language: The text language


#### /docs
The /docs route offers a OpenAPI/swagger-ui interface. 

### Through the message broker

STT-Worker accepts requests with the following arguments:
```text: str, language: str```

* <ins>text</ins>: Input text
* <ins>language</ins>: Language

#### Return format
On a successfull transcription the returned object is a text.

## License
This project is developped under the AGPLv3 License (see LICENSE).

## Acknowlegment.
