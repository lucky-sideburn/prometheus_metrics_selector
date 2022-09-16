import unittest
from envyaml import EnvYAML


class UnitTest(unittest.TestCase):
    """
    Class for unit test
    """

    __application_settings = EnvYAML("resources/app-test.yml")
    __payload = \
        """
        etcd_network_peer_round_trip_time_seconds_storage{To="b7e806966cb16aa8",le="0.0002"}
        etcd_network_peer_round_trip_time_seconds_mem{To="b7e806966cb16aa8",le="0.0004"}
        etcd_network_peer_round_trip_time_seconds_bucket{To="b7e806966cb16aa9",le="0.0005"}
        """
    __tags = [{"container": "openshift-apiserver-operator", "endpoint": "https", "instance": "10.130.0.49:8443"}]

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
        except Exception as e:
            return name

    def test_read_etcd_metrics(self):
        """
        Read etcd metrics
        """
        enriched_metric = ""
        for line in self.__payload.splitlines():
            line = line.strip()
            if line is not None and line != "" and not str.isspace(line) and not line.startswith("#"):
                metric_name = UnitTest.get_metric_name(line)
                for metric in self.__application_settings["metrics.enricher"]:
                    if metric["name"] == metric_name:
                        i = line.rindex("}")
                        tags = ""
                        for tag in self.__tags:
                            for key, value in tag.items():
                                tags = tags + "," + key + "=" + value
                        enriched_metric = enriched_metric + line[:i] + tags + line[i:] + "\n"
                        print(enriched_metric)


if __name__ == "__main__":
    unittest.main()
