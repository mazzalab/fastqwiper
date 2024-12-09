import os
import gzip
import argparse
import subprocess
from pathlib import Path
from enum import auto, Enum
from fastqwiper.wipertool_abstract import WiperTool


class GatherFastq(WiperTool):
    def __init__(self):
        super().__init__("fastqgather")

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

        def files_choices(choices, fname):
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
                raise ValueError(
                    f"File '{fname}' doesn't end with one of {choices}")
            return fname

        parser.add_argument(
            "-i",
            "--in_fastq",
            nargs="+",
            type=lambda s: files_choices(
                (e.name.lower().replace("_", ".") for e in FastqExtEnum), s),
            help="List of FASTQ files to be joined",
            required=True,
        )
        parser.add_argument(
            "-o",
            "--out_fastq",
            type=lambda s: files_choices(
                (e.name.lower().replace("_", ".") for e in FastqExtEnum), s),
            help="Name of the resulting fastq file",
            required=True
        )
        # Optional arguments
        parser.add_argument(
            "-p",
            "--prefix",
            nargs="?",
            help="Prefix common to the files to be joined",
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
            help="Print the version and exits",
        )

    def run(self, argv: argparse.Namespace):
        in_fastq: list[str] = argv.in_fastq
        out_fastq: str = argv.out_fastq
        prefix: str = argv.prefix
        opsys: str = argv.os

        # Check if output file already exists and remove it
        if os.path.exists(out_fastq):
            os.remove(out_fastq)

        self.concatenate_fastq(in_fastq, out_fastq, prefix, opsys)

    # Utility methods and properties
    @staticmethod
    def concatenate_fastq(input_files: list[str], output_file: str, prefix: str, opsys: str) -> None:
        # Filter files with the given prefix, if specified
        files = [x for x in input_files if x.startswith(
            prefix)] if prefix else input_files

        if not files:
            print(f"No files with prefix {prefix}.")
            return

        # Separate gzipped files from regular files
        gz_files = [f for f in files if f.endswith(
            "fastq.gz") or f.endswith("fq.gz")]
        regular_files = [f for f in files if f.endswith(
            ".fastq") or f.endswith(".fq")]

        try:
            if opsys == "cross_platform":
                GatherFastq.__concat_cross_platform(
                    regular_files, gz_files, output_file
                )
            else:
                GatherFastq.__concat_unix(
                    " ".join(regular_files), " ".join(gz_files), output_file
                )

            print("Files concatenated successfully.")
        except Exception as e:
            print(f"Error while concatenating files: {e}")

    @staticmethod
    def __concat_unix(regular_files: str, gz_files: str, outfile: str):
        if regular_files:
            process_regular = subprocess.Popen(
                f"cat {regular_files} > {outfile}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # Wait for the command to complete and get output.
            stdout, stderr = process_regular.communicate()

            if process_regular.returncode != 0:
                print(f"Error occurred: {stderr.decode()}")

        if gz_files:
            process_gzip = subprocess.Popen(
                f"zcat {gz_files} >> {outfile}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # Wait for the command to complete and get output.
            stdout, stderr = process_gzip.communicate()

            if process_gzip.returncode != 0:
                print(f"Error occurred: {stderr.decode()}")

        if outfile.endswith(".gz"):
            uncompressed_file = outfile.removesuffix(".gz")

            process_compress = subprocess.Popen(
                f"mv {outfile} {uncompressed_file} && gzip {
                    uncompressed_file}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # Wait for the command to complete and get output.
            stdout, stderr = process_compress.communicate()

            if process_compress.returncode != 0:
                print(f"Error occurred: {stderr.decode()}")

    @staticmethod
    def __concat_cross_platform(regular_files, gz_files, outfile: str):
        with (
            gzip.open(outfile, "wb")
            if outfile.endswith(".gz")
            else open(outfile, "wt", encoding="utf-8") as output_file
        ):
            # Concatenate regular text files
            for file_path in regular_files:
                with open(file_path, "r", encoding="utf-8", errors="replace") as infile:
                    data = infile.read()
                    # Count the replacement characters
                    replacement_count = data.count("�")
                    if replacement_count > 0:
                        print(f"Warning: File '{file_path}' contains {
                              replacement_count} unreadable characters that were replaced.")

                    if isinstance(output_file, gzip.GzipFile):
                        # Write as bytes for gzip
                        output_file.write(data.encode())
                    else:
                        # Write as string for regular text file
                        output_file.write(data)

            # Concatenate gzipped fastq files
            for file_path in gz_files:
                with gzip.open(file_path, "rb") as infile:
                    data = infile.read()

                    if isinstance(output_file, gzip.GzipFile):
                        # Write as bytes for gzip
                        output_file.write(data)
                    else:
                        try:
                            # Decode bytes to string for regular text file
                            decoded_data = data.decode("utf-8")
                        except UnicodeDecodeError:
                            # Gracefully handle decoding errors
                            print(f"Warning: Decoding error in {
                                  file_path}, replacing invalid characters.")
                            decoded_data = data.decode(
                                "utf-8", errors="replace")
                        output_file.write(decoded_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WiperTools FASTQ gather")
    fs = GatherFastq()
    fs.set_parser(parser)

    args = parser.parse_args()
    fs.run(args)
