from abc import ABC, abstractmethod
from argparse import Namespace
import os
import yaml


class WiperTool(ABC):
    name: str
    config: str

    def __init__(self, name):
        self.name = name

        yaml_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conda-recipe', 'conda_build_config.yaml')
        # Read the YAML file
        with open(yaml_file_path, 'r') as yaml_file:
            self.config = yaml.safe_load(yaml_file)

    def version(self):
        return self.config.get(self.name + "_version", [None])[0]

    @abstractmethod
    def set_parser(self, parser):
        pass

    @abstractmethod
    def run(self, argv: Namespace):
        pass
