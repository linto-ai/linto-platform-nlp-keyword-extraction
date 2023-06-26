import os
import string
import re
import numpy as np
import pytextrank
import spacy
from collections import Counter, OrderedDict
from typing import Dict, Any
from .TextRank4Keyword import TextRank4Keyword

spacy_nlp = None

def preprocess(s):
    lang = os.environ.get("LANGUAGE", "fr")
    
    if lang == 'fr':
        stop_words = ['au', 'aux', 'avec', 'ce', 'ces', 'dans', 'de', 'des', 'du', 'elle', 'en', 'et', 
                      'eux', 'il', 'je', 'la', 'le', 'leur', 'lui', 'ma', 'mais', 'me', 'même', 'mes', 
                      'moi', 'mon', 'ne', 'nos', 'notre', 'nous', 'on', 'ou', 'par', 'pas', 'pour', 'qu', 
                      'que', 'qui', 'sa', 'se', 'ses', 'son', 'sur', 'ta', 'te', 'tes', 'toi', 'ton', 'tu', 
                      'un', 'une', 'vos', 'votre', 'vous', 'c', 'd', 'j', 'l', 'à', 'm', 'n', 's', 't', 'y', 
                      'été', 'étée', 'étées', 'étés', 'étant', 'suis', 'es', 'est', 'sommes', 'êtes', 'sont', 
                      'serai', 'seras', 'sera', 'serons', 'serez', 'seront', 'serais', 'serait', 'serions', 
                      'seriez', 'seraient', 'étais', 'était', 'étions', 'étiez', 'étaient', 'fus', 'fut', 'fûmes', 
                      'fûtes', 'furent', 'sois', 'soit', 'soyons', 'soyez', 'soient', 'fusse', 'fusses', 'fût', 
                      'fussions', 'fussiez', 'fussent', 'ayant', 'eu', 'eue', 'eues', 'eus', 'ai', 'as', 'avons', 
                      'avez', 'ont', 'aurai', 'auras', 'aura', 'aurons', 'aurez', 'auront', 'aurais', 'aurait', 
                      'aurions', 'auriez', 'auraient', 'avais', 'avait', 'avions', 'aviez', 'avaient', 'eut', 
                      'eûmes', 'eûtes', 'eurent', 'aie', 'aies', 'ait', 'ayons', 'ayez', 'aient', 'eusse', 
                      'eusses', 'eût', 'eussions', 'eussiez', 'eussent', 'ceci', 'celà', 'cet', 'cette', 
                      'ici', 'ils', 'les', 'leurs', 'quel', 'quels', 'quelle', 'quelles', 'sans', 'soi',
                      "l'", "n'", "c'", "j'", "m'", "t'", "s'", "d'"]
    elif lang == 'en':
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
    else:
        stop_words = []
    
    punctuation = """'!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'"""
    s = s.lower()
    s = s.replace("'", "' ")
    s = s.translate(str.maketrans('', '', punctuation))
    words = [t for t in re.findall(r"[A-Za-z-]+", s) if t not in stop_words and len(t) > 1]
    return words

    
def get_word_frequencies(doc, parameters) -> Dict[str, int]:
    words = preprocess(doc)
    threshold = parameters.get("threshold", 0)
    return dict([(w, c) for w, c in Counter(words).most_common() if c > threshold])

def load_spacy(parameters):
    global spacy_nlp
    if spacy_nlp == None:
        print('Loading SpaCy model')
        if "spacy_model" in parameters:
            spacy_model = parameters[spacy_model]
        else:
            lang = os.environ.get("LANGUAGE", "fr")
            if lang == 'en':
                spacy_model = "en_core_web_sm"
            else:
                spacy_model = "fr_core_news_sm"
        spacy_nlp = spacy.load(spacy_model)
    return spacy_nlp


def get_textrank_topwords(doc, parameters) -> Dict[str, int]:
    spacy_nlp = load_spacy(parameters)
    damping, steps = parameters.get("damping", 0.85), parameters.get("steps", 10)
    textranker = TextRank4Keyword(damping=damping, steps=steps, spacy_nlp=spacy_nlp)
    textranker.analyze(doc, lower=True)
    return dict(textranker.get_keywords())


def get_topicrank_topwords(doc, parameters) -> Dict[str, int]:
    spacy_nlp = load_spacy(parameters)
    if "topicrank" not in spacy_nlp.pipe_names:
        spacy_nlp.add_pipe("topicrank", config={ "stopwords": { "word": ["NOUN"] } })
    
    phrase_count_threshold = parameters.get("phrase_count_threshold", 0)
    
    doc = spacy_nlp(doc)

    keywords = []
    for phrase in doc._.phrases:
        if phrase.count > phrase_count_threshold:
            keywords.append((phrase.text, phrase.rank))
    return dict((keywords))