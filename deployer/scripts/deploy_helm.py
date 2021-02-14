#!/usr/bin/env python3

import subprocess
import sys
import click
import os

from ..utils import *

GOOGLE_APPLICATION_CREDENTIALS="/tmp/key-file.json"

@click.command(context_settings={'show_default': True})
@click.argument("chart-name")
@click.argument("gcp-project")
@click.argument("gcp-key")
@click.option("--gcp-cluster", "-g", default="elasticsearch-cluster", help="gcp k8s cluster name")
@click.option("--aws-key", "-k", default="K8S_PRD_AWS", help="the key that contain aws secrets")
@click.option("--aws-cluster", "-c", default="production", help="aws k8s cluster name")
@click.option("--tag", "-t", default="BITBUCKET_COMMIT", help="tag to be applied to this deploy")
@click.option("--deploy_env", "-e", default="BITBUCKET_DEPLOYMENT_ENVIRONMENT", help="environment to be applied to this deploy")
@click.option("--deploy-type", "-d", default="gcp", help="type of deploy. Can be gcp, aws or multi")

def deploy_helm(chart_name, gcp_project, gcp_key, aws_key, gcp_cluster, aws_cluster, tag, deploy_env, deploy_type):
    """Tool to deploy k8s by helm."""
    try:
        gcp_key_base64 = os.getenv(gcp_key, "")
        if len(gcp_key_base64) == 0: raise ValueError("The value of gcp-key is empty.")
        sh("echo \"{gcp_key}\" | base64 -d >> {key_file}".format(gcp_key=gcp_key_base64, key_file=GOOGLE_APPLICATION_CREDENTIALS))
        setup_gcp_account(gcp_project, GOOGLE_APPLICATION_CREDENTIALS)
        chart_file = helm_package_and_push(chart_name, tag, deploy_env)
        if deploy_type in ["GCP", "MULTI"]:
            install_helm_on_gcp(gcp_project, gcp_cluster, chart_name, chart_file)
        if deploy_type in ["AWS", "MULTI"]:
           install_helm_on_aws(aws_key, aws_cluster, chart_name, chart_file)
        click.echo("Image pushed successfully")
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        exit(1)

def install_helm_on_gcp(gcp_project, gcp_cluster, chart_name, chart_file):
    sh(f"gcloud container clusters get-credentials {gcp_cluster}-cluster --zone us-central1-a --project ${gcp_project}")
    install_helm(chart_name, chart_file)


def install_helm_on_aws(aws_key, aws_cluster, chart_name, chart_file):
    aws_key_env = os.getenv(aws_key, "")
    if len(aws_key_env) == 0: raise ValueError("The value of aws key is empty.")
    setup_aws_account(aws_key_env)
    sh(f"aws eks update-kubeconfig --name {aws_cluster}")
    install_helm(chart_name, chart_file)

def install_helm(chart_name, chart_file):
    click.echo("Deploy on GCP")
    sh(f"helm upgrade {chart_name} {chart_file} --install")

def helm_package_and_push(chart_name, app_version, deploy_env):
    gcs_bucket_name = f"gs://volanty-charts-{deploy_env}/{chart_name}"
    base_chart = "./helm/${chart_name}"
    click.echo("Initializing helm repo")
    sh(f"helm gcs init {gcs_bucket_name}")
    click.echo(f"Adding gcs bucket repo {gcs_bucket_name}")
    sh(f"helm repo add private {gcs_bucket_name}")
    sh(f"helm repo index . --url {gcs_bucket_name}")
    sh(f"helm package --app-version {app_version} {base_chart}")
    result = subprocess.run(f"helm package --app-version {app_version} {base_chart}", shell=True, check=True, capture_output=True)
    chart_file = result.stdout.decote().split(" ")[-1]
    click.echo("Pushing $chart_file...")
    sh(f"helm gcs push {chart_file} private --force")
    return chart_file


if __name__ == '__main__':
    deploy_helm()