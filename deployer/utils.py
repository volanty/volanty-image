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