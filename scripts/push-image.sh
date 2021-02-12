#!/usr/bin/env bash

# push-image flags
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -n|--name)
    CONTAINER_NAME="$2"
    shift
    shift
    ;;
    -g|--gcr-name)
    GCR_CONTAINER_NAME="$2"
    shift
    shift
    ;;
    -p|--gcp-project)
    GCP_PROJECT="$2"
    shift
    shift
    ;;
    -k|--gcp-key)
    GCP_KEY="$2"
    shift
    shift
    ;;
    -d|--deploy-args)
    DEPLOY_ARGS="$2"
    shift
    shift
    ;;
    *)    # unknown option
    printf "Error: Unknown Argument. \nUsage: ./push-image.sh --name <CONTAINER_NAME> --gcr-name <GCR_CONTAINER_NAME> --gcp-project <GCP_PROJECT> --gcp-key <GCP_KEY> --deploy-args <DEPLOY_ARGS>\n"
    exit 1
    shift
    ;;
esac
done
set -- "${POSITIONAL[@]}"

echo "${GCP_KEY}" | base64 -d >> /tmp/key-file.json
gcloud auth activate-service-account --gcp-key-file /tmp/key-file.json --quiet
gcloud config set project ${GCP_PROJECT} --quiet
gcloud auth configure-docker --quiet

docker build -t volanty/${CONTAINER_NAME}:${BITBUCKET_COMMIT} ${DEPLOY_ARGS} .
docker tag volanty/${CONTAINER_NAME}:${BITBUCKET_COMMIT} us.gcr.io/volanty/${GCR_CONTAINER_NAME}:${BITBUCKET_COMMIT}
docker push us.gcr.io/volanty/${GCR_CONTAINER_NAME}:${BITBUCKET_COMMIT}
