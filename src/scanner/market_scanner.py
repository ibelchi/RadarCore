import logging
import pandas as pd
from typing import Optional

from src.data.ingestion import get_market_symbols, get_historical_data, get_company_info
from src.database.db import SessionLocal, Opportunity, StrategyConfig
from src.strategies.buy_the_dip import BuyTheDipStrategy

logger = logging.getLogger(__name__)

class MarketScanner:
    def __init__(self):
        # List of active plugins
        self.strategies = [
            BuyTheDipStrategy()
        ]
        
    def run_scan(self, market: str = "sp500", limit_symbols: Optional[int] = None):
        """
        Executes all active strategies over the appropriate market symbols.
        :param market: Market code to scan.
        :param limit_symbols: Limit the number of stocks to scan (useful for testing)
        """
        logger.info(f"Starting Market Scanner ({market})...")
        symbols = get_market_symbols(market)
        
        if not symbols or len(symbols) == 0:
            raise RuntimeError(f"The scanner was unable to obtain any base list of symbols for the {market} market. Please check the data source.")
            
        if limit_symbols:
            symbols = symbols[:limit_symbols]
            
        logger.info(f"Scanning {len(symbols)} symbols...")
        
        db = SessionLocal()
        try:
            for strategy in self.strategies:
                # Retrieve parameters from DB if available, otherwise use defaults
                config_record = db.query(StrategyConfig).filter(StrategyConfig.strategy_name == strategy.name).first()
                config = config_record.parameters if config_record else strategy.default_parameters
                
                logger.info(f"Executing strategy: {strategy.name}")
                
                for idx, sym in enumerate(symbols):
                    try:
                        if idx % 50 == 0 and idx > 0:
                            logger.info(f"Progress: {idx}/{len(symbols)} scanned.")
                            
                        # Download necessary data
                        hist_data = get_historical_data(sym)
                        info_data = get_company_info(sym)
                        
                        if hist_data.empty:
                            continue
                            
                        # Execute plugin strategy logic
                        result = strategy.analyze(sym, hist_data, info_data, config)
                        
                        if result.get("is_opportunity"):
                            logger.info(f"-> 🟢 SUCCESS {sym} | Conf: {result.get('confidence')}% | Reason: {result.get('reason')}")
                            
                            op = Opportunity(
                                symbol=sym,
                                strategy_name=strategy.name,
                                current_price=result.get("current_price"),
                                strategy_config=config,
                                explanation=result.get("reason"),
                                metrics=result.get("metrics"),
                                market=market, # Store the market where found
                                currency=info_data.get("currency", "USD") # Store the actual currency
                                # market_context & ai_explanation will be filled by AI later (Phase 6)
                            )
                            db.add(op)
                            db.commit()
                            
                    except Exception as e:
                        logger.error(f"Error analyzing symbol {sym} with {strategy.name}: {e}")
                        db.rollback()
                        
        finally:
            db.close()
            logger.info("Market Scan completed!")
