import sys
import os
import re

try:
    from importlib import util
except:
    sys.stdout.write(
        "\nIt seems that importlib library is not available on this machine. Please install pip (e.g. for Ubuntu, run "
        "'sudo apt-get install python3-pip'.\n"
    )
    sys.exit()

if util.find_spec("setuptools") is None:
    sys.stdout.write(
        "\nIt seems that setuptools is not available on this machine. Please install pip (e.g. for Ubuntu, run "
        "'sudo apt-get install python3-pip'.\n"
    )
    sys.exit()

from setuptools import setup, find_packages

print(sys.version_info)
if sys.version_info.major != 3 and sys.version_info.minor < 7:
    sys.exit("Sorry, Python < 3.7 is not supported")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get and set the build version
VERSION = "2023.2." + os.environ["GITHUB_RUN_NUMBER"]
print("version {} passed to setup.py".format(VERSION))
assert re.match("^[0-9]+\.[0-9]+\.[0-9]+$", VERSION), "Invalid version number"

setup(
    name="fastqwiper",
    version=VERSION,
    author="Tommaso Mazza",
    author_email="bioinformatics@css-mendel.it",
    description="An ensamble method to recover corrupted FASTQ files, drop or fix pesky lines, remove unpaired reads, and fix reads interleaving",
    url="https://github.com/mazzalab/fastqwiper",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["fastqwiper = fastq_wiper.wiper:wipe_fastq"]},
    # setup_requires=['numpy'],
    install_requires=["setuptools", "colorama", "click"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        # 'Documentation': 'http://pyntacle.css-mendel.it:10080/#docs',
        "Source": "https://github.com/mazzalab/fastqwiper",
        "Tracker": "https://github.com/mazzalab/fastqwiper/issues",
        "Developmental plan": "https://github.com/mazzalab/fastqwiper/projects",
    },
    keywords="genomics, ngs, fastq, bioinformatics",
    python_requires=">=3.7",
)
