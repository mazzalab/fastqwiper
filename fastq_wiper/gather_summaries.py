import argparse

def gather(summaries, final_summary):
    print(summaries)
    print(final_summary)


def main():
    parser = argparse.ArgumentParser(description='FastqWiper summaries gather')
    parser.add_argument("-s", '--summaries', nargs='+', help='The corrupted FASTQ file', required=True)
    parser.add_argument("-f", '--final_summary', help='The wiped FASTQ file', required=True)
    args = parser.parse_args()

    gather(args.summaries, args.final_summary)


if __name__ == "__main__":
    main()