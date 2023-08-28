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
    shell:
        "gzrecover -o {output} {input} -v 2> {log}"


rule wipe_fastq:
    input:
        "data/{sample}_fixed.fastq"
    output:
        "data/{sample}_fixed_wiped.fastq.gz"
    log:
        "logs/wipe_fastq/wipe_fastq.{sample}.log"
    shell:
        "fastqwiper --fastq_in {input} --fastq_out {output} 2> {log}"


