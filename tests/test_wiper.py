from io import TextIOWrapper
from codecs import StreamReaderWriter
from fastqwiper.fastq_wiper import FastqWiper


class TestClass:
    def __init__(self):
        self.fw = FastqWiper()

    def test_open_fastq(self):
        fin = self.fw.open_fastq_file("./testdata/")
        assert fin == None
    
    def test_open_fastq2(self):
        fin = self.fw.open_fastq_file("./tests/testdata/test.fastq")
        assert isinstance(fin, StreamReaderWriter)

    def test_open_fastq3(self):
        fin = self.fw.open_fastq_file("./tests/testdata/test.fastq.gz")
        assert isinstance(fin, TextIOWrapper)

    def test_write_clean_fastq(self, tmp_path):
        d = str(tmp_path) + "/test_fastq.fastq"
        fout = self.fw.write_fastq_file(d)
        assert isinstance(fout, TextIOWrapper)

    ########################################################################
    
    
    