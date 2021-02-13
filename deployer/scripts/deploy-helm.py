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
@click.option("--aws-key", "-k", default="K8S_PRD_AWS", help="the key that contain aws secrets")
@click.option("--aws-cluster", "-c", default="production", help="deploy arguments")
@click.option("--tag", "-t", default="BITBUCKET_COMMIT", help="tag to be applied to this deploy")
@click.option("--deploy_env", "-e", default="BITBUCKET_DEPLOYMENT_ENVIRONMENT", help="environment to be applied to this deploy")
@click.option("--deploy-type", "-d", default="gcp", help="type of deploy. Can be gcp, aws or multi")
def deploy_helm(chart_name, gcp_project, gcp_key, aws_key, aws_cluster, tag, deploy_env, deploy_type):
    """Tool to deploy k8s by helm."""
    try:
        gcp_key_base64 = os.getenv(gcp_key, "")
        if len(gcp_key_base64) == 0: raise ValueError("The value of gcp-key is empty.")
        sh("echo \"{gcp_key}\" | base64 -d >> {key_file}".format(gcp_key=gcp_key_base64, key_file=GOOGLE_APPLICATION_CREDENTIALS))
        setup_gcp_account(gcp_project, GOOGLE_APPLICATION_CREDENTIALS)
        chart_file = helm_package_and_push(chart_name, tag, deploy_env)
        if deploy_type in ["GCP", "MULTI"]:
            gcp_deploy(chart_name, chart_file)
        if deploy_type in ["GCP", "MULTI"]:
            gcp_deploy(chart_name, chart_file)
        click.echo("Image pushed successfully")
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        exit(1)

def gcp_deploy(chart_name, chart_file):
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
    sh(f"helm package --app-version "{app_version}" ${base_chart}
    result = subprocess.run(f"helm package --app-version {app_version} {base_chart}", shell=True, check=True, capture_output=True)
    chart_file = result.stdout.decote().split(" ")[-1]
    click.echo("Pushing $chart_file...")
    sh(f"helm gcs push {chart_file} private --force")
    return chart_file


if __name__ == '__main__':
    push_image()