FROM google/cloud-sdk

RUN curl -L https://storage.googleapis.com/scripts.volanty.com/install-helm.sh | bash -
RUN apt install unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
COPY scripts/release.sh /usr/bin/release
RUN chmod +x /usr/bin/release