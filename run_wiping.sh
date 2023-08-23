#!/bin/bash

mode=$1
cores=$(($2))

if [ $mode == "paired" ]
then
  echo "Processing paired-end files"
  snakemake -s pipeline/fix_wipe_pairs_reads.smk --use-conda --cores $cores
else
  echo "Processing single-end file"
  snakemake -s pipeline/fix_wipe_single_reads.smk --use-conda --cores $cores
fi