import requests
from flask import Flask
from utils import ConfigWrapper, Scraper, Enricher
import logging as LOG

app = Flask(__name__)


@app.route('/')
def hello_world():
    config = ConfigWrapper()
    app.logger.info(' '.join(map(str, config.get_configured_namespaces())))
    app.logger.info(' '.join(map(str, config.get_configured_jobs())))
    return 'Welcome to Prometheus Metrics Selector'


@app.route('/metrics')
def metrics():
    global_payload = ""
    app.logger.info(f"Called /metrics endpoint")

    config = ConfigWrapper()

    scrape_urls = []
    headers = {"Authorization": f"Bearer {ConfigWrapper.get_stripped_token()}"}
    payload = requests.get(f"{config.get_prometheus_url()}/api/v1/targets", verify=False, headers=headers,
                           allow_redirects=True)
    targets = payload.json()

    for target in targets['data']['activeTargets']:
        # checking for namespace
        LOG.info(f"Checking namespaces {target['discoveredLabels']['__meta_kubernetes_namespace']}")
        if target['labels']['namespace'] in config.get_configured_namespaces():
            LOG.info(f">>> Selected target {target}")
            scrape_urls.append({"target": target['scrapeUrl'],
                                "discovered_label": target['discoveredLabels']['__meta_kubernetes_namespace'],
                                "tags": [target["labels"]]})
        # checking for job
        LOG.info(f"Checking job {target['discoveredLabels']['job']}")
        if target['labels']['job'] in config.get_configured_jobs():
            LOG.info(f"Selected target {target}")
            scrape_urls.append({"target": target['scrapeUrl'], "discovered_label": target['discoveredLabels']['job'],
                                "tags": [target["labels"]]})
    # scraping
    for scrape_url in scrape_urls:
        LOG.info(f"Scraping metrics from {scrape_url['target']}")
        LOG.info(f"Computing discovered_label {scrape_url['discovered_label']}")
        # use scraper
        scraper = Scraper(scrape_url['target'], headers, scrape_url['discovered_label'])
        global_payload = scraper.to_scrape()
        # enricher
        enricher = Enricher()
        enricher.to_enrich(global_payload, scrape_url["tags"])
        # rejoin payload
        LOG.info(f"Appending metrics from {payload.text} to the global_payload")
        if global_payload != "":
            global_payload = f"{global_payload}\n1%{payload.text}"
        else:
            global_payload = payload.text
    return global_payload
