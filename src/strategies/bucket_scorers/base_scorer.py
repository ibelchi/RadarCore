from abc import ABC, abstractmethod
import pandas as pd

class BaseBucketScorer(ABC):
    @abstractmethod
    def score(self, hist_data: pd.DataFrame, metrics: dict) -> dict:
        """
        Retorna {"score":int, "reasoning":str, "key_metrics":dict}
        """
        pass
