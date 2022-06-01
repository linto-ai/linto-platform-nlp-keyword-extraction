# LINTO-PLATFORM-NLP-KEYWORD-EXTRACTION
This repository is for building a Docker image for LinTO's NLP service: Keyword Extraction on the basis of linto-platform-nlp-core, can be deployed along with LinTO stack or in a standalone way (see Develop section in below).

## Pre-requisites


### Docker
The transcription service requires docker up and running.

### (micro-service) Service broker and shared folder
The microservice only entry point in job mode are tasks posted on a message broker. Supported message broker are RabbitMQ, Redis, Amazon SQS.
On addition, as to prevent large audio from transiting through the message broker, STT-Worker use a shared storage folder.

## Deploy linto-platform-nlp-keyword-extraction
linto-platform-nlp-keyword-extraction can be deployed two ways:
* As a standalone keyword extraction service through an HTTP API.
* As a micro-service connected to a message broker.

```bash
git clone https://github.com/linto-ai/linto-platform-nlp-keyword-extraction.git
cd linto-platform-nlp-keyword-extraction
docker build . -t linto-platform-nlp-keyword-extraction:latest
```

### HTTP API

```bash
docker run --rm \
-p HOST_SERVING_PORT:80 \
--env SERVICE_MODE=http \
--env CONCURRENCY=10 \
linto-platform-nlp-keyword-extraction:latest
```

This will run a container providing an http API binded on the host HOST_SERVING_PORT port.

**Parameters:**
| Variables | Description | Example |
|:-|:-|:-|
| HOST_SERVING_PORT | Host serving port | 80 |
| CONCURRENCY | Number of worker | 4 |

### Micro-service within LinTO-Platform stack
>LinTO-platform-nlp-keyword-extraction can be deployed within the linto-platform-stack through the use of linto-platform-services-manager. Used this way, the container spawn celery worker waiting for disfluency task on a message broker.
>LinTO-platform-keyword-extraction in task mode is not intended to be launch manually.
>However, if you intent to connect it to your custom message's broker here are the parameters:

You need a message broker up and running at MY_SERVICE_BROKER.

```bash
docker run --rm \
--env SERVICES_BROKER=MY_SERVICE_BROKER \
--env BROKER_PASS=MY_BROKER_PASS \
--env SERVICE_MODE=task \
--env CONCURRENCY=10 \
linto-platform-nlp-keyword-extraction:dev
```

**Parameters:**
| Variables | Description | Example |
|:-|:-|:-|
| SERVICES_BROKER | Service broker uri | redis://my_redis_broker:6379 |
| BROKER_PASS | Service broker password (Leave empty if there is no password) | my_password |
| CONCURRENCY | Number of worker (1 worker = 1 cpu) | [ 1 -> numberOfCPU] |

## Usages

### HTTP API

#### /healthcheck

Returns the state of the API

Method: GET

Returns "1" if healthcheck passes.

#### /keyword-extraction

Keyword Extraction API

* Method: POST
* Response content: application/json
* Text: The text to process
* Method: "frequency", "textrank", or "topicrank"


#### /docs
The /docs route offers a OpenAPI/swagger-ui interface. 

### Through the message broker

Worker accepts requests with the following arguments:
```text: str, language: str```

* <ins>text</ins>: Input text
* <ins>method</ins>: Algorithm to compute the Keywords

#### Return format
A JSON object containing the keywords as keys and their scores as values.


## Test

### Curl
You can test you http API using curl:

```
curl -X POST "http://SERVICE:PORT/keyword_extraction" -H  "accept: text/plain" -H  "Content-Type: application/json" -d "{  \"text\": \"Your text here.\", \"method\": \"topicrank\" }"
```


## License
This project is developped under the AGPLv3 License (see LICENSE).
