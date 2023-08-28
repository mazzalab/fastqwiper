#cmd: snakemake --config sample_name=sample_R1 -s pipeline/fix_wipe_single_reads_parallel.smk --use-conda --cores 4

import os
import shutil

SAMPLE=config["sample_name"]

rule all:
    input:
        expand("data/{s}_fixed_wiped.fastq.gz", s=SAMPLE)


rule fix_gzrt:
    input:
        "data/{sample}.fastq.gz"
    output:
        temp("data/{sample}_fixed.fastq")
    log:
        "logs/fix_gzrt/fix_gzrt.{sample}.log"
    message: 
        "Executing gzrt on {input}."
    shell:
        "gzrecover -o {output} {input} -v 2> {log}"


# this shall trigger re-evaluation of the DAG
checkpoint split_fastq:
    input:
        "data/{sample}_fixed.fastq"
    output:
        directory("data/{sample}_chunks")
    message: 
        "Splitting {input} into chunks."
    shell:'''
        mkdir data/{wildcards.sample}_chunks
        split -l 2000 --numeric-suffixes {input} data/{wildcards.sample}_chunks/chunk --additional-suffix=.fastq
        '''
    

rule wipe_fastq_parallel:
    input:
        "data/{sample}_chunks/chunk{i}.fastq"
    output:
        "data/{sample}_chunks/chunk{i}.fastq_fixed_wiped.fastq.gz"
    log:
        "logs/wipe_fastq/wipe_fastq.{sample}.chunk{i}.fastq.log"
    message: 
        "Running FastqWiper on {input}."
    shell:
        "python fastq_wiper/wiper.py --fastq_in {input} --fastq_out {output} 2> {log}"
    

def aggregate_input(wildcards):
    checkpoint_output = checkpoints.split_fastq.get(**wildcards).output[0]
    
    return expand("data/{sample}_chunks/chunk{i}.fastq_fixed_wiped.fastq.gz",
        sample=wildcards.sample,
        i=glob_wildcards(os.path.join(checkpoint_output, "chunk{i}.fastq")).i)


# an aggregation over all produced clusters
rule aggregate:
    input:
        aggregate_input
    output:
        "data/{sample}_fixed_wiped.fastq.gz"
    message: 
        "Gathering cleaned chunks."
    shell:
        "cat {input} > {output}"

onsuccess:
    print("Workflow finished, no error. Clean-up and shutdown")
    shutil.rmtree(f"data/{SAMPLE}_chunks")
    os.unlink(f"data/{SAMPLE}_fixed.fastq")
    