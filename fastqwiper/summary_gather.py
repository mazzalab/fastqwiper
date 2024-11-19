import argparse
import re
from fastqwiper.wipertool_abstract import WiperTool
from fastqwiper.fastq_wiper import (TOTAL_LINES, WELLFORMED, CLEAN, MISPLACED_HEADER, 
                                    BAD_SEQ, BAD_PLUS, BAD_QUAL, LENGTH_SEQ_QUAL, BLANKS)

# region CONST REGEX for output
INT_PERCENT_REGEX   : str = r"\s*(?P<var>\d+)\s*\(.+\)\s*"
INT_INT_REGEX       : str = r"\s*(?P<var>\d+)\s*\(.+\).+(?P<var2>\d+).+"
INT_REGEX           : str = r"\s*(?P<var>\d+)\s*"
# endregion

RECOVERED_HEADER: str = ""


class GatherSummaries(WiperTool):
    def __init__(self):
        super().__init__("summarygather")

    # Inherited methods
    def set_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("-s", '--summaries', nargs='+', help='List of summary files', required=True)
        parser.add_argument("-f", '--final_summary', help='The final summary file', required=True)
        # Add a version flag that prints the version and exits
        parser.add_argument('-v', '--version', action='version', version=self.version(), help='It prints the version and exists')

    def run(self, argv: argparse.Namespace):
        summary_filepaths = argv.summaries
        final_summary_filepath = argv.final_summary

        all_parsed = self.parse_all_summary_files(summary_filepaths)
        final_summary = self.aggregate_results(all_parsed)

        with open(final_summary_filepath, 'w') as file_out:
            file_out.write("FASTQWIPER SUMMARY:\n\n")

            file_out.write(f"{TOTAL_LINES}: {final_summary[TOTAL_LINES]}\n")
            file_out.write(f"{WELLFORMED}: {final_summary[WELLFORMED]} ({round((final_summary[WELLFORMED] / final_summary[TOTAL_LINES]) * 100, 2)}%)" + "\n")
            file_out.write(f"{CLEAN}: {final_summary[CLEAN]}\n")
            file_out.write(f"{MISPLACED_HEADER}: {final_summary[MISPLACED_HEADER]} ({round((final_summary[MISPLACED_HEADER] / final_summary[TOTAL_LINES]) * 100, 2)}%) of which {final_summary[RECOVERED_HEADER]} fixed\n")
            file_out.write(f"{BAD_SEQ}: {final_summary[BAD_SEQ]} ({round((final_summary[BAD_SEQ] / final_summary[TOTAL_LINES]) * 100, 2)}%)" + "\n")
            file_out.write(f"{BAD_PLUS}: {final_summary[BAD_PLUS]} ({round((final_summary[BAD_PLUS] / final_summary[TOTAL_LINES]) * 100, 2)}%)" + "\n")
            file_out.write(f"{BAD_QUAL}: {final_summary[BAD_QUAL]} ({round((final_summary[BAD_QUAL] / final_summary[TOTAL_LINES]) * 100, 2)}%)" + "\n")
            file_out.write(f"{LENGTH_SEQ_QUAL}: {final_summary[LENGTH_SEQ_QUAL]}" + "\n")
            file_out.write(f"{BLANKS}: {final_summary[BLANKS]} ({round((final_summary[BLANKS] / final_summary[TOTAL_LINES]) * 100, 2)}%)" + "\n")

    # Utility methods and properties
    @staticmethod
    def parse_summary_file(filepath):
        with open(filepath, 'r') as file:
            data = {}
            
            for line in file:
                line = line.rstrip()
                if line.startswith(TOTAL_LINES):
                    right = line.split(':')[1]
                    m = re.match(INT_REGEX, right)
                    if(m):
                        data[TOTAL_LINES] = int(m.group('var'))
                    else:
                        raise ValueError(f"TOT_LINES match failed for line: {right}")
                elif line.startswith(WELLFORMED):
                    right = line.split(':')[1]
                    m = re.match(INT_PERCENT_REGEX, right)
                    if m:
                        raise ValueError(f"WELLFORMED match failed for line: {right}")
                    else:
                        data[WELLFORMED] = 0
                elif line.startswith(CLEAN):
                    right = line.split(':')[1]
                    m = re.match(INT_REGEX, right)
                    if m:
                        data[CLEAN] = int(m.group('var'))
                    else:
                        raise ValueError(f"CLEAN match failed for line: {right}")
                elif line.startswith(MISPLACED_HEADER):
                    right = line.split(':')[1]
                    m = re.match(INT_INT_REGEX, right)
                    if m:
                        data[MISPLACED_HEADER] = int(m.group('var'))
                        data[RECOVERED_HEADER] = int(m.group('var2'))
                    else:
                        raise ValueError(f"MISPLACED_HEADER and RECOVERED_HEADER match failed for line: {right}")
                elif line.startswith(BAD_SEQ):
                    right = line.split(':')[1]
                    m = re.match(INT_PERCENT_REGEX, right)
                    if m:
                        data[BAD_SEQ] = int(m.group('var'))
                    else:
                        raise ValueError(f"BAD_SEQ match failed for line: {right}")
                elif line.startswith(BAD_PLUS):
                    right = line.split(':')[1]
                    m = re.match(INT_PERCENT_REGEX, right)
                    if m:
                        data[BAD_PLUS] = int(m.group('var'))
                    else:
                        raise ValueError(f"BAD_PLUS match failed for line: {right}")
                elif line.startswith(BAD_QUAL):
                    right = line.split(':')[1]
                    m = re.match(INT_PERCENT_REGEX, right)
                    if m:
                        data[BAD_QUAL] = int(m.group('var'))
                    else:
                        raise ValueError(f"BAD_QUAL match failed for line: {right}")
                elif line.startswith(LENGTH_SEQ_QUAL):
                    right = line.split(':')[1]
                    m = re.match(INT_REGEX, right)
                    if m:
                        data[LENGTH_SEQ_QUAL] = int(m.group('var'))
                    else:
                        raise ValueError(f"LENGTH_SEQ_QUAL match failed for line: {right}")
                elif line.startswith(BLANKS):
                    right = line.split(':')[1]
                    m = re.match(INT_PERCENT_REGEX, right)
                    if m:
                        data[BLANKS] = int(m.group('var'))
                    else:
                        raise ValueError(f"BLANKS match failed for line: {right}")

            return data

    def parse_all_summary_files(self, filepaths):
        results = []
        for s in filepaths:
            result = self.parse_summary_file(s)
            results.append(result)
        return results

    @staticmethod
    def aggregate_results(results):
        total_lines = 0
        wellformed = 0
        clean = 0
        misplaced_header = 0
        recovered_header = 0
        total_bad_seq = 0
        total_bad_plus = 0
        total_bad_qual = 0
        total_length = 0
        total_blanks = 0

        for result in results:
            total_lines = total_lines + result[TOTAL_LINES]
            wellformed = wellformed + result[WELLFORMED]
            clean = clean + result[CLEAN]
            misplaced_header = misplaced_header + result[MISPLACED_HEADER]
            recovered_header = recovered_header + result[RECOVERED_HEADER]
            total_bad_seq = total_bad_seq + result[BAD_SEQ]
            total_bad_plus = total_bad_plus + result[BAD_PLUS]
            total_bad_qual = total_bad_qual + result[BAD_QUAL]
            total_length = total_length + result[LENGTH_SEQ_QUAL]
            total_blanks = total_blanks + result[BLANKS]

        return {
            TOTAL_LINES: total_lines,
            WELLFORMED: wellformed,
            CLEAN: clean,
            MISPLACED_HEADER: misplaced_header,
            RECOVERED_HEADER: recovered_header,
            BAD_SEQ: total_bad_seq,
            BAD_PLUS: total_bad_plus,
            BAD_QUAL: total_bad_qual,
            LENGTH_SEQ_QUAL: total_length,
            BLANKS: total_blanks
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FastqWiper summaries gather')
    gs = GatherSummaries()
    gs.set_parser(parser)

    args = parser.parse_args()
    gs.run(args)
