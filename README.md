# Description
This repository is for building a Docker image for LinTO's NLP service for Keyword and Keyphrase Extraction, which can be deployed as a task on [the LinTO NLP services stack](https://github.com/linto-ai/linto-platform-nlp-services) or as a standalone service (see Develop section in below). It is based on [the LinTO microservices template](https://github.com/linto-ai/linto-template-microservice).

Folder structure is as followed:
* `celery_app` contains celery related files for connectivity, registration and the task definition.
* `document` contains the swagger definition file.
* `http_server` contains http serving files, centered around API definition in `ingress.py`
* `keyword_extraction` contains the code related to the keyword extraction algorithms.


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

### Docker
The *service* requires docker up and running.

### (micro-service) Service broker
The *service*'s only entry point in job mode are tasks posted on a REDIS message broker using [Celery](https://github.com/celery/celery). 

## Deploy
*The service* can be deployed two different ways:
* As a standalone *service* through an HTTP API.
* As a micro-service connected to a task queue.

**1- First step is to build the image:**

```bash
git clone [PUBLIC-REPOSITORY]
cd [PUBLIC-REPOSITORY]
docker compose build
```

or 
```bash
docker pull [TBR - REGISTRY URL]
```


### HTTP


Fill the .env with your values.

**Parameters:**
| Variables | Description | Example |
|:-|:-|:-|
| SERVICES_BROKER | Service broker uri | redis://my_redis_broker:6379 |
| BROKER_PASS | Service broker password (Leave empty if there is no password) | my_password |
| QUEUE_NAME | (Optionnal) overide the generated queue's name (See Queue name bellow) | my_queue |
| SERVICE_NAME | Service's name | keyword_extraction_fr |
| SERVICE_MODE | Whether the service is launched as a task or standalone | task |
| LANGUAGE | Language code as a BCP-47 code | en-US or * or languages separated by "\|" |
| CONCURRENCY | Number of worker (1 worker = 1 cpu) | >1 |
| TOKENIZERS_PARALLELISM | Activate parallelism for tokenizers | False



**2- Run with docker**

```bash
docker run --rm \
-v [TBR-HOST LOCATION]:[TBR-CONTAINER LOCATION] \
-p HOST_SERVING_PORT:80 \
--env-file .env \
[TBR- IMAGE NAME]
```

This will run a container providing an http API binded on the host HOST_SERVING_PORT port.

> ⚠️ Not fully tested.


### Micro-service
>*Service* can be deployed as a microservice. Used this way, the container spawn celery workers waiting for keyword extraction tasks on a dedicated task queue.
>*Service* in task mode requires a configured REDIS broker.

You need a message broker up and running at MY_SERVICE_BROKER. Instance are typically deployed as services in a docker swarm using the docker compose command:

**1- Fill the .env**

Fill the .env with your values.

**Parameters:**
| Variables | Description | Example |
|:-|:-|:-|
| SERVICES_BROKER | Service broker uri | redis://my_redis_broker:6379 |
| BROKER_PASS | Service broker password (Leave empty if there is no password) | my_password |
| QUEUE_NAME | (Optionnal) overide the generated queue's name (See Queue name bellow) | my_queue |
| SERVICE_NAME | Service's name, uniquely identifies the task | keyword_extraction_fr |
| SERVICE_MODE | Whether the service is launched as a task or standalone | task |
| LANGUAGE | Language code as a BCP-47 code | en-US or * or languages separated by "\|" |
| CONCURRENCY | Number of worker (1 worker = 1 cpu) | >1 |
| TOKENIZERS_PARALLELISM | Activate parallelism for tokenizers | False


**2- Fill the docker-compose.yml**

`#docker-compose.yml`
```yaml
version: '3.7'

services:
  keyword_extraction:
    build: .
    env_file: .env
    deploy:
      replicas: 1
    networks:
      - linto-net

networks:
  linto-net:
    external: true
```

**3- Run with docker compose**

```
docker compose build
docker compose up
```

**Queue name:**

By default the service queue name is generated using SERVICE_NAME and LANGUAGE: `keyword_extraction_{LANGUAGE}_{SERVICE_NAME}`.

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

### Request
When this service is deployed as a task on the NLP services stack (hosted at `[HOST]` on port `[PORT]`), it expects the following request: 

