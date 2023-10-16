#cmd: snakemake --config sample_name=sample_R1 chunk_size=50000000 -s pipeline/fix_wipe_single_reads_parallel.smk --use-conda --cores 4

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
        "Dropping unreadable reads from {input}."
    shell:
        "gzrecover -o {output} {input} -v 2> {log}"


# this shall trigger re-evaluation of the DAG
checkpoint split_fastq:
    input:
        "data/{sample}_fixed.fastq"
    output:
        directory("data/{sample}_chunks")
    params:
        chunk_size=config["chunk_size"]
    message: 
        "Splitting {input} into chunks."
    shell:'''
        mkdir data/{wildcards.sample}_chunks
        split -l {params.chunk_size} --numeric-suffixes {input} data/{wildcards.sample}_chunks/chunk --additional-suffix=.fastq
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
        "fastqwiper --fastq_in {input} --fastq_out {output} --log_out ./data/{sample}_chunks/{sample}_final_summary.txt 2> {log}"
    

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

    if os.path.isdir(f"data/{SAMPLE}_chunks"):
        shutil.rmtree(f"data/{SAMPLE}_chunks")
    
    if os.path.isfile(f"data/{SAMPLE}_fixed.fastq"):
        os.remove(f"data/{SAMPLE}_fixed.fastq")