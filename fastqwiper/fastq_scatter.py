import os
import gzip
import argparse
import subprocess
from pathlib import Path
from enum import auto, Enum
from wipertool_abstract import WiperTool


class SplitFastq(WiperTool):
    def __init__(self):
        super().__init__("fastqscatter")

    # Inherited methods
    def set_parser(self, parser: argparse.ArgumentParser):
        class OsEnum(Enum):
            UNIX = auto()
            CROSS_PLATFORM = auto()

        class FastqExtEnum(Enum):
            FASTQ = auto()
            FQ = auto()
            FASTQ_GZ = auto()
            FQ_GZ = auto()

        def file_choices(choices, fname):
            # Extract double extensions if present
            path = Path(fname)
            if len(path.suffixes) == 2:  # Handle double extensions like ".fastq.gz"
                # Combine the suffixes and remove the dot
                ext = ''.join(path.suffixes)[1:]
            else:
                ext = path.suffix[1:]  # Single extension

            if ext not in choices:
                parser.error(
                    f"File '{fname}' doesn't end with one of {choices}")
            return fname

        parser.add_argument("-f", "--fastq", type=lambda s: file_choices((e.name.lower().replace("_", ".")
                            for e in FastqExtEnum), s), help="The FASTQ file to be split", required=True)
        parser.add_argument("-n", "--num_splits", type=int,
                            help="Number of splits", required=True)
        parser.add_argument(
            "-p", "--prefix", help="The prefix of the names of the split files", required=True)
        # Optional arguments
        parser.add_argument(
            "-s",
            "--suffix",
            nargs="?",
            help="The suffix of the names of the split files",
            required=False,
        )
        parser.add_argument(
            "-e",
            "--ext",
            help="The extension of the split files",
            default="fastq.gz",
            choices=[e.name.lower().replace("_", ".") for e in FastqExtEnum],
            required=False,
        )
        parser.add_argument(
            "-o",
            "--out_folder",
            help="The folder name where to put the splits",
            default=os.path.join(os.getcwd(), "chunks"),
            required=False,
        )
        parser.add_argument(
            "-O",
            "--os",
            help="Underlying OS (Default: %(default)s)",
            default="cross_platform",
            choices=[e.name.lower() for e in OsEnum],
            required=False,
        )
        # Add a version flag that prints the version and exits
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=self.version(),
            help="Print the version and exit",
        )

    def run(self, argv: argparse.Namespace):
        fastq: str = argv.fastq
        splits: int = argv.num_splits
        prefix: str = argv.prefix
        suffix: str = argv.suffix
        ext: str = argv.ext
        out_folder: str = argv.out_folder
        opsys: str = argv.os

        try:
            # Create the output directory if not existing
            if not os.path.exists(out_folder):
                os.mkdir(out_folder)

                if opsys == "cross_platform":
                    self.split_cross_platform(
                        fastq, splits, prefix, suffix, ext, out_folder
                    )
                else:
                    self.split_on_unix(fastq, splits, prefix,
                                       suffix, ext, out_folder)
            else:
                print(f"The destination folder ({
                      out_folder}) is not empty. Aborted!")

        except PermissionError:
            print(f"Permission denied: Unable to create '{out_folder}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Utility methods and properties
    @staticmethod
    def line_count(file_path: str):
        with open(file_path, "r", encoding="ISO-8859-1") as f:
            return sum(1 for _ in f)

    @staticmethod
    def split_on_unix(
        file_path: str, splits: int, prefix: str, suffix: str, ext: str, out_folder: str
    ):
        formatted_suffix = "_" + suffix if suffix else ""

        if file_path.endswith(".fastq.gz") or file_path.endswith(".fq.gz"):
            cmd_total_lines = f"gzip -dc {file_path} | wc -l"
            process = subprocess.Popen(
                cmd_total_lines,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise RuntimeError(
                    f"Error calculating line count: {stderr.decode().strip()}"
                )

            total_lines = int(stdout.strip())
            # add 1 if the division produces a nonzero remainder. This has the benefit of not introducing floating-point
            # imprecision, so it'll be correct in extreme cases where math.ceil produces the wrong answer.
            lines_per_split = total_lines // splits + \
                bool(total_lines % splits)

            if ext == "fastq.gz" or ext == "fq.gz":
                command = (
                    f"gzip -dc {file_path} | "
                    f"split -d -a3 -l {lines_per_split} --additional-suffix={
                        formatted_suffix}.fastq "
                    f"--filter='gzip > $FILE.gz' - {out_folder}/{prefix}_"
                )
            else:
                command = (
                    f"gzip -dc {file_path} | "
                    f"split -d -a3 -l {lines_per_split} --additional-suffix={
                        formatted_suffix}.fastq "
                    f"- {out_folder}/{prefix}_"
                )
        else:
            if ext == "fastq.gz" or ext == "fq.gz":
                command = (
                    f"split -d -a3 -n {splits} --additional-suffix={
                        formatted_suffix}.fastq "
                    f"--filter='gzip > $FILE.gz' {
                        file_path} {out_folder}/{prefix}_"
                )
            else:
                command = (
                    f"split -d -a3 -n {splits} --additional-suffix={
                        formatted_suffix}.fastq "
                    f"{file_path} {out_folder}/{prefix}_"
                )

        try:
            # Run the split command with shell=True due to the variable expansion.
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Wait for the command to complete and get output.
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                print("Split operation completed successfully.")
            else:
                print(f"Error occurred: {stderr.decode()}")

        except Exception as e:
            print(f"Exception occurred: {e}")

    @staticmethod
    def split_cross_platform(
        file_path: str, splits: int, prefix: str, suffix: str, ext: str, out_folder: str
    ):
        formatted_suffix = "_" + suffix if suffix else ""
        rows = SplitFastq.line_count(file_path)

        # add 1 if the division produces a nonzero remainder. This has the benefit of not introducing floating-point
        # imprecision, so it'll be correct in extreme cases where math.ceil produces the wrong answer.
        rows_per_file = rows // splits + bool(rows % splits)

        with (
            gzip.open(file_path, "rb")
            if file_path.endswith(".fastq.gz") or file_path.endswith(".fq.gz")
            else open(file_path, "r", encoding="ISO-8859-1")
        ) as f:
            for split in range(1, splits + 1):
                split_file_name = (
                    f"{out_folder}/{prefix}_{split}-of-{splits}{formatted_suffix}.{ext}"
                )

                with (
                    open(split_file_name, "w")
                    if ext == "fastq" or ext == "fq"
                    else gzip.open(split_file_name, "wb") as split_file
                ):
                    i = 0
                    while i < rows_per_file:
                        line = f.readline()
                        # Handle the data based on whether it's bytes or string
                        if isinstance(line, bytes):  # Case for gzip input files
                            # Convert bytes to string
                            line = line.decode("ISO-8859-1")

                        # Write as string for normal file, encode as bytes for gzip
                        if isinstance(split_file, gzip.GzipFile):
                            # Write as bytes
                            split_file.write(line.encode("ISO-8859-1"))
                        else:
                            split_file.write(line)  # Write as a string
                        i += 1

        print("Split operation completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WiperTools FASTQ splitter")
    fs = SplitFastq()
    fs.set_parser(parser)

    args = parser.parse_args()
    fs.run(args)
