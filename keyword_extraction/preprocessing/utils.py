import string
import re
import numpy as np
import pytextrank
import spacy
from collections import Counter, OrderedDict
from typing import Dict, Any
from .TextRank4Keyword import TextRank4Keyword

def preprocess(s):
    stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
                  'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'just', 'don', 
                  'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'now',
                  'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'can', 'will', 
                  'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'should', 'how', 
                  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'no', 
                  'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
                  'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
                  'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 
                  'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 
                  'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 
                  'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 
                  'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't']
    punctuation = """'!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'"""
    s = s.lower()
    s = s.translate(str.maketrans('', '', punctuation))
    words = [t for t in re.findall(r"[A-Za-z-]+", s) if t not in stop_words and len(t) > 1]
    return words
    
    
def get_word_frequencies(doc: str, parameters: dict) -> Dict[str, int]:
    words = preprocess(doc)
    threshold = parameters.get("threshold", 0)
    return dict([(w, c) for w, c in Counter(words).most_common() if c > threshold])

def get_textrank_topwords(text, parameters: dict):
    damping, steps = parameters.get("damping", 0.85), parameters.get("steps", 10)
    textranker = TextRank4Keyword(damping=damping, steps=steps)
    textranker.analyze(text, lower=True)
    return dict(textranker.get_keywords())

def get_topicrank_topwords(text, parameters: dict):
    spacy_model = parameters.get("spacy_model", "en_core_web_sm")
    phrase_count_threshold = parameters.get("phrase_count_threshold", 0)
    
    nlp = spacy.load(spacy_model)
    nlp.add_pipe("topicrank", config={ "stopwords": { "word": ["NOUN"] } })
    doc = nlp(text)

    keywords = []
    for phrase in doc._.phrases:
        if phrase.count > phrase_count_threshold:
            keywords.append((phrase.text, phrase.rank))
    return dict((keywords))