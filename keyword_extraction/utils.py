import os
import string
import re
import numpy as np
import pytextrank
import spacy
from collections import Counter, OrderedDict
from typing import Dict, Any
from .TextRank4Keyword import TextRank4Keyword

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from keybert import KeyBERT
from spacy.tokens import Doc

spacy_nlp = None

def preprocess(s):
    lang = os.environ.get("LANGUAGE", "fr")
    
    if lang.startswith('fr'):
        stop_words = ['allaient', 'ta', 'vers', 'eue', 'ceux', 'est', 'tu', 'étions', 'multiples', 'sept', 
                      'retour', 'quelconque', 'abord', 'neuvième', 'huitième', 'ha', 'revoici', 'aurez', 'es', 'dernier', 
                      'tandis', 'ho', 'fussiez', 'septième', 'a', 's',
                      'quatre', 'ainsi', 'concernant', 'hum', 'enfin', 'seriez', 'lorsque', 'ma', 'eût', 'quant-à-soi', 'avaient', 
                      'tend', 'procedant', 'brrr', 'deux', 'seulement', 'elles', 'unes', 'soyons', 'hep', 'suffisant', 'aies', 
                      'multiple', 'quoi', 'êtes', 'nous-mêmes', 'parfois', 'relative', 'dite', 'pif', 'se', 'quel', 'subtiles', 
                      'néanmoins', 'son', 'hui', 'paf', 'pourrais', 'étant', 'entre', 'lesquelles', 'tel', 'non', 'certain', 
                      'deuxièmement', 'cette', 'différentes', 'bah', 'zut', 'eues', 'différents', 'mienne', 'dos', 'celle', 'chacune',
                      'soi', 'particulièrement', 'celui-là', 'parle', 'debout', 'd', 'étant', 'ci', 'quand', 'celle-ci', 
                      'relativement', 'lesquels', 'jusque', 'préalable', 'delà', 'dès', 'miennes', 'sein', 'eu', 'vas', 'auquel', 
                      'chacun', 'envers', 'possible', 'longtemps', 'seras', 'desquelles', 'dedans', 'dring', 'onze', 'nôtres', 
                      'eussent', 'ayant', 'ouias', 'parseme', 'dixième', 'fi', 'cet', 'cinquantaine', 'ore', 'puisque', 
                      'doit', 'plein', 'voie', 'avions', 'allons', 'chers', 'maint', 'pour', 'ollé', 'ils', 
                      'fussent', 'déjà', 'beau', 'sinon', 'z', 'parole', 'dix', 'quelque', 'que', 'uns', 'auxquels', 'ce',
                      'pan', 'eussions', 'derrière', 'auraient', 'seize', 'du', 'valeur', 'outre', 'm', 
                      'une', 'y', 'hurrah', 'ah', 'cinq', 'quarante', 'eussiez', 'serai', 'très', 'derriere', 'fûmes', 't', 
                      'dehors', 'e', 'certains', 'pouvait', 'surtout', 'attendu', 'autrement', 'quels', 'fut', 'fûtes', 'semble', 
                      'dessus', 'eusse', 'eux', 'chères', 'mais', 'r', 'selon', 'nous', 'chère', 'ait', 'sait', 'tien', 
                      'miens', 'même', 'toujours', 'avons', 'precisément', 'duquel', 'malgré', 'moi-même', 'unique', 
                      'premier', 'aura', 'début', 'furent', 'pu', 'avant', 'être', 'suis', 'environ', 'té', 
                      'vive', 'désormais', 'semblent', 'vôtre', 'auriez', 'étais', 'eh', 'quelques', 'seront', 'alors', 
                      'particulier', 'vlan', 'aie', 'serais', 'moi-même', 'mince', 'il',
                      'ayons', 'olé', 'ou', 'ceci', 'mot', 'serez', 'dix-huit', 'ohé', 'quatorze', 
                      'auras', 'elles-mêmes', 'tant', 'ceux-ci', 'avez', 'ici', 'assez', 'comme', 'toutes', 
                      'permet', 'pendant', 'plutôt', 'lors', 'après', 'lui-meme', 'pouah', 'certes', 'font', 'cependant', 
                      'près', 'celles-là', 'personne', 'comment', 'suivants', 'certaine', 'quanta', 'ès', 'ayez',
                      'hem', "quelqu'un", 'pire', 'suffit', 'oust', 'car', 'â', 'rien', 'cela', 'voient', 
                      'sixième', 'peuvent', 'soyez', 'état', 'bas', 'dit', 'telle', 'via', 'vous-mêmes', 'devant', 'f', 'tic', 
                      'pas', 'devrait', 'clac', 'hue', 'vais', 'où', 'me', 'encore', 'les', 'mon', 'autres', 'revoilà', 'trente',
                      'donc', 'avais', 'houp', 'bravo', 'vives', 'excepté', 'restent', 'été', 'bon', 'fût', 'des',
                      'ailleurs', 'siens', 'troisième', 'fois', 'soit', 'quatrième', 'aurions', 'fussions', 'seule', 'celui-ci', 
                      'différente', 'sien', 'dire', 'nos', 'ceux-là', 'maintenant', 'nouveaux', 'celle-là', 'lequel', 'sacrebleu',
                      'tac', 'sommes', 'partant', 'bien', 'h', 'étiez', 'flac', 'trois', 'cher', 'pfft', 'quiconque', 'sa', 
                      'tardive', 'lui-même', 'étées', 'lès', 'toutefois', 'vôtres', 'à', 'serait', 'onzième', 'quelles', 'eut', 
                      'fait', 'reste', 'votre', 'vé', 'x', 'laquelle', 'dont', 'toute', 'faites', 'par', 'ô', 'fusses', 'probante', 
                      'celles-ci', 'eurent', 'b', 'pourrait', 'plusieurs', 'étés', 'aient', 'l', 'soient', 'da', 'celles', 
                      'moindres', 'douze', 'neanmoins', 'psitt', 'j', 'hormis', 'quoique', 'différent', 'sont', 'o|', 'la',
                      'soi-même', 'toi-même', 'aurais', 'ton', 'aussi', 'rarement', 'vingt', 'speculatif', 'different', 'q', 
                      'superpose', 'parce', "aujourd'hui", 'fus', 'ni', 'je', 'afin', 'ouste', 'si', 'contre', 'parler', 'tellement', 
                      'bigre', 'dits', 'tenant', 'sauf', 'sois', 'remarquable', 'absolument', 'qu', 'voici', 'force', 'faisant', 
                      'mille', 'tsouin', 'haut', 'na', 'suffisante', 'basee', 'suit', 'en', 'tels', 'leur', 'va', 'avec', 'sur',
                      'peu', 'suivre', 'avait', 'hé', 'probable', 'o', 'sent', 'las', 'très', 'ouverts', 'eûtes', 'boum', 'hou',
                      'sans', 'devra', 'vos', 'quatre-vingt', 'ses', 'un', 'nouveau', 'treize', 'souvent', 'restrictif', 'tout', 
                      'exactement', 'notre', 'troisièmement', 'vont', 'telles', 'ai', 'cinquante', 'peux', 'uniques',
                      'aurons', 'ouf', 'allo', 'clic', 'feront', 'six', 'depuis', 'première', 'là', 'egale', 'autrefois',
                      'couic', 'dix-sept', 'on', 'autrui', 'dans', 'quant', 'elle', 'et', 'de', 'plouf',
                      'fusse', 'g', 'deuxième', 'touchant', 'holà', 'quinze', 'cinquantième', 'même', 'puis', 'au', 'serons',
                      'premièrement', 'certaines', 'tiens', 'chaque', 'hein', 'euh', 'auront', 'aviez', 'nul', 'sous', 'diverses',
                      'effet', 'ouvert', 'soixante', 'ne', 'desquels', 'pourquoi', 'eusses', 'hors', 'étée', 'toc', 'chut', 'hi', 
                      'égales', 'fais', 'aucuns', 'dessous', 'ont', 'sera', 'strictement', 'eus', 'gens', 'leurs', 'cent', 'le', 
                      'trop', 'allô', 'après', 'auxquelles', 'bat', 'merci', 'te', 'jusqu', 
                      'desormais', 'tiennes', 'tienne', 'directe', 'moyennant', 'oh', 'également', 'auprès', 'naturelle', 'nôtre',
                      'naturel', 'vu', 'étaient', 'combien', 'sapristi', 'seraient', 'particulière', 'u', 'vous', 'juste', 'façon', 
                      'suivante', 'hop', 'aux', 'hélas', 'as', 'parmi', 'v', 'c', 'nommés', 'mien', 'laisser', 'mes', 'siennes', 
                      'aucune', 'près', 'rares', 'toi', 'eûmes', 'faisaient', 'tes', 'divers', 'était', 'plupart', 'beaucoup', 
                      'uniformement', 'etc', 'moi', 'semblaient', 'directement', 'durant', 'tous', 'pfut', 'pff', 'moins', 'voilà',
                      'serions', 'ces', 'dix-neuf', 'i', 'possibles', 'sienne', 'nombreux', 'parlent', 'diverse', 'mêmes', 'avoir', 
                      'chez', 'douzième', 'tenir', 'mêmes', 'tente', 'notamment', 'anterieure', 'aucun', 'peut', 'lui', 'extérieur', 
                      'importe', 'malgré', 'celui', 'suivant', 'semblable', 'quelle', 'qui', 'n', 'aujourd', 'huit', 'celà', 'doivent',
                      'ça', 'comparable', 'rare', 'quatrièmement', 'k', 'autre', 'aurait', 'vivat', 'naturelles', 'nécessairement', 
                      'devers', 'neuf', 'etre', 'aurai', 'rendre', 'essai', 'cinquième', 'dernière', 'stop', 'prochain', 'prochaine', 
                      'tsoin', 'elle-même', 'plus', 'eux-mêmes', 'w', 'oui','non', 'euh', 'ah']
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
    words = preprocess(doc)
    threshold = parameters.get("threshold", 0)
    sum_values = sum([c for w, c in Counter(words).most_common()])
    return dict([(w, c/sum_values) for w, c in Counter(words).most_common() if c > threshold])


