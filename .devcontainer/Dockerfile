FROM condaforge/mambaforge
LABEL maintainer="mazza.tommaso@gmail.com"

COPY data data
COPY ./.devcontainer/environment.yml environment.yml

RUN mamba env update --file environment.yml --name base
RUN git config --global core.autocrlf true

WORKDIR /fastqwiper
