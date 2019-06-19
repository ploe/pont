#! /usr/bin/env python3

import os

from flask import Flask, abort, jsonify, request
app = Flask(__name__)

from domain import Domain

@app.route('/')
def status():
	return 'up!'

@app.route('/favicon.ico')
def favicon():
    abort(404)


@app.route('/<path:endpoint>', methods=['DELETE', 'GET', 'POST', 'PATCH'])
def endpoint_method(endpoint):
        print("get endpoint")
        domain = Domain(endpoint, request)
        importer, driver, transformer = domain.get()

        importer.load(request)
	# importer, driver, transformer 

        # if not importer.load():
        #   return {importer.errors()}
        #
        # driver.method(importer.imported())
        #
        # transformer.transform(driver.data)

	# return Response(jsonify(transformer.data()))
        return jsonify(importer.errors)
