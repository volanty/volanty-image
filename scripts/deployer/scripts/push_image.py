#!/usr/bin/env python3

import subprocess
import sys
import click
import os

from ..utils import *

GOOGLE_APPLICATION_CREDENTIALS="/tmp/key-file.json"

@click.command(context_settings={'show_default': True})
@click.argument("name")
@click.argument("tag")
@click.argument("gcp-project")
@click.argument("gcp-key")
@click.option("--base-repo", "-b", default="us.gcr.io", help="docker base repository")
@click.option("--deploy-args", "-a", default="", help="deploy arguments")
def push_image(base_repo, deploy_args, name, tag, gcp_project, gcp_key):
    """Tool to push your docker image to grc."""
    try:
        gcp_key_base64 = os.getenv(gcp_key, "")
        if len(gcp_key_base64) == 0: raise ValueError("The value of gcp-key is empty.")
        sh("echo \"{gcp_key}\" | base64 -d >> {key_file}".format(gcp_key=gcp_key_base64, key_file=GOOGLE_APPLICATION_CREDENTIALS))
        setup_gcp_account(gcp_project, GOOGLE_APPLICATION_CREDENTIALS)
        push_docker_image(base_repo, name, tag, deploy_args)
        click.echo("Image pushed successfully")
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    push_image()