from abc import ABC, abstractmethod
from argparse import Namespace
import json
import os


class WiperTool(ABC):
    name: str
    config: dict

    def __init__(self, name):
        self.name = name

        versions_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'versions.json')
        with open(versions_file_path) as f:
            self.config = json.load(f)

    def version(self):
        return self.config.get(self.name, "")

    @abstractmethod
    def set_parser(self, parser):
        pass

    @abstractmethod
    def run(self, argv: Namespace):
        pass
