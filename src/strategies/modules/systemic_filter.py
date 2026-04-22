import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SystemicFilter:
    """
    Independent module to verify if a drop is systemic or idiosyncratic.
    """
    def __init__(self, min_relative_drop_pct: float = 5.0):
        self.min_relative_drop_pct = min_relative_drop_pct

    def analyze(self, symbol_hist: pd.DataFrame, spy_hist: Optional[pd.DataFrame], lookback_days: int = 60) -> Dict[str, Any]:
        """
        Returns a dict with 'is_systemic' (bool) and 'relative_drop_pct'
        """
        if symbol_hist.empty or len(symbol_hist) < lookback_days or spy_hist is None or spy_hist.empty:
            return {"is_systemic": False, "relative_drop_pct": 0.0, "reason": "Insufficient data for filter"}

        recent_data = symbol_hist.tail(lookback_days).copy()
        period_high = float(recent_data["High"].max())
        period_low = float(recent_data["Low"].min())
        high_idx = recent_data["High"].idxmax()
        low_idx = recent_data["Low"].idxmin()

        drop_from_high_pct = ((period_high - period_low) / period_high) * 100 if period_high > 0 else 0.0

        try:
            # Ensure indices are comparable (both localized or both naive)
            if spy_hist.index.tz is not None and recent_data.index.tz is None:
                spy_hist_local = spy_hist.tz_localize(None)
            elif spy_hist.index.tz is None and recent_data.index.tz is not None:
                spy_hist_local = spy_hist.tz_localize(recent_data.index.tz)
            else:
                spy_hist_local = spy_hist

            # Check SPY drop in the exact same timeframe the stock dropped
            # We must be careful if high_idx > low_idx (meaning it went up)
            start_date = min(high_idx, low_idx)
            end_date = max(high_idx, low_idx)

            spy_period = spy_hist_local.loc[(spy_hist_local.index >= start_date) & (spy_hist_local.index <= end_date)]
            
            if not spy_period.empty:
                spy_high = float(spy_period["High"].max())
                spy_low = float(spy_period["Low"].min())
                spy_drop_pct = ((spy_high - spy_low) / spy_high) * 100 if spy_high > 0 else 0.0
                
                relative_drop_pct = drop_from_high_pct - spy_drop_pct
                is_systemic = relative_drop_pct <= self.min_relative_drop_pct
                
                return {
                    "is_systemic": is_systemic,
                    "relative_drop_pct": round(relative_drop_pct, 2),
                    "spy_drop_pct": round(spy_drop_pct, 2),
                    "symbol_drop_pct": round(drop_from_high_pct, 2)
                }
        except Exception as e:
            logger.warning(f"SystemicFilter analysis failed: {e}")
            
        return {"is_systemic": False, "relative_drop_pct": 0.0, "reason": "Calculation error"}
