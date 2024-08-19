#cmd: snakemake --config sample_name=sample_R1 qin=33 alphabet=ACGTN log_freq=1000 -s pipeline/fix_wipe_single_reads_parallel.smk --use-conda --cores 4

import os
import shutil

SAMPLE=config["sample_name"]
ALPHABET=config["alphabet"]
LOG_FREQ=config["log_freq"]

scattergather:
    split=workflow.cores

rule all:
    input:
        expand("data/{s}_fixed_wiped.fastq.gz", s=SAMPLE),
        expand("data/{s}_final_summary.txt", s=SAMPLE)


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
       mkdir -p data/{wildcards.sample}_chunks
       wipertools splitfastq -f {input} -n {params.split_total} -o data/{wildcards.sample}_chunks -p chunk -s .fastq
       '''

rule wipe_fastq_parallel:
    input:
        "data/{sample}_chunks/chunk{scatteritem}.fastq"
    output:
        wiped_out   = "data/{sample}_chunks/chunk{scatteritem}.fastq_fixed_wiped.fastq.gz",
        summary_out = "data/{sample}_chunks/{sample}_{scatteritem}_summary.txt"
    log:
        "logs/wipe_fastq/wipe_fastq.{sample}.chunk{scatteritem}.fastq.log"
    message: 
        "Running FastqWiper on {input}."
    shell:'''
        wipertools fastqwiper --fastq_in {input} --fastq_out {output.wiped_out} --log_out {output.summary_out} --alphabet {ALPHABET} --log_frequency {LOG_FREQ} 2> {log}
        '''

rule gather_fastq:
    input:
        chunks = gather.split("data/{{sample}}_chunks/chunk{scatteritem}.fastq_fixed_wiped.fastq.gz")
    output:
        fastq_out = "data/{sample}_fixed_wiped.fastq.gz"
    message:
        "Merging healed fastq files"
    shell:'''
        cat {input.chunks} > {output.fastq_out}
        '''

rule gather_summary:
    input:
        summaries = gather.split("data/{{sample}}_chunks/{{sample}}_{scatteritem}_summary.txt")
    output:
        summary_out = "data/{sample}_final_summary.txt"
    message:
        "Gathering FastqWiper summaries"
    shell:'''
        wipertools summarygather -s {input.summaries} -f {output.summary_out}
        '''

onsuccess:
    print("Workflow finished, no error. Clean-up and shutdown")

    if os.path.isdir(f"data/{SAMPLE}_chunks"):
        shutil.rmtree(f"data/{SAMPLE}_chunks")
    
    if os.path.isfile(f"data/{SAMPLE}_fixed.fastq"):
        os.remove(f"data/{SAMPLE}_fixed.fastq")