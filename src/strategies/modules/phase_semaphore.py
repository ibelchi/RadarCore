import pandas as pd
from typing import Dict, Any

class PhaseSemaphore:
    """
    Independent module to generate a traffic light indicator for the current asset phase.
    🔴 CAIGUDA: Drop is active, price is > 10% below peak and hasn't bounced.
    🟡 BASE: Consolidating laterally or forming a bottom.
    🟢 RUPTURA: Pattern confirmed, ascending/breaking out.
    """
    def __init__(self, lookback_days: int = 120, min_drop_pct: float = 10.0, base_range_pct: float = 8.0, rebound_val_pct: float = 2.0):
        self.lookback_days = lookback_days
        self.min_drop_pct = min_drop_pct
        self.base_range_pct = base_range_pct
        self.rebound_val_pct = rebound_val_pct

    def analyze(self, hist_data: pd.DataFrame) -> Dict[str, str]:
        """
        Returns a dict with 'phase_emoji' and 'phase_name'.
        """
        if hist_data is None or hist_data.empty or len(hist_data) < 20:
            return {"phase_emoji": "⚪", "phase_name": "SENSE DADES"}

        recent_data = hist_data.tail(self.lookback_days).copy()
        current_price = float(hist_data["Close"].iloc[-1])
        
        period_high = float(recent_data["High"].max())
        period_low = float(recent_data["Low"].min())
        
        drop_pct = ((period_high - current_price) / period_high) * 100 if period_high > 0 else 0.0
        rebound_pct = ((current_price - period_low) / period_low) * 100 if period_low > 0 else 0.0
        
        # Base logic (last 15 days)
        base_data = hist_data.tail(15)
        base_high = float(base_data["High"].max())
        base_low = float(base_data["Low"].min())
        range_pct = ((base_high - base_low) / base_low) * 100 if base_low > 0 else 99.0
        
        if drop_pct >= self.min_drop_pct and rebound_pct < self.rebound_val_pct and range_pct > self.base_range_pct:
            return {"phase_emoji": "🔴", "phase_name": "CAIGUDA"}
        elif range_pct <= self.base_range_pct and drop_pct >= (self.min_drop_pct / 2):
            return {"phase_emoji": "🟡", "phase_name": "BASE"}
        elif rebound_pct >= self.rebound_val_pct:
            return {"phase_emoji": "🟢", "phase_name": "RUPTURA"}
        else:
            # If it's near ATH
            if drop_pct < self.min_drop_pct:
                return {"phase_emoji": "🟢", "phase_name": "ALTS"}
            return {"phase_emoji": "⚪", "phase_name": "INDECISIÓ"}

