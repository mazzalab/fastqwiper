import sys
import os.path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
from fastqwiper.summary_gather import GatherSummaries
from fastqwiper.fastq_scatter import SplitFastq
from fastqwiper.fastq_wiper import FastqWiper
from fastqwiper.fastq_gather import GatherFastq


def main():
    parser = argparse.ArgumentParser(description='FastqWiper program help')
    subparsers = parser.add_subparsers(help='Choices', dest='selected_subparser')

    # create the parser for the FastqWiper main program
    fw_parser = subparsers.add_parser('fastqwiper', help='FastqWiper program')
    fw = FastqWiper()
    fw.set_parser(fw_parser)

    # create the parser for the split_fastq program
    fs_parser = subparsers.add_parser('fastqscatter', help='FASTQ splitter program')
    fs = SplitFastq()
    fs.set_parser(fs_parser)

    # create the parser for the gather_fastq program
    fg_parser = subparsers.add_parser('fastqgather', help='FASTQ gather program')
    fg = GatherFastq()
    fg.set_parser(fg_parser)

    # create the parser for the gather_summaries program
    sg_parser = subparsers.add_parser('summarygather', help='Gatherer of FastqWiper summary files')
    sg = GatherSummaries()
    sg.set_parser(sg_parser)

    # Process command-line arguments and parse them
    args = parser.parse_args()

    if args.selected_subparser == 'fastqwiper':
        fw.run(args)
    elif args.selected_subparser == 'fastqscatter':
        fs.run(args)
    elif args.selected_subparser == 'fastqgather':
        fg.run(args)
    elif args.selected_subparser == 'summarygather':
        sg.run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
