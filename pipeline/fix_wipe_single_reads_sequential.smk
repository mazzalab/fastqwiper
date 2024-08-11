#cmd: snakemake --config sample_name=sample_R1 qin=33 alphabet=ACGTN log_freq=1000 -s pipeline/fix_wipe_single_reads_sequential.smk --use-conda --cores 4

SAMPLES=config["sample_name"]
ALPHABET=config["alphabet"]
LOG_FREQ=config["log_freq"]

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
    shell:'''
    fastqwiper --fastq_in {input} --fastq_out {output} --log_out data/{wildcards.sample}_final_summary.txt --alphabet {ALPHABET} --log_frequency {LOG_FREQ} 2> {log}
    '''
