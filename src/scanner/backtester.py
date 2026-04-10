import logging
import pandas as pd
from typing import Optional, List, Dict
from datetime import timedelta

from src.data.ingestion import get_historical_data, get_company_info
from src.strategies.buy_the_dip import BuyTheDipStrategy

logger = logging.getLogger(__name__)

class Backtester:
    def __init__(self):
        self.strategy = BuyTheDipStrategy()
        
    def run_backtest(self, symbols: List[str], start_date: str, end_date: str, custom_config: Optional[Dict] = None) -> List[Dict]:
        """
        Emulates the passage of time by slicing historical DataFrames day by day to 
        see when our strategy would have given a signal.
        """
        logger.info(f"Starting Backtest from {start_date} to {end_date} for {len(symbols)} assets.")
        config = custom_config or self.strategy.default_parameters
        results = []
        
        for sym in symbols:
            # We download an extra year of data before start_date to ensure having
            # enough info for moving averages and "lookback_days".
            hist_start = pd.to_datetime(start_date) - timedelta(days=365)
            # We use yfinance 'history' downloading all necessary data, here we choose
            # to simplify by downloading the maximum and slicing.
            hist_data = get_historical_data(sym, period="2y")
            info_data = get_company_info(sym)
            
            if hist_data.empty:
                continue
                
            # Filter between start_date and end_date to simulate
            mask = (hist_data.index >= pd.to_datetime(start_date, utc=True)) & (hist_data.index <= pd.to_datetime(end_date, utc=True))
            sim_indexes = hist_data[mask].index
            
            for sim_date in sim_indexes:
                # The "past" at the evaluation point
                past_data = hist_data[hist_data.index <= sim_date]
                
                # We attempt to analyze as if we were at that day
                res = self.strategy.analyze(sym, past_data, info_data, config)
                
                if res.get("is_opportunity"):
                    # "Virtual" purchase
                    entry_price = res["current_price"]
                    
                    # We verify if it would have been a success or failure (ex: look for performance at +30 days)
                    future_data = hist_data[hist_data.index > sim_date].head(20) # We look at the next 20 sessions (approx 1 month)
                    if not future_data.empty:
                        max_future_price = future_data["High"].max()
                        profit_pct = ((max_future_price - entry_price) / entry_price) * 100
                    else:
                        profit_pct = 0.0
                        
                    results.append({
                        "sim_date": sim_date.strftime('%Y-%m-%d'),
                        "symbol": sym,
                        "entry_price": entry_price,
                        "confidence": res.get("confidence"),
                        "max_1mo_profit_pct": round(profit_pct, 2)
                    })
                    
        return results
