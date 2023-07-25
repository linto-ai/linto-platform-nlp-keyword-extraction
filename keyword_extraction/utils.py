import os
import string
import re
import numpy as np
import pytextrank
import spacy
from collections import Counter
from typing import Dict, Any

from keyword_extraction.frekeybert import get_stop_words
from .TextRank4Keyword import TextRank4Keyword
from sentence_transformers import SentenceTransformer


import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from keybert import KeyBERT
from spacy.tokens import Doc


spacy_nlp = None

def preprocess(s, stop_words):

    punctuation = """'!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'"""
    s = s.lower()
    s = s.replace("'", "' ")
    s = s.translate(str.maketrans('', '', punctuation))
    words = [t for t in re.findall(r"(\w+)", s) if t not in stop_words and len(t) > 1]
    return words

def get_data(doc: Doc) -> Dict[str, Any]:
    """Extract the data to return from the REST API given a Doc object. Modify
    this function to include other data."""
    keyphrases = [
        {
            "text": keyphrase[0],
            "score": keyphrase[1]
        }
        for keyphrase in doc._.keyphrases
    ]
    return {"text": doc.text, "keyphrases": keyphrases}  



def get_word_frequencies(doc, parameters) -> Dict[str, int]:
    lang = os.environ.get("LANGUAGE", "fr")
    
    stop_words = get_stop_words(lang) if "stopwords" not in parameters else parameters['stopwords']
    if 'add_stopwords' in parameters:
        stop_words.extend(parameters['add_stopwords'])

    words = preprocess(doc, stop_words)
    threshold = parameters.get("threshold", 0)
    sum_values = sum([c for w, c in Counter(words).most_common()])
    return dict([(w, c/sum_values) for w, c in Counter(words).most_common() if c > threshold])



def get_spacy(parameters):
    global spacy_nlp
    if spacy_nlp == None:
        if "spacy_model" in parameters:
            spacy_model = parameters[spacy_model].lower()
        else:
            lang = os.environ.get("LANGUAGE", "fr")
            if lang.startswith('en'):
                spacy_model = "en_core_web_md"
            elif lang.startswith('fr'):
                spacy_model = "fr_core_news_md"
        print('Loading SpaCy('+ spacy_model+').. ')
        spacy_nlp = spacy.load(spacy_model)
        
    return spacy_nlp



def get_textrank_topwords(doc, parameters) -> Dict[str, int]:
    lang = os.environ.get("LANGUAGE", "fr")
    stop_words = get_stop_words(lang) if "stopwords" not in parameters else parameters['stopwords']
    if 'add_stopwords' in parameters:
        stop_words.extend(parameters['add_stopwords'])

    spacy_nlp = get_spacy(parameters)
    words = preprocess(doc, stop_words)
    doc = ' '.join(words)
    damping, steps = parameters.get("damping", 0.85), parameters.get("steps", 10)
    textranker = TextRank4Keyword(damping=damping, steps=steps, spacy_nlp=spacy_nlp)
    textranker.analyze(doc, lower=True)
    
    scores = dict(textranker.get_keywords())
    sum_values = sum([c for w, c in scores.items()])

    return dict([(w, c/sum_values) for w, c in scores.items()])



def get_topicrank_topwords(doc, parameters) -> Dict[str, int]:
    spacy_nlp = get_spacy(parameters)
    if "topicrank" not in spacy_nlp.pipe_names:
        spacy_nlp.add_pipe("topicrank", config={ "stopwords": { "word": ["NOUN"] } })
    
    phrase_count_threshold = parameters.get("phrase_count_threshold", 0)

    lang = os.environ.get("LANGUAGE", "fr")
    stop_words = get_stop_words(lang) if "stopwords" not in parameters else parameters['stopwords']
    if 'add_stopwords' in parameters:
        stop_words.extend(parameters['add_stopwords'])
    
    words = preprocess(doc, stop_words)
    doc = ' '.join(words)
    doc = spacy_nlp(doc)

    keywords = []
    for phrase in doc._.phrases:
        if phrase.count > phrase_count_threshold and len(phrase.text) > 1:
            keywords.append((phrase.text, phrase.rank))
    return dict((keywords))

def get_keybert_keywords_2(doc, parameters) -> Dict[str, int]:
    print('KPE task received')

    # Check language availability
    model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
    lang = os.environ.get("LANGUAGE", "fr").lower()
    if lang.startswith('en'):
        model_name = "all-MiniLM-L6-v2"
    elif lang.startswith('fr'):
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    else:
        raise RuntimeError(f"{lang} is not yet loaded.")
    nlp = spacy.blank(lang)
    nlp.add_pipe("kpe", config={"model": {"@misc": "get_model", "name": model_name}})

    keywords = nlp.pipe(doc, component_cfg=parameters)

    return keywords

def get_keybert_keywords(doc, parameters) -> Dict[str, int]:
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    if 'model' in parameters:
        model_name = parameters['model_name']
        del parameters['model_name']
    
    if 'keyphrase_ngram_range' in parameters:
        parameters["keyphrase_ngram_range"] = tuple(parameters["keyphrase_ngram_range"])
    
    lang = os.environ.get("LANGUAGE", "fr")
    stop_words = get_stop_words(lang) if "stopwords" not in parameters else parameters['stopwords']
    if 'add_stopwords' in parameters:
        stop_words.extend(parameters['add_stopwords'])
        del parameters['add_stop_words']
    parameters['stop_words'] = stop_words

    kw_model = KeyBERT(model_name)
    keywords = kw_model.extract_keywords(doc, **parameters)

    return {k:s for k,s in keywords}