#!/bin/bash
docker build . -t docker.io/luckysideburn/ocp_metrics_selector:v1.0.0
docker push docker.io/luckysideburn/ocp_metrics_selector:v1.0.0
#docker stop ocp_metrics_selector
#docker run -p5000:5000 docker.io/luckysideburn/ocp_metrics_selector:v1.0.0
