#cmd: snakemake --config sample_name=sample qin=33 alphabet=ACGTN log_freq=1000 chunk_size=50000000 -s ./pipeline/fix_wipe_pairs_reads_parallel.smk --use-conda --cores 4

import os
import shutil
from snakemake.io import expand, temp

SAMPLE=config["sample_name"]
QIN=config["qin"]
ALPHABET=config["alphabet"]
LOG_FREQ=config["log_freq"]

scattergather:
    split=workflow.cores

rule all:
    input: 
        expand("data/{s}_R{r}_fixed_wiped_paired_interleaving.fastq.gz", s = SAMPLE, r = [1, 2]),
        expand("data/{s}_R{r}_final_summary.txt", s=SAMPLE, r = [1, 2])

rule fix_gzrt:
    input:
        "data/{sampleR}.fastq.gz"
    output:
        temp("data/{sampleR}_fixed.fastq")
    log:
        "logs/fix_gzrt/fix_gzrt.{sampleR}.log"
    message: 
        "Dropping unreadable reads from {input}."
    shell:
        "gzrecover -o {output} {input} -v 2> {log}"

rule split_fastq:
    input:
        "data/{sampleR}_fixed.fastq"
    output:
        scatter.split("data/{{sampleR}}_chunks/chunk{scatteritem}.fastq")
    params:
        split_total = workflow._scatter["split"]
    message:
        "Splitting {input} into chunks."
    shell:'''
       mkdir -p data/{wildcards.sampleR}_chunks
       wipertools splitfastq -f {input} -n {params.split_total} -o data/{wildcards.sampleR}_chunks -p chunk -s .fastq
       '''

rule wipe_fastq_parallel:
    input:
        "data/{sampleR}_chunks/chunk{scatteritem}.fastq"
    output:
        wiped_out   = "data/{sampleR}_chunks/chunk{scatteritem}.fastq_fixed_wiped.fastq.gz",
        summary_out = "data/{sampleR}_chunks/{sampleR}_{scatteritem}_summary.txt"
    log:
        "logs/wipe_fastq/wipe_fastq.{sampleR}.chunk{scatteritem}.fastq.log"
    message: 
        "Running FastqWiper on {input}."
    shell:'''
        wipertools fastqwiper --fastq_in {input} --fastq_out {output.wiped_out} --log_out {output.summary_out} --log_frequency {LOG_FREQ} --alphabet {ALPHABET} 2> {log}
        '''

rule gather_fastq:
    input:
        chunks = gather.split("data/{{sampleR}}_chunks/chunk{scatteritem}.fastq_fixed_wiped.fastq.gz")
    output:
        fastq_out = "data/{sampleR}_fixed_wiped.fastq.gz"
    message:
        "Merging healed fastq files"
    shell:'''
        cat {input.chunks} > {output.fastq_out}
        '''

rule gather_summary:
    input:
        summaries = gather.split("data/{{sampleR}}_chunks/{{sampleR}}_{scatteritem}_summary.txt")
    output:
        summary_out = "data/{sampleR}_final_summary.txt"
    message:
        "Gathering FastqWiper summaries"
    shell:'''
        wipertools summarygather -s {input.summaries} -f {output.summary_out}
        '''

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
        out2 = "data/{sample}_R2_fixed_wiped_paired_interleaving.fastq.gz",
        out3 = temp("data/{sample}_singletons.fastq.gz")
    log:
        "logs/interleaving/interleaving.{sample}.log"
    message:
        "Repair reads interleaving from {input} (qin={QIN})."
    threads:
        1
    cache: False
    shell:
        "bbmap/repair.sh qin={QIN} in={input.in1} in2={input.in2} out={output.out1} out2={output.out2} outsingle={output.out3} 2> {log}"

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