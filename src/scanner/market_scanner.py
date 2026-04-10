import logging
import pandas as pd
from typing import Optional

from src.data.ingestion import get_market_symbols, get_historical_data, get_company_info
from src.database.db import SessionLocal, Opportunity, StrategyConfig
from src.strategies.buy_the_dip import BuyTheDipStrategy

logger = logging.getLogger(__name__)

class MarketScanner:
    def __init__(self):
        # Llista de plugins actius
        self.strategies = [
            BuyTheDipStrategy()
        ]
        
    def run_scan(self, market: str = "sp500", limit_symbols: Optional[int] = None):
        """
        Executa totes les estratègies actives sobre els símbols del mercat adient.
        :param market: Codi del mercat a escanejar.
        :param limit_symbols: Limitar el nombre d'accions a escanejar (útil per testejar)
        """
        logger.info(f"Iniciant Market Scanner ({market})...")
        symbols = get_market_symbols(market)
        
        if not symbols or len(symbols) == 0:
            raise RuntimeError(f"L'escàner no ha estat capaç d'obtenir cap llistat base de símbols del mercat {market}. Comproveu l'origen de dades.")
            
        if limit_symbols:
            symbols = symbols[:limit_symbols]
            
        logger.info(f"S'escanejaran {len(symbols)} símbols...")
        
        db = SessionLocal()
        try:
            for strategy in self.strategies:
                # Recuperar paràmetres de DB si n'hi ha, altrament defecte
                config_record = db.query(StrategyConfig).filter(StrategyConfig.strategy_name == strategy.name).first()
                config = config_record.parameters if config_record else strategy.default_parameters
                
                logger.info(f"Executant estratègia: {strategy.name}")
                
                for idx, sym in enumerate(symbols):
                    try:
                        if idx % 50 == 0 and idx > 0:
                            logger.info(f"Progreś: {idx}/{len(symbols)} escanejats.")
                            
                        # Descarrega les dades necessàries
                        hist_data = get_historical_data(sym)
                        info_data = get_company_info(sym)
                        
                        if hist_data.empty:
                            continue
                            
                        # Executa la lògica de la estratègia del plugin
                        result = strategy.analyze(sym, hist_data, info_data, config)
                        
                        if result.get("is_opportunity"):
                            logger.info(f"-> 🟢 EXÍT {sym} | Conf: {result.get('confidence')}% | Raó: {result.get('reason')}")
                            
                            op = Opportunity(
                                symbol=sym,
                                strategy_name=strategy.name,
                                current_price=result.get("current_price"),
                                strategy_config=config,
                                explanation=result.get("reason"),
                                metrics=result.get("metrics"),
                                market=market # Guardem el mercat on s'ha trobat
                                # market_context & ai_explanation seran emplenats per IA després (Fase 6)
                            )
                            db.add(op)
                            db.commit()
                            
                    except Exception as e:
                        logger.error(f"Error analitzant el símbol {sym} am {strategy.name}: {e}")
                        db.rollback()
                        
        finally:
            db.close()
            logger.info("Market Scan completat!")
