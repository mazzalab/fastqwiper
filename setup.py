import os
from setuptools import setup, find_packages

version_string = os.environ.get("WIPERTOOLS_VERSION", "0.0.0.dev0")

setup(
    name="wipertools",
    version=version_string,
    packages=find_packages(exclude=("tests",)),
    # https://setuptools.pypa.io/en/latest/userguide/datafiles.html
    # package_data={"": ["*.txt"], "mypkg1": ["data1.rst"]},
    # include_package_data=True,
    # exclude_package_data={"tests": [""]},
    install_requires=[],
    entry_points={
        "console_scripts": [
            "wipertools=fastqwiper.wipertools:main"
        ]
    },
    author="Tommaso Mazza",
    author_email="mazza.tommaso@gmail.com",
    description="A suite of programs that drop or fix pesky lines in FASTQ files and that split or merge FASTQ chunk files.",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/mazzalab/fastqwiper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)