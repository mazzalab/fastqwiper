import os
import argparse
from itertools import count

def line_count2(file_path):
    with open(file_path, "r") as f:
        return sum(1 for _ in f)

def line_count(file_path):
    return int(os.popen(f'wc -l {file_path}').read().split()[0])

def split_fastq(fastq, splits, prefix, suffix, out_folder):
    rows = line_count(fastq)
    # rows = line_count2(args.fastq) TODO: to be benchmarked

    # add 1 if the division produces a nonzero remainder. This has the benefit of not introducing floating-point
    # imprecision, so it'll be correct in extreme cases where math.ceil produces the wrong answer.
    rows_per_file = rows // splits + bool(rows % splits)
    with open(fastq, "r", encoding='ISO-8859-1') as f:
        for split in range(1, splits+1):
            split_file_name = out_folder+"/"+prefix+str(split)+"-of-"+str(splits)+suffix
            with open(split_file_name, "w") as split_file:
                i = 0
                while i < rows_per_file:
                    split_file.write(f"{f.readline()}")
                    i = i+1


def main():
    parser = argparse.ArgumentParser(description='FastqWiper FASTQ splitter')
    parser.add_argument("-f", '--fastq', help='The FASTQ file to be split', required=True)
    parser.add_argument("-n", '--num_splits', type=int, help='The number of splits', required=True)
    parser.add_argument("-o", '--out_folder', help='The folder where to put the splits', required=True)
    parser.add_argument("-p", '--prefix', help='The prefix of the names of the split files', required=True)
    parser.add_argument("-s", '--suffix', help='The suffix of the names of the split files', required=True)

    args = parser.parse_args()

    split_fastq(args.fastq, args.num_splits, args.prefix, args.suffix, args.out_folder)


if __name__ == "__main__":
    main()