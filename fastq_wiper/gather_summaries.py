import argparse
from wiper import NOTPRINT_HEADER, FIXED_HEADER, BAD_SEQ, BAD_PLUS, FIXED_PLUS, BAD_QUAL, QUAL_OUT_RANGE, LENGTH_SEQ_QUAL, BLANKS

def gather(summaries, final_summary):
    print(summaries)
    print(final_summary)

    tot_lines = 0

    for s in summaries:
        pass


def main():
    parser = argparse.ArgumentParser(description='FastqWiper summaries gather')
    parser.add_argument("-s", '--summaries', nargs='+', help='The corrupted FASTQ file', required=True)
    parser.add_argument("-f", '--final_summary', help='The wiped FASTQ file', required=True)
    args = parser.parse_args()

    gather(args.summaries, args.final_summary)


if __name__ == "__main__":
    main()