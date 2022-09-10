# Openshift Prometheus Metrics Selector
## Description

Prometheus Stack on Openshift exposes tons of metrics. All are important, but what are definitely significants?
Sometime too many metrics and alerts can confuse SysOps teams. There is not clarity of what is important for a first-level monitoring system.

OCP_pms is a Prometheus exporter that performs the following actions:

1. Collect metrics from selected exporters across an openshift cluster
2. Use regular expression for selecting only specific exporter or metrics

OCP_pms is also useful when you install Prometheus thorough an operator and you need to do some change quickly on label or annotation of Prometheus pod. 
Usually them are controlled by the operator.

## Prerequisites

1. OCP_pms must be installed into the project openshift-monitoring for found automatically required secrets (for TLS cert client)
2. Put a token (Base64 encoded) of a ServiceAccount into the secret secret-ocp-metrics-selector located into the manifests folder. This account in my case is admin of the project openshift-monitoring but I am sure that we can create a custom role with no admin grants but just the required grants...

## Installation

```bash
oc create -f manifests/dc-ocp-metrics-selector.yaml

# Change token of your sevice account that can be authenticated to the internale Openshift Prometheus
oc create -f manifests/secret-ocp-metrics-selector.yaml

# Change url and regex for your needs
oc create configmap ocp-metrics-selector-cm --from-file=metrics_selector.ini -n metrics-selector
```
## Configuration Example
```bash
[prometheus]
url = https://prometheus.local
jobs = node-exporter,prometheus-k8s,openshift-state-metrics
namespaces = openshift-etcd
```
## ConfigMap Example
```bash
apiVersion: v1
data:
  metrics_selector.ini: |
    [prometheus]
    url = https://prometheus.local
    jobs = node-exporter,openshift-state-metrics
    namespaces = openshift-etcd
kind: ConfigMap
metadata:
  name: ocp-metrics-selector-cm
  namespace: metrics-selector
```