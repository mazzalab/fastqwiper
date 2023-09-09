from io import TextIOWrapper
from codecs import StreamReaderWriter
from fastq_wiper.wiper import open_fastq_file, write_fastq_file


class TestClass:
    def test_open_fastq(self):
        fin = open_fastq_file("./testdata/")
        assert fin == None
    
    def test_open_fastq2(self):
        fin = open_fastq_file("./tests/testdata/test.fastq")
        assert isinstance(fin, StreamReaderWriter)

    def test_open_fastq3(self):
        fin = open_fastq_file("./tests/testdata/test.fastq.gz")
        assert isinstance(fin, TextIOWrapper)

    def test_write_clean_fastq(self, tmp_path):
        d = str(tmp_path) + "/test_fastq.fastq"
        fout = write_fastq_file(d)
        assert isinstance(fout, TextIOWrapper)

    ########################################################################
    
    
    