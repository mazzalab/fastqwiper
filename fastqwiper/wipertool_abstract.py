from abc import ABC, abstractmethod
from argparse import Namespace


class WiperTool(ABC):

    @abstractmethod
    def set_parser(self, parser):
        pass

    def run(self, argv: Namespace):
        pass
