from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class StrategyBase(ABC):
    """
    Base class for all investment strategies (plugins).
    Ensures a common contract so that the Market Scanner can
    use multiple strategies interchangeably.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Identifying name of the strategy."""
        pass
        
    @property
    @abstractmethod
    def default_parameters(self) -> Dict[str, Any]:
        """Default parameters if none have been previously configured or in the DB."""
        pass

    @abstractmethod
    def analyze(self, symbol: str, hist_data, info_data, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes a stock's data and determines whether there is an opportunity or not.
        
        Args:
            symbol (str): Stock ticker
            hist_data (pd.DataFrame): EOD (End of Day) historical data
            info_data (dict): Fundamental data such as market capitalization, sector
            config (dict): Configuration (parameters) to use (overrides defaults)
            
        Returns:
            Dict with the result:
            {
                "is_opportunity": bool,
                "confidence": float,
                "current_price": float,
                "reason": str (technical explanation for reports)
            }
        """
        pass
