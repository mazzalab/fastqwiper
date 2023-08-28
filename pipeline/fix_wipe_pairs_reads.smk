# cmd:  snakemake -s pipeline/fix_wipe_pairs_reads.smk --use-conda --cores 2
# zgrep -n -x '[^+]\{0,10\}' data/cov3-200825_S1_R1_001_fixed_wiped.fastq.gz

from snakemake.io import expand, temp

SAMPLES=config["sample_name"]

rule all:
    input: 
        expand("data/{s}_R{r}_fixed_wiped_paired_interleaving.fastq.gz", s = SAMPLES, r = [1, 2])

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
        temp("data/{sample}_fixed_wiped.fastq.gz")
    log:
        "logs/wipe_fastq/wipe_fastq.{sample}.log"
    shell:
        "fastqwiper --fastq_in {input} --fastq_out {output} 2> {log}"

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
    params:
        trimmer = ["MINLEN:20"]
    threads:
        4
    cache: False
    wrapper:
        "v2.2.1/bio/trimmomatic/pe"

rule fix_interleaving:
    input:
        in1 = "data/{sample}_R1_fixed_wiped_paired.fastq.gz",
        in2 = "data/{sample}_R2_fixed_wiped_paired.fastq.gz"
    output:
        out1 = "data/{sample}_R1_fixed_wiped_paired_interleaving.fastq.gz",
        out2 = "data/{sample}_R2_fixed_wiped_paired_interleaving.fastq.gz"
    log:
        "logs/pairing/pairing.{sample}.log"
    threads:
        1
    cache: False
    shell:
        "bbmap/repair.sh in={input.in1} in2={input.in2} out={output.out1} out2={output.out2} outsingle=singletons.fastq.gz 2> {log}"
