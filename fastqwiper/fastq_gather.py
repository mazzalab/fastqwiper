import os
import gzip
import argparse
import subprocess
from enum import auto, Enum
from fastqwiper.wipertool_abstract import WiperTool


class GatherFastq(WiperTool):
    def __init__(self):
        super().__init__("fastqgather")
        
    # Inherited methods
    def set_parser(self, parser: argparse.ArgumentParser):
        class OsEnum(Enum):
            UNIX    = auto()
            WINDOWS = auto()

        parser.add_argument("-f", '--in_folder', help='Path of the folder containing the files to be joined', required=True)
        parser.add_argument("-o", '--out_fastq', help='Name of the resulting fastq file', required=True)
        parser.add_argument("-p", '--prefix', help='Prefix common to the files to be joined', required=False)
        parser.add_argument("-O", '--os', help='Underlying OS (Default: %(default)s)', default='windows', choices=[e.name.lower() for e in OsEnum],  required=False)
        # Add a version flag that prints the version and exits
        parser.add_argument('-v', '--version', action='version', version=self.version(), help='Print the version and exits')

    def run(self, argv: argparse.Namespace):
        in_folder: str  = argv.in_folder
        prefix: str     = argv.prefix
        out_fastq: str  = argv.out_fastq
        opsys: str      = argv.os

        # Check if output file already exists and remove it
        if os.path.exists(out_fastq):
            os.remove(out_fastq)

        self.concatenate_fastq(in_folder, out_fastq, prefix, opsys)

    # Utility methods and properties
    @staticmethod
    def concatenate_fastq(input_directory, output_file, prefix, opsys):
        # List all files in the directory with the given prefix
        files = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.startswith(prefix)] if prefix else [os.path.join(input_directory, f) for f in os.listdir(input_directory)]
        
        if not files:
            print(f"No files found in {input_directory} with prefix {prefix}.")
            return
        
        # Separate gzipped files from regular files
        gz_files = [f for f in files if f.endswith('.gz')]
        regular_files = [f for f in files if f.endswith('.fastq')]

        try:
            if opsys == "windows":
                GatherFastq.__concat_windows(regular_files, gz_files, output_file)
            else:
                GatherFastq.__concat_unix(' '.join(regular_files), ' '.join(gz_files), output_file)

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
                stderr=subprocess.PIPE
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
                stderr=subprocess.PIPE
            )
            # Wait for the command to complete and get output.
            stdout, stderr = process_gzip.communicate()

            if process_gzip.returncode != 0:
                print(f"Error occurred: {stderr.decode()}")

        if outfile.endswith('.gz'):
            uncompressed_file = outfile.removesuffix('.gz')

            process_compress = subprocess.Popen(
                f"mv {outfile} {uncompressed_file} && gzip {uncompressed_file}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Wait for the command to complete and get output.
            stdout, stderr = process_compress.communicate()

            if process_compress.returncode != 0:
                print(f"Error occurred: {stderr.decode()}")


    def __concat_windows(regular_files, gz_files, outfile: str):
        with gzip.open(outfile, 'wb') if outfile.endswith(".gz") else open(outfile, "w") as output_file:
            for file_path in regular_files:
                with open(file_path, 'r') as infile:
                    data = infile.read()
                    if isinstance(output_file, gzip.GzipFile):
                        output_file.write(data.encode())  # Write as bytes for gzip
                    else:
                        output_file.write(data)  # Write as string for regular text file

            # Concatenate gzipped fastq files
            for file_path in gz_files:
                with gzip.open(file_path, 'rb') as infile:
                    data = infile.read()
                    if isinstance(output_file, gzip.GzipFile):
                        output_file.write(data)  # Write as bytes for gzip
                    else:
                        output_file.write(data.decode())  # Decode bytes to string for regular text file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WiperTools FASTQ gather')
    fs = GatherFastq()
    fs.set_parser(parser)

    args = parser.parse_args()
    fs.run(args)