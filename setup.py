import sys

try:
    from importlib import util
except:
    sys.stdout.write(
        "\nIt seems that importlib library is not available on this machine. Please install pip (e.g. for Ubuntu, run "
        "'sudo apt-get install python3-pip'.\n")
    sys.exit()

import glob

if util.find_spec("setuptools") is None:
    sys.stdout.write(
        "\nIt seems that setuptools is not available on this machine. Please install pip (e.g. for Ubuntu, run "
        "'sudo apt-get install python3-pip'.\n")
    sys.exit()

from setuptools import setup, find_packages

if sys.version_info <= (3, 7):
    sys.exit('Sorry, Python < 3.7 is not supported')

with open('README.md') as f:
    long_description = f.read()

setup(
    name='fastqwiper',
    version='0.1',
    author='Tommaso Mazza',
    author_email='bioinformatics@css-mendel.it',
    description="A workflow to recover corrupted fastq.gz files, skip uncomplaint reads and remove unpaired reads",
    url="https://github.com/mazzalab/fastqwiper",
    packages=find_packages(),
    include_package_data=True,
    license='GPL3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'fastqwiper = fastq_wiper.wiper:wipe_fastq'
        ]
    },
    setup_requires=['numpy'],
    install_requires=[
        "setuptools",
        "colorama==0.4.4",
        "click==7.1.2",
    ],
)
