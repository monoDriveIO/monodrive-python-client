# syntax=docker/dockerfile:experimental

# docker image to run simple collision prediction UUT example
FROM ubuntu:18.04 as build
MAINTAINER support@monodrive.io

# setup
ENV BASE_DIR /home/build
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR ${BASE_DIR}
RUN apt-get update && \
    apt-get install -y wget git openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# miniconda
RUN mkdir ${BASE_DIR}/dump
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ${BASE_DIR}/dump/miniconda.sh
RUN /bin/bash ${BASE_DIR}/dump/miniconda.sh -b -p /opt/conda

# add known host for github
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

# create environment
COPY environment.yml ${BASE_DIR}/environment.yml
RUN --mount=type=ssh /opt/conda/bin/conda env create -f ${BASE_DIR}/environment.yml

# runtime
FROM ubuntu:18.04

# setup
ENV BASE_DIR /home/uut

# grab environment
COPY --from=build /opt/conda/envs/uut-collision /opt/conda/envs/uut-collision

# add UUT source
COPY main.py ${BASE_DIR}/main.py

# activate environment
ENV PATH /opt/conda/envs/uut-collision/bin:$PATH

# runtime
WORKDIR ${BASE_DIR}
CMD ["python", "-u", "/home/uut/main.py", "--cloud", "--assets", "/mdassets"]
