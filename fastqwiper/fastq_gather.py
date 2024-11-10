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
        parser.add_argument("-p", '--prefix', help='Prefix common to the files to be joined', required=True)
        parser.add_argument("-o", '--out_fastq', help='The name of the resulting fastq file', required=True)
        parser.add_argument("-O", '--os', help='The underlying OS (Default: %(default)s)', default='windows', choices=[e.name.lower() for e in OsEnum],  required=False)
        # Add a version flag that prints the version and exits
        parser.add_argument('-v', '--version', action='version', version=self.version(), help='It prints the version and exists')

    def run(self, argv: argparse.Namespace):
        in_folder: str  = argv.in_folder
        prefix: str     = argv.prefix
        out_fastq: str  = argv.out_fastq
        opsys: str      = argv.os

        if opsys == "windows":
            self.concatenate_fastq_windows(in_folder, out_fastq, prefix)
        else:
            self.concatenate_fastq_unix(in_folder, out_fastq, prefix)


    # Utility methods and properties
    @staticmethod
    def concatenate_fastq_unix(input_directory, output_file, prefix):
        # List all files in the directory with the given prefix
        files = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.startswith(prefix)]
        
        if not files:
            print(f"No files found in {input_directory} with prefix {prefix}.")
            return
        
        # Separate gzipped files from regular files
        gz_files = [f for f in files if f.endswith('.gz')]
        regular_files = [f for f in files if f.endswith('.fastq')]

        try:
            # Handle gzipped output
            if output_file.endswith('.gz'):
                with gzip.open(output_file, 'wb') as outfile:
                    GatherFastq.__concat_unix(regular_files, gz_files, outfile)
                        
            else:
                # Handle plain output file
                with open(output_file, 'wb') as outfile:
                    GatherFastq.__concat_unix(regular_files, gz_files, outfile)

            print("Files concatenated successfully.")
        except Exception as e:
            print(f"Error while concatenating files: {e}")

    @staticmethod
    def concatenate_fastq_windows(input_directory, output_file, prefix):
        # List all files in the directory with the given prefix
        files = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.startswith(prefix)]

        if not files:
            print(f"No files found in {input_directory} with prefix {prefix}.")
            return

        # Separate gzipped files from regular files
        gz_files = [f for f in files if f.endswith('.gz')]
        regular_files = [f for f in files if f.endswith('.fastq')]

        try:
            # Handle gzipped output
            if output_file.endswith('.gz'):
                with gzip.open(output_file, 'wb') as outfile:
                    GatherFastq.__concat_windows(regular_files, gz_files, outfile)
            else:
                # Handle plain output file
                with open(output_file, 'wb') as outfile:
                    GatherFastq.__concat_windows(regular_files, gz_files, outfile)

            print("Files concatenated successfully.")
        except Exception as e:
            print(f"Error while concatenating files: {e}")
    
    @staticmethod
    def __concat_unix(regular_files, gz_files, outfile):
        # Concatenate regular fastq files
        for file_path in regular_files:
            with open(file_path, 'rb') as infile:
                outfile.write(infile.read())

        # Use zcat with subprocess for gz files
        for file_path in gz_files:
            process = subprocess.Popen(['zcat', file_path], stdout=subprocess.PIPE)
            while True:
                chunk = process.stdout.read(1024)
                if not chunk:
                    break
                outfile.write(chunk)
            process.stdout.close()
            process.wait()

    def __concat_windows(regular_files, gz_files, outfile):
        # Concatenate regular fastq files
        for file_path in regular_files:
            with open(file_path, 'rb') as infile:
                outfile.write(infile.read())

        # Concatenate gzipped fastq files
        for file_path in gz_files:
            with gzip.open(file_path, 'rb') as infile:
                outfile.write(infile.read())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WiperTools FASTQ gather')
    fs = GatherFastq()
    fs.set_parser(parser)

    args = parser.parse_args()
    fs.run(args)