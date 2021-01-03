# FastqWiper
`FastqWiper` is a Python application that wipes out wrong and uncompliant reads from FASTQ files. 

Complex workflows that join `FastqWiper` with other existing tools to **recover** corrupted `fastq.gz` 
files, **drop** wrong lines and **remove** unpaired reads can be run 
through Snakemake and the preconfigured 
[pipeline files](https://github.com/mazzalab/fastqwiper/tree/main/pipeline) provided here.

* Compatibility: Python <3.9
* OS: Windows (excluding pipelines), Linux, Mac OS
* Contributions: [bioinformatics@css-mendel.it](bioinformatics@css-mendel.it)
* Pypi: https://pypi.org/project/fastqwiper
* Conda: https://anaconda.org/bfxcss/fastqwiper
* Docker Hub: available soon
* Bug report: [https://github.com/mazzalab/fastqwiper/issues](https://github.com/mazzalab/fastqwiper/issues)


## Installation
`FastqWiper` alone can be installed using both Conda and PyPi and runs smoothly on all OS 
specified above.

### Anaconda or Miniconda
[![Anaconda-Server Badge](https://anaconda.org/bfxcss/fastqwiper/badges/version.svg)](https://anaconda.org/bfxcss/fastqwiper) [![Anaconda-Server Badge](https://anaconda.org/bfxcss/fastqwiper/badges/latest_release_date.svg)](https://anaconda.org/bfxcss/fastqwiper) [![Anaconda-Server Badge](https://anaconda.org/bfxcss/fastqwiper/badges/platforms.svg)](https://anaconda.org/bfxcss/fastqwiper) [![Anaconda-Server Badge](https://anaconda.org/bfxcss/fastqwiper/badges/downloads.svg)](https://anaconda.org/bfxcss/fastqwiper)

Create and activate an empty Conda environment, if not already available.<br/>
```
$ conda create -n FastqWiper python=3.8
$ conda activate FastqWiper
```

then<br/>
`$ conda install -y -c bfxcss -c conda-forge fastqwiper`

### Pypi
`pip install fastqwiper`

### Usage
`FastqWiper` - in the current release - accepts three parameters:
```
Options:
  --fastq_in TEXT          The input FASTQ file to be cleaned  [required]
  --fastq_out TEXT         The wiped FASTQ file                [required]
  --log_frequency INTEGER  The number of processed reads that you want to print a status message after
```
It  accepts in input and outputs `*.fastq` or `*.fastq.gz` files.


## Snakemake
To enable the use of preconfigured [pipelines](https://github.com/mazzalab/fastqwiper/tree/main/pipeline), you need to install **Snakemake**. The 
recommended way to install Snakemake is via Conda, because it enables **Snakemake** to 
[handle software dependencies of your workflow](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#integrated-package-management).
However, the default conda solver is slow and often hangs. Therefore, we recommend 
installing [Mamba](https://github.com/mamba-org/mamba) as a drop-in replacement via

`$ conda install -c conda-forge mamba`

and then creating and activating a clean environment as above:

```
$ mamba create -c conda-forge -c bioconda -n FastqWiper snakemake
$ conda activate FastqWiper
```

and finally:<br/>
`conda install -y -c bfxcss -c conda-forge fastqwiper`

### Usage

