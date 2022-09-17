import requests
from flask import Flask
from src.utils import ConfigWrapper, Scraper, Enricher
import logging as LOG

app = Flask(__name__)


@app.route('/')
def welcome():
    config = ConfigWrapper()
    print(' '.join(map(str, config.get_configured_namespaces())))
    print(' '.join(map(str, config.get_configured_jobs())))
    return 'Welcome to Prometheus Metrics Selector'


@app.route('/metrics')
def metrics():
    print(f"Called /metrics endpoint")

    # catch the exception
    config = ConfigWrapper()

    scrape_urls = []
    headers = {"Authorization": f"Bearer {ConfigWrapper.get_stripped_token()}"}
    prometheus_payload = requests.get(f"{config.get_prometheus_url()}/api/v1/targets", verify=False, headers=headers,
                                      allow_redirects=True)
    targets = prometheus_payload.json()

    enriched_payload = ""
    for target in targets['data']['activeTargets']:
        # checking for namespace
        print(f"Checking namespaces {target['discoveredLabels']['__meta_kubernetes_namespace']}")
        print(f"configured_namespaces {config.get_configured_namespaces()}")
        if target['labels']['namespace'] in config.get_configured_namespaces():
            print(f">>> Selected target {target}")
            scrape_urls.append({"target": target['scrapeUrl'],
                                "discovered_label": target['discoveredLabels']['__meta_kubernetes_namespace'],
                                "tags": [target["labels"]]})
        # checking for job
        print(f"Checking job {target['discoveredLabels']['job']}")
        print(f"configured_jobs {config.get_configured_jobs()}")
        if target['labels']['job'] in config.get_configured_jobs():
            print(f"Selected target {target}")
            scrape_urls.append({"target": target['scrapeUrl'], "discovered_label": target['discoveredLabels']['job'],
                                "tags": [target["labels"]]})
    # scraping
    for scrape_url in scrape_urls:
        print(f"Scraping metrics from {scrape_url['target']}")
        print(f"Computing discovered_label {scrape_url['discovered_label']}")
        # use scraper
        scraper = Scraper(scrape_url['target'], headers, scrape_url['discovered_label'])
        scraped_payload = scraper.to_scrape(config)
        if scraped_payload is not None:
            print(f"scraped_payload.text {scraped_payload.text}")
            # enricher
            enricher = Enricher()
            print(f"scraped_payload: {scraped_payload} and tags: {scrape_url['tags']}")
            enriched_payload = enriched_payload + enricher.to_enrich(scraped_payload.text, scrape_url["tags"])
    print(f"global_payload {enriched_payload}")
    return enriched_payload
