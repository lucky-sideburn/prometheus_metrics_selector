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
    app.logger.error(' '.join(map(str, namespaces))) 
    app.logger.error(' '.join(map(str, jobs))) 
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
    
    app.logger.error(f"Checking namespaces { target['discoveredLabels']['__meta_kubernetes_namespace']}")
    
    if target['discoveredLabels']['__meta_kubernetes_namespace'] in namespaces:
      app.logger.error(f">>> Selected target {target}")
      scrape_urls.append({"target": target['scrapeUrl'], "discovered_label": target['discoveredLabels']['__meta_kubernetes_namespace']})
    
    app.logger.error(f"Checking job { target['discoveredLabels']['job']}")
    
    if target['discoveredLabels']['job'] in jobs:
      app.logger.error(f"Selected target {target}")
      scrape_urls.append({"target": target['scrapeUrl'], "discovered_label": target['discoveredLabels']['job']}) 

  for scrape_url in scrape_urls:
    app.logger.error(f"Scraping metrics from {scrape_url["target"]}")
    cert = ""
    key = ""
    if re.match(r"^.*etcd.*$", scrape_url["discovered_label"]}):
      cert = "/etc/prometheus/secrets/kube-etcd-client-certs/etcd-client.crt"
      key = "/etc/prometheus/secrets/kube-etcd-client-certs/etcd-client.key"
  
    payload = requests.get(f"{scrape_url["target"]}", verify=False, headers=headers, allow_redirects=True, cert=cert)
    app.logger.error(f"Appending metrics from {payload.text} to the global_payload")
    global_payload = f"{global_payload}\n1%{payload.text}"

  return global_payload
