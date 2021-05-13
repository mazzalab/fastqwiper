import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from colorama import init
init(convert=True)
import click
import gzip
import re
import codecs
from fastq_wiper import log


def open_fastq_file(file_path: str):
    fastq_file_handler = None

    if '/' not in file_path and '\\' not in file_path:
        file_path = os.path.join(os.getcwd(), file_path)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        if file_path.endswith('.gz'):
            fastq_file_handler = gzip.open(file_path, 'rt', encoding="utf-8", errors='ignore')
        elif file_path.endswith('.fastq'):
            fastq_file_handler = codecs.open(file_path, encoding='utf-8', errors='ignore')
            # fastq_file_handler = open(file_path, 'rt', encoding="utf8", errors='strict')

    return fastq_file_handler


def write_fastq_file(file_path: str):
    fastq_file_handler = None

    if '/' not in file_path and '\\' not in file_path:
        parent_folder = os.getcwd()
    else:
        parent_folder = os.path.abspath(os.path.join(file_path, os.pardir))

    if os.path.isdir(parent_folder):
        if file_path.endswith('.gz'):
            fastq_file_handler = gzip.open(file_path, 'wt', encoding="utf-8")
        elif file_path.endswith('.fastq'):
            fastq_file_handler = open(file_path, 'wt', encoding="utf-8")

    return fastq_file_handler


@click.command()
@click.option("--fastq_in", required=True, help="The input FASTQ file")
@click.option("--fastq_out", required=True, help="The wiped FASTQ file")
@click.option("--log_frequency", type=click.INT, default=500000,
              help="The number of reads you want to print a status message")
def wipe_fastq(fastq_in: str, fastq_out: str, log_frequency: int):
    # region Variables for final report
    tot_lines: int = 0
    clean_reads: int = 0
    seq_len_neq_qual_len = 0
    qual_out_range = 0
    plus_row = 0
    seq_odd_chars = 0
    qual_odd_chars = 0
    head_print = 0
    head_at = 0
    blank = 0
    head_plus = 0
    unexpected_line = 0
    # endregion

    MIN_HEADER_LEN = 10

    fin = open_fastq_file(fastq_in)
    if not fin:
        log.error('The input FASTQ file does not exist or bad extension')
        click.echo(click.style("The input FASTQ file does not exist or bad extension", fg='red'))
    else:
        click.echo(click.style(f"Start wiping {fastq_in}", fg='blue'))

        # Allowed character of the SEQ line
        reg = re.compile('^[ACGTN]+$')

        # Open file out stream
        fout = write_fastq_file(fastq_out)

        # Loop through 4-line reads
        at_found = False
        seq_found = False
        plus_found = False
        qual_found = False
        for line in fin:
            line = line.rstrip()

            tot_lines += 1

            if clean_reads % log_frequency == 0 and clean_reads > 0:
                log.info(f"Cleaned {clean_reads} reads")

            while True:
                if line:
                    break
                else:
                    blank += 1
                    line = fin.readline()
                    continue

            # header line
            if line.isprintable() and "@" in line:  # and len(line) > MIN_HEADER_LEN:
                at_found = True
                seq_found = False
                plus_found = False

                # Drop all character preceding the last @ character of the header
                if line.rfind('@') > 0:
                    line = line[line.rfind('@'):]
                    head_at += 1

                header: str = line.rstrip()

            # seq line
            elif line.isprintable() and at_found and reg.match(line):
                seq_found = True
                raw_seq: str = line

            # + line
            elif '+' in line and line.isprintable() and at_found and seq_found:
                plus_found = True

                if line != "+":
                    # Drop all characters except + of the qual line separator
                    line = '+'
                    head_plus += 1

                head_qual_sep: str = line

            # qual line
            elif line.isprintable() and at_found and seq_found and plus_found:
                qual_found = True

                min_ascii = min(ord(c) for c in line)
                max_ascii = max(ord(c) for c in line)
                if min_ascii >= 33 and max_ascii <= 126:
                    qual: str = line

                    if len(raw_seq) == len(qual) and len(qual) != 0:
                        fout.write(header + '\n')
                        fout.write(raw_seq + '\n')
                        fout.write(head_qual_sep + '\n')
                        fout.write(qual + '\n')

                        clean_reads += + 1
                    else:
                        seq_len_neq_qual_len += 1
                else:
                    qual_out_range += 1

                at_found = False
                seq_found = False
                plus_found = False
                qual_found = False

            # unexpected line
            else:
                if not at_found:
                    head_print += 1
                elif not seq_found:
                    seq_odd_chars += 1
                elif not plus_found:
                    plus_row += 1
                elif not qual_found:
                    qual_odd_chars += 1
                else:
                    unexpected_line += 1

                at_found = False
                seq_found = False
                plus_found = False
                qual_found = False

        fout.close()
        fin.close()

    click.echo(click.style("Successfully terminated\n", fg='blue'))

    click.echo(click.style(f"Wiped lines: {clean_reads*4}/{tot_lines} ({round((clean_reads*4 / tot_lines) * 100, 2)}%)",
                           fg='blue' if tot_lines == clean_reads else 'yellow'))
    click.echo(click.style(f"Len(SEQ) neq Len(QUAL): {seq_len_neq_qual_len}/{tot_lines}",
                           fg='blue' if seq_len_neq_qual_len == 0 else 'red'))
    click.echo(click.style(f"BAD QUAL lines: {qual_out_range}/{tot_lines}",
                           fg='blue' if qual_out_range == 0 else 'red'))
    click.echo(click.style(f"BAD + lines: {plus_row}/{tot_lines}",
                           fg='blue' if plus_row == 0 else 'red'))
    click.echo(click.style(f"BAD SEQ lines: {seq_odd_chars}/{tot_lines}",
                           fg='blue' if seq_odd_chars == 0 else 'red'))
    click.echo(click.style(f"Not printable header lines: {head_print}/{tot_lines}",
                           fg='blue' if head_print == 0 else 'red'))
    click.echo(click.style(f"Not printable qual lines: {qual_odd_chars}/{tot_lines}",
                           fg='blue' if qual_odd_chars == 0 else 'red'))
    click.echo(click.style(f"Fixed header lines: {head_at}/{tot_lines}",
                           fg='blue' if head_at == 0 else 'yellow'))
    click.echo(click.style(f"Fixed + lines: {head_plus}/{tot_lines}",
                           fg='blue' if head_plus == 0 else 'yellow'))
    click.echo(click.style(f"Blank lines: {blank}/{tot_lines}",
                           fg='blue' if blank == 0 else 'yellow'))
    click.echo(click.style(f"Missplaced lines: {unexpected_line}/{tot_lines}",
                           fg='blue' if unexpected_line == 0 else 'yellow'))


if __name__ == '__main__':
    # click.clear()
    wipe_fastq()
