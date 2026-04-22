import pandas as pd
from src.strategies.bucketers.base_bucketer import BaseBucketer
from src.strategies.bucketers.era_bucketer import EraBucketer
from src.strategies.bucket_scorers.score_swing import SwingScorer
from src.strategies.bucket_scorers.score_rise import RiseScorer
from src.strategies.bucket_scorers.score_lateral import LateralScorer
from src.strategies.bucket_scorers.score_highs import HighsScorer
from src.strategies.bucket_scorers.score_descending import DescendingScorer

class PatternClassifier:
    def __init__(self, bucketer: BaseBucketer = None):
        if bucketer is None:
            self.bucketer = EraBucketer()
        else:
            self.bucketer = bucketer

    def classify(self, hist_data: pd.DataFrame) -> dict:
        from src.utils.data_utils import normalize_yfinance_df
        hist_data = normalize_yfinance_df(hist_data)
        
        if hist_data is None or len(hist_data) < 60:
            return {
                "bucket": "UNKNOWN",
                "confidence": 0,
                "all_scores": {},
                "era_sequence": [],
                "upside_pct": 0.0,
                "pivot_points": [],
                "subtype": ""
            }

        all_scores = self.bucketer.get_bucket_scores(hist_data)
        
        highest_score = 0
        bucket_guanyador = "LATERAL"
        
        # Ordre definit de desempats
        tie_breaker = ["SWING", "RISE", "LATERAL", "HIGHS", "DESCENDING"]
        
        for name in tie_breaker:
            score = all_scores.get(name, 0)
            if score > highest_score:
                highest_score = score
                bucket_guanyador = name

        if highest_score <= 30:
            bucket_guanyador = "LATERAL"
            highest_score = 20

        # Recuperar la era_sequence de l'estat exposat si el bucketer la genera
        era_sequence = []
        if hasattr(self.bucketer, 'last_era_sequence'):
            era_sequence = getattr(self.bucketer, 'last_era_sequence')

        # ADDICIÓ 1: Pivot points
        pivot_points = []
        try:
            closes = hist_data['Close'].values
            dates = hist_data.index
            
            def _perpendicular_distance(pt, line_start, line_end):
                import math
                x0, y0 = pt
                x1, y1 = line_start
                x2, y2 = line_end
                numerator = abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1)
                denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
                if denominator == 0:
                    return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)
                return numerator / denominator

            def rdp_local(points, epsilon):
                dmax = 0.0
                index = 0
                end = len(points) - 1
                for i in range(1, end):
                    d = _perpendicular_distance(points[i], points[0], points[end])
                    if d > dmax:
                        index = i
                        dmax = d
                if dmax > epsilon:
                    result1 = rdp_local(points[:index+1], epsilon)
                    result2 = rdp_local(points[index:], epsilon)
                    return result1[:-1] + result2
                else:
                    return [points[0], points[-1]]

            Close = hist_data["Close"]
            pts = [(i, closes[i]) for i in range(len(closes))]
            
            TARGET_MIN = 6
            TARGET_MAX = 16
            max_iterations = 20
            
            # Epsilon inicial conservador
            price_range = float(Close.max() - Close.min())
            daily_vol = float(Close.pct_change().abs().median())
            avg_price = float(Close.mean())
            epsilon = max(price_range * 0.03,
                          daily_vol * avg_price * 10)
            
            if epsilon > 0:
                key_points = rdp_local(pts, epsilon)
                iteration = 0
                
                # Si massa pivots: augmenta epsilon
                while len(key_points) > TARGET_MAX and \
                      iteration < max_iterations:
                    epsilon *= 1.4
                    key_points = rdp_local(pts, epsilon)
                    iteration += 1
                
                # Si massa pocs pivots: redueix epsilon
                iteration = 0
                while len(key_points) < TARGET_MIN and \
                      iteration < max_iterations:
                    epsilon *= 0.7
                    key_points = rdp_local(pts, epsilon)
                    iteration += 1
                
                print(f"[RDP] final pivots={len(key_points)} "
                      f"epsilon={epsilon:.2f} "
                      f"iterations={iteration}")
                
                if len(key_points) >= 2:
                    peak_count = 1
                    trough_count = 1
                    
                    for i in range(len(key_points)):
                        idx, price = key_points[i]
                        date_str = dates[idx].strftime('%Y-%m-%d') if hasattr(dates[idx], 'strftime') else str(dates[idx])
                        
                        p_type = ""
                        if i == 0:
                            p_type = "PEAK" if price > key_points[1][1] else "TROUGH"
                        elif i == len(key_points) - 1:
                            p_type = "PEAK" if price > key_points[i-1][1] else "TROUGH"
                        else:
                            prev_p = key_points[i-1][1]
                            next_p = key_points[i+1][1]
                            if price > prev_p and price > next_p:
                                p_type = "PEAK"
                            elif price < prev_p and price < next_p:
                                p_type = "TROUGH"
                            else:
                                # Si no és ni pic ni vall clar (segment recte intermedi)
                                # El puntejarem com el predecessor o successor segons tendència?
                                # Les instruccions diuen PEAK si > anterior i > següent.
                                # Si no es compleix cap, deixem-lo buit o classifiquem-lo basat en l'anterior?
                                # Les instruccions NO diuen què fer si no és ni pic ni vall.
                                # Però RDP sol retornar pics i valls.
                                p_type = "PEAK" if price > prev_p else "TROUGH"
                        
                        label = ""
                        if p_type == "PEAK":
                            label = f"P{peak_count}"
                            peak_count += 1
                        else:
                            label = f"T{trough_count}"
                            trough_count += 1
                            
                        pivot_points.append({
                            "index": int(idx),
                            "date": date_str,
                            "price": float(price),
                            "type": p_type,
                            "label": label
                        })
        except Exception:
            pivot_points = []

        # ADDICIÓ 2: Subtypes
        subtype = self.get_subtype(hist_data, bucket_guanyador, pivot_points)

        # Upside percentual (a màxim 252 dies)
        try:
            high_252 = hist_data['High'].tail(252).max()
            close = hist_data['Close'].iloc[-1]
            upside_pct = (high_252 - close) / close * 100 if close > 0 else 0.0
        except:
            upside_pct = 0.0

        return {
            "bucket": bucket_guanyador,
            "confidence": highest_score,
            "all_scores": all_scores,
            "era_sequence": era_sequence,
            "upside_pct": upside_pct,
            "pivot_points": pivot_points,
            "subtype": subtype
        }

    def get_subtype(self, hist_data: pd.DataFrame, bucket: str, pivot_points: list) -> str:
        if not pivot_points or len(pivot_points) < 2:
            return ""
            
        peaks = [p for p in pivot_points if p["type"] == "PEAK"]
        troughs = [p for p in pivot_points if p["type"] == "TROUGH"]
        
        if not peaks or not troughs:
            return ""
            
        last_peak = peaks[-1]
        last_trough = troughs[-1]
        
        closes = hist_data['Close']
        highs = hist_data['High']
        current_price = closes.iloc[-1]
        recent_high_20d = highs.tail(20).max()
        
        # Data objects to check distance (days)
        last_date = hist_data.index[-1]
        
        def days_between(d1_str, d2):
            try:
                import pandas as pd
                d1 = pd.to_datetime(d1_str)
                # Ensure same timezone context if applicable
                if d2.tzinfo is not None and d1.tzinfo is None:
                    d1 = d1.tz_localize(d2.tzinfo)
                elif d2.tzinfo is None and d1.tzinfo is not None:
                    d1 = d1.tz_convert(None)
                return (d2 - d1).days
            except:
                return 999

        if bucket == "SWING":
            # BREAKOUT
            if current_price > last_peak["price"] * 1.02 and days_between(last_peak["date"], last_date) <= 30:
                return "BREAKOUT"
            
            # PULLBACK
            if (recent_high_20d > last_peak["price"] * 1.02 and 
                current_price < recent_high_20d * 0.97 and 
                current_price > last_trough["price"]):
                return "PULLBACK"
                
            # RETEST
            if (abs(current_price - last_trough["price"]) / last_trough["price"] < 0.03 and 
                days_between(last_trough["date"], last_date) <= 20):
                return "RETEST"
                
        elif bucket == "RISE":
            # BREAKOUT
            ath_252d = highs.tail(252).max()
            if current_price >= ath_252d * 0.99:
                return "BREAKOUT"
                
            # PULLBACK
            if current_price < recent_high_20d * 0.95 and closes.tail(5).is_monotonic_decreasing:
                return "PULLBACK"
                
        return ""

    def classify_with_score(self, hist_data: pd.DataFrame) -> dict:
        result = self.classify(hist_data)
        bucket = result.get("bucket", "UNKNOWN")
        
        scorers = {
            "SWING": SwingScorer,
            "RISE": RiseScorer,
            "LATERAL": LateralScorer,
            "HIGHS": HighsScorer,
            "DESCENDING": DescendingScorer
        }
        
        scorer_class = scorers.get(bucket)
        if scorer_class:
            scorer = scorer_class()
            score_res = scorer.score(hist_data, result)
            result["bucket_score"] = score_res.get("score", 0)
            result["bucket_reasoning"] = score_res.get("reasoning", "")
            result["bucket_key_metrics"] = score_res.get("key_metrics", {})
        else:
            result["bucket_score"] = 0
            result["bucket_reasoning"] = ""
            result["bucket_key_metrics"] = {}
            
        return result

    def analyze_phase(self, hist_data: pd.DataFrame) -> dict:
        from src.utils.data_utils import normalize_yfinance_df
        hist_data = normalize_yfinance_df(hist_data)
        
        result = {
            "phase": "N/A",
            "progress_pct": 0.0,
            "pivot_price": 0.0,
            "pivot_date": "",
            "ath_3y": 0.0,
            "ath_5y": 0.0,
            "upside_to_ath3y": 0.0,
            "upside_to_ath5y": 0.0,
            "drop_to_pivot": 0.0,
            "phase_label": "N/A"
        }

        # NORMALITZACIÓ
        hist_data = hist_data.copy()
        if not isinstance(hist_data.index, pd.DatetimeIndex):
            hist_data.index = pd.to_datetime(hist_data.index)
        if hist_data.index.tz is not None:
            hist_data.index = hist_data.index.tz_localize(None)

        # Robustesa de columnes (evita MultiIndex i duplicats de yfinance)
        if isinstance(hist_data.columns, pd.MultiIndex):
            hist_data.columns = hist_data.columns.get_level_values(-1)
        hist_data = hist_data.loc[:, ~hist_data.columns.duplicated()].copy()

        if hist_data is None or len(hist_data) < 150:
            return result

        try:
            # 1. PIVOT
            closes = hist_data['Close']
            pivot_price = closes.tail(90).min()
            pivot_idx = closes.tail(90).idxmin()
            pivot_date = pivot_idx.strftime('%Y-%m-%d') if hasattr(pivot_idx, 'strftime') else str(pivot_idx)

            # 2. VALIDACIÓ
            # Get data exactly up to pivot_date avoiding SettingWithCopyWarning
            pre_pivot_data = hist_data.loc[:pivot_idx]
            if len(pre_pivot_data) == 0:
                return result

            max_before_pivot = pre_pivot_data['Close'].tail(60).max()
            if max_before_pivot <= 0:
                return result

            drop_to_pivot = (max_before_pivot - pivot_price) / max_before_pivot * 100

            if drop_to_pivot < 10:
                result["phase"] = "NO_PATTERN"
                result["phase_label"] = "⚪ Sense patró confiat"
                return result

            # 3. REFERÈNCIES
            highs = hist_data['High']
            ath_3y = highs.tail(252 * 3).max()
            ath_5y = highs.tail(min(252 * 5, len(hist_data))).max()
            current = closes.iloc[-1]

            # 4. PROGRESS
            progress = (current - pivot_price) / (ath_3y - pivot_price) if (ath_3y - pivot_price) > 0 else 0
            progress_pct = min(max(progress * 100, 0), 100)

            # 5. FASE
            if progress_pct < 20:
                phase = "VALLEY"
                phase_label = "🟢 Inici — màxim recorregut, màxim risc"
            elif progress_pct < 65:
                phase = "MID"
                phase_label = "🟡 Sweet spot — tendència confirmada"
            elif progress_pct < 85:
                phase = "MATURE"
                phase_label = "🟠 Madur — poc upside restant"
            else:
                phase = "LATE"
                phase_label = "🔴 Tard — ja no és candidat"

            # 6. UPSIDES
            upside_to_ath3y = (ath_3y - current) / current * 100 if current > 0 else 0
            upside_to_ath5y = (ath_5y - current) / current * 100 if current > 0 else 0

            result.update({
                "phase": phase,
                "progress_pct": progress_pct,
                "pivot_price": pivot_price,
                "pivot_date": pivot_date,
                "ath_3y": ath_3y,
                "ath_5y": ath_5y,
                "upside_to_ath3y": upside_to_ath3y,
                "upside_to_ath5y": upside_to_ath5y,
                "drop_to_pivot": drop_to_pivot,
                "phase_label": phase_label
            })

            return result
        except Exception:
            return result
