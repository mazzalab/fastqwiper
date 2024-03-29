#!/bin/bash

mode=$1
cores=$(($2))
sample_name=$3
chunk_size=$(($4))

# Enter the FastqWiper folder
cd /fastqwiper

if [ $mode == "paired" ]
then
  if [ $cores -gt 1 ]
  then
    echo "Processing paired-end files in parallel"
    snakemake --config sample_name=$sample_name chunk_size=$chunk_size -s ./pipeline/fix_wipe_pairs_reads_parallel.smk --use-conda --cores $cores
  else
    echo "Processing paired-end files sequentially"
    snakemake --config sample_name=$sample_name -s ./pipeline/fix_wipe_pairs_reads_sequential.smk --use-conda --cores $cores
  fi
elif [ $mode == "single" ]
then
  if [ $cores -gt 1 ]
  then
    echo "Processing single-end file in parallel"
    snakemake --config sample_name=$sample_name chunk_size=$chunk_size -s ./pipeline/fix_wipe_single_reads_parallel.smk --use-conda --cores $cores
  else
    echo "Processing single-end file sequentially"
    snakemake --config sample_name=$sample_name -s ./pipeline/fix_wipe_single_reads_sequential.smk --use-conda --cores $cores
  fi
else
  echo "Snakemake help"
  snakemake --help
fi
