FROM google/cloud-sdk
COPY ./scripts .
RUN ./install-helm.sh
RUN apt install unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN apt install python3-pip
RUN pip3 install --editable .
COPY scripts/release.sh /usr/bin/release
RUN chmod +x /usr/bin/release
