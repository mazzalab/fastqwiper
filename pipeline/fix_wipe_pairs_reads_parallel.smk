# cmd:  snakemake -s pipeline/fix_wipe_pairs_reads_parallel.smk --use-conda --cores 2

import os
from snakemake.io import expand, temp, glob_wildcards, directory, dynamic
from snakemake import checkpoints

# SAMPLES = ["sample", "excerpt"]
# SAMPLES = ["cov3-200825"]
SAMPLES = ["test_bad2_reads"]

rule all:
    input:
        # expand("data/{s}_S1_R{r}_001_fixed_wiped_paired_interleaving.fastq.gz", s=SAMPLES, r = [1,2])
        expand("data/{sample}_S1_R{r}_001_fixed_wiped_merged.fastq.gz", sample=SAMPLES, r = [1])

rule fix_gzrt:
    input:
        "data/{sample}.fastq.gz"
    output:
        "data/{sample}_fixed.fastq"
    log:
        "logs/fix_gzrt/fix_gzrt.{sample}.log"
    shell:
        "gzrt/gzrecover -o {output} {input} -v 2> {log}"

checkpoint split_fastq:
    input:
        "data/{sample}_fixed.fastq"
    output:
        directory("data/{sample}_fixed.fastq.chunks")
    log:
        "logs/split_fastq/split_fastq_chunks.{sample}.log"
    shell:
        "split -l 4 --numeric-suffixes {input} {output}/{input}."

# rule rename_fastq_chunks:
#     input:
#         "data/{sample}_fixed.fastq.{chunk}"
#     output:
#         "data/{sample}_fixed.{chunk}.fastq"
#     log:
#         "logs/rename_fastq_chunks/rename_fastq_chunks.{sample}.{chunk}.log"
#     shell:
#         "mv {input} {output}"
#
# rule wipe_fastq:
#     input:
#         "data/{sample}_fixed.{chunk}.fastq"
#     output:
#         "data/{sample}_fixed_wiped.{chunk}.fastq.gz"
#     log:
#         "logs/wipe_fastq/wipe_fastq.{sample}.{chunk}.log"
#     shell:
#         "python fastq_wiper/wiper.py --fastq_in {input} --fastq_out {output} 2> {log}"

# def aggregate_input(wildcards):
#     checkpoint_output = checkpoints.split_fastq.get(**wildcards).output[0]
#     return expand("data/{sample}_fixed.fastq.chunks/{i}.txt",
#         sample=wildcards.sample,
#         i=glob_wildcards(os.path.join(checkpoint_output,"{i}")).i)
#
# rule merge_fastq_chunks:
#     input:
#         aggregate_input
#         # expand("data/{sample}_fixed_wiped.{chunk}.fastq.gz")
#     output:
#         "data/{sample}_fixed_wiped_merged.fastq.gz"
#     log:
#         "logs/merge_fastq_chunks/merge_fastq_chunks.{sample}.log"
#     shell:
#         "zcat {input} > {output}"

# rule drop_unpaired:
#     input:
#         r1 = "data/{sample}_S1_R1_001_fixed_wiped.fastq.gz",
#         r2 = "data/{sample}_S1_R2_001_fixed_wiped.fastq.gz"
#     output:
#         r1 = temp("data/{sample}_S1_R1_001_fixed_wiped_paired.fastq.gz"),
#         r2 = temp("data/{sample}_S1_R2_001_fixed_wiped_paired.fastq.gz"),
#         r1_unpaired = temp("data/{sample}_S1_R1_001_fixed_wiped_unpaired.fastq.gz"),
#         r2_unpaired = temp("data/{sample}_S1_R2_001_fixed_wiped_unpaired.fastq.gz")
#     log:
#         "logs/pairing/pairing.{sample}.log"
#     params:
#         trimmer = ["MINLEN:20"]
#     threads:
#         1
#     cache: False
#     wrapper:
#         "0.74.0/bio/trimmomatic/pe"
#
#
# rule fix_interleaving:
#     input:
#         in1 = "data/{sample}_S1_R1_001_fixed_wiped_paired.fastq.gz",
#         in2 = "data/{sample}_S1_R2_001_fixed_wiped_paired.fastq.gz"
#     output:
#         out1 = "data/{sample}_S1_R1_001_fixed_wiped_paired_interleaving.fastq.gz",
#         out2 = "data/{sample}_S1_R2_001_fixed_wiped_paired_interleaving.fastq.gz"
#     log:
#         "logs/pairing/pairing.{sample}.log"
#     threads:
#         1
#     cache: False
#     shell:
#         "bbmap/repair.sh in={input.in1} in2={input.in2} out={output.out1} out2={output.out2} outsingle=singletons.fastq.gz 2> {log}"
