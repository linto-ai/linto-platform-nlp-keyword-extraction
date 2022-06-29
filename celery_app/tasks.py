import os
import requests
import json
from celery_app.celeryapp import celery

from keyword_extraction.preprocessing.utils import get_word_frequencies, get_textrank_topwords, get_topicrank_topwords

service_name = os.environ.get("SERVICE_NAME")

@celery.task(name=service_name)
def keyword_extraction(text: str, parameters: dict):
    """ return keywords and their weights """
    result = {}
    method = parameters["method"]

    if method == "frequencies":
        result = get_word_frequencies(text, parameters)
    elif method == "textrank":
        result = get_textrank_topwords(text, parameters)
    elif method == "topicrank":
        result = get_topicrank_topwords(text, parameters)
    else:
        raise Exception("Invalid method") 
    return result
