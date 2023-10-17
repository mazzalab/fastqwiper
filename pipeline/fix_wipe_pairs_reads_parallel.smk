#cmd: snakemake --config sample_name=sample chunk_size=50000000 -s ./pipeline/fix_wipe_pairs_reads_parallel.smk --use-conda --cores 4

import os
import shutil
from snakemake.io import expand, temp

SAMPLE=config["sample_name"]

rule all:
    input: 
        expand("data/{s}_R{r}_fixed_wiped_paired_interleaving.fastq.gz", s = SAMPLE, r = [1, 2])

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
    shell:'''
        fastqwiper --fastq_in {input} --fastq_out {output} --log_out data/{wildcards.sample}_chunks/{wildcards.sample}_final_summary.txt --log_frequency 300 2> {log}
        ''''

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
        temp("data/{sample}_fixed_wiped.fastq.gz")
    message: 
        "Gathering cleaned chunks."
    shell:
        "cat {input} > {output}"

rule drop_unpaired:
    input:
        r1 = "data/{sample}_R1_fixed_wiped.fastq.gz",
        r2 = "data/{sample}_R2_fixed_wiped.fastq.gz"
    output:
        r1 = temp("data/{sample}_R1_fixed_wiped_paired.fastq.gz"),
        r2 = temp("data/{sample}_R2_fixed_wiped_paired.fastq.gz"),
        r1_unpaired = temp("data/{sample}_R1_fixed_wiped_unpaired.fastq.gz"),
        r2_unpaired = temp("data/{sample}_R2_fixed_wiped_unpaired.fastq.gz")
    log:
        "logs/pairing/pairing.{sample}.log"
    message:
        "Dropping unpaired reads from {input}"
    threads:
        workflow.cores
    shell:
        "trimmomatic PE {input.r1} {input.r2} {output.r1} {output.r1_unpaired} {output.r2} {output.r2_unpaired} MINLEN:20"

rule fix_interleaving:
    input:
        in1 = "data/{sample}_R1_fixed_wiped_paired.fastq.gz",
        in2 = "data/{sample}_R2_fixed_wiped_paired.fastq.gz"
    output:
        out1 = "data/{sample}_R1_fixed_wiped_paired_interleaving.fastq.gz",
        out2 = "data/{sample}_R2_fixed_wiped_paired_interleaving.fastq.gz"
    log:
        "logs/pairing/pairing.{sample}.log"
    message:
        "Repair reads interleaving from {input}."
    threads:
        1
    cache: False
    shell:
        "bbmap/repair.sh in={input.in1} in2={input.in2} out={output.out1} out2={output.out2} outsingle=singletons.fastq.gz 2> {log}"

onsuccess:
    print("Workflow finished, no error. Clean-up and shutdown")

    if os.path.isdir(f"data/{SAMPLE}_R1_chunks"):
        shutil.rmtree(f"data/{SAMPLE}_R1_chunks")
    
    if os.path.isdir(f"data/{SAMPLE}_R2_chunks"):
        shutil.rmtree(f"data/{SAMPLE}_R2_chunks")

    if os.path.isfile(f"data/{SAMPLE}_R1_fixed.fastq"):
        os.remove(f"data/{SAMPLE}_R1_fixed.fastq")
    
    if os.path.isfile(f"data/{SAMPLE}_R2_fixed.fastq"):
        os.unlink(f"data/{SAMPLE}_R2_fixed.fastq")