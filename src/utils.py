import configparser
import os
import re
import requests
from envyaml import EnvYAML

import logging as LOG


class Singleton(type):
    """
    Singeton object using metaclass approach
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigWrapper(metaclass=Singleton):
    """
    This Singleton class represents the configuration class.
    """

    # instance attribute
    __instance = None

    # configparser config
    __config: configparser.ConfigParser = None

    def __init__(self, *args, **kwargs):
        self.__config = configparser.ConfigParser()
        if self.__config is not None:
            self.__config.sections()
            self.__config.read(os.getenv("CONFIG_FILE", "/app/conf/metrics_selector.ini"))
        else:
            raise Exception("ConfigParse is None")

    @staticmethod
    def get_stripped_token() -> str:
        """
        Get stripped token
        """
        token_env = os.environ["TOKEN"]
        if token_env is None:
            raise Exception(f"Token is None")
        return token_env.strip()

    def config(self) -> configparser.ConfigParser:
        """
        Return the config of the ConfigParser
        """
        return self.__config

    def get_prometheus_url(self) -> str:
        """
        Get the prometheus url
        """
        try:
            return self.config()["prometheus"]["url"]
        except Exception as e:
            raise e

    def get_configured_namespaces(self) -> list:
        """
        Get configured namespaces as list
        """
        try:
            print(f"namespaces: {self.config()['prometheus']['namespaces'].split(',')}")
            return self.config()["prometheus"]["namespaces"].split(",")
        except Exception as e:
            raise e

    def get_configured_jobs(self) -> list:
        """
        Get configured jobs as list
        """
        try:
            print(f"jobs: {self.config()['prometheus']['jobs'].split(',')}")
            return self.config()["prometheus"]["jobs"].split(",")
        except Exception as e:
            raise e

    def get_etcd_ssl_cert(self):
        """
        Get ssl cert for etcd job exporter
        """
        try:
            return self.config()["ssl.etcd"]["cert"]
        except Exception as e:
            raise e

    def get_ksm_ssl_cert(self):
        """
        Get ssl cert for etcd job exporter
        """
        try:
            return self.config()["ssl.kst"]["cert"]
        except Exception as e:
            raise e

    def get_etcd_ssl_key(self):
        """
        Get ssl cert for etcd job exporter
        """
        try:
            return self.config()["ssl.etcd"]["key"]
        except Exception as e:
            raise e

    def get_ksm_ssl_key(self):
        """
        Get ssl cert for etcd job exporter
        """
        try:
            return self.config()["ssl.kst"]["key"]
        except Exception as e:
            raise e


class Scraper:
    """
    This class represents a scraper class.
    """

    __url: str = None
    __verify = False
    __headers = {}
    __allow_redirects = True,
    __job: str = None

    __etcd_scraper_regex_str = r"^.*etcd.*$"
    __kst_scraper_regex_str = r"^.*kubernetes-state-metric.*$"

    def __init__(self, url: str, headers: dict, job: str, verify=False, allow_redirect=True):
        """
        Constructor
        """
        self.__url = url
        self.__headers = headers
        self.__job = job
        self.__verify = verify
        self.__allow_redirects = allow_redirect

    def to_scrape(self, config):
        """
        Scrape ulr metrics
        """
        ssl = []
        print(f"to_scrape: {config} and "
              f"{self.__job} and etcd regex and "
              f"{self.__etcd_scraper_regex_str} and "
              f"ksm regex {self.__kst_scraper_regex_str}")
        if config is not None:
            if re.match(self.__etcd_scraper_regex_str, self.__job):
                print("etcd Matched certs")
                ssl.append(config.get_etcd_ssl_cert())
                ssl.append(config.get_etcd_ssl_cert())
            elif re.match(self.__kst_scraper_regex_str, self.__job):
                print("ksm Matched certs")
                ssl.append(config.get_ksm_ssl_cert())
                ssl.append(config.get_ksm_ssl_key())
            LOG.info(f"For {self.__job} will use {ssl[0]} and {ssl[1]} as client cert")
            return requests.get(f"{self.__url}",
                                verify=self.__verify,
                                headers=self.__headers,
                                allow_redirects=self.__allow_redirects,
                                cert=tuple(ssl)) if len(ssl) > 0 \
                else requests.get(f"{self.__url}",
                                  verify=self.__verify,
                                  headers=self.__headers,
                                  allow_redirects=self.__allow_redirects)
        else:
            raise Exception("Config class is None")


class Enricher:
    """
    This class enrich the global metrics payload using app.yml configuration file
    """

    __application_settings: EnvYAML = None

    def __init__(self):
        """
        Constructor
        """
        self.__application_settings = EnvYAML("/app/conf/app.yml")

    @staticmethod
    def get_metric_name(line: str):
        """
        Return metric name starting from payload line
        """
        name = None
        try:
            upper_bound = line.index("{")
            if upper_bound is not None:
                name = line[0:upper_bound]
            return name
        except ValueError as e:
            LOG.error(f"Error during get index for line {line}")
            raise ValueError(e)

    def to_enrich(self, payload: str, tags: list):
        """
        Enrich payload, Return the enriched payload
        """
        enriched_metric = ""
        try:
            for line in payload.splitlines():
                line = line.strip()
                if line is not None and line != "" and not str.isspace(line) and not line.startswith("#"):
                    metric_name = Enricher.get_metric_name(line)
                    for metric in self.__application_settings["metrics.enricher"]:
                        if metric["name"] == metric_name:
                            i = line.rindex("}")
                            tags_to_inject = ""
                            for tag in tags:
                                for key, value in tag.items():
                                    # now we inject tags as is, but we can use the app.yml to drive injection
                                    tags_to_inject = tags_to_inject + "," + key + "=" + value
                            enriched_metric = enriched_metric + line[:i] + tags_to_inject + line[i:] + "\n"
            return enriched_metric
        except Exception as e:
            LOG.error("Error during enrich line metric for ew tag")
            raise e
