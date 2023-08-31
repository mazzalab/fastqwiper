FROM condaforge/mambaforge
LABEL maintainer="mazza.tommaso@gmail.com"

ENV bbmap_version 39.01
ENV PATH "$PATH:/tmp/jre1.8.0_161/bin/"

# Downgrade Python to 3.8
RUN mamba install python=3.10
# RUN mamba install tabulate=0.8.10

# RUN conda install -c conda-forge mamba
# RUN mamba install -c conda-forge -c bioconda snakemake=7.25.0 -y
RUN mamba install -c conda-forge -c bioconda snakemake=7.32.3 -y
RUN mamba install -c conda-forge colorama click -y

# Install fastqwiper from conda
RUN mamba install -y -c bfxcss -c conda-forge fastqwiper

# Install gzrt, BBmap, and Java
RUN apt update
RUN apt-get install gzrt -y
ADD https://sourceforge.net/projects/bbmap/files/BBMap_39.01.tar.gz/download /fastqwiper/BBMap_${bbmap_version}.tar.gz
RUN cd fastqwiper &&\
    tar -xvzf BBMap_${bbmap_version}.tar.gz &&\
    rm BBMap_${bbmap_version}.tar.gz 
ADD http://javadl.oracle.com/webapps/download/AutoDL?BundleId=230532_2f38c3b165be4555a1fa6e98c45e0808 /tmp/java.tar.gz
RUN cd /tmp/ &&\
	tar xvzf java.tar.gz

WORKDIR /fastqwiper

COPY run_wiping.sh run_wiping.sh
COPY pipeline pipeline

## PAIRED
# file names like: "sample_R1.fastq.gz" and "sample_R2.fastq.gz"
# Then, keep the "_R1.fastq.gz" and ""_R2.fastq.gz"" parts of the file names fixed and vary only the prepending text

## SINGLE
# file names like: "excerpt_R1_001.fastq.gz"
# Then, keep the ".fastq.gz" part of the file name fixed and vary only the prepending text (i.e., "excerpt_R1_001")
ENTRYPOINT ["/fastqwiper/run_wiping.sh"]
CMD ["paired", "4", "sample"]

# docker build -t test .
# docker run --rm -ti --name test -v "D:\desktop_links\CSS-Bioinformatics\FastqWiper\FastqWiper\data:/fastqwiper/data" test paired 8 sample
# docker exec -ti test /bin/bash