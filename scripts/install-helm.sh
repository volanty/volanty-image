#!/usr/bin/env bash

set -o errexit

HELM_VERSION=3.5.0
HELM_GCS_VERSION=0.3.9

echo "Installing Helm..."
curl -O https://get.helm.sh/helm-v${HELM_VERSION}-linux-amd64.tar.gz
tar -zxf helm-v${HELM_VERSION}-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm
helm version

echo "Installing helm-gcs plugin..."
helm plugin install https://github.com/hayorov/helm-gcs --version ${HELM_GCS_VERSION}