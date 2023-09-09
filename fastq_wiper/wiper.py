import os.path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from colorama import init

init(convert=True)
import click
import gzip
import re
import codecs
from fastq_wiper import log


# region Variables for final report
tot_lines: int = 0
clean_reads: int = 0
seq_len_neq_qual_len: int = 0
qual_out_range: int = 0
plus_row: int = 0
seq_odd_chars: int = 0
qual_odd_chars: int = 0
head_print: int = 0
head_at: int = 0
blank: int = 0
head_plus: int = 0
unexpected_line: int = 0
# endregion

# Allowed character of the SEQ line
reg = re.compile("^[ACGTN]+$")


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


def fix_header_line(line: str, checkpoint_flags: dict) -> str:
    checkpoint_flags["at"] = True

    # Drop all character preceding the last @ character of the header
    if line.rfind("@") > 0:
        line = line[line.rfind("@") :]

        global head_at
        head_at += 1

    header: str = line.rstrip()
    return header


def fix_seq_line(line: str, checkpoint_flags: dict) -> str:
    raw_seq: str = ""

    if reg.match(line):
        checkpoint_flags["seq"] = True
        raw_seq = line

    return raw_seq


def fix_plus_line(line: str, checkpoint_flags: dict) -> str:
    checkpoint_flags["plus"] = True

    if line != "+":
        # Drop all characters except + of the qual line separator
        line = "+"

        global head_plus
        head_plus += 1

    return line


def fix_qual_line(line: str, checkpoint_flags: dict) -> str:
    qual: str = ""

    min_ascii = min(ord(c) for c in line)
    max_ascii = max(ord(c) for c in line)
    if min_ascii >= 33 and max_ascii <= 126:
        checkpoint_flags["qual"] = True
        qual: str = line
    else:
        global qual_out_range
        qual_out_range += 1

    return qual


def skip_empty_lines(line: str, fin) -> str:
    while True:
        if line:
            line = line.rstrip()
            break
        else:
            global blank
            blank += 1
            line = fin.readline()
            continue

    return line


def print_log_during_reading(lines, log_frequency):
    if lines % log_frequency == 0:
        log.info(f"Cleaned {lines} reads")


def print_to_file(header, raw_seq, head_qual_sep, qual, fout):
    fout.write(header + "\n")
    fout.write(raw_seq + "\n")
    fout.write(head_qual_sep + "\n")
    fout.write(qual + "\n")


def print_log_to_file(log_out):
    global tot_lines, clean_reads, seq_len_neq_qual_len, head_print, seq_odd_chars, plus_row, qual_odd_chars, unexpected_line

    # Open file out summary log
    flog = open(log_out, "wt", encoding="utf-8")

    flog.write("SUMMARY:" + "\n" + "\n")
    flog.write(
        f"Clean lines: {clean_reads*4}/{tot_lines} ({round((clean_reads*4 / tot_lines) * 100, 2)}%)"
        + "\n"
    )
    flog.write(f"Len(SEQ) neq Len(QUAL): {seq_len_neq_qual_len}/{tot_lines}" + "\n")
    flog.write(f"BAD QUAL lines: {qual_out_range}/{tot_lines}" + "\n")
    flog.write(f"BAD '+' lines: {plus_row}/{tot_lines}" + "\n")
    flog.write(f"BAD SEQ lines: {seq_odd_chars}/{tot_lines}" + "\n")
    flog.write(
        f"Not printable or uncompliant header lines: {head_print}/{tot_lines}" + "\n"
    )
    flog.write(f"Not printable qual lines: {qual_odd_chars}/{tot_lines}" + "\n")
    flog.write(f"Fixed header lines: {head_at}/{tot_lines}" + "\n")
    flog.write(f"Fixed + lines: {head_plus}/{tot_lines}" + "\n")
    flog.write(f"Blank lines: {blank}/{tot_lines}" + "\n")
    flog.write(f"Missplaced lines: {unexpected_line}/{tot_lines}" + "\n")

    flog.close()


def print_log_to_screen():
    global tot_lines, clean_reads, seq_len_neq_qual_len, head_print, seq_odd_chars, plus_row, qual_odd_chars, unexpected_line

    click.echo(
        click.style(
            f"Clean lines: {clean_reads*4}/{tot_lines} ({round((clean_reads*4 / tot_lines) * 100, 2)}%)",
            fg="blue" if tot_lines == clean_reads else "yellow",
        )
    )
    click.echo(
        click.style(
            f"Len(SEQ) neq Len(QUAL): {seq_len_neq_qual_len}/{tot_lines}",
            fg="blue" if seq_len_neq_qual_len == 0 else "red",
        )
    )
    click.echo(
        click.style(
            f"BAD QUAL lines: {qual_out_range}/{tot_lines}",
            fg="blue" if qual_out_range == 0 else "red",
        )
    )
    click.echo(
        click.style(
            f"BAD '+' lines: {plus_row}/{tot_lines}",
            fg="blue" if plus_row == 0 else "red",
        )
    )
    click.echo(
        click.style(
            f"BAD SEQ lines: {seq_odd_chars}/{tot_lines}",
            fg="blue" if seq_odd_chars == 0 else "red",
        )
    )
    click.echo(
        click.style(
            f"Not printable or uncompliant header lines: {head_print}/{tot_lines}",
            fg="blue" if head_print == 0 else "red",
        )
    )
    click.echo(
        click.style(
            f"Not printable qual lines: {qual_odd_chars}/{tot_lines}",
            fg="blue" if qual_odd_chars == 0 else "red",
        )
    )
    click.echo(
        click.style(
            f"Fixed header lines: {head_at}/{tot_lines}",
            fg="blue" if head_at == 0 else "yellow",
        )
    )
    click.echo(
        click.style(
            f"Fixed + lines: {head_plus}/{tot_lines}",
            fg="blue" if head_plus == 0 else "yellow",
        )
    )
    click.echo(
        click.style(
            f"Blank lines: {blank}/{tot_lines}",
            fg="blue" if blank == 0 else "yellow",
        )
    )
    click.echo(
        click.style(
            f"Missplaced lines: {unexpected_line}/{tot_lines}",
            fg="blue" if unexpected_line == 0 else "yellow",
        )
    )


