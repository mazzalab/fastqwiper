import os.path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gzip
import re
import codecs
import argparse
import logging

logging.basicConfig(level=logging.DEBUG)

# region Variables for final report
blank: int = 0
tot_lines: int = 0
bad_seq: int = 0
fixed_header: int = 0
bad_header: int = 0
bad_plus: int = 0
fixed_plus: int = 0
bad_qual: int = 0
qual_out_of_range: int = 0
clean_reads: int = 0
seq_len_neq_qual_len: int = 0
# endregion


def open_fastq_file(file_path: str):
    fastq_file_handler = None

    if "/" not in file_path and "\\" not in file_path:
        file_path = os.path.join(os.getcwd(), file_path)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        if file_path.endswith(".gz"):
            fastq_file_handler = gzip.open(
                file_path, "rt", encoding="utf-8", errors="ignore"
            )
        elif file_path.endswith(".fastq"):
            fastq_file_handler = codecs.open(
                file_path, encoding="utf-8", errors="ignore"
            )

    return fastq_file_handler


def read_next_line(fin, log_frequency: int):
    global tot_lines

    line = fin.readline()
    if line:
        # increment the total number of read not-empty lines
        tot_lines += 1
        print_log_during_reading(tot_lines, log_frequency)

    return line


def write_fastq_file(file_path: str):
    fastq_file_handler = None

    if "/" not in file_path or "\\" not in file_path:
        parent_folder = os.getcwd()
    else:
        parent_folder = os.path.abspath(os.path.join(file_path, os.pardir))

    if os.path.isdir(parent_folder):
        if file_path.endswith(".gz"):
            fastq_file_handler = gzip.open(file_path, "wt", encoding="utf-8")
        elif file_path.endswith(".fastq"):
            fastq_file_handler = open(file_path, "wt", encoding="utf-8")

    return fastq_file_handler


def check_header_line(line: str) -> str:
    global fixed_header, bad_header
    header: str = ""

    if line.isprintable() and line.rfind("@") == 0:
        header = line
    elif not line.isprintable():
        # This is a not printable header
        bad_header += 1
    elif "@" not in line:
        # This is an uncompliant header line
        bad_header += 1
    else:  # elif header.rfind("@") > 0:
        header = line
        header = header[header.rfind("@"):]
        fixed_header += 1

    return header


def check_seq_line(line: str) -> str:
    global bad_seq
    raw_seq: str = ""

    if not line.isprintable() or not reg.match(line):
        bad_seq += 1
    else:
        raw_seq = line

    return raw_seq


def check_plus_line(line: str) -> str:
    global bad_plus, fixed_plus
    plus: str = ""

    if not line.isprintable() or line.find("+") == -1:
        bad_plus += 1
    elif line.find("+") > 0:
        # Drop all characters except '+' character
        plus = '+'
        fixed_plus += 1
    else:
        plus = line

    return plus


def check_qual_line(line: str) -> str:
    global qual_out_of_range, bad_qual
    qual: str = ""

    if not line.isprintable():
        bad_qual += 1

    if line:
        min_ascii = min(ord(c) for c in line)
        max_ascii = max(ord(c) for c in line)
        if min_ascii >= 33 and max_ascii <= 126:
            qual = line
        else:
            qual_out_of_range += 1

    return qual


def print_log_during_reading(lines, log_frequency):
    if lines % log_frequency == 0:
        logging.info(f"Cleaned {lines} reads")


def print_to_file(header, raw_seq, head_qual_sep, qual, fout):
    fout.write(header + "\n")
    fout.write(raw_seq + "\n")
    fout.write(head_qual_sep + "\n")
    fout.write(qual + "\n")


def print_log_to_file(log_out):
    global tot_lines, clean_reads, seq_len_neq_qual_len, bad_qual, qual_out_of_range, bad_plus, \
        bad_seq, bad_header, fixed_header, fixed_plus, blank

    # Open file out summary log
    flog = open(log_out, "wt", encoding="utf-8")

    flog.write("SUMMARY:" + "\n" + "\n")
    flog.write(
        f"Clean lines: {clean_reads*4}/{tot_lines} ({round((clean_reads*4 / tot_lines) * 100, 2)}%)"
        + "\n"
    )
    flog.write(f"Not printable or uncompliant header lines: {bad_header}/{tot_lines}" + "\n")
    flog.write(f"Fixed header lines: {fixed_header}/{tot_lines}" + "\n")
    flog.write(f"BAD SEQ lines: {bad_seq}/{tot_lines}" + "\n")
    flog.write(f"BAD '+' lines: {bad_plus}/{tot_lines}" + "\n")
    flog.write(f"Fixed + lines: {fixed_plus}/{tot_lines}" + "\n")
    flog.write(f"BAD QUAL lines: {bad_qual}/{tot_lines}" + "\n")
    flog.write(f"QUAL out of range lines: {qual_out_of_range}/{tot_lines}" + "\n")
    flog.write(f"Len(SEQ) neq Len(QUAL): {seq_len_neq_qual_len}/{tot_lines}" + "\n")
    flog.write(f"Blank lines: {blank}/{tot_lines}" + "\n")

    flog.close()


