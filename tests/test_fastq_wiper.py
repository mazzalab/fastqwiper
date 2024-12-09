import os
import re
import pytest
import argparse
from typing import Pattern
from io import TextIOWrapper
from codecs import StreamReaderWriter
from fastqwiper.fastq_wiper import FastqWiper


@pytest.fixture
def fw():
    f = FastqWiper()

    yield f

    print("\nTearing down resources...")
    try:
        os.remove("./tests/testdata/new.fastq")
    except OSError:
        pass


@pytest.fixture
def fw_fastq(fw):
    return fw.open_fastq_file("./tests/testdata/test.fastq")


@pytest.fixture
def fw_fastq_gz(fw):
    return fw.open_fastq_file("./tests/testdata/test.fastq.gz")


@pytest.fixture
def fw_bad_fastq(fw):
    return fw.open_fastq_file("./tests/testdata/bad.fastq")


@pytest.fixture
def fw_parser():
    fastq_in: str = "./tests/testdata/bad.fastq"
    fastq_out: str = "./tests/testdata/bad_wiped.fastq"
    report: str = "./tests/testdata/bad.report"
    log_frequency: int = 100
    alphabet: str = "ACGTN"

    return argparse.Namespace(
        fastq_in=fastq_in,
        fastq_out=fastq_out,
        report=report,
        log_frequency=log_frequency,
        alphabet=alphabet,
    )


@pytest.fixture
def fw_run(fw, fw_parser):
    fw.run(fw_parser)

    print("\nSetting up resources...")
    with open("./tests/testdata/bad_wiped.fastq", "r") as file:
        data = file.read()
    with open("./tests/testdata/bad.report", "r") as file_log:
        data_log = file_log.read()

    # Execute the actual test
    yield (data, data_log)

    print("\nTearing down resources...")
    os.remove("./tests/testdata/bad_wiped.fastq")
    os.remove("./tests/testdata/bad.report")


def test_set_parser(fw, fw_parser):
    with pytest.raises(ValueError):
        fw.set_parser(fw_parser)
    # print(f"\n{excinfo.value}")


def test_set_parser_bad_argument_ext(fw, fw_parser):
    fw_parser.fastq_out = "wrong_ext.txt"

    with pytest.raises(ValueError):
        fw.set_parser(fw_parser)
    # print(f"\n{excinfo.value}")


def test_run(fw_run):
    with open("./tests/testdata/bad_wiped_test.fastq", "r") as file_test:
        data_test = file_test.read()

        assert fw_run[0] == data_test


def test_run_wrong_filein(fw, fw_parser):
    fw_parser.fastq_in = "wrong_file.txt"

    with pytest.raises(ValueError):
        fw.run(fw_parser)
    # print(f"\n{excinfo.value}")


def test_report(fw_run):
    with open("./tests/testdata/bad_test.report", "r") as file_log_test:
        data_test = file_log_test.read()

        assert fw_run[1] == data_test


def test_fastq_file_exist(fw_fastq):
    assert isinstance(fw_fastq, StreamReaderWriter)


def test_fastq_gz_file_exist(fw_fastq_gz):
    assert isinstance(fw_fastq_gz, TextIOWrapper)


def test_read_next_line(fw, fw_fastq):
    fw.read_next_line(fw_fastq, 100)
    fw.read_next_line(fw_fastq, 100)
    fw.read_next_line(fw_fastq, 100)
    fw.read_next_line(fw_fastq, 100)
    line = fw.read_next_line(fw_fastq, 100)

    assert line == "@NS500299:185:HK57NBGXG:1:11101:19673:1046 2:N:0:CGAGGCTG"


def test_create_fastq_write_file_handler(fw):
    assert isinstance(
        fw.create_fastq_write_file_handler("./tests/testdata/new.fastq"),
        TextIOWrapper,
    )


def test_check_wellformed_header_line(fw, fw_bad_fastq):
    assert fw.check_header_line(fw.read_next_line(fw_bad_fastq, 100))


def test_check_mallformed_header_line(fw, fw_bad_fastq):
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    plus_line = fw.read_next_line(fw_bad_fastq, 100)

    assert fw.check_header_line(plus_line) == ""


def test_check_wellformed_seq_line(fw, fw_bad_fastq):
    reg: Pattern[str] = re.compile("^[ACGTN]+$")

    fw.read_next_line(fw_bad_fastq, 100)
    assert fw.check_seq_line(fw.read_next_line(fw_bad_fastq, 100), reg)


def test_check_mallformed_seq_line(fw, fw_bad_fastq):
    reg: Pattern[str] = re.compile("^[ACGTN]+$")

    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    assert fw.check_seq_line(fw.read_next_line(fw_bad_fastq, 100), reg) == ""


def test_check_wellformed_plus_line(fw, fw_bad_fastq):
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    assert fw.check_plus_line(fw.read_next_line(fw_bad_fastq, 100)) == "+"


def test_check_malformed_plus_line(fw, fw_bad_fastq):
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    assert fw.check_plus_line(fw.read_next_line(fw_bad_fastq, 100)) == ""


def test_check_wellformed_qual_line(fw, fw_bad_fastq):
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)

    assert (
        fw.check_qual_line(fw.read_next_line(fw_bad_fastq, 100))
        == "#A<AA/EEEEEEEEEEEEEAEEEEEEEEE#EEEE#EE#EEE#EE<###E#EEEE/"
        "EEEEEEE/EEEEEEAEEEAEE"
    )


def test_check_malformed_qual_line(fw, fw_bad_fastq):
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)
    fw.read_next_line(fw_bad_fastq, 100)

    assert fw.check_qual_line(fw.read_next_line(fw_bad_fastq, 100)) == ""
