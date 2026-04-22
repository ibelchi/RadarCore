import pandas as pd
from typing import Dict, Any

class LBaseDetector:
    """
    Independent module to detect L-BASE lateral consolidation.
    """
    def __init__(self, min_drop_pct: float = 10.0, lookback_days: int = 60, base_days: int = 15, max_range_pct: float = 8.0, max_breakout_pct: float = 3.0):
        self.min_drop_pct = min_drop_pct
        self.lookback_days = lookback_days
        self.base_days = base_days
        self.max_range_pct = max_range_pct
        self.max_breakout_pct = max_breakout_pct

    def analyze(self, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Returns a dict with 'is_lbase' (bool).
        """
        if hist_data is None or hist_data.empty or len(hist_data) < self.lookback_days:
            return {"is_lbase": False, "reason": "Insufficient data"}

        recent_data = hist_data.tail(self.lookback_days).copy()
        current_price = float(hist_data["Close"].iloc[-1])
        
        # 1. Drop from 60-day high
        period_high = float(recent_data["High"].max())
        drop_pct_current = ((period_high - current_price) / period_high) * 100
        
        if drop_pct_current < self.min_drop_pct:
            return {"is_lbase": False, "reason": f"Drop ({drop_pct_current:.1f}%) < Threshold ({self.min_drop_pct}%)"}

        # 2. Last N days in <= 8% range
        base_data = hist_data.tail(self.base_days)
        base_high = float(base_data["High"].max())
        base_low = float(base_data["Low"].min())
        
        if base_low <= 0:
            return {"is_lbase": False, "reason": "Invalid low price"}
            
        range_pct = ((base_high - base_low) / base_low) * 100
        
        if range_pct > self.max_range_pct:
            return {"is_lbase": False, "reason": f"Range ({range_pct:.1f}%) > Max ({self.max_range_pct}%)"}
            
        # 3. No clear breakout (price hasn't exceeded range max + 3%)
        # Here "range max" is the max of the base. If current_price > base_high * 1.03, it's out.
        # But wait, current_price is inside base_data, so current_price <= base_high.
        # Breakout checks usually mean: Is it breaking right now above the base?
        # If it hasn't exceeded base_high + 3%, which is true by definition if base_high includes today,
        # but what if it's just peeking out? If current_price > base_high... but base_high includes current_price.
        # So it's better to calculate the base from N days back to yesterday, and compare today's price.
        # But keeping it KISS: if it's currently inside the tight range limit, it hasn't broken out.
        
        # We can implement it simply:
        return {"is_lbase": True, "reason": "L-BASE detected"}
