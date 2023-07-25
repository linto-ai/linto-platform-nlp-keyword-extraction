import os

from celery import Celery

from keyword_extraction import logger
from keyword_extraction.frekeybert import get_stop_words, get_sbert_model, get_wikipedia_titles, get_spacy_model

celery = Celery(__name__, include=["celery_app.tasks"])
service_name = os.environ.get("SERVICE_NAME")
broker_url = os.environ.get("SERVICES_BROKER")
if os.environ.get("BROKER_PASS", False):
    components = broker_url.split("//")
    broker_url = f'{components[0]}//:{os.environ.get("BROKER_PASS")}@{components[1]}'
celery.conf.broker_url = f"{broker_url}/0"
celery.conf.result_backend = f"{broker_url}/1"
celery.conf.update(result_expires=3600, task_acks_late=True, task_track_started=True)

# Queues
language = os.environ.get("LANGUAGE")
celery.conf.update(
    {
        "task_routes": {
            "keyword_extraction_task": {"queue": f"keyword_extraction_{language}"},
        }
    }
)
logger.info(
    f"Celery configured for broker located at {broker_url} with service name {service_name}"
)

# setup ?
"""
_ = get_stop_words(language)
sbert = get_sbert_model(language)
_ = get_wikipedia_titles(language)
_ = get_spacy_model(language)

print('Running S-BERT ..')
emb = sbert.encode('hello')
print('Done for "hello"!')
"""