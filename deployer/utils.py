import subprocess

def sh(cmd):
    subprocess.run(cmd, shell=True, check=True)

def setup_gcp_account(gcp_project, gcp_credentials_file):
    sh(f"gcloud auth activate-service-account --key-file {gcp_credentials_file} --quiet")
    sh(f"gcloud config set project {gcp_project} --quiet")
    sh(f"gcloud container clusters get-credentials elasticsearch-cluster --zone us-central1-a --project {gcp_project}")

def push_docker_image(base, name, tag, args):
    sh("gcloud auth configure-docker --quiet")
    sh(f"docker build -t ${base}/{name}:{tag} {args} .")
    sh(f"docker push ${base}/{name}:{tag}")

def setup_aws_account(aws_credential_string):
    aws_access_key_id, aws_secret_access_key, region = aws_credentials_to_dict(aws_credential_string)
    sh(f"aws configure set aws_access_key_id {aws_access_key_id}")
    sh(f"aws configure set aws_secret_access_key {aws_secret_access_key}")
    sh(f"aws configure set default.region {region}")    

def aws_credentials_to_dict(aws_credential_string):
    list_credentials = list(map(lambda x: tuple(x.split("=")), aws_credential_string.split(";")))
    return dict(list_credentials)