```python
import requests

url = "[HOST]:[POST]"
headers = {"accept":"application/json"}

data = {
        "documents": ["Document 1", "Document 2"],
        "nlpConfig": { "keywordExtractionConfig": 
                          { 
                            "enableKeywordExtraction": True, 
                            "serviceName": "keyword_extraction_fr",
                            "method": "[METHOD]",
                            "methodConfig":
                              {
                                "configParameter1": "value",
                                "configParameter2": "value",
                                # ..
                              }
                          },
                     },
       }

job_id = requests.post(url+'/nlp', json=data, headers = headers).json()['jobid']

job = requests.get(url+"/job/"+jobid).json()

keywords = requests.get(url+"/results/"+job['result_id'], headers = headers).json()
```

The supported methods are listed below, as well as their method-specific configurations.

#### FreKeyBERT
A model combining frenquencies and KeyBERT:
1. Extract the most frequent n-grams (up to 3-grams) in the document
2. Filter out unlikely keywords (containing no nouns, all stopwords, not corresponding to Wikipedia article titles)
3. Remove particles from beginning of keywords
4. Fuse smaller keywords into longer ones if they're frequent enough ('open' + 'source' = 'open source')
5. Generate keyword embeddings and score them based on their similarity ti segments of text
6. Remove near duplicates using embeddings

| Config parameter | Description | Default Value |
| --- | --- | --- |
| `top_n` | Final (maximum) number of keywords extracted | Unbounded |
| `number_of_segments` | Expected number of topical segments | 10 |
| `top_candidates` | Number of final set of potential keywords to be sorted | [stopwords_fr](keyword_extraction/data/stopwords_fr) |
| `add_stopwords` | List of words to be added to the default stopword list | [] |
| `sbert_model` | SentenceBERT model name to use for embedding | `paraphrase-multilingual-MiniLM-L12-v2` |
| `verbose` | Whether or not to print out the extraction progress | False |
| `stopwords` | List of words to be used to filter out stopwords | [stopwords_fr](keyword_extraction/data/stopwords_fr) |
| `add_stopwords` | List of words to be added to the default stopword list | [] |


#### KeyBERT
Paper: [Preprint](https://www.preprints.org/manuscript/201908.0073/download/final_file)
Repo: [MaartenGr/KeyBERT](https://github.com/MaartenGr/KeyBERT)

| Config parameter | Description | Default Value |
| --- | --- | --- |
| `model_name` | SentenceBERT model name to use for embedding | `paraphrase-multilingual-MiniLM-L12-v2` |
| `keyphrase_ngram_range` | Minimum and maximum length of extracted keywords | (1, 2) |
| `stopwords` | List of words to be used to filter out stopwords | [stopwords_fr](keyword_extraction/data/stopwords_fr) |
| `add_stopwords` | List of words to be added to the default stopword list | [] |


#### TextRank
Paper: [EMNLP'04](https://aclanthology.org/W04-3252/)

| Config parameter | Description | Default Value |
| --- | --- | --- |
| `spacy_model` | SpaCy model to use for POS tagging | `fr_core_news_md` |
| `damping` | Damping parameter for the PageRank algorithm, to be kept between 0.8 and 0.9 | 0.85 |
| `steps` | NUmber of iterations for PageRank | 10 |
| `stopwords` | List of words to be used to filter out stopwords | [stopwords_fr](keyword_extraction/data/stopwords_fr) |
| `add_stopwords` | List of words to be added to the default stopword list | [] |


#### TopicRank

Paper: [IJCNLP'13](https://aclanthology.org/I13-1062/)

| Config parameter | Description | Default Value |
| --- | --- | --- |
| `spacy_model` | SpaCy model to use for POS tagging | `fr_core_news_md` |
| `phrase_count_threshold` | Minimum number of occurences for a phrase to be counted | 0 |
| `stopwords` | List of words to be used to filter out stopwords | [stopwords_fr](keyword_extraction/data/stopwords_fr) |
| `add_stopwords` | List of words to be added to the default stopword list | [] |



#### Frequencies
Simply compute

| Config parameter | Description | Default Value |
| --- | --- | --- |
| `threshold` | Minimum number of occurences a word appears in the text to be included | 1 |
| `stopwords` | List of words to be used to filter out stopwords | ['thing', 'stuff'] |
| `add_stopwords` | List of words to be added to the default stopword list | ['wow', 'yes', 'non'] |

### Return format



## License
This project is developped under the AGPLv3 License (see LICENSE).
