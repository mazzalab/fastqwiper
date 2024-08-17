#cmd: snakemake --config sample_name=sample_R1 qin=33 alphabet=ACGTN log_freq=1000 chunk_size=500 -s pipeline/fix_wipe_single_reads_parallel.smk --use-conda --cores 4

import os
import shutil

SAMPLE=config["sample_name"]
ALPHABET=config["alphabet"]
LOG_FREQ=config["log_freq"]

scattergather:
    split=8

rule all:
    input:
        expand("data/{s}_fixed_wiped.fastq.gz", s=SAMPLE) #,
#        expand("data/{s}_final_summary.txt", s=SAMPLE)


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
#checkpoint split_fastq:
#    input:
#        "data/{sample}_fixed.fastq"
#    output:
#        directory("data/{sample}_chunks")
#    params:
#        chunk_size=config["chunk_size"]
#    message:
#        "Splitting {input} into chunks."
#    shell:'''
#        mkdir data/{wildcards.sample}_chunks
#        split -l {params.chunk_size} --numeric-suffixes {input} data/{wildcards.sample}_chunks/chunk --additional-suffix=.fastq
#        '''

rule split_fastq:
    input:
        "data/{sample}_fixed.fastq"
    output:
        scatter.split("data/{{sample}}_chunks/chunk{scatteritem}.fastq")
    params:
        split_total = workflow._scatter["split"]
    message:
        "Splitting {input} into chunks."
    shell:'''
       python fastq_wiper/split_fastq.py -f {input} -n {params.split_total} -o data/{wildcards.sample}_chunks -p chunk -s .fastq
       '''

# ruleorder: wipe_fastq_parallel > aggregate

rule wipe_fastq_parallel:
    input:
        "data/{sample}_chunks/chunk{scatteritem}.fastq"
    output:
        "data/{sample}_chunks/chunk{scatteritem}.fastq_fixed_wiped.fastq.gz"
    log:
        "logs/wipe_fastq/wipe_fastq.{sample}.chunk{scatteritem}.fastq.log"
    message: 
        "Running FastqWiper on {input}."
    shell:'''
        fastqwiper --fastq_in {input} --fastq_out {output} --log_out data/{wildcards.sample}_chunks/{wildcards.sample}_{wildcards.scatteritem}_summary.txt --alphabet {ALPHABET} --log_frequency {LOG_FREQ} 2> {log}
        '''

rule gather:
    input:
        gather.split("data/{{sample}}_chunks/chunk{scatteritem}.fastq_fixed_wiped.fastq.gz")
#        gather.split("split/{scatteritem}.post.txt")
    output:
        "data/{sample}_fixed_wiped.fastq.gz"
    shell:
        "cat {input} > {output}"

#def aggregate_temp_fastq(wildcards):
#    checkpoint_output = checkpoints.split_fastq.get(**wildcards).output[0]
    
#    return expand("data/{sample}_chunks/chunk{i}.fastq_fixed_wiped.fastq.gz",
#        sample=wildcards.sample,
#        i=glob_wildcards(os.path.join(checkpoint_output, "chunk{i}.fastq")).i)

#def aggregate_temp_summary(wildcards):
#    checkpoint_output = checkpoints.split_fastq.get(**wildcards).output[0]

#    return expand("data/{sample}_chunks/{sample}_{i}_summary.txt",
#        sample=wildcards.sample,
#        i=glob_wildcards(os.path.join(checkpoint_output, "chunk{i}.fastq")).i)


# an aggregation over all produced clusters
#rule aggregate:
#    input:
#        aggregate_temp_fastq
#    output:
#        "data/{sample}_fixed_wiped.fastq.gz"
#    message:
#        "Gathering cleaned chunks."
#    shell:
#        "cat {input} > {output}"

# aggregation over all produced fastqwiper summaries
#rule aggregate_summary:
#    input:
#        aggregate_temp_summary
#    output:
#        "data/{sample}_final_summary.txt"
#    message:
#        "Gathering FastqWiper summaries"
#    shell:
#        "python fastq_wiper/gather_summaries.py -s {input} -f {output}"

#onsuccess:
#    print("Workflow finished, no error. Clean-up and shutdown")

#    if os.path.isdir(f"data/{SAMPLE}_chunks"):
#        shutil.rmtree(f"data/{SAMPLE}_chunks")
    
#    if os.path.isfile(f"data/{SAMPLE}_fixed.fastq"):
#        os.remove(f"data/{SAMPLE}_fixed.fastq")