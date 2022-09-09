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
app.logger.error("Starting OCP Prometheus Selector")

config = configparser.ConfigParser()
config.sections()
config.read('/app/conf/metrics_selector.ini')

app.logger.error('Read configuration from selector.ini')
prometheus_url = config['prometheus']['url']
app.logger.error(f"Prometheus URL is {prometheus_url}")

token_env = os.environ["TOKEN"]
token = token_env.strip()

namespaces = list(config['prometheus']['namespaces'].split(",")) 
jobs = list(config['prometheus']['jobs'].split(","))  

scrape_urls = []

@app.route('/')
def hello_world():
    return 'Welcome to Prometheus Metrics Selector'

@app.route('/metrics')
def metrics():
  global_payload = ""
  app.logger.error(f"Called /metrics endpoint")

  scrape_urls = []
  headers = {"Authorization": f"Bearer {token}"}
  payload = requests.get(f"{prometheus_url}/api/v1/targets", verify=False, headers=headers, allow_redirects=True)
  targets = payload.json()
  
  for target in targets['data']['activeTargets']:
    app.logger.error(f"Computing target {target}")
  if target['discoveredLabels']['namespace'] in namespaces:
    app.logger.error(f">>> Selected target {target}")
    scrape_urls.append(target['scrapeUrl'])
  if target['discoveredLabels']['job'] in jobs:
    app.logger.error(f">>> Selected target {target}")
    scrape_urls.append(target['scrapeUrl']) 
  for scrape_url in scrape_urls:
    app.logger.error(f"Scraping metrics from {scrape_url}")
    payload = requests.get(f"f{scrape_url}", verify=False, headers=headers, allow_redirects=True)
    app.logger.error(f"Appending metrics from {payload.text} to the global_payload")
    global_payload = f"{global_payload}\n1%{payload.text}"

  return global_payload
