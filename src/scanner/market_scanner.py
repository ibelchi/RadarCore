import logging
import time
import pandas as pd
import yfinance as yf
from typing import Optional

from src.data.ingestion import get_market_symbols, get_historical_data, get_company_info, get_detailed_info, RateLimitException
from src.database.db import SessionLocal, Opportunity, StrategyConfig, Watchlist
from src.strategies.buy_the_dip import BuyTheDipStrategy
from src.strategies.pattern_classifier import PatternClassifier
from src.strategies.modules.l_base_detector import LBaseDetector
from src.strategies.modules.systemic_filter import SystemicFilter
from src.strategies.modules.phase_semaphore import PhaseSemaphore

logger = logging.getLogger(__name__)

class MarketScanner:
    def __init__(self):
        # List of active plugins
        self.strategies = [
            BuyTheDipStrategy()
        ]
        
    def run_scan(self, market: str = "sp500", limit_symbols: Optional[int] = None, on_opportunity_found=None, use_universe_filter: bool = False, scan_logger=None, strategy_overrides: Optional[dict] = None):
        """
        Executes all active strategies over the appropriate market symbols.
        :param market: Market code to scan.
        :param limit_symbols: Limit the number of stocks to scan (useful for testing)
        :param on_opportunity_found: Optional callback function triggered when an opportunity is found.
        :param use_universe_filter: If True, applies the initial UniverseFilter to weed out noise.
        :param strategy_overrides: Dynamic parameters from UI to override the DB config.
        """
        logger.info(f"Starting Market Scanner ({market})...")
        symbols = get_market_symbols(market)
        classifier = PatternClassifier()
        lbase_det = LBaseDetector()
        sys_filter = SystemicFilter()
        phase_sem = PhaseSemaphore()
        
        if not symbols or len(symbols) == 0:
            raise RuntimeError(f"The scanner was unable to obtain any base list of symbols for the {market} market. Please check the data source.")
            
        if limit_symbols:
            symbols = symbols[:limit_symbols]
            
        logger.info(f"Scanning {len(symbols)} symbols...")
        
        # Download SPY data once for systemic market analysis
        spy_data = pd.DataFrame()
        try:
            spy_data = get_historical_data("SPY", period="2y")
            if spy_data.empty:
                logger.warning("Could not download SPY data. Relative market analysis will be disabled.")
            else:
                logger.info("SPY data downloaded successfully for market context.")
        except Exception as e:
            logger.warning(f"Initial SPY Context fetch failed: {e}. Moving on without market relative analysis.")
        
        db = SessionLocal()
        try:
            for strategy in self.strategies:
                # Retrieve parameters from DB if available, otherwise use defaults
                config_record = db.query(StrategyConfig).filter(StrategyConfig.strategy_name == strategy.name).first()
                config = config_record.parameters if config_record else strategy.default_parameters
                
                # Assign dynamic overrides from UI if any
                if strategy_overrides and strategy.name in strategy_overrides:
                    # Update a copy so we don't accidentally mutate default_parameters reference
                    import copy
                    config = copy.deepcopy(config)
                    config.update(strategy_overrides[strategy.name])
                    
                logger.info(f"Executing strategy: {strategy.name} with config: {config}")
                
                # 1. PRE-FETCH DATA IN BATCHES (Avoids 429 errors from too many requests)
                logger.info(f"Pre-fetching data for {len(symbols)} symbols in batches...")
                batch_size = 30
                all_hist_data = {}
                for i in range(0, len(symbols), batch_size):
                    batch = symbols[i:i+batch_size]
                    try:
                        logger.info(f"Downloading batch {i//batch_size + 1}/{(len(symbols)-1)//batch_size + 1}...")
                        data = yf.download(batch, period="2y", group_by='ticker', progress=False, timeout=30, auto_adjust=True)
                        for sym in batch:
                            if len(batch) > 1:
                                if sym in data.columns.levels[0]:
                                    all_hist_data[sym] = data[sym].dropna(how='all')
                            else:
                                all_hist_data[sym] = data.dropna(how='all')
                    except Exception as e:
                        logger.warning(f"Batch download failed for {batch}: {e}")
                    
                    time.sleep(2.0) # Small break between batches

                logger.info("Starting individual analysis...")
                for idx, sym in enumerate(symbols):
                    try:
                        if idx % 20 == 0 and idx > 0:
                            logger.info(f"Progress: {idx}/{len(symbols)} scanned.")
                            
                        # Retrieve pre-fetched data
                        hist_data = all_hist_data.get(sym, pd.DataFrame())
                        
                        # Fallback to individual if batch failed/missing
                        if hist_data.empty:
                            hist_data = get_historical_data(sym)
                            time.sleep(1.0) # Additional delay for individual fallback

                        # Verifica immediatament després de la descàrrega:
                        from src.utils.data_utils import normalize_yfinance_df
                        hist_data = normalize_yfinance_df(hist_data, sym)
                        if hist_data is None or hist_data.empty or "Close" not in hist_data.columns:
                            if scan_logger:
                                scan_logger.log(sym, "DOWNLOAD", "FAIL", "Empty after normalization")
                            continue
                            
                        print(f"[{sym}] downloaded {len(hist_data)} rows")

                        info_data = get_company_info(sym)
                        

                        if use_universe_filter:
                            from src.filters.universe_filter import UniverseFilter
                            uf = UniverseFilter()
                            uf_result = uf.is_eligible(sym, hist_data, info_data)
                            if not uf_result.get("eligible", False):
                                if scan_logger:
                                    scan_logger.log(sym, "UNIVERSE_FILTER", "SKIP", uf_result.get("reason", ""))
                                if on_opportunity_found:
                                    on_opportunity_found(sym, hist_data, {"is_opportunity": False, "reason": "Univers: " + uf_result.get("reason", "")})
                                continue
                            else:
                                if scan_logger:
                                    scan_logger.log(sym, "UNIVERSE_FILTER", "PASS", "Criteris de liquiditat i historial correctes")

                        # 0. L-BASE Detection
                        lbase_res = lbase_det.analyze(hist_data)
                        if lbase_res.get("is_lbase"):
                            from src.utils.watchlist_utils import add_to_watchlist
                            add_to_watchlist([sym], db, source='scanner_lbase')
                            
                            # Add some note to the DB item manually if we want
                            w_item = db.query(Watchlist).filter(Watchlist.symbol == sym).first()
                            if w_item:
                                w_item.notes = "L-BASE Detectat automàticament"
                                w_item.active = True
                            db.commit()

                            if scan_logger:
                                scan_logger.log(sym, "L-BASE", "SKIP", "Mogut a Watchlist separada.")
                            if on_opportunity_found:
                                on_opportunity_found(sym, hist_data, {"is_opportunity": False, "reason": "L-BASE enviat a watchlist"})
                            continue
                            
                        # Mòdul Sistèmic i Semàfor (S'avaluen aquí però els resultats seran agregats només si l'estratègia fa pass)
                        sys_res = sys_filter.analyze(hist_data, spy_data)
                        sem_res = phase_sem.analyze(hist_data)

                        # Execute plugin strategy logic
                        result = strategy.analyze(sym, hist_data, info_data, config, spy_hist_data=spy_data)
                        if result.get("is_opportunity"):
                            # 1. Integració del Classificador de Patrons i Fase
                            try:
                                pattern_result = classifier.classify_with_score(hist_data)
                                phase_result = classifier.analyze_phase(hist_data)
                                
                                # Enriquir les mètriques amb el patró i la fase
                                metrics = result.get("metrics", {})
                                metrics.update({
                                    "bucket": pattern_result["bucket"],
                                    "bucket_score": pattern_result.get("bucket_score", 0),
                                    "subtype": pattern_result.get("subtype", ""),
                                    "phase": phase_result["phase"],
                                    "progress_pct": phase_result["progress_pct"],
                                    "upside_to_ath3y": phase_result["upside_to_ath3y"],
                                    "era_sequence": pattern_result.get("era_sequence", []),
                                    "pivot_points": pattern_result.get("pivot_points", [])
                                })
                                # Enriquir amb les dades dels nous mòduls independents
                                metrics.update({
                                    "is_systemic_new": sys_res.get("is_systemic", False),
                                    "systemic_relative_drop": sys_res.get("relative_drop_pct", 0.0),
                                    "phase_emoji": sem_res.get("phase_emoji", "⚪"),
                                    "phase_name_new": sem_res.get("phase_name", "INDECISIÓ")
                                })
                                result["metrics"] = metrics
                            except Exception as e:
                                logger.error(f"[{sym}] PatternClassifier error: {e}")

                            if scan_logger:
                                scan_logger.log(sym, "STRATEGY", "PASS", result.get("reason", ""))
                                scan_logger.log(sym, "CLASSIFIER", "INFO", f"Bucket: {result['metrics'].get('bucket', 'N/A')}")
                                scan_logger.log(sym, "PHASE", "INFO", f"Phase: {result['metrics'].get('phase', 'N/A')}")
                            
                            logger.info(f"-> SUCCESS {sym} | Conf: {result.get('confidence')}%")
                            
                            # 2. EXTRA FETCH (Info detallada i earnings per les oportunitats)
                            detailed = get_detailed_info(sym)
                            from src.data.earnings_fetcher import get_earnings_dates
                            earns = get_earnings_dates(sym)
                            
                            metrics = result.get("metrics", {})
                            metrics.update({
                                "next_earnings": earns.get("next"),
                                "days_to_next_earnings": earns.get("days_to_next"),
                                "earnings_risk_level": earns.get("risk_level"),
                                "past_earnings": earns.get("past", [])
                            })

                            # 3. GUARDAT A LA BASE DE DADES
                            op = Opportunity(
                                symbol=sym,
                                company_name=detailed.get("short_name") or info_data.get("short_name") or sym,
                                strategy_name=strategy.name,
                                current_price=result.get("current_price"),
                                strategy_config=config,
                                explanation=result.get("reason"),
                                metrics=metrics,
                                confidence=result.get("confidence", 0.0),
                                market=market,
                                currency=info_data.get("currency", "USD")
                            )
                            # Update metrics with detailed info
                            op.metrics.update(detailed)
                            db.add(op)
                            db.commit()
                        else:
                            # CAS DE DESCART: Només registrem al scan_logger
                            if scan_logger:
                                scan_logger.log(sym, "STRATEGY", "SKIP", result.get("reason", "Filtered by strategy"))
                            
                        # Trigger UI callback for BOTH success and filtered items (Transparency)
                        if on_opportunity_found:
                            on_opportunity_found(sym, hist_data, result)
                            
                    except RateLimitException as rle:
                        logger.warning(f"RATE LIMIT: {rle}. Pausing scan for 60 seconds...")
                        if on_opportunity_found:
                             on_opportunity_found(sym, None, {"is_opportunity": False, "reason": "Paused: Rate Limit hit"})
                        time.sleep(60) # Massive pause to let Yahoo breathe
                        db.rollback()
                        # Do NOT raise, just continue to next symbol (which will wait again)
                    except Exception as e:
                        logger.error(f"Error analyzing symbol {sym} with {strategy.name}: {e}")
                        if on_opportunity_found:
                            on_opportunity_found(sym, None, {"is_opportunity": False, "reason": f"System error: {str(e)[:50]}"})
                        db.rollback()
                        
        finally:
            db.close()
            logger.info("Market Scan completed!")
