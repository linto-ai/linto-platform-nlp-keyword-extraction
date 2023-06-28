#!/usr/bin/env python3

import json
import logging

import requests
from celery_app.tasks import get_word_frequencies
from confparser import createParser
from flask import Flask, json, request
from serving import GunicornServing
from swagger import setupSwaggerUI

from keyword_extraction import logger

app = Flask("__keyword_extraction-worker__")


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return json.dumps({"healthcheck": "OK"}), 200


@app.route("/oas_docs", methods=["GET"])
def oas_docs():
    return "Not Implemented", 501


@app.route("/keyword_extraction", methods=["POST"])
def keyword_extraction_route():
    try:
        print("########### At /keyword_extraction ###########")
        print("########### Header: " - str(request.headers.get('accept')))
        logger.debug("Keyword Extraction request received")
        # Fetch data/parameters
        logger.debug(request.headers.get('accept').lower())
        request_body = json.loads(request.data)
        documents = request_body.get("documents", "")
        config = request_body.get("config", {})
        method = config.get("method", "")
        assert(method in ("frequencies", "textrank", "topicrank"))

        results = []

        try:
            if method == "frequencies":
                results = get_word_frequencies(documents, config)
        except Exception as e:
            print(request_body);
            return "Failed to process text: {}".format(e), 500

        # Return result
        return results, 200

    except Exception as e:
        print(request.data)
        return "Missing request parameter: {}".format(e)

# Rejected request handlers
@app.errorhandler(405)
def method_not_allowed(_):
    return "The method is not allowed for the requested URL", 405


@app.errorhandler(404)
def page_not_found(_):
    return "The requested URL was not found", 404


@app.errorhandler(500)
def server_error(error):
    logger.error(error)
    return "Server Error", 500


if __name__ == "__main__":
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

    serving = GunicornServing(
        app,
        {
            "bind": f"0.0.0.0:{args.service_port}",
            "workers": args.workers,
        },
    )
    logger.info(args)
    try:
        serving.run()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(str(e))
        logger.critical("Service is shut down (Error)")
        exit(e)
