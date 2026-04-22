from typing import Any, Dict, Optional
import pandas as pd
from .strategy_base import StrategyBase

class BuyTheDipStrategy(StrategyBase):
    """
    BuyTheDipStrategy — RadarCore (Swing Trading Intelligence)
    ==========================================================
    Improved version:
    1. Corrected drop calculation (High to Period Low).
    2. Pattern detection (L-BASE, V-RECOVERY, EARLY).
    3. Relative market filter (Systemic vs Idiosyncratic).
    4. Enhanced confidence formula.
    """

    @property
    def name(self) -> str:
        return "Buy the Recovery (Swing)"

    @property
    def default_parameters(self) -> Dict[str, Any]:
        return {
            "min_drop_pct": 10.0,       # Lowered from 15% to be more inclusive
            "lookback_days": 60,
            "min_rebound_pct": 2.0,
            "min_market_cap_b": 2.0,    # Lowered from 10B to include European midcaps
            "min_volume_m": 0.5         # Lowered from 1M to 0.5M
        }

    def analyze(
        self,
        symbol: str,
        hist_data: pd.DataFrame,
        info_data: dict,
        config: Optional[Dict[str, Any]] = None,
        spy_hist_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Detects stocks that have fallen and started recovering, classifying as L-BASE, V-RECOVERY or EARLY.
        """
        from src.utils.data_utils import normalize_yfinance_df
        hist_data = normalize_yfinance_df(hist_data)
        
        p = self.default_parameters.copy()
        if config:
            p.update(config)

        result = {
            "is_opportunity": False,
            "confidence": 0.0,
            "current_price": 0.0,
            "reason": ""
        }

        if hist_data.empty or len(hist_data) < p["lookback_days"]:
            result["reason"] = f"Not enough historical data to analyze {symbol}"
            return result

        current_price = float(hist_data["Close"].iloc[-1])
        result["current_price"] = current_price

        # 1. Liquidity filter
        market_cap = info_data.get("market_cap", 0) / 1e9
        avg_volume_10d = hist_data["Volume"].tail(10).mean() / 1e6

        if market_cap < p["min_market_cap_b"]:
            result["reason"] = f"Market cap too low ({market_cap:.1f}B < {p['min_market_cap_b']}B)"
            return result

        if avg_volume_10d < p["min_volume_m"]:
            result["reason"] = f"Volume too low ({avg_volume_10d:.1f}M < {p['min_volume_m']}M)"
            return result

        # 2. Key Drop & Rebound calculations
        recent_data = hist_data.tail(p["lookback_days"]).copy()
        period_high = float(recent_data["High"].max())
        period_low = float(recent_data["Low"].min())
        high_idx = recent_data["High"].idxmax()
        low_idx = recent_data["Low"].idxmin()

        drop_from_high_pct = ((period_high - period_low) / period_high) * 100
        drop_pct_current = ((period_high - current_price) / period_high) * 100
        rebound_pct = ((current_price - period_low) / period_low) * 100

        if drop_from_high_pct < p["min_drop_pct"]:
            result["reason"] = f"Insufficient drop ({drop_from_high_pct:.1f}% < {p['min_drop_pct']}%)."
            return result

        if rebound_pct < p["min_rebound_pct"]:
            result["reason"] = f"No confirmed turn (rebound {rebound_pct:.1f}% < {p['min_rebound_pct']}%)."
            return result

        # 3. Pattern classification
        pattern_type = "V-RECOVERY"

        # Market filter has been moved to an independent module.

        result["metrics"] = {
            "period_high": period_high,
            "period_low": period_low,
            "drop_pct": round(drop_pct_current, 2),
            "rebound_pct": round(rebound_pct, 2),
            "lookback_days": p["lookback_days"],
            "market_cap": round(market_cap, 2),
            "volume": round(avg_volume_10d, 2),
            "per": info_data.get("per", 0),
            "eps": info_data.get("eps", 0),
            "dividend_yield": info_data.get("dividend_yield", 0),
            "next_earnings": info_data.get("next_earnings", "Unknown"),
            "drop_from_high_pct": round(drop_from_high_pct, 2),
            "pattern_type": pattern_type
        }

        # 5. Enhanced Confidence
        conf_drop = min(drop_from_high_pct / 40.0, 1.0) * 0.50
        conf_rebound = min(rebound_pct / 10.0, 1.0) * 0.35
        conf_pattern = 0.15
        
        result["confidence"] = round((conf_drop + conf_rebound + conf_pattern) * 100, 2)
        result["is_opportunity"] = True

        result["reason"] = (
            f"Opportunity '{pattern_type}' detected in {symbol}. "
            f"Dropped {drop_from_high_pct:.1f}% from high. "
            f"Price: ${current_price:.2f}, rebound: {rebound_pct:.1f}%."
        )

        return result
