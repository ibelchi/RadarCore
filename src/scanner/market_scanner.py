import logging
import time
import pandas as pd
from typing import Optional

from src.data.ingestion import get_market_symbols, get_historical_data, get_company_info, RateLimitException
from src.database.db import SessionLocal, Opportunity, StrategyConfig
from src.strategies.buy_the_dip import BuyTheDipStrategy

logger = logging.getLogger(__name__)

class MarketScanner:
    def __init__(self):
        # List of active plugins
        self.strategies = [
            BuyTheDipStrategy()
        ]
        
    def run_scan(self, market: str = "sp500", limit_symbols: Optional[int] = None, on_opportunity_found=None):
        """
        Executes all active strategies over the appropriate market symbols.
        :param market: Market code to scan.
        :param limit_symbols: Limit the number of stocks to scan (useful for testing)
        :param on_opportunity_found: Optional callback function triggered when an opportunity is found.
        """
        logger.info(f"Starting Market Scanner ({market})...")
        symbols = get_market_symbols(market)
        
        if not symbols or len(symbols) == 0:
            raise RuntimeError(f"The scanner was unable to obtain any base list of symbols for the {market} market. Please check the data source.")
            
        if limit_symbols:
            symbols = symbols[:limit_symbols]
            
        logger.info(f"Scanning {len(symbols)} symbols...")
        
        # Download SPY data once for systemic market analysis
        spy_data = get_historical_data("SPY", period="2y")
        if spy_data.empty:
            logger.warning("Could not download SPY data. Relative market analysis will be disabled.")
        else:
            logger.info("SPY data downloaded successfully for market context.")
        
        db = SessionLocal()
        try:
            for strategy in self.strategies:
                # Retrieve parameters from DB if available, otherwise use defaults
                config_record = db.query(StrategyConfig).filter(StrategyConfig.strategy_name == strategy.name).first()
                config = config_record.parameters if config_record else strategy.default_parameters
                
                logger.info(f"Executing strategy: {strategy.name}")
                
                for idx, sym in enumerate(symbols):
                    try:
                        # Safety delay to avoid "Too Many Requests" (429) from Yahoo Finance
                        time.sleep(1.5)

                        if idx % 50 == 0 and idx > 0:
                            logger.info(f"Progress: {idx}/{len(symbols)} scanned.")
                            
                        # Download necessary data
                        hist_data = get_historical_data(sym)
                        info_data = get_company_info(sym)
                        
                        if hist_data.empty:
                            if on_opportunity_found:
                                on_opportunity_found(sym, None, {"is_opportunity": False, "reason": "No historical data available"})
                            continue
                            
                        # Execute plugin strategy logic
                        result = strategy.analyze(sym, hist_data, info_data, config, spy_hist_data=spy_data)
                        
                        if result.get("is_opportunity"):
                            logger.info(f"-> 🟢 SUCCESS {sym} | Conf: {result.get('confidence')}% | Reason: {result.get('reason')}")
                            
                            op = Opportunity(
                                symbol=sym,
                                company_name=info_data.get("short_name") or sym,
                                strategy_name=strategy.name,
                                current_price=result.get("current_price"),
                                strategy_config=config,
                                explanation=result.get("reason"),
                                metrics=result.get("metrics"),
                                confidence=result.get("confidence", 0.0),
                                market=market,
                                currency=info_data.get("currency", "USD")
                            )
                            db.add(op)
                            db.commit()
                            
                        # Trigger UI callback for BOTH success and filtered items (Transparency)
                        if on_opportunity_found:
                            on_opportunity_found(sym, hist_data, result)
                            
                    except RateLimitException as rle:
                        logger.error(str(rle))
                        db.rollback()
                        raise  # Re-raise to immediately stop the entire scan
                    except Exception as e:
                        logger.error(f"Error analyzing symbol {sym} with {strategy.name}: {e}")
                        if on_opportunity_found:
                            on_opportunity_found(sym, None, {"is_opportunity": False, "reason": f"System error: {str(e)[:50]}"})
                        db.rollback()
                        
        finally:
            db.close()
            logger.info("Market Scan completed!")
