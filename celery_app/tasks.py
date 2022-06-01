import os
import requests
import json
from celery_app.celeryapp import celery

from keyword_extraction.preprocessing.utils import get_word_frequencies, get_textrank_topwords, get_topicrank_topwords


@celery.task(name="keyword_extraction_task")
def keyword_extraction_task(text: str, method: str):
    """ return keywords and their weights """
    if method == "frequencies":
        result = get_word_frequencies(text)
    elif method == "textrank":
        result = get_textrank_topwords(text)
    elif method == "topicrank":
        result = get_topicrank_topwords(text)
    return result
