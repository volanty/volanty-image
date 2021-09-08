#!/usr/bin/env bash

set -o errexit
set -o pipefail

if [  $# -ge 3 ]; then
    CHART_NAME=$1
    gcp_project=$2
    gcp_key=${!3}
  else
    printf "Error: Chart name is required. \n.Usage: ./helm-release.sh <CHART_NAME> <GCP_PROJECT> <GCP_KEY> [AWS_KEY] [AWS_CLUSTER_NAME]\n"
    exit 1
fi

if [ -z "$DEPLOY_TYPE" ]; then
    deployType=GCP
else
    deployType=$DEPLOY_TYPE
fi

echo "Setting gcp project to ${gcp_project}"

echo "${gcp_key}" | base64 -d >> /tmp/key-file.json
gcloud auth activate-service-account --key-file /tmp/key-file.json --quiet
gcloud config set project ${gcp_project} --quiet
gcloud container clusters get-credentials elasticsearch-cluster --zone us-central1-a --project ${gcp_project}
export GOOGLE_APPLICATION_CREDENTIALS=/tmp/key-file.json

GCS_BUCKET_NAME="gs://volanty-charts-${BITBUCKET_DEPLOYMENT_ENVIRONMENT}/${CHART_NAME}"
BASE_CHART="./helm/${CHART_NAME}"
mv "${BASE_CHART}/values-${BITBUCKET_DEPLOYMENT_ENVIRONMENT}".yaml ${BASE_CHART}/values.yaml
echo "Initializing helm repo"
helm gcs init "${GCS_BUCKET_NAME}"
# add gcs bucket as helm repo
echo "Adding gcs bucket repo ${GCS_BUCKET_NAME}"
helm repo add private "${GCS_BUCKET_NAME}"
helm repo index . --url "${GCS_BUCKET_NAME}"
helm package --app-version "${BITBUCKET_COMMIT}" ${BASE_CHART}
chart_file=$(helm package --app-version "${BITBUCKET_COMMIT}" ${BASE_CHART} | awk '{print $NF}')
echo "Pushing $chart_file..."
helm gcs push "$chart_file" private --force

# Deploy on GCP
if [ "$deployType" == "GCP" ] || [ "$deployType" == "MULTI" ]; then
    echo "Deploy on GCP"
    helm upgrade "${CHART_NAME}" "${chart_file}" --install --atomic
fi

# Deploy on AWS
if [ "$deployType" == "AWS" ] || [ "$deployType" == "MULTI" ]; then
    if [ -z "$4" ] || [ -z "$5" ]; then
        echo "To deploy on AWS the parameters AWS_KEY and AWS_CLUSTER_NAME are required."
        exit 1
    fi
    eval ${!4}
    awsCluster=$5
    echo "Deploy on AWS on cluster $awsCluster"
    aws configure set aws_access_key_id ${aws_access_key_id}
    aws configure set aws_secret_access_key ${aws_secret_access_key}
    aws configure set default.region ${region}
    aws eks update-kubeconfig --name "${awsCluster}"
    helm upgrade "${CHART_NAME}" "${chart_file}" --install --atomic
fi