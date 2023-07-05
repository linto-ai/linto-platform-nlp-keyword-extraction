import spacy
from spacy.language import Language
from typing import List, Union, Tuple
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from thinc.api import Config

import os
import ast
import sys
import spacy
from time import time
import logging

from keybert import KeyphraseExtractor

# Load components' defaut configuration
default_config = Config().from_disk("component_config.cfg")
logger = logging.getLogger("__keyword_extraction__")

@Language.factory("kpe", default_config=default_config["components"]["kpe"])
def make_keyphrase_extractor(
    nlp: Language,
    name: str,
    model: SentenceTransformer,
    candidates: List[str] = None,
    keyphrase_ngram_range: Tuple[int, int] = (1, 1),
    stop_words: Union[str, List[str]] = None,
    top_n: int = 5,
    min_df: int = 1,
    use_maxsum: bool = False,
    use_mmr: bool = False,
    diversity: float = 0.5,
    nr_candidates: int = 20,
    vectorizer: CountVectorizer = None,
    highlight: bool = False,
    seed_keywords: List[str] = None
    ):

    kwargs = locals()
    del kwargs['nlp']
    del kwargs['name']
    del kwargs['model']

    return KeyphraseExtractor(model, **kwargs)


logger.info("Loading language model for KeyBERT...")
start = time()

LM_MAP = ast.literal_eval(os.environ["LM_MAP"])

MODELS = {
    "fr": SentenceTransformer("/app/assets/paraphrase-multilingual-MiniLM-L12-v2"),
    "en": SentenceTransformer("/app/assets/all-MiniLM-L6-v2")
}

@spacy.registry.misc("get_model")
def get_model(name):
    return MODELS[name]   

logger.info(f"(t={time() - start}s). Loaded {len(MODELS)} models: {MODELS.keys()}.")
