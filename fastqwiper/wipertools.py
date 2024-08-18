import sys, os.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from gather_summaries import GatherSummaries
from split_fastq import SplitFastq
from fastq_wiper import FastqWiper


def main():
    parser = argparse.ArgumentParser(description='FastqWiper program help')
    subparsers = parser.add_subparsers(help='Choices', dest='selected_subparser')

    # create the parser for the FastqWiper main program
    fw_parser = subparsers.add_parser('fastqwiper', help='FastqWiper program')
    fw = FastqWiper()
    fw.set_parser(fw_parser)

    # create the parser for the split_fastq program
    sf_parser = subparsers.add_parser('splitfastq', help='FASTQ splitter program')
    sf = SplitFastq()
    sf.set_parser(sf_parser)

    # create the parser for the gather_summaries program
    gs_parser = subparsers.add_parser('summarygather', help='Gatherer of the FastqWiper summaries')
    gs = GatherSummaries()
    gs.set_parser(gs_parser)

    # Process command-line arguments and parse them
    args = parser.parse_args()

    if args.selected_subparser == 'fastqwiper':
        fw.run(args)
    elif args.selected_subparser == 'splitfastq':
        sf.run(args)
    elif args.selected_subparser == 'summarygather':
        gs.run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
