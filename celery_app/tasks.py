import os

from stt import logger
from stt.processing import model
from celery_app.celeryapp import celery
from stt.processing.utils import load_wave
from stt.processing.decoding import decode

@celery.task(name="disfluency_task")
def transcribe_task(text: str, language: str):
    """ transcribe_task do a synchronous call to the transcribe worker API """
    logger.info("Received transcription task")
    # Load wave
    
    # INSERT PROCESSING HERE
    
    return "result"

    