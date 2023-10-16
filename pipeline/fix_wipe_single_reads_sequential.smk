# cmd: snakemake -s fix_wipe_single_reads.smk --use-conda --cores 2

SAMPLES=config["sample_name"]

rule all:
    input:
        expand("data/{s}_fixed_wiped.fastq.gz", s=SAMPLES),

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


rule wipe_fastq:
    input:
        "data/{sample}_fixed.fastq"
    output:
        "data/{sample}_fixed_wiped.fastq.gz"
    log:
        "logs/wipe_fastq/wipe_fastq.{sample}.log"
    message: 
        "Running FastqWiper on {input}."
    shell:
        "fastqwiper --fastq_in {input} --fastq_out {output} --log_out ./data/{sample}_final_summary.txt 2> {log}"


