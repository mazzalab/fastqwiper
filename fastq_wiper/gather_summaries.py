import argparse
from wiper import (NOTPRINT_HEADER, FIXED_HEADER, BAD_SEQ, BAD_PLUS, FIXED_PLUS, BAD_QUAL, QUAL_OUT_RANGE,
                   LENGTH_SEQ_QUAL, BLANKS)


def parse_summary_file(filepath):
    with open(filepath, 'r') as file:
        data = {}
        for line in file:
            if line.startswith(NOTPRINT_HEADER):
                left, right = map(int, line.split()[-1].split('/'))
                data[NOTPRINT_HEADER] = (left, right)
            elif line.startswith(FIXED_HEADER):
                left, right = map(int, line.split()[-1].split('/'))
                data[FIXED_HEADER] = (left, right)
            elif line.startswith(BAD_SEQ):
                left, right = map(int, line.split()[-1].split('/'))
                data[BAD_SEQ] = (left, right)
            elif line.startswith(BAD_PLUS):
                left, right = map(int, line.split()[-1].split('/'))
                data[BAD_PLUS] = (left, right)
            elif line.startswith(FIXED_PLUS):
                left, right = map(int, line.split()[-1].split('/'))
                data[FIXED_PLUS] = (left, right)
            elif line.startswith(BAD_QUAL):
                left, right = map(int, line.split()[-1].split('/'))
                data[BAD_QUAL] = (left, right)
            elif line.startswith(QUAL_OUT_RANGE):
                left, right = map(int, line.split()[-1].split('/'))
                data[QUAL_OUT_RANGE] = (left, right)
            elif line.startswith(LENGTH_SEQ_QUAL):
                left, right = map(int, line.split()[-1].split('/'))
                data[LENGTH_SEQ_QUAL] = (left, right)
            elif line.startswith(BLANKS):
                left, right = map(int, line.split()[-1].split('/'))
                data[BLANKS] = (left, right)

        return data


def parse_all_summary_file(summaries):
    results = []
    for s in summaries:
        result = parse_summary_file(s)
        results.append(result)
    return results


def aggregate_results(results):
    total_not_printable = (0, 0)
    total_fixed_headers = (0, 0)
    total_bad_seq = (0, 0)
    total_bad_plus = (0, 0)
    total_fixed_plus = (0, 0)
    total_bad_qual = (0, 0)
    total_qual_range = (0, 0)
    total_length = (0, 0)
    total_blanks = (0, 0)

    for result in results:
        total_not_printable = (total_not_printable[0] + result[NOTPRINT_HEADER][0],
                               total_not_printable[1] + result[NOTPRINT_HEADER][1])
        total_fixed_headers = (total_fixed_headers[0] + result[FIXED_HEADER][0],
                               total_fixed_headers[1] + result[FIXED_HEADER][1])
        total_bad_seq = (total_bad_seq[0] + result[BAD_SEQ][0],
                         total_bad_seq[1] + result[BAD_SEQ][1])
        total_bad_plus = (total_bad_plus[0] + result[BAD_PLUS][0],
                          total_bad_plus[1] + result[BAD_PLUS][1])
        total_fixed_plus = (total_fixed_plus[0] + result[FIXED_PLUS][0],
                            total_fixed_plus[1] + result[FIXED_PLUS][1])
        total_bad_qual = (total_bad_qual[0] + result[BAD_QUAL][0],
                          total_bad_qual[1] + result[BAD_QUAL][1])
        total_qual_range = (total_qual_range[0] + result[QUAL_OUT_RANGE][0],
                            total_qual_range[1] + result[QUAL_OUT_RANGE][1])
        total_length = (total_length[0] + result[LENGTH_SEQ_QUAL][0],
                        total_length[1] + result[LENGTH_SEQ_QUAL][1])
        total_blanks = (total_blanks[0] + result[BLANKS][0],
                        total_blanks[1] + result[BLANKS][1])

    return {
        NOTPRINT_HEADER: total_not_printable,
        FIXED_HEADER: total_fixed_headers,
        BAD_SEQ: total_bad_seq,
        BAD_PLUS: total_bad_plus,
        FIXED_PLUS: total_fixed_plus,
        BAD_QUAL: total_bad_qual,
        QUAL_OUT_RANGE: total_qual_range,
        LENGTH_SEQ_QUAL: total_length,
        BLANKS: total_blanks
    }


def main():
    parser = argparse.ArgumentParser(description='FastqWiper summaries gather')
    parser.add_argument("-s", '--summaries', nargs='+', help='List of summary files', required=True)
    parser.add_argument("-f", '--final_summary', help='The final summary file', required=True)
    args = parser.parse_args()

    all_parsed = parse_all_summary_file(args.summaries)
    final_summary = aggregate_results(all_parsed)

    with open(args.final_summary, 'w') as file_out:
        file_out.write("FASTQWIPER SUMMARY:\n\n")
        file_out.write(f"{NOTPRINT_HEADER}: {final_summary[NOTPRINT_HEADER][0]}/{final_summary[NOTPRINT_HEADER][1]}\n")
        file_out.write(f"{FIXED_HEADER}: {final_summary[FIXED_HEADER][0]}/{final_summary[FIXED_HEADER][1]}\n")
        file_out.write(f"{BAD_SEQ}: {final_summary[BAD_SEQ][0]}/{final_summary[BAD_SEQ][1]}\n")
        file_out.write(f"{BAD_PLUS}: {final_summary[BAD_PLUS][0]}/{final_summary[BAD_PLUS][1]}\n")
        file_out.write(f"{FIXED_PLUS}: {final_summary[FIXED_PLUS][0]}/{final_summary[FIXED_PLUS][1]}\n")
        file_out.write(f"{BAD_QUAL}: {final_summary[BAD_QUAL][0]}/{final_summary[BAD_QUAL][1]}\n")
        file_out.write(f"{QUAL_OUT_RANGE}: {final_summary[QUAL_OUT_RANGE][0]}/{final_summary[QUAL_OUT_RANGE][1]}\n")
        file_out.write(f"{LENGTH_SEQ_QUAL}: {final_summary[LENGTH_SEQ_QUAL][0]}/{final_summary[LENGTH_SEQ_QUAL][1]}\n")
        file_out.write(f"{BLANKS}: {final_summary[BLANKS][0]}/{final_summary[BLANKS][1]}\n")


if __name__ == "__main__":
    main()