# FastqWiper
[![Build status](https://ci.appveyor.com/api/projects/status/y09medho67x2nrgn?svg=true)](https://ci.appveyor.com/project/mazzalab/fastqwiper) [![GitHub issues](https://img.shields.io/github/issues-raw/mazzalab/fastqwiper)](https://github.com/mazzalab/fastqwiper/issues) ![Docker Pulls](https://img.shields.io/docker/pulls/mazzalab/fastqwiper)

[![Anaconda-Server Badge](https://anaconda.org/bfxcss/fastqwiper/badges/version.svg)](https://anaconda.org/bfxcss/fastqwiper) [![Anaconda-Server Badge](https://anaconda.org/bfxcss/fastqwiper/badges/latest_release_date.svg)](https://anaconda.org/bfxcss/fastqwiper) [![Anaconda-Server Badge](https://anaconda.org/bfxcss/fastqwiper/badges/platforms.svg)](https://anaconda.org/bfxcss/fastqwiper) [![Anaconda-Server Badge](https://anaconda.org/bfxcss/fastqwiper/badges/downloads.svg)](https://anaconda.org/bfxcss/fastqwiper)

`FastqWiper` is a Snakemake-enabled application that wipes out bad reads from broken FASTQ files. The available and pre-designed workflows allows **recovering** corrupted `fastq.gz`, **dropping** or **fixing** pesky lines, **removing** unpaired reads, and **fixing** reads interleaving. More complex workflows, as **recover** corrupted `fastq.gz`, **dropping** or **fixing** pesky lines, **removing** unpaired reads, and **fixing** reads interleaving, can be executed using Snakemake and the preconfigured [pipeline files](https://github.com/mazzalab/fastqwiper/tree/main/pipeline) provided here.

* Compatibility: Python 3.8
* OS: Windows (through Docker), Linux, Mac OS
* Contributions: [bioinformatics@css-mendel.it](bioinformatics@css-mendel.it)
* Docker: https://hub.docker.com/r/mazzalab/fastqwiper
* Bug report: [https://github.com/mazzalab/fastqwiper/issues](https://github.com/mazzalab/fastqwiper/issues)


## Installation
There is an <b>easy</b> and a <b>hard</b> way to install and use `FastqWiper`. 

### The easy way (Docker, all OS)
1. Pull the Docker image available from DockerHub:

`docker pull mazzalab/fastqwiper`

2. Once downloaded the image, you can type:

`docker run --rm -ti --name fastqwiper -v "YOUR_LOCAL_PATH_TO_DATA_FOLDER:/fastqwiper/data" mazzalab/fastqwiper paired 8 sample`

where:

- `YOUR_LOCAL_PATH_TO_DATA_FOLDER` is the path to the folder where the fastq.gz files to be wiped are located;
- `paired` triggers the cleaning of R1 and R2. Alternatively, `single` will trigger the wiping of individual FASTQ files;
- `8` is the number of computing cores to be spawned;
- `sample` is part of the names of the FASTQ files to be wiped. <b>Be aware</b> that: for <b>paired-end</b> files (e.g., "sample_R1.fastq.gz" and "sample_R2.fastq.gz"), your files must finish with `_R1.fastq.gz` and `_R2.fastq.gz`. Therefore, the argument to pass is everything <u>before</u> these texts: `sample` in this case. For <b>single end</b>/individual files (e.g., "excerpt_R1_001.fastq.gz"), your file must end with the string `.fastq.gz`; the preceding text, i.e., "excerpt_R1_001" in this case, will be the text to be passed to the command as an argument. E.g., 

`docker run --rm -ti --name fastqwiper -v "YOUR_LOCAL_PATH_TO_DATA_FOLDER:/fastqwiper/data" mazzalab/fastqwiper single 8 excerpt_R1_001`

### The hard way (Linux only)
To enable the use of preconfigured [pipelines](https://github.com/mazzalab/fastqwiper/tree/main/pipeline), you need to install **Snakemake**. The recommended way to install Snakemake is via Conda, because it enables **Snakemake** to [handle software dependencies of your workflow](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#integrated-package-management).
However, the default conda solver is slow and often hangs. Therefore, we recommend installing [Mamba](https://github.com/mamba-org/mamba) as a drop-in replacement via

`$ conda install -c conda-forge mamba`

and then creating and activating a clean environment as above:

```
$ mamba create -c conda-forge -c bioconda -n FastqWiper snakemake
$ conda activate FastqWiper
$ conda install colorama click
$ conda install mamba -c conda-forge
```


### Usage
Clone the FastqWiper repository:

`git clone https://github.com/mazzalab/fastqwiper.git`.

It contains, in particular, a folder `data` containing the fastq files to be processed, a folder `pipeline` containing the released pipelines and a folder `fastq_wiper` with the source files of `FastqWiper`. <br/>
Input files to be processed should be copied into the **data** folder. All software packages not fetched from `Conda` and used by the pipelines should be copied, even if it is not strictly mandatory, in the root directory of the cloned repository. 

Currently, to run the `FastqWiper` pipelines, the following packages are not included in `Conda` but are required:

### required packages:
[gzrt](https://github.com/arenn/gzrt) (install [instructions](https://github.com/arenn/gzrt/blob/master/README.build))

[BBTools](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/) (install [instructions](https://jgi.doe.gov/data-and-tools/software-tools/bbtools/bb-tools-user-guide/installation-guide/))

```
$ cd fastqwiper
$ git clone https://github.com/arenn/gzrt.git
$ cd gzrt
$ make
$ cd ..
$ cd fastqwiper
$ tar -xvzf BBMap_(version).tar.gz
```

### Commands:
#### Paired-end files
- **Personalize a pipeline**. Using `fix_wipe_pairs_reads.smk` requires you to edit line 3 of the file with the name of the fastq files stored in `data` folder that you want to process. If the files were:
```
excerpt_S1_R1_001.fastq.gz
excerpt_S1_R2_001.fastq.gz
sample_S1_R1_001.fastq.gz
sample_S1_R2_001.fastq.gz
```
the SAMPLE vector should be: `SAMPLES = ["sample", "excerpt"]`

- **Get a dry run** of a pipeline (e.g., `fix_wipe_pairs_reads.smk`):<br />
`snakemake -s pipeline/fix_wipe_pairs_reads.smk --use-conda --cores 2 -np`

- **Generate the planned DAG**:<br />
`snakemake -s pipeline/fix_wipe_pairs_reads.smk --dag | dot -Tpdf > dag.pdf`<br />
<img src="https://github.com/mazzalab/fastqwiper/blob/main/pipeline/fix_wipe_pairs_reads.png?raw=true" width="400">

- **Run the pipeline** (n.b., during the first execution, Snakemake will download and install some required remote packages and may take longer). The number of computing cores can be tuned accordingly:<br />
`snakemake -s pipeline/fix_wipe_pairs_reads.smk --use-conda --cores 2`

Fixed files will be copied in the `data` folder and will be suffixed with the string `_fixed_wiped_paired_interleaving`.
We remind that the `fix_wipe_pairs_reads.smk` pipeline performs the following actions:
- execute `gzrt` on corrupted fastq.gz files (i.e., that cannot be unzipped because of errors) and recover readable reads;
- execute `fastqwiper` on recovered reads to make them compliant with the FASTQ format (source: [Wipipedia](https://en.wikipedia.org/wiki/FASTQ_format))
- execute `Trimmomatic` on wiped reads to remove residual unpaired reads
- execute `BBmap (repair.sh)` on paired reads to fix the correct interleaving and sort fastq files.  

#### Single-end files
Using `fix_wipe_pairs_reads.smk` requires you to make the same edits as above. This pipeline will not execute 
`trimmomatic` and BBmap's `repair.sh`.

- **Get a dry run** of a pipeline (e.g., `fix_wipe_single_reads.smk`):<br />
`snakemake -s pipeline/fix_wipe_single_reads.smk --use-conda --cores 2 -np`

- **Generate the planned DAG**:<br />
`snakemake -s pipeline/fix_wipe_single_reads.smk --dag | dot -Tpdf > dag.pdf`<br />
<img src="https://github.com/mazzalab/fastqwiper/blob/main/pipeline/fix_wipe_single_reads.png?raw=true" width="200">

- **Run the pipeline** (n.b., during the first execution, Snakemake will download and install some required remote 
  packages and may take longer). The number of computing cores can be tuned accordingly:<br />
`snakemake -s pipeline/fix_wipe_single_reads.smk --use-conda --cores 2`

# Author
**Tommaso Mazza**  
[![Tweeting](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/irongraft)

Laboratory of Bioinformatics</br>
Fondazione IRCCS Casa Sollievo della Sofferenza</br>
Viale Regina Margherita 261 - 00198 Roma IT</br>
Tel: +39 06 44160526 - Fax: +39 06 44160548</br>
E-mail: t.mazza@css-mendel.it</br>
Web page: http://www.css-mendel.it</br>
Web page: http://bioinformatics.css-mendel.it</br>
