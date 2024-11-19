from abc import ABC, abstractmethod
from argparse import Namespace
import os


class WiperTool(ABC):
    name: str
    config: dict

    def __init__(self, name):
        self.name = name
        
        versions_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'versions')
        with open(versions_file_path, 'r') as file:
            self.config = {line.split(':')[0]: line.split(':')[1].strip() for line in file if line.strip()}

    def version(self):
        return self.config.get(self.name, "")

    @abstractmethod
    def set_parser(self, parser):
        pass

    @abstractmethod
    def run(self, argv: Namespace):
        pass
