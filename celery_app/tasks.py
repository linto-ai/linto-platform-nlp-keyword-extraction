import os
import requests
import json
from celery_app.celeryapp import celery

from keyword_extraction.utils import get_word_frequencies


@celery.task(name="keyword_extraction_task")
def keyword_extraction_task(text: str):
    """ return word frequencies """
    word_frequencies = get_word_frequencies(text)
    return word_frequencies
