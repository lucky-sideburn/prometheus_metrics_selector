# Openshift Prometheus Metrics Selecta


## Description

Prometheus Stack on Openshift exposes tons of metrics. All are important, but what are definitely significants?
Sometime too many metrics and alerts can confuse SysOps teams. There is not clarity of what is important for a first-level monitoring system.

OCP_pms is a Prometheus exporter that performs the following actions:

1. Collect metrics from selected exportes across an openshift cluster
2. Use regular expression for selecting only specific exporter or metrics

OCP_pms is also usefule when you install Prometheus thorough an operator and you need to do some change quickly to label or annotation of Prometheus pod. Usually them are controlled by the operator.

# Installation

oc create -f manifests/ocp_metrics_selector.yaml
oc create -f manifests/secret-ocp-metrics-selector.yaml
oc create configmap ocp-metrics-selector-cm --from-file=metrics_selector.ini -n metrics-selector