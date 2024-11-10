import os
import argparse
from enum import auto, Enum
from fastqwiper.wipertool_abstract import WiperTool


class SplitFastq(WiperTool):
    def __init__(self):
        super().__init__("fastqscatter")
        
    # Inherited methods
    def set_parser(self, parser: argparse.ArgumentParser):
        class OsEnum(Enum):
            UNIX    = auto()
            WINDOWS = auto()

        parser.add_argument("-f", '--fastq', help='The FASTQ file to be split', required=True)
        parser.add_argument("-n", '--num_splits', type=int, help='The number of splits', required=True)
        parser.add_argument("-o", '--out_folder', help='The folder where to put the splits', required=True)
        parser.add_argument("-p", '--prefix', help='The prefix of the names of the split files', required=True)
        parser.add_argument("-s", '--suffix', help='The suffix of the names of the split files', required=True)
        parser.add_argument("-O", '--os', help='The underlying OS (Default: %(default)s)', default='windows', choices=[e.name.lower() for e in OsEnum],  required=False)
        # Add a version flag that prints the version and exits
        parser.add_argument('-v', '--version', action='version', version=self.version(), help='It prints the version and exists')

    def run(self, argv: argparse.Namespace):
        fastq: str      = argv.fastq
        splits: int     = argv.num_splits
        prefix: str     = argv.prefix
        suffix: str     = argv.suffix
        out_folder: str = argv.out_folder
        opsys: str      = argv.os

        if opsys == "windows":
            rows = self.line_count_crossplatform(fastq)
        else:
            rows = self.line_count_unix(fastq)

        # add 1 if the division produces a nonzero remainder. This has the benefit of not introducing floating-point
        # imprecision, so it'll be correct in extreme cases where math.ceil produces the wrong answer.
        rows_per_file = rows // splits + bool(rows % splits)
        with open(fastq, "r", encoding='ISO-8859-1') as f:
            for split in range(1, splits + 1):
                split_file_name = out_folder + "/" + prefix + str(split) + "-of-" + str(splits) + suffix
                with open(split_file_name, "w") as split_file:
                    i = 0
                    while i < rows_per_file:
                        split_file.write(f"{f.readline()}")
                        i = i + 1

    # Utility methods and properties
    @staticmethod
    def line_count_crossplatform(file_path: str):
        with open(file_path, "r", encoding='ISO-8859-1') as f:
            return sum(1 for _ in f)

    @staticmethod
    def line_count_unix(file_path: str):
        return int(os.popen(f'wc -l {file_path}').read().split()[0])
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WiperTools FASTQ splitter')
    fs = SplitFastq()
    fs.set_parser(parser)

    args = parser.parse_args()
    fs.run(args)