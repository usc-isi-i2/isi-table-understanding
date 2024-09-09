from abc import ABC, abstractmethod

from logger.logger import MyLogger


class Pipeline(ABC):
    """Abstract class for training/prediction pipelines

    Attributes:
        stages: list[Stage]
            List of stages in-order of their execution
    """

    def __init__(self, stages):
        self.stages = stages
        self.logger = MyLogger.get_logger()

    @abstractmethod
    def trigger(self):
        """Abstract method to trigger pipeline stages"""
        pass
