#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config

import elasticsearch
import hashlib
import json
import pyjq
import requests
import sys

from flask import jsonify, request, Flask, Response
from urllib.parse import urlencode

application = app = Flask(__name__)

@app.route('/<id>', methods=['GET'])
def root_get(id):
	try:
		es = elasticsearch.Elasticsearch([config.elasticsearch['uri']], verify_certs=False)
		return es.get(index=config.elasticsearch['index'], id=id)['_source']
	except elasticsearch.exceptions.NotFoundError:
		return jsonify({'reason': 'Not Found'}), 404


@app.route('/', methods=['POST'])
def root_post():
	data = request.json
	id = hashlib.sha1()
	try:
		id.update(('%s: (%s, %s); %s'%(data['description'], data['latitude'], data['longitude'], data['timestamp'])).encode())
	except KeyError:
		print(data)
		return jsonify({'reason': 'Bad Request'}), 400
	es = elasticsearch.Elasticsearch([config.elasticsearch['uri']], verify_certs=False)
	es.indices.create(index=config.elasticsearch['index'], ignore=[400])
	es.index(
		index=config.elasticsearch['index'],
		id='0x%s' % id.hexdigest(),
		document=data)
	return jsonify({'id': '0x%s' % id.hexdigest()})

@app.route('/last',          methods=['GET'])
@app.route('/last/',         methods=['GET'])
@app.route('/last/<format>', methods=['GET'])
def last(format=None):
	if format == 'svg':
		return Response('''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><style>circle {fill: %s;}</style><circle cx="50" cy="50" r="47"/></svg>''' % (_search()[0]['naivecolor']), mimetype='image/svg+xml')
	return json.dumps(_search()[0])

@app.route('/search', methods=['GET', 'POST'])
def search():
	return json.dumps(_search())

def _search():
	query = '{"query": {"match_all": {}}, "size": 1, "sort": [{"timestamp": {"order": "desc"}}]}'
	if request.data:
		query = request.data
	es = elasticsearch.Elasticsearch([config.elasticsearch['uri']], verify_certs=False)
	response = es.search(index=config.elasticsearch['index'], body=query)
	return pyjq.all(".hits.hits[]._source", response)

@app.route('/ping', methods=['GET'])
def ping():
	try:
		if elasticsearch.Elasticsearch([config.elasticsearch['uri']], verify_certs=False).ping():
			return jsonify({'result': 'pong'})
		1/0
	except:
		return jsonify({'result': 'oops'}), 500

@app.route('/_cat/<endpoint>', methods=['GET'])
def _cat(endpoint=None):
	r = requests.get('%s/_cat/%s?%s' % (config.elasticsearch['uri'], endpoint, urlencode(request.args)), verify=False)
	return r.text

if __name__ == "__main__":
	app.debug = config.debug
	app.run(**config.flask)

