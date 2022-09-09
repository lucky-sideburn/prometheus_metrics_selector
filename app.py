import time
import requests
import json
import configparser
import re
import logging
import os

from flask import Flask
logging.info('Starting OCP Prometheus Selector')
app = Flask(__name__)
config = configparser.ConfigParser()
config.sections()
config.read('/app/conf/metrics_selector.ini')
logging.info('Read configuration from selector.ini')
prometheus_url = config['prometheus']['url']
logging.info(f"Prometheus URL is {prometheus_url}")
token = os.environ["TOKEN"]
regex = config['prometheus']['regex']
logging.info(f"OCP Prometheus Metrics Selecta will use this regex {regex}")

scrape_urls = []
global_payload = ""

@app.route('/')
def hello_world():
    return 'Welcome to Prometheus Metrics Selector'

@app.route('/metrics')
def metrics():
    logging.info(f"Called /metrics endpoint")
    scrape_urls = []
    headers = {"Authorization": f"Bearer {token}"}
    return headers
    payload = requests.get(f"{prometheus_url}/api/v1/targets", verify=False, headers=headers, allow_redirects=True)
    targets = json.loads(payload.text)
    for target in targets['data']['activeTargets']:
      logging.info(f"Computing target {target}")
      if re.match(regex, target['scrapePool']):
        logging.info(f">>> Selected target {target}")
        scrape_urls.append(target['scrapeUrl'])
    for scrape_url in scrape_urls:
        logging.info(f"Scraping metrics from {scrape_url}")
        payload = requests.get(f"f{scrape_url}", verify=False, headers=headers, allow_redirects=True)
        logging.info(f"Appending metrics from {payload.text} to the global_payload")
        global_payload = f"{global_payload}\n1%{payload.text}"
    return global_payload
