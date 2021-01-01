# FastqWiper
A workflow to **recover** corrupted `fastq.gz` files, **drop** wrong lines and **remove** unpaired reads.

* Compatibility: Python >3.7
* OS: Windows (partly), Linux, Mac OS
* Contributions: [bioinformatics@css-mendel.it](bioinformatics@css-mendel.it)
* Pypi: available soon
* Conda: available soon
* Docker Hub: available soon
* Bug report: [https://github.com/mazzalab/fastqwiper/issues](https://github.com/mazzalab/fastqwiper/issues)


## Installation
FastqWiper can be installed using both Conda and PyPi and runs smoothly on all OS 
specified above.

### Anaconda or Miniconda
Create and activate an empty Conda environment, if not already available.<br/>
```
$ conda create -n FastqWiper python=3.9
$ conda activate FastqWiper
```

then<br/>
`$ conda install -y -c bfxcss -c conda-forge fastqwiper`

### Pypi
_available soon_


### Snakemake
To enable the use of preconfigured workflows, you need to install **Snakemake**. The 
recommended way to install Snakemake is via Conda, because it enables **Snakemake** to 
[handle software dependencies of your workflow](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#integrated-package-management).
However, the default conda solver is slow and often hungs. Therefore, we recommend 
installing [Mamba](https://github.com/mamba-org/mamba) as a drop-in replacement via

`$ conda install -c conda-forge mamba`

and then creating and activating a clean environment as above:

```
$ mamba create -c conda-forge -c bioconda -n FastqWiper snakemake
$ conda activate FastqWiper
```

and finally:<br/>
`conda install -y -c bfxcss -c conda-forge fastqwiper`

 
