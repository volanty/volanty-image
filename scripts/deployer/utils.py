import subprocess

def sh(cmd):
    subprocess.run(cmd, shell=True, check=True)

def setup_gcp_account(gcp_project, gcp_credentials_file):
    sh(f"gcloud auth activate-service-account --key-file {gcp_credentials_file} --quiet")
    sh(f"gcloud config set project {gcp_project} --quiet")

def push_docker_image(base, name, tag, args):
    sh("gcloud auth configure-docker --quiet")
    sh(f"docker build -t {base}/{name}:{tag} {args} .")
    sh(f"docker push {base}/{name}:{tag}")

def setup_aws_account(aws_credentials_csv_file, region):
    sh(f"aws configure import --csv file://{aws_credentials_csv_file}")
    sh(f"aws configure set default.region {region}")    
