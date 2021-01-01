# cmd:  snakemake -s fix_wipe_pairs_reads.smk --use-conda --cores 2

SAMPLES = ["sample", "excerpt"]
print(SAMPLES)


rule all:
    input:
        expand("data/{s}_S1_R{r}_001_fixed_wiped_paired.fastq.gz", s=SAMPLES, r = [1,2]),
        expand("data/{s}_S1_R{r}_001_fixed_wiped_unpaired.fastq.gz", s = SAMPLES, r = [1, 2])

rule fix_gzrt:
    input:
        "data/{sample}.fastq.gz"
    output:
        temp("data/{sample}_fixed.fastq")
    log:
        "logs/fix_gzrt/fix_gzrt.{sample}.log"
    shell:
        "gzrt/gzrecover -o {output} {input} -v 2> {log}"


rule wipe_fastq:
    input:
        "data/{sample}_fixed.fastq"
    output:
        temp("data/{sample}_fixed_wiped.fastq.gz")
    log:
        "logs/wipe_fastq/wipe_fastq.{sample}.log"
    shell:
        "python fastq_wiper/wiper.py --fastq_in {input} --fastq_out {output} 2> {log}"


rule drop_unpaired:
    input:
        r1 = "data/{sample}_S1_R1_001_fixed_wiped.fastq.gz",
        r2 = "data/{sample}_S1_R2_001_fixed_wiped.fastq.gz"
    output:
        r1 = "data/{sample}_S1_R1_001_fixed_wiped_paired.fastq.gz",
        r2="data/{sample}_S1_R2_001_fixed_wiped_paired.fastq.gz",
        r1_unpaired="data/{sample}_S1_R1_001_fixed_wiped_unpaired.fastq.gz",
        r2_unpaired = "data/{sample}_S1_R2_001_fixed_wiped_unpaired.fastq.gz"
    log:
        "logs/drop_unpaired/drop_unpaired.{sample}.log"
    params:
        trimmer=["MINLEN:20"]
    threads:
        1
    wrapper:
        "0.68.0/bio/trimmomatic/pe"