def reset_flags(checkpoint_flags: dict):
    checkpoint_flags["at"] = False
    checkpoint_flags["seq"] = False
    checkpoint_flags["plus"] = False
    checkpoint_flags["qual"] = False


def count_remainder():
    global tot_lines
    return tot_lines % 4


@click.command()
@click.option(
    "--fastq_in", type=click.STRING, required=True, help="The input FASTQ file"
)
@click.option(
    "--fastq_out", type=click.STRING, required=True, help="The wiped FASTQ file"
)
@click.option(
    "--log_out",
    type=click.STRING,
    required=False,
    help="The file name of the final quality report summary",
)
@click.option(
    "--log_frequency",
    type=click.INT,
    default=500000,
    help="The number of reads you want to print a status message",
)
def wipe_fastq(fastq_in: str, fastq_out: str, log_out: str, log_frequency: int):
    # MIN_HEADER_LEN = 10

    fin = open_fastq_file(fastq_in)
    if not fin:
        click.echo(
            click.style(
                "The input FASTQ file does not exist or bad extension (.gz or .fastq.gz)",
                fg="red",
            )
        )
    else:
        click.echo(click.style(f"Start wiping {fastq_in}", fg="blue"))

        # Open file out stream
        fout = write_fastq_file(fastq_out)

        # change if a lines is parsed succesfully
        checkpoint_flags = {
            "at": False,
            "seq": False,
            "plus": False,
            "qual": False,
        }

        # Cleaned lines to be printed
        header: str = ""
        raw_seq: str = ""
        head_qual_sep: str = ""
        qual: str = ""

        # global variables anchor
        global tot_lines, clean_reads, seq_len_neq_qual_len, head_print, seq_odd_chars, plus_row, qual_odd_chars, unexpected_line

        # Loop through 4-line reads
        for line in fin:
            tot_lines += 1  # increment the total number of read lines

            print_log_during_reading(tot_lines, log_frequency)
            line = skip_empty_lines(line, fin)

            # header line
            if (
                line.isprintable()
                and "@" in line
                and not checkpoint_flags["at"]
                and not checkpoint_flags["seq"]
                and not checkpoint_flags["plus"]
                and not checkpoint_flags["qual"]
            ):
                header = fix_header_line(line, checkpoint_flags)

            # seq line
            elif (
                line.isprintable()
                and checkpoint_flags["at"]
                and not checkpoint_flags["seq"]
                and not checkpoint_flags["plus"]
                and not checkpoint_flags["qual"]
            ):
                raw_seq = fix_seq_line(line, checkpoint_flags)

            # + line
            elif (
                "+" in line
                and line.isprintable()
                and checkpoint_flags["at"]
                and checkpoint_flags["seq"]
                and not checkpoint_flags["plus"]
                and not checkpoint_flags["qual"]
            ):
                head_qual_sep = fix_plus_line(line, checkpoint_flags)

            # qual line
            elif (
                line.isprintable()
                and checkpoint_flags["at"]
                and checkpoint_flags["seq"]
                and checkpoint_flags["plus"]
                and not checkpoint_flags["qual"]
            ):
                qual = fix_qual_line(line, checkpoint_flags)

                if len(raw_seq) == len(qual) and len(qual) != 0:
                    print_to_file(header, raw_seq, head_qual_sep, qual, fout)
                    clean_reads += 1
                else:
                    seq_len_neq_qual_len += 1

                reset_flags(checkpoint_flags)

            # unexpected line
            else:
                if (
                    "@" in line
                    and not checkpoint_flags["at"]
                    and not checkpoint_flags["seq"]
                    and not checkpoint_flags["plus"]
                    and not checkpoint_flags["qual"]
                ):
                    head_print += 1
                elif (
                    "@" not in line
                    and not checkpoint_flags["at"]
                    and not checkpoint_flags["seq"]
                    and not checkpoint_flags["plus"]
                    and not checkpoint_flags["qual"]
                ):
                    unexpected_line += 1
                elif (
                    checkpoint_flags["at"]
                    and not checkpoint_flags["seq"]
                    and not checkpoint_flags["plus"]
                    and not checkpoint_flags["qual"]
                ):
                    seq_odd_chars += 1
                elif (
                    checkpoint_flags["at"]
                    and checkpoint_flags["seq"]
                    and not checkpoint_flags["plus"]
                    and not checkpoint_flags["qual"]
                ):
                    plus_row += 1
                elif (
                    checkpoint_flags["at"]
                    and checkpoint_flags["seq"]
                    and checkpoint_flags["plus"]
                    and not checkpoint_flags["qual"]
                ):
                    qual_odd_chars += 1
                else:
                    unexpected_line += 1

                reset_flags(checkpoint_flags)

        # All lines that do not refer to any header at the end of the file are considered "unexpected" (1 to 3 lines max)
        unexpected_line += count_remainder()

        fout.close()
        fin.close()

        # Print short report
        click.echo(click.style("Successfully terminated\n", fg="blue"))

        if log_out:
            print_log_to_file(log_out)
        else:
            print_log_to_screen()


if __name__ == "__main__":
    wipe_fastq()
