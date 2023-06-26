import json
import re
from typing import Union, Dict, Any
from collections import Counter, OrderedDict

from keyword_extraction.utils import get_word_frequencies, get_textrank_topwords, get_topicrank_topwords

from celery_app.celeryapp import celery

@celery.task(name="keyword_extraction_task", bind=True) # Task name definition
def keyword_extraction_task(self, documents: list, method: str, config: dict): # Task parameters
    """keyword_extraction_task"""
    self.update_state(state="STARTED")
    print(config)

    methods_map = {"frequencies": get_word_frequencies,
                  "textrank": get_textrank_topwords,
                  "topicrank": get_topicrank_topwords}
    print("Using" + method + "to extract keywords from " + str(documents))

    result = []
    if method in methods_map:
        extract_keywords = methods_map[method.lower()]
        for doc in documents:
            result.append(extract_keywords(doc, config)) 
    else:
        result = ["Method " + method + " can't be found"]

    return result