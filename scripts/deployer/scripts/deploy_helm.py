#!/usr/bin/env python3

import subprocess
import sys
import click
import os

from ..utils import *

@click.command(context_settings={'show_default': True})
@click.argument("chart-name")
@click.argument("gcp-project")
@click.argument("gcp-credentials", default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
@click.argument("tag", default=os.getenv("BITBUCKET_COMMIT"))
@click.argument("deploy-env", default=os.getenv("BITBUCKET_DEPLOYMENT_ENVIRONMENT"))
@click.option("--gcp-cluster", "-g", default="elasticsearch-cluster", help="gcp k8s cluster name")
@click.option("--aws-credentials", "-c", default="/tmp/aws-credentials.json", help="the aws credentials csv file")
@click.option("--aws-region", "-r", default="us-west-2", help="the aws region")
@click.option("--aws-cluster", "-a", default="production", help="aws k8s cluster name")
@click.option("--deploy-type", "-d", default="gcp", help="type of deploy. Can be gcp, aws or multi")
@click.option("--gcp-zone", "-r", default="us-central1-a", help="the gcp zone")
def deploy_helm(chart_name, gcp_project, gcp_credentials, tag, deploy_env, gcp_cluster, aws_credentials, aws_region, aws_cluster, deploy_type, gcp_zone):
    """Tool to deploy k8s by helm."""
    try:
        click.echo(f"Trying deploy {chart_name}, gcp project: {gcp_project}, gcp-cred: {gcp_credentials}, tag: {tag}, deploy env: {deploy_env}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_credentials
        setup_gcp_account(gcp_project, gcp_credentials)
        chart_file = helm_package_and_push(chart_name, tag, deploy_env)
        if deploy_type in ["gcp", "multi"]:
            install_helm_on_gcp(gcp_project, gcp_cluster, gcp_zone, chart_name, chart_file)
        if deploy_type in ["aws", "multi"]:
           install_helm_on_aws(aws_credentials, aws_region, aws_cluster, chart_name, chart_file)
        click.echo("Image pushed successfully")
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        exit(1)

def install_helm_on_gcp(gcp_project, gcp_cluster, gcp_zone, chart_name, chart_file):
    sh(f"gcloud container clusters get-credentials {gcp_cluster} --zone {gcp_zone} --project {gcp_project}")
    install_helm(chart_name, chart_file)

def install_helm_on_aws(aws_credentials, aws_region, aws_cluster, chart_name, chart_file):
    setup_aws_account(aws_credentials, aws_region)
    sh(f"aws eks update-kubeconfig --name {aws_cluster}")
    install_helm(chart_name, chart_file)

def install_helm(chart_name, chart_file):
    click.echo(f"Helm deploy {chart_name} {chart_file}")
    sh(f"helm upgrade {chart_name} {chart_file} --install")

def helm_package_and_push(chart_name, app_version, deploy_env):
    gcs_bucket_name = f"gs://volanty-charts-{deploy_env}/{chart_name}"
    base_chart = f"./helm/{chart_name}"
    os.rename(f"{base_chart}/values-{deploy_env}.yaml", f"{base_chart}/values.yaml")
    click.echo("Initializing helm repo")
    sh(f"helm gcs init {gcs_bucket_name}")
    click.echo(f"Adding gcs bucket repo {gcs_bucket_name}")
    sh(f"helm repo add private {gcs_bucket_name}")
    sh(f"helm repo index . --url {gcs_bucket_name}")
    sh(f"helm package --app-version {app_version} {base_chart}")
    result = subprocess.run(f"helm package --app-version {app_version} {base_chart}", shell=True, check=True, capture_output=True)
    chart_file = result.stdout.decode().split(" ")[-1].strip()
    click.echo(f"Pushing {chart_file}...")
    sh(f"helm gcs push {chart_file} private --force")
    return chart_file


if __name__ == '__main__':
    deploy_helm()