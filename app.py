#!/usr/bin/env python
# -*- coding: utf-8 -*-

import elasticsearch
import requests
import sys

from flask import request, Flask
from urllib.parse import urlencode

application = app = Flask(__name__)


@app.route('/')
def root():
	return 'Up and running'

@app.route('/_cat/<endpoint>', methods=['GET'])
def _cat(endpoint=None):
	r = requests.get('%s/_cat/%s?%s' % (config['elasticsearch']['uri'], endpoint, urlencode(request.args)))
	return r.text

@app.route('/publish', methods=['POST'])
def publish():
	es = elasticsearch.Elasticsearch([config['elasticsearch']['uri']])
	es.indices.create(index=config['elasticsearch']['index'], ignore=[400])
	es.index(
		index=config['elasticsearch']['index'],
		document=request.json)
	return request.json

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

