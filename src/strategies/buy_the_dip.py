import pandas as pd
from typing import Dict, Any, Optional
from .strategy_base import StrategyBase

class BuyTheDipStrategy(StrategyBase):
    
    @property
    def name(self) -> str:
        return "Buy the Dip (Swing)"
        
    @property
    def default_parameters(self) -> Dict[str, Any]:
        return {
            "min_drop_pct": 15.0,        # Minimum drop from high
            "lookback_days": 60,         # Window of days to observe the high
            "min_rebound_pct": 2.0,      # Must rise a minimum of 2% from the bottom to confirm trend change
            "min_market_cap_b": 10.0,    # Minimum capitalization in Billions
            "min_volume_m": 1.0          # Minimum daily volume in Millions
        }
        
    def analyze(self, symbol: str, hist_data: pd.DataFrame, info_data: dict, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detects stocks that have fallen from their recent high but have
        already started to rebound from a low.
        """
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
            
        current_price = hist_data['Close'].iloc[-1]
        result["current_price"] = current_price
        
        # 1. Company filter checks (Market Cap & Volume)
        market_cap = info_data.get("market_cap", 0) / 1e9 # In Billions
        avg_volume_10d = hist_data['Volume'].tail(10).mean() / 1e6 # In Millions
        
        if market_cap < p["min_market_cap_b"]:
            result["reason"] = f"Market capitalization too low ({market_cap:.1f}B < {p['min_market_cap_b']}B)"
            return result
            
        if avg_volume_10d < p["min_volume_m"]:
            result["reason"] = f"Trading volume too low ({avg_volume_10d:.1f}M < {p['min_volume_m']}M)"
            return result
            
        # 2. Càlcul de caiguda i fons
        # Històric de X dies anteriors sense incloure avui (o depèn de preferències)
        recent_data = hist_data.tail(p["lookback_days"])
        period_high = recent_data['High'].max()
        period_low = recent_data['Low'].min()
        
        # Calculate devaluation from high relative to current price
        drop_pct = ((period_high - current_price) / period_high) * 100
        
        # 3. Calculate current rebound
        # Check if from the bottom (period_low) it has rebounded indicating start of "recovery"
        rebound_pct = ((current_price - period_low) / period_low) * 100
        
        result["metrics"] = {
            "period_high": float(period_high),
            "period_low": float(period_low),
            "drop_pct": float(drop_pct),
            "rebound_pct": float(rebound_pct),
            "lookback_days": p["lookback_days"],
            "market_cap": float(market_cap),
            "volume": float(avg_volume_10d),
            "per": info_data.get("per", 0),
            "eps": info_data.get("eps", 0),
            "dividend_yield": info_data.get("dividend_yield", 0),
            "next_earnings": info_data.get("next_earnings", "Unknown")
        }
        
        if drop_pct < p["min_drop_pct"]:
            result["reason"] = f"Has not fallen enough from recent high ({drop_pct:.1f}% < {p['min_drop_pct']}%). Period High: ${period_high:.2f}, Current Price: ${current_price:.2f}"
            return result
            
        if rebound_pct < p["min_rebound_pct"]:
            result["reason"] = f"No sign that the bleeding has ended (rebound of {rebound_pct:.1f}% < {p['min_rebound_pct']}%)."
            return result
            
        # Also maybe we are not interested if it has already risen too much from the bottom (> e.g. a percent of the drop).
        # Simple implementation for now.
        
        # If we reached here, it's an "entry opportunity!"
        result["is_opportunity"] = True
        
        # Rudimentary "Confidence" formula
        # More drop and a robust (but not excessive) rebound = more confidence.
        conf_drop = min(drop_pct / 30.0, 1.0) * 0.6  # 60% weight
        conf_rebound = min(rebound_pct / 5.0, 1.0) * 0.4 # 40% weight
        result["confidence"] = round((conf_drop + conf_rebound) * 100, 2)
        
        result["reason"] = (
            f"Buy the Dip opportunity detected in {symbol}. "
            f"The value has fallen {drop_pct:.1f}% from its recent {p['lookback_days']}-day high (${period_high:.2f}). "
            f"Currently priced at ${current_price:.2f}, having rebounded {rebound_pct:.1f}% from the local low (${period_low:.2f}), validating the start of a recovery."
        )
        return result
