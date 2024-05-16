FROM condaforge/mambaforge
LABEL maintainer="mazza.tommaso@gmail.com"

ENV bbmap_version 39.01
ENV PATH "$PATH:/tmp/jre1.8.0_161/bin/"

# RUN mamba config --set channel_priority strict
RUN mamba install python=3.10
RUN mamba install -c conda-forge -c bioconda snakemake=7.32.3 -y
RUN mamba install -c conda-forge colorama click -y
RUN mamba install -c bioconda trimmomatic -y

# Install fastqwiper from conda
RUN mamba install -y -c bfxcss -c conda-forge fastqwiper

# Install gzrt, BBmap, and Java
RUN apt update
RUN apt-get install gzrt -y
ADD https://sourceforge.net/projects/bbmap/files/BBMap_${bbmap_version}.tar.gz/download /fastqwiper/BBMap_${bbmap_version}.tar.gz
RUN cd fastqwiper &&\
    tar -xvzf BBMap_${bbmap_version}.tar.gz &&\
    rm BBMap_${bbmap_version}.tar.gz 
ADD http://javadl.oracle.com/webapps/download/AutoDL?BundleId=230532_2f38c3b165be4555a1fa6e98c45e0808 /tmp/java.tar.gz
RUN cd /tmp/ &&\
	tar xvzf java.tar.gz

WORKDIR /fastqwiper

COPY pipeline pipeline
COPY run_wiping.sh run_wiping.sh
RUN chmod +x run_wiping.sh


ENTRYPOINT ["/fastqwiper/run_wiping.sh"]
# paired mode, 4 cores, sample name, #rows-per-chunk, ASCII offset (33=Sanger, 64=old Solexa)
CMD ["paired", "4", "sample", "50000000", "33"]

# docker build -t test .
# docker run --rm -ti --name test -v "D:\desktop_links\CSS-Bioinformatics\FastqWiper\FastqWiper\data:/fastqwiper/data" test paired 8 sample 50000000
# docker exec -ti test /bin/bash