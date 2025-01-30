import argparse
import json
import os
from wipertools.fastq_gather import GatherFastq
from wipertools.fastq_wiper import FastqWiper
from wipertools.fastq_scatter import SplitFastq
from wipertools.report_gather import GatherReport


def main():
    parser = argparse.ArgumentParser(description="FastqWiper program help")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=version(),
        help="It prints the version and exists",
    )

    subparsers = parser.add_subparsers(
        help="Choices", dest="selected_subparser")

    # create the parser for the FastqWiper main program
    fw_parser = subparsers.add_parser("fastqwiper", help="FastqWiper program")
    fw = FastqWiper()
    fw.set_parser(fw_parser)

    # create the parser for the split_fastq program
    fs_parser = subparsers.add_parser(
        "fastqscatter", help="FASTQ splitter program")
    fs = SplitFastq()
    fs.set_parser(fs_parser)

    # create the parser for the gather_fastq program
    fg_parser = subparsers.add_parser(
        "fastqgather", help="FASTQ gather program")
    fg = GatherFastq()
    fg.set_parser(fg_parser)

    # create the parser for the gather_reports program
    rg_parser = subparsers.add_parser(
        "reportgather", help="FastqWiper reports gather program"
    )
    rg = GatherReport()
    rg.set_parser(rg_parser)

    # Process command-line arguments and parse them
    try:
        args = parser.parse_args()
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as ex:
        print(f"GENERAL ERROR: {ex}")

    if args.selected_subparser == "fastqwiper":
        fw.run(args)
    elif args.selected_subparser == "fastqscatter":
        fs.run(args)
    elif args.selected_subparser == "fastqgather":
        fg.run(args)
    elif args.selected_subparser == "reportgather":
        rg.run(args)
    else:
        parser.print_help()


def version():
    versions_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "versions.json"
    )
    with open(versions_file_path) as f:
        config = json.load(f)
        return config.get("wipertools", "")


if __name__ == "__main__":
    main()
