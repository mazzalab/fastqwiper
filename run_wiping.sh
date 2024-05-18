#!/bin/bash

if [ $# -eq 0 ]; then
  mode="paired"
  cores=4
  sample_name="sample"
  chunk_size=50000000
  qin=33

  echo "Running with custom arguments: " "$@"
elif [ $# -ge 3 ] && [ $# -le 5 ]; then
  mode=$1
  cores=$(($2))
  sample_name=$3

  # Optional
  chunk_size=$(($4))
  if [ "$chunk_size" -eq "0" ]; then
    chunk_size=50000000
  fi

  # Optional
  qin=$(($5))
  if [ "$qin" -eq "0" ]; then
    qin=33
  fi

  if [ "$mode" == "paired" ]; then
    if [ "$cores" -gt 1 ]; then
      echo "Processing paired-end files in parallel"
      snakemake --config sample_name=$sample_name chunk_size=$chunk_size qin=$qin -s ./pipeline/fix_wipe_pairs_reads_parallel.smk --use-conda --cores $cores
    else
      echo "Processing paired-end files sequentially"
      snakemake --config sample_name=$sample_name qin=$qin -s ./pipeline/fix_wipe_pairs_reads_sequential.smk --use-conda --cores $cores
    fi
  elif [ "$mode" == "single" ]; then
    if [ "$cores" -gt 1 ]; then
      echo "Processing single-end file in parallel"
      snakemake --config sample_name=$sample_name chunk_size=$chunk_size -s ./pipeline/fix_wipe_single_reads_parallel.smk --use-conda --cores $cores
    else
      echo "Processing single-end file sequentially"
      snakemake --config sample_name=$sample_name -s ./pipeline/fix_wipe_single_reads_sequential.smk --use-conda --cores $cores
    fi
  else
    echo "Allowed computing modes are: 'paired' or 'single'"
  fi
else
    echo "You must provide three + 2 optional arguments [computing mode ('paired' or 'single'), # of cores (int), sample name (string), chunk size (optional, int), ASCII offset (optional, 33 or 64)]"
    exit 1
fi