def load_spacy(parameters):
    global spacy_nlp
    if spacy_nlp == None:
        print('Loading SpaCy model')
        if "spacy_model" in parameters:
            spacy_model = parameters[spacy_model]
        else:
            lang = os.environ.get("LANGUAGE", "fr").lower()
            if lang.startswith('en'):
                spacy_model = "en_core_web_sm"
            elif lang.startswith('fr'):
                spacy_model = "fr_core_news_sm"
        spacy_nlp = spacy.load(spacy_model)
    return spacy_nlp


def get_textrank_topwords(doc, parameters) -> Dict[str, int]:
    spacy_nlp = load_spacy(parameters)
    words = preprocess(doc)
    doc = ' '.join(words)
    damping, steps = parameters.get("damping", 0.85), parameters.get("steps", 10)
    textranker = TextRank4Keyword(damping=damping, steps=steps, spacy_nlp=spacy_nlp)
    textranker.analyze(doc, lower=True)
    
    scores = dict(textranker.get_keywords())
    sum_values = sum([c for w, c in scores.items()])

    return dict([(w, c/sum_values) for w, c in scores.items()])


def get_topicrank_topwords(doc, parameters) -> Dict[str, int]:
    spacy_nlp = load_spacy(parameters)
    if "topicrank" not in spacy_nlp.pipe_names:
        spacy_nlp.add_pipe("topicrank", config={ "stopwords": { "word": ["NOUN"] } })
    
    phrase_count_threshold = parameters.get("phrase_count_threshold", 0)
    
    words = preprocess(doc)
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
    kw_model = KeyBERT(model_name)
    keywords = kw_model.extract_keywords(doc, **parameters)

    return {k:s for k,s in keywords}