from abc import ABC, abstractmethod


class Stage(ABC):
    """Abstract class for a stage

    Attributes:
        name: str
            Name of the stage
        params: dict
            Dictionary object containing parameters necessary for the running the stage
    """

    def __init__(self, name, params):
        self.name = name
        self.params = params

    @abstractmethod
    def run(self):
        """Every stage should implement a run function perform stage task"""
        pass
