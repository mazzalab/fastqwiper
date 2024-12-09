import os.path
import gzip
import re
import codecs
import logging
import argparse
from enum import auto, Enum
from pathlib import Path
from typing import Pattern, TextIO
from fastqwiper.wipertool_abstract import WiperTool


# region Variables for final report
blank: int = 0
tot_lines: int = 0
bad_seq: int = 0
header_length: int = 0
fixed_header: int = 0
bad_header: int = 0
bad_plus: int = 0
bad_qual: int = 0
clean_reads: int = 0
seq_len_neq_qual_len: int = 0
# endregion

# region CONST text for output
TOTAL_LINES: str = "Total lines"
WELLFORMED: str = "Well-formed lines"
CLEAN: str = "Clean reads"
MISPLACED_HEADER: str = "Bad headers or misplaced lines"
FIXED_HEADER: str = "Fixed header lines"
BAD_SEQ: str = "BAD SEQ lines"
BAD_PLUS: str = "BAD '+' lines"
BAD_QUAL: str = "BAD QUAL lines"
LENGTH_SEQ_QUAL: str = "Reads discarded because len(SEQ) neq len(QUAL)"
BLANKS: str = "Blank lines"
# endregion


class FastqWiper(WiperTool):
    def __init__(self):
        super().__init__("fastqwiper")

        self.reg = None
        logging.basicConfig(level=logging.DEBUG)

    # Inherited methods
    def set_parser(self, parser: argparse.ArgumentParser):
        if isinstance(parser, argparse.ArgumentParser):
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
                    raise ValueError(f"File '{fname}' doesn't end with one of {choices}")
                return fname

            parser.add_argument("-i", "--fastq_in", help="FASTQ file to be wiped", type=lambda s: file_choices(
                (e.name.lower().replace("_", ".") for e in FastqExtEnum), s), required=True)
            parser.add_argument("-o", "--fastq_out", type=lambda s: file_choices((e.name.lower(
            ).replace("_", ".") for e in FastqExtEnum), s), help="Wiped FASTQ file", required=True)

            # Optional arguments
            parser.add_argument("-r", "--report", nargs="?",
                                help="File name of the final quality report. Print on screen if not specified")
            parser.add_argument("-f", "--log_frequency", type=int, nargs="?", default=500000, const=500000,
                                help="Number of reads you want to print a status message. Default: 500000")
            parser.add_argument("-a", "--alphabet", type=str, nargs="?", default="ACGTN",
                                const="ACGTN", help="Allowed characters set in the SEQ line. Default: ACGTN")
            # Add a version flag that prints the version and exits
            parser.add_argument("-v", "--version", action="version",
                                version=self.version(), help="Prints the version and exists")
        else:
            logging.critical(
                " Incorrect parser. set_parser accepts an instance of "
                + f"argparse.Namespace. Passed: {parser}"
            )
            raise ValueError(
                "Incorrect parser. set_parser accepts an instance of "
                + f"argparse.Namespace. Passed: {parser}"
            )

    def run(self, argv: argparse.Namespace):
        fastq_in: str = argv.fastq_in
        fastq_out: str = argv.fastq_out
        report: str = argv.report
        log_frequency: int = argv.log_frequency
        alphabet: str = argv.alphabet

        fin = self.open_fastq_file(fastq_in)
        if not fin:
            logging.critical(
                f" {fastq_in} does not exist or is not a file"
            )
            raise ValueError(
                f"{fastq_in} does not exist or is not a file"
            )

        else:
            logging.info(f" Start wiping {fastq_in}")

            # Open file out stream
            fout: TextIO = self.create_fastq_write_file_handler(
                fastq_out
            )

            # global variables anchor
            global tot_lines, clean_reads, seq_len_neq_qual_len, blank
            # Allowed characters of the SEQ line
            reg: Pattern[str] = re.compile(f"^[{alphabet}]+$")

            # Loop through 4-line reads
            for line in fin:
                tot_lines += 1
                self.print_log_during_reading(tot_lines, log_frequency)

                if not line.rstrip():
                    blank += 1
                    continue

                # PROCESS THE HEADER LINE
                header: str = self.check_header_line(line.rstrip())
                if not header:
                    continue

                # PROCESS THE SEQ LINE
                line = self.read_next_line(fin, log_frequency)
                raw_seq: str = self.check_seq_line(line, reg)
                if not raw_seq:
                    continue

                # PROCESS the + line
                line = self.read_next_line(fin, log_frequency)
                plus: str = self.check_plus_line(line)
                if not plus:
                    continue

                # PROCESS the QUAL line
                line = self.read_next_line(fin, log_frequency)
                qual: str = self.check_qual_line(line)
                if not qual:
                    continue

                # Eventually print to file
                if len(raw_seq) == len(qual) and len(qual) != 0:
                    self.print_read_to_file(header, raw_seq, plus, qual, fout)
                    clean_reads += 1
                else:
                    seq_len_neq_qual_len += 1

            fout.close()
            fin.close()

            # Print short report
            logging.info(" Successfully wiped\n")

            if report:
                self.print_report_to_file(report)
            else:
                self.print_report_to_screen()

    # Utility methods and properties
    def open_fastq_file(self, file_path: str) -> None | TextIO:
        fastq_file_handler = None

        if "/" not in file_path and "\\" not in file_path:
            file_path = os.path.join(os.getcwd(), file_path)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            if file_path.endswith("fastq.gz") or file_path.endswith("fq.gz"):
                fastq_file_handler = gzip.open(
                    file_path, "rt", encoding="utf-8", errors="replace"
                )
            # if file_path.endswith(".fastq") or file_path.endswith(".fq"):
            else:
                fastq_file_handler = codecs.open(
                    file_path, encoding="utf-8", errors="replace"
                )
        
        return fastq_file_handler

    def read_next_line(self, fin: TextIO, log_frequency: int) -> str:
        global tot_lines, blank

        line: str = ""

        for line in fin:
            tot_lines += 1
            self.print_log_during_reading(tot_lines, log_frequency)

            line = line.rstrip()
            if not line:
                blank += 1
            else:
                return line

        return line

    @staticmethod
    def create_fastq_write_file_handler(file_path: str) -> TextIO:
        fastq_file_handler = None

        if file_path.endswith("fastq.gz") or file_path.endswith("fq.gz"):
            fastq_file_handler = gzip.open(
                file_path, "wt", encoding="utf-8"
            )
        # elif file_path.endswith(".fastq") or file_path.endswith(".fq"):
        else:
            fastq_file_handler = open(file_path, "wt", encoding="utf-8")

        return fastq_file_handler

    @staticmethod
    def check_header_line(line: str) -> str:
        global fixed_header, bad_header, header_length
        header: str = ""

        if line.isprintable() and line.rfind("@") == 0:
            header = line
            header_length = len(header)
        elif not line.isprintable():
            bad_header += 1

            rescued_header = line[line.rfind("@"):]
            if len(rescued_header) == header_length:
                fixed_header += 1
                header = rescued_header
        elif "@" not in line:
            # This is an uncompliant header line
            bad_header += 1
        else:  # elif header.rfind("@") > 0:
            bad_header += 1

            header = line
            header = header[header.rfind("@"):]
            fixed_header += 1

        return header

    @staticmethod
    def check_seq_line(line: str, reg: Pattern[str]) -> str:
        global bad_seq
        raw_seq: str = ""

        if not line.isprintable() or not reg.match(line):
            bad_seq += 1
        else:
            raw_seq = line

        return raw_seq

    @staticmethod
    def check_plus_line(line: str) -> str:
        global bad_plus
        plus: str = ""

        if not line.isprintable() or line.find("+") != 0:
            bad_plus += 1
        else:
            plus = line

        return plus

    @staticmethod
    def check_qual_line(line: str) -> str:
        global bad_qual
        qual: str = ""

        if not line.isprintable():
            bad_qual += 1
        else:
            qual = line

        return qual

    @staticmethod
    def print_log_during_reading(lines: int, log_frequency: int) -> None:
        if lines % log_frequency == 0:
            logging.info(f" Cleaned {lines} reads")

    @staticmethod
    def print_read_to_file(
        header: str, raw_seq: str, head_qual_sep: str, qual: str, fout: TextIO
    ):
        fout.write(header + "\n")
        fout.write(raw_seq + "\n")
        fout.write(head_qual_sep + "\n")
        fout.write(qual + "\n")

    @staticmethod
    def print_report_to_file(report: str) -> None:
        global \
            tot_lines, \
            clean_reads, \
            seq_len_neq_qual_len, \
            bad_qual, \
            bad_plus, \
            bad_seq, \
            bad_header, \
            fixed_header, \
            blank

        # Open report file
        flog: TextIO = open(report, "wt", encoding="utf-8")

        flog.write("FASTQWIPER REPORT:" + "\n\n")
        flog.write(f"{TOTAL_LINES}: {tot_lines}"+"\n")

        flog.write(
            f"{WELLFORMED}: {clean_reads*4} "
            f"({round((clean_reads*4 / tot_lines) * 100, 2)}%)"
            + "\n"
        )
        flog.write(f"{CLEAN}: {clean_reads}\n")
        flog.write(
            f"{MISPLACED_HEADER}: {bad_header} "
            f"({round((bad_header / tot_lines) * 100, 2)}%) "
            f"of which {fixed_header} fixed" + "\n"
        )
        flog.write(
            f"{BAD_SEQ}: {bad_seq} ({round((bad_seq / tot_lines) * 100, 2)}%)"
            + "\n"
        )
        flog.write(
            f"{BAD_PLUS}: {bad_plus} "
            f"({round((bad_plus / tot_lines) * 100, 2)}%)"
            + "\n"
        )
        flog.write(
            f"{BAD_QUAL}: {bad_qual} "
            f"({round((bad_qual / tot_lines) * 100, 2)}%)"
            + "\n"
        )
        flog.write(f"{LENGTH_SEQ_QUAL}: {seq_len_neq_qual_len}" + "\n")
        flog.write(
            f"{BLANKS}: {blank} ({round((blank / tot_lines) * 100, 2)}%)"
            + "\n"
        )

        flog.close()

    @staticmethod
    def print_report_to_screen() -> None:
        global \
            tot_lines, \
            clean_reads, \
            seq_len_neq_qual_len, \
            bad_qual, \
            bad_plus, \
            bad_seq, \
            bad_header, \
            fixed_header, \
            blank

        print("------------------------------")
        logging.info(" FASTQWIPER REPORT:" + "\n")
        logging.info(f" {TOTAL_LINES}: {tot_lines}")
        logging.info(
            f" {WELLFORMED}: {clean_reads*4} "
            f"({round((clean_reads*4 / tot_lines) * 100, 2)}%)"
        )
        logging.info(f" {CLEAN}: {clean_reads}")

        logging.warning(
            f" {MISPLACED_HEADER}: {bad_header} "
            f"({round((bad_header / tot_lines) * 100, 2)}%) "
            f"of which {fixed_header} fixed"
        )
        logging.warning(
            f" {BAD_SEQ}: {bad_seq} ({round((bad_seq / tot_lines) * 100, 2)}%)"
        )
        logging.warning(
            f" {BAD_PLUS}: {bad_plus} "
            f"({round((bad_plus / tot_lines) * 100, 2)}%)"
        )
        logging.warning(
            f" {BAD_QUAL}: {bad_qual} "
            f"({round((bad_qual / tot_lines) * 100, 2)}%)"
        )
        logging.warning(f" {LENGTH_SEQ_QUAL}: {seq_len_neq_qual_len}")
        logging.warning(
            f" {BLANKS}: {blank} ({round((blank / tot_lines) * 100, 2)}%)"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FastqWiper program help")
    fw = FastqWiper()
    fw.set_parser(parser)

    args: argparse.Namespace = parser.parse_args()
    fw.run(args)
