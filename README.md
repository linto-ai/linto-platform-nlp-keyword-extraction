The repository contains project template to develop LinTO micro-services.

The files are annotated with field to replace using the TBR (To be replaced) keyword. Use the search function to locate values to replace.

Folder structure is as followed:
* `celery_app` contains celery related files for connectivity, registration and the task definition.
* `document` contains the swagger definition file.
* `http_server` contains http serving files, centered around API definition in `ingress.py`
* `TBR_service_type` is designed to host processing files.


# LINTO-PLATFORM-MYSERVICE
*Description of the service purpose.*

## Table of content
* [Prerequisites](#pre-requisites)
* [Deploy](#deploy)
  * [HTTP](#http-api)
  * [MicroService](#micro-service)
* [Usage](#usages)
  * [HTTP API](#http-api)
    * [/healthcheck](#healthcheck)
    * [/serviceroute](#serviceroute) TBR
    * [/docs](#docs)
  * [Using celery](#using-celery)

* [License](#license)
***

## Pre-requisites

*Any prerequisites for the service to work such as models, infrastructure, hardware, ...*

### Docker
The *service* requires docker up and running.

### (micro-service) Service broker
The *service* only entry point in job mode are tasks posted on a REDIS message broker using [Celery](https://github.com/celery/celery). 

## Deploy
*The service* can be deployed two different ways:
* As a standalone *service* through an HTTP API.
* As a micro-service connected to a task queue.

**1- First step is to build the image:**

```bash
git clone [TBR-PUBLIC REPOSITORY]
cd [TBR-FOLDER]
docker build . -t [TBR-IMAGE NAME]
```

or 
```bash
docker pull [TBR - REGISTRY URL]
```

**2- Additional steps**

*Step description*

### HTTP

**1- Fill the .env**
```bash
cp .env_default_http .env
```

Fill the .env with your values.

**Parameters:**
| Variables | Description | Example |
|:-|:-|:-|
| VARIABLE NAME | Variable description | exemple (default) |

**2- Run with docker**

```bash
docker run --rm \
-v [TBR-HOST LOCATION]:[TBR-CONTAINER LOCATION] \
-p HOST_SERVING_PORT:80 \
--env-file .env \
[TBR- IMAGE NAME]
```

This will run a container providing an http API binded on the host HOST_SERVING_PORT port.


### Micro-service
>*Service* can be deployed as a microservice. Used this way, the container spawn celery workers waiting for punctuation tasks on a dedicated task queue.
>*Service* in task mode requires a configured REDIS broker.

You need a message broker up and running at MY_SERVICE_BROKER. Instance are typically deployed as services in a docker swarm using the docker compose command:

**1- Fill the .env**
```bash
cp .env_default_task .env
```

Fill the .env with your values.

**Parameters:**
| Variables | Description | Example |
|:-|:-|:-|
| SERVICES_BROKER | Service broker uri | redis://my_redis_broker:6379 |
| BROKER_PASS | Service broker password (Leave empty if there is no password) | my_password |
| QUEUE_NAME | (Optionnal) overide the generated queue's name (See Queue name bellow) | my_queue |
| SERVICE_NAME | Service's name | punctuation-ml |
| LANGUAGE | Language code as a BCP-47 code | en-US or * or languages separated by "\|" |
| MODEL_INFO | Human readable description of the model | "Bert based model for french punctuation prediction" | 
| CONCURRENCY | Number of worker (1 worker = 1 cpu) | >1 |

> Do not use spaces or character "_" for SERVICE_NAME or language.

**2- Fill the docker-compose.yml**

`#docker-compose.yml`
```yaml
version: '3.7'

services:
  [TBR-SERVICE NAME]:
    image: [TBR- IMAGE NAME]
    volumes:
      - [TBR-HOST LOCATION]:[TBR-CONTAINER LOCATION]
    env_file: .env
    deploy:
      replicas: 1
    networks:
      - your-net

networks:
  your-net:
    external: true
```

**3- Run with docker compose**

```bash
docker stack deploy --resolve-image always --compose-file docker-compose.yml your_stack
```

**Queue name:**

By default the service queue name is generated using SERVICE_NAME and LANGUAGE: `[TBR-SERVICE TYPE]_{LANGUAGE}_{SERVICE_NAME}`.

The queue name can be overided using the QUEUE_NAME env variable. 

**Service discovery:**

As a micro-service, the instance will register itself in the service registry for discovery. The service information are stored as a JSON object in redis's db0 under the id `service:{HOST_NAME}`.

The following information are registered:

```json
{
  "service_name": $SERVICE_NAME,
  "host_name": $HOST_NAME,
  "service_type": "[TBR-SERVICE TYPE]",
  "service_language": $LANGUAGE,
  "queue_name": $QUEUE_NAME,
  "version": "1.2.0", # This repository's version
  "info": "This specific service version does something",
  "last_alive": 65478213,
  "concurrency": 1
}
```

## Usages

### HTTP API

#### /healthcheck

Returns the state of the API

Method: GET

Returns "1" if healthcheck passes.

#### /[TBR- ROUTE NAME]

[TBR- SERVICE NAME] API

* Method: POST
* Response content: text/plain or application/json
* Body: A json object structured as follows:

*Describe input and outputs with exemples*

#### /docs
The /docs route offers a OpenAPI/swagger interface. 

### Using Celery

[TBR- SERVICE NAME] worker accepts celery tasks with the following arguments:

*Describes expected inputs*

#### Return format

*describes expected outputs*

## Test
### Curl
*Add a curl exemple of http request*

## License
This project is developped under the AGPLv3 License (see LICENSE).
