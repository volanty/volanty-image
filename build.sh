#!/usr/bin/env bash
docker build . -t volanty/volanty-image:latest
docker push volanty/volanty-image:latest