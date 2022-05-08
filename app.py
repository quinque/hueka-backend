#!/usr/bin/env python
# -*- coding: utf-8 -*-

import elasticsearch
import hashlib
import requests
import sys

from flask import jsonify, request, Flask
from urllib.parse import urlencode

application = app = Flask(__name__)


@app.route('/<id>', methods=['GET'])
def root_get(id):
	try:
		es = elasticsearch.Elasticsearch([config['elasticsearch']['uri']])
		return es.get(index=config['elasticsearch']['index'], id=id)['_source']
	except elasticsearch.exceptions.NotFoundError:
		return jsonify({'reason': 'Not Found'}), 404


@app.route('/', methods=['POST'])
def root_post():
	data = request.json
	id = hashlib.sha1()
	try:
		id.update(('%s: (%s, %s); %s'%(data['desc'], data['lat'], data['long'], data['timestamp'])).encode())
	except KeyError:
		return jsonify({'reason': 'Bad Request'}), 400
	es = elasticsearch.Elasticsearch([config['elasticsearch']['uri']])
	es.indices.create(index=config['elasticsearch']['index'], ignore=[400])
	es.index(
		index=config['elasticsearch']['index'],
		id='0x%s' % id.hexdigest(),
		document=data)
	return jsonify({'id': '0x%s' % id.hexdigest()})

@app.route('/ping', methods=['GET'])
def ping():
	try:
		if elasticsearch.Elasticsearch([config['elasticsearch']['uri']]).ping():
			return jsonify({'result': 'pong'})
		1/0
	except:
		return jsonify({'result': 'oops'}), 500

@app.route('/_cat/<endpoint>', methods=['GET'])
def _cat(endpoint=None):
	r = requests.get('%s/_cat/%s?%s' % (config['elasticsearch']['uri'], endpoint, urlencode(request.args)))
	return r.text

if __name__ == "__main__":
	config = {
		'debug': True,
		'elasticsearch': {
			'index': 'hueka',
			'uri': 'http://elasticsearch.jupiter.gdv:9200',
		}
	} if '-d' in sys.argv else {
		'debug': False,
		'elasticsearch': {
			'index': 'hueka',
			'uri': 'https://vpc-hueka-4px6papks3uo4ws44bn6vsoyke.eu-central-1.es.amazonaws.com',
		}
	}
	app.debug = config['debug']
	app.run()

