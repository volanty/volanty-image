#!/usr/bin/env python3

import subprocess
import sys
import click
import os

from ..utils import *

@click.command(context_settings={'show_default': True})
@click.argument("name")
@click.argument("tag")
@click.argument("gcp-project")
@click.argument("gcp-credentials", default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
@click.option("--base-repo", "-b", default="us.gcr.io/volanty", help="docker base repository")
@click.option("--deploy-args", "-a", default="", help="deploy arguments")
def push_image(name, tag, gcp_project, gcp_credentials, base_repo, deploy_args):
    """Tool to push your docker image to grc."""
    try:
        setup_gcp_account(gcp_project, gcp_credentials)
        push_docker_image(base_repo, name, tag, deploy_args)
        click.echo("Image pushed successfully")
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    push_image()