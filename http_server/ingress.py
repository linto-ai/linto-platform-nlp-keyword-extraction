#!/usr/bin/env python3

import os
from time import time
import logging
import json

from flask import Flask, request, abort, Response, json

from serving import GunicornServing
from confparser import createParser
from swagger import setupSwaggerUI

from keyword_extraction.utils import get_word_frequencies

# IMPORT YOUR PROCESSING FUNCTION HERE

app = Flask("__stt-standalone-worker__")

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger("__stt-standalone-worker__")

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return json.dumps({"healthcheck": "OK"}), 200

@app.route("/oas_docs", methods=['GET'])
def oas_docs():
    return "Not Implemented", 501

@app.route('/keyword_extraction', methods=['POST'])
def extract_keywords():
    logger.info('Keyword extraction request received')

    # get response content type
    logger.debug(request.headers.get('accept').lower())
    if not request.headers.get('accept').lower() == 'text/plain':
        return "Accept header must be set with text/plain", 400
        
    # Retrieve request text
    try:
        input_text = request.form.get("text")
    except Exception as e:
        return "Missing request parameter: {}".format(e)

    try:
        result = get_word_frequencies(text)
    except Exception as e:
        return "Failed to process text: {}".format(e), 500

    return result, 200

# Rejected request handlers
@app.errorhandler(405)
def method_not_allowed(error):
    return 'The method is not allowed for the requested URL', 405

@app.errorhandler(404)
def page_not_found(error):
    return 'The requested URL was not found', 404

@app.errorhandler(500)
def server_error(error):
    logger.error(error)
    return 'Server Error', 500

if __name__ == '__main__':
    logger.info("Startup...")

    parser = createParser()
    args = parser.parse_args()
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    try:
        # Setup SwaggerUI
        if args.swagger_path is not None:
            setupSwaggerUI(app, args)
            logger.debug("Swagger UI set.")
    except Exception as e:
        logger.warning("Could not setup swagger: {}".format(str(e)))
    
    serving = GunicornServing(app, {'bind': '{}:{}'.format("0.0.0.0", args.service_port),
                                    'workers': args.workers,})
    logger.info(args)
    try:
        serving.run()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(str(e))
        logger.critical("Service is shut down (Error)")
        exit(e)
