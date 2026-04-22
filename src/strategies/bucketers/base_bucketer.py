from abc import ABC, abstractmethod
import pandas as pd

class BaseBucketer(ABC):
    @abstractmethod
    def get_bucket_scores(self, hist_data: pd.DataFrame) -> dict:
        """Retorna {"SWING":int,"RISE":int,"DESCENDING":int,"HIGHS":int,"LATERAL":int} tots 0-100"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