def print_log_to_screen():
    global tot_lines, clean_reads, seq_len_neq_qual_len, bad_qual, qual_out_of_range, bad_plus, \
        bad_seq, bad_header, fixed_header, fixed_plus, blank

    if tot_lines == (clean_reads*4):
        logging.info(f"Clean lines: {clean_reads * 4}/{tot_lines} ({round((clean_reads * 4 / tot_lines) * 100, 2)}%)")
    else:
        logging.warning(
            f"Clean lines: {clean_reads * 4}/{tot_lines} ({round((clean_reads * 4 / tot_lines) * 100, 2)}%)")

    if bad_header == 0:
        logging.info(f"Not printable or uncompliant header lines: {bad_header}/{tot_lines}")
    else:
        logging.warning(f"Not printable or uncompliant header lines: {bad_header}/{tot_lines}")

    if fixed_header == 0:
        logging.info(f"Fixed header lines: {fixed_header}/{tot_lines}")
    else:
        logging.warning(f"Fixed header lines: {fixed_header}/{tot_lines}")

    if bad_seq == 0:
        logging.info(f"BAD SEQ lines: {bad_seq}/{tot_lines}")
    else:
        logging.warning(f"BAD SEQ lines: {bad_seq}/{tot_lines}")

    if bad_plus == 0:
        logging.info(f"BAD '+' lines: {bad_plus}/{tot_lines}")
    else:
        logging.warning(f"BAD '+' lines: {bad_plus}/{tot_lines}")

    if fixed_plus == 0:
        logging.info(f"Fixed + lines: {fixed_plus}/{tot_lines}")
    else:
        logging.warning(f"Fixed + lines: {fixed_plus}/{tot_lines}")

    if bad_qual == 0:
        logging.info(f"BAD QUAL lines: {qual_out_of_range}/{tot_lines}")
    else:
        logging.warning(f"BAD QUAL lines: {qual_out_of_range}/{tot_lines}")

    if qual_out_of_range == 0:
        logging.info(f"QUAL out of range lines: {qual_out_of_range}/{tot_lines}")
    else:
        logging.warning(f"QUAL out of range lines: {qual_out_of_range}/{tot_lines}")

    if seq_len_neq_qual_len == 0:
        logging.info(f"Len(SEQ) neq Len(QUAL): {seq_len_neq_qual_len}/{tot_lines}")
    else:
        logging.warning(f"Len(SEQ) neq Len(QUAL): {seq_len_neq_qual_len}/{tot_lines}")

    if blank == 0:
        logging.info(f"Blank lines: {blank}/{tot_lines}")
    else:
        logging.warning(f"Blank lines: {blank}/{tot_lines}")


def wipe_fastq(fastq_in: str, fastq_out: str, log_out: str, log_frequency: int):
    # MIN_HEADER_LEN = 10

    fin = open_fastq_file(fastq_in)
    if not fin:
        logging.critical("The input FASTQ file does not exist or bad extension (.gz or .fastq.gz)")
    else:
        logging.info(f"Start wiping {fastq_in}")

        # Open file out stream
        fout = write_fastq_file(fastq_out)

        # global variables anchor
        global tot_lines, clean_reads, seq_len_neq_qual_len

        # Loop through 4-line reads
        for line in fin:
            if not line.strip():
                # skip empty lines
                continue

            tot_lines += 1
            print_log_during_reading(tot_lines, log_frequency)

            # PROCESS THE HEADER LINE
            header: str = check_header_line(line.rstrip())
            if not header:
                continue

            # PROCESS THE SEQ LINE
            line = read_next_line(fin, log_frequency)
            raw_seq: str = check_seq_line(line.rstrip())
            if not raw_seq:
                continue

            # PROCESS the + line
            line = read_next_line(fin, log_frequency)
            plus: str = check_plus_line(line.rstrip())
            if not plus:
                continue

            # PROCESS the QUAL line
            line = read_next_line(fin, log_frequency)
            qual: str = check_qual_line(line.rstrip())
            if not qual:
                continue

            # Eventually print to file
            if len(raw_seq) == len(qual) and len(qual) != 0:
                print_to_file(header, raw_seq, plus, qual, fout)
                clean_reads += 1
            else:
                seq_len_neq_qual_len += 1

        fout.close()
        fin.close()

        # Print short report
        logging.info("Successfully terminated\n")

        if log_out:
            print_log_to_file(log_out)
        else:
            print_log_to_screen()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FastqWiper entrypoint')
    parser.add_argument("-i", '--fastq_in', help='The corrupted FASTQ file', required=True)
    parser.add_argument("-o", '--fastq_out', help='The wiped FASTQ file', required=True)
    parser.add_argument("-l", '--log_out', nargs='?',
                        help='The file name of the final quality report summary. Print on the screen if not specified')
    parser.add_argument("-f", '--log_frequency', type=int, nargs='?', default=500000, const=500000,
                        help='The number of reads you want to print a status message. Default: 500000')
    parser.add_argument("-a", '--alphabet', type=str, nargs='?', default="ACGTN", const="ACGTN",
                        help='Allowed character in the SEQ line. Default: ACGTN')
    args = parser.parse_args()

    # Allowed character of the SEQ line
    reg = re.compile(f"^[{args.alphabet}]+$")

    wipe_fastq(args.fastq_in, args.fastq_out,args.log_out, args.log_frequency)
