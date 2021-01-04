# FastqWiper
[![Build status](https://ci.appveyor.com/api/projects/status/y09medho67x2nrgn?svg=true)](https://ci.appveyor.com/project/mazzalab/fastqwiper)
[![GitHub issues](https://img.shields.io/github/issues-raw/mazzalab/fastqwiper)](https://github.com/mazzalab/fastqwiper/issues)

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
[![PyPI version](https://badge.fury.io/py/fastqwiper.svg)](https://badge.fury.io/py/fastqwiper)

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


### Usage
Clone the FastqWiper repository:

`git clone https://github.com/mazzalab/fastqwiper.git`.

It contains, in particular, a folder `data` containing the fastq files to be processed, a folder `pipeline` containing the released pipeline and a folder `fastq_wiper` with the source files of FastqWiper. Copy further fastq files to be processed into the **data** folder. All software packages not fetched from `Conda` and used by the pipelines should be copied, even if it is not strictly mandatory, in the root directory. 

Currently, to run the FastqWiper pipelines, the following packages are not included in `Conda` but are required:

### required packages:
[gzrt](https://github.com/arenn/gzrt) (install [instructions](https://github.com/arenn/gzrt/blob/master/README.build))
```
$ (within the FastqWiper root folder) git clone https://github.com/arenn/gzrt.git
$ cd gzrt
$ make
$ cd ..
```

### Commands:
- Personalize a pipeline: using, for example, `fix_wipe_pairs_reads.smk` requires you to edit line 3 of the file with the name of the fastq files stored in `data` folder that you want to process. If the files are:
```
excerpt_S1_R1_001.fastq.gz
excerpt_S1_R2_001.fastq.gz
sample_S1_R1_001.fastq.gz
sample_S1_R2_001.fastq.gz
```
the SAMPLE vector should be: `SAMPLES = ["sample", "excerpt"]`

- Get a dry run of a pipeline (e.g., `fix_wipe_pairs_reads.smk`):<br />
`snakemake -s pipeline/fix_wipe_pairs_reads.smk --use-conda --cores 2 -np`

- Generate the planned DAG:<br />
`snakemake -s pipeline/fix_wipe_pairs_reads.smk --dag -Tpdf > dag.pdf`<br />
<img src="https://github.com/mazzalab/fastqwiper/blob/main/pipeline/fix_wipe_pairs_reads.png?raw=true" width="600">

- Run the pipeline (n.b., during the first execution, Snakemake will download and install some required remote 
  packages and may take longer). The number of computing cores can be tuned accordingly:<br />
`snakemake -s pipeline/fix_wipe_pairs_reads.smk --use-conda --cores 2`

Fixed files will be copied in the `data` folder and will be suffixed with the string `_fixed_wiped_paired`. We remind 
that the `fix_wipe_pairs_reads.smk` pipeline performs the following actions:
- execute `gzrt` on corrupted fastq.gz files (i.e., that cannot be unzipped because of errors) and recover readable reads;
- execute `fastqwiper` on recovered reads to make them compliant with the FASTQ format (source: [Wipipedia](https://en.wikipedia.org/wiki/FASTQ_format))
- execute `trimmomatic` on wiped reads to remove residual unpaired reads 


# Author
**Tommaso Mazza**  
![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2Firongraft)

Laboratory of Bioinformatics<br/>
Fondazione IRCCS Casa Sollievo della Sofferenza<br/>
Viale Regina Margherita 261 - 00198 Roma IT<br/>
Tel: +39 06 44160526 - Fax: +39 06 44160548<br/>
E-mail: t.mazza@css-mendel.it <br/>
Web page: http://www.css-mendel.it <br/>
Web page: http://bioinformatics.css-mendel.it <br/>

