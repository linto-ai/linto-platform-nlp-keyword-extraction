import os
import requests
import json
from celery_app.celeryapp import celery

from keyword_extraction.preprocessing.utils import get_word_frequencies, get_textrank_topwords, get_topicrank_topwords

service_name = os.environ.get("SERVICE_NAME")

@celery.task(name=service_name)
def keyword_extraction(text: str, method: str):
    """ return keywords and their weights """
    result = {}
    if method == "frequencies":
        result = get_word_frequencies(text)
    elif method == "textrank":
        result = get_textrank_topwords(text)
    elif method == "topicrank":
        result = get_topicrank_topwords(text)
    else:
        raise Exception("Invalid method") 
    return result
