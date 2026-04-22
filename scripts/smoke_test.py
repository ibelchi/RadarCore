# Script de smoke test — executa'l després de cada canvi important
# Guarda'l com: scripts/smoke_test.py

import sys
sys.path.insert(0, '.')

def get_hist(ticker="MSFT"):
    import yfinance as yf
    import pandas as pd
    df = yf.download(ticker, period="2y", auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df

def test_normalize_yfinance_df():
    import yfinance as yf
    import pandas as pd
    from src.utils.data_utils import normalize_yfinance_df
    
    # Test amb ticker real
    raw = yf.download("V", period="1y",
                      auto_adjust=True, progress=False)
    normalized = normalize_yfinance_df(raw, "V")
    
    assert not normalized.empty, "FAIL: empty after normalize"
    assert "Close" in normalized.columns, \
        f"FAIL: no Close column. Columns: {normalized.columns.tolist()}"
    assert isinstance(normalized.index,
                      pd.DatetimeIndex), \
        "FAIL: index not DatetimeIndex"
    assert normalized.index.tz is None, \
        "FAIL: index has timezone"
    assert normalized["Close"].dtype in \
        [float, "float64", "float32"], \
        f"FAIL: Close is not float: {normalized['Close'].dtype}"
    
    print(f"OK normalize_yfinance_df: "
          f"{len(normalized)} rows, "
          f"columns={normalized.columns.tolist()}")

def test_pattern_classifier():
    from src.strategies.pattern_classifier import PatternClassifier
    hist = get_hist("MSFT")
    classifier = PatternClassifier()
    
    result = classifier.classify(hist)
    assert "bucket" in result, "FAIL: bucket missing"
    assert result["bucket"] != "UNKNOWN", "FAIL: bucket is UNKNOWN"
    assert "pivot_points" in result, "FAIL: pivot_points missing"
    assert len(result["pivot_points"]) > 0, "FAIL: no pivot points"
    assert "era_sequence" in result, "FAIL: era_sequence missing"
    print(f"OK PatternClassifier: {result['bucket']} "
          f"conf={result['confidence']} "
          f"pivots={len(result['pivot_points'])}")

def test_phase_analyzer():
    from src.strategies.pattern_classifier import PatternClassifier
    hist = get_hist("MSFT")
    classifier = PatternClassifier()
    phase = classifier.analyze_phase(hist)
    
    assert "phase" in phase, "FAIL: phase missing"
    assert phase["phase"] != "", "FAIL: empty phase"
    assert phase["upside_to_ath3y"] != 0, "FAIL: upside is 0"
    print(f"OK PhaseAnalyzer: {phase['phase']} "
          f"progress={phase['progress_pct']:.1f}% "
          f"upside={phase['upside_to_ath3y']:.1f}%")

def test_universe_filter():
    from src.filters.universe_filter import UniverseFilter
    hist = get_hist("AAPL")
    info = {"market_cap": 3_000_000_000_000, "sector": "Technology"}
    uf = UniverseFilter()
    result = uf.is_eligible("AAPL", hist, info)
    
    assert result["eligible"] == True, \
        f"FAIL: AAPL not eligible. Reason: {result['reason']}"
    print(f"OK UniverseFilter: AAPL eligible "
          f"({len(result['passed_criteria'])} criteria passed)")

def test_strategy_params():
    """Verifica que els paràmetres de la UI arriben a l'orquestrador"""
    from src.strategies.buy_the_dip import BuyTheDipStrategy
    hist = get_hist("MSFT")
    strategy = BuyTheDipStrategy()
    
    # Test amb filtre molt restrictiu — no hauria de trobar res
    result_strict = strategy.analyze(
        "MSFT", hist, {"market_cap": 3e12},
        config={"min_drop_pct": 99.0}
    )
    assert not result_strict["is_opportunity"], \
        "FAIL: strategy ignores min_drop_pct parameter"
    
    # Test amb filtre molt permissiu — hauria de trobar
    result_loose = strategy.analyze(
        "MSFT", hist, {"market_cap": 3e12},
        config={"min_drop_pct": 1.0, "min_rebound_pct": 0.1}
    )
    assert result_loose["is_opportunity"], \
        "FAIL: strategy too restrictive even with loose params"
    
    print("OK Strategy params: correctly applied")

if __name__ == "__main__":
    tests = [
        test_normalize_yfinance_df,
        test_pattern_classifier,
        test_phase_analyzer,
        test_universe_filter,
        test_strategy_params,
    ]
    
    failed = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"[CRASH] {test.__name__} CRASHED: {e}")
            failed.append(test.__name__)
    
    print(f"\n{'='*40}")
    if failed:
        print(f"[FAIL] {len(failed)} tests failed: {failed}")
    else:
        print(f"[OK] All {len(tests)} tests passed")
