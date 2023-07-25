import logging
import os

from .frekeybert import get_stop_words, get_sbert_model, get_wikipedia_titles, get_spacy_model

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)

logger = logging.getLogger("__keyword_extraction__")
