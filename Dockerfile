FROM condaforge/mambaforge
LABEL maintainer="mazza.tommaso@gmail.com"

ENV bbmap_version 39.01
ENV PATH "$PATH:/tmp/jre1.8.0_161/bin/"

# RUN conda install -c conda-forge mamba
RUN mamba install -c conda-forge -c bioconda snakemake -y
RUN mamba install -c conda-forge colorama click -y

RUN apt update
RUN apt install git
RUN git clone https://github.com/mazzalab/fastqwiper.git

RUN apt-get install gzrt -y
ADD https://sourceforge.net/projects/bbmap/files/BBMap_39.01.tar.gz/download /fastqwiper/BBMap_${bbmap_version}.tar.gz
RUN cd fastqwiper &&\
    tar -xvzf BBMap_${bbmap_version}.tar.gz &&\
    rm BBMap_${bbmap_version}.tar.gz &&\
    rm -rf .vscode conda-recipe &&\
    rm environment.yml requirements.txt setup.py .gitignore README.md appveyor.yml

ADD http://javadl.oracle.com/webapps/download/AutoDL?BundleId=230532_2f38c3b165be4555a1fa6e98c45e0808 /tmp/java.tar.gz
RUN cd /tmp/ &&\
	tar xvzf java.tar.gz

WORKDIR /fastqwiper

COPY run_wiping.sh run_wiping.sh

ENTRYPOINT ["/fastqwiper/run_wiping.sh"]
CMD ["paired", "4"]

# ENTRYPOINT echo "Welcome to the Computational Genomics lesson"
# docker build -t test .
# docker run --rm -ti --name test -d -v "D:\desktop_links\CSS-Bioinformatics\FastqWiper\FastqWiper\data:/fastqwiper/data" -v "D:\desktop_links\CSS-Bioinformatics\FastqWiper\FastqWiper\pipeline:/fastqwiper/pipeline" test paired 8
# docker exec -ti test /bin/bash