import time
import requests
import json
import configparser
import re
import logging
import os
import sys
from flask import Flask

app = Flask(__name__)
app.logger.info("Starting OCP Prometheus Selector", file=sys.stdout)

config = configparser.ConfigParser()
config.sections()
config.read('/app/conf/metrics_selector.ini')

app.logger.info('Read configuration from selector.ini', file=sys.stdout)
prometheus_url = config['prometheus']['url']
app.logger.info(f"Prometheus URL is {prometheus_url}", file=sys.stdout)

token_env = os.environ["TOKEN"]
token = token_env.strip()
regex = config['prometheus']['regex']
app.logger.info(f"OCP Prometheus Metrics Selector will use this regex {regex}")

scrape_urls = []

@app.route('/')
def hello_world():
    return 'Welcome to Prometheus Metrics Selector'

@app.route('/metrics')
def metrics():
    global_payload = ""
    app.logger.info(f"Called /metrics endpoint", file=sys.stdout)

    scrape_urls = []
    headers = {"Authorization": f"Bearer {token}"}
    payload = requests.get(f"{prometheus_url}/api/v1/targets", verify=False, headers=headers, allow_redirects=True)
    targets = json.loads(payload.text)
    for target in targets['data']['activeTargets']:
      logging.info(f"Computing target {target}")
      if re.match(regex, target['scrapePool']):
        app.logger.info(f">>> Selected target {target}", file=sys.stdout)
        scrape_urls.append(target['scrapeUrl'])
    for scrape_url in scrape_urls:
        app.logger.info(f"Scraping metrics from {scrape_url}", file=sys.stdout)
        payload = requests.get(f"f{scrape_url}", verify=False, headers=headers, allow_redirects=True)
        app.logger.info(f"Appending metrics from {payload.text} to the global_payload", file=sys.stdout)
        global_payload = f"{global_payload}\n1%{payload.text}"
    return global_payload
