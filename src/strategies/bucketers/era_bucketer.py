import pandas as pd
import numpy as np
from src.strategies.bucketers.base_bucketer import BaseBucketer
import math

class EraBucketer(BaseBucketer):
    name = "EraBucketer_v1"

    def __init__(self):
        self.last_era_sequence = []

    def get_bucket_scores(self, hist_data: pd.DataFrame) -> dict:
        scores = {"SWING": 0, "RISE": 0, "DESCENDING": 0, "HIGHS": 0, "LATERAL": 0}
        
        if hist_data is None or len(hist_data) < 60:
            return scores
            
        def rdp(points, epsilon):
            dmax = 0.0
            index = 0
            end = len(points) - 1
            for i in range(1, end):
                d = self._perpendicular_distance(points[i], points[0], points[end])
                if d > dmax:
                    index = i
                    dmax = d
            if dmax > epsilon:
                result1 = rdp(points[:index+1], epsilon)
                result2 = rdp(points[index:], epsilon)
                return result1[:-1] + result2
            else:
                return [points[0], points[-1]]

        closes = hist_data['Close'].values
        epsilon = 0.02 * (closes.max() - closes.min())
        if epsilon == 0:
            return scores
            
        points = [(i, closes[i]) for i in range(len(closes))]
        key_points = rdp(points, epsilon)
        
        # Segona passada RDP per la tendència macro
        self.macro_points = rdp(key_points, epsilon * 3)
        
        eras = []
        for i in range(len(key_points) - 1):
            p_init = key_points[i][1]
            p_final = key_points[i+1][1]
            if p_init <= 0:
                continue
            canvi = (p_final - p_init) / p_init
            if canvi > 0.03:
                eras.append("UP")
            elif canvi < -0.03:
                eras.append("DOWN")
            else:
                eras.append("FLAT")
                
        self.last_era_sequence = eras[-6:] if len(eras) >= 6 else eras
        era_sequence = self.last_era_sequence

        high_60d = hist_data['High'].tail(60).max()
        low_60d = hist_data['Low'].tail(60).min()
        close = closes[-1]
        
        drop_pct = (high_60d - low_60d) / high_60d if high_60d > 0 else 0
        rebound_pct = (close - low_60d) / low_60d if low_60d > 0 else 0
        
        try:
            ema50 = hist_data['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
            ema200 = hist_data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        except:
            ema50 = close
            ema200 = close
            
        # SWING
        last_4 = era_sequence[-4:]
        if len(last_4) == 4:
            is_perfect_alternating = True
            for i in range(1, 4):
                if last_4[i] == last_4[i-1]:
                    is_perfect_alternating = False
                    break
            
            if is_perfect_alternating:
                scores["SWING"] += 50
            else:
                # Partial alternance logic (2 de 3)
                if last_4[-1] != last_4[-2] and len(set(last_4)) > 1:
                    scores["SWING"] += 25
                    
        if era_sequence and era_sequence[-1] == "UP":
            scores["SWING"] += 20
        if drop_pct >= 0.15:
            scores["SWING"] += 15
        if rebound_pct >= 0.02:
            scores["SWING"] += 15
            
        # RISE
        last_3 = era_sequence[-3:]
        up_count = last_3.count("UP")
        if up_count == 3:
            scores["RISE"] += 60
        elif up_count == 2:
            scores["RISE"] += 35
        if close > ema50:
            scores["RISE"] += 20
        if ema50 > ema200:
            scores["RISE"] += 20
            
        # DESCENDING
        down_count = last_3.count("DOWN")
        if down_count == 3:
            scores["DESCENDING"] += 60
        elif down_count == 2:
            scores["DESCENDING"] += 35
        if close < ema50:
            scores["DESCENDING"] += 20
        if ema50 < ema200:
            scores["DESCENDING"] += 20
            
        # HIGHS
        if close >= high_60d * 0.95:
            scores["HIGHS"] += 60
        elif close >= high_60d * 0.90:
            scores["HIGHS"] += 30
        if close > ema50:
            scores["HIGHS"] += 40
            
        # LATERAL
        high_15d = hist_data['High'].tail(15).max()
        low_15d = hist_data['Low'].tail(15).min()
        if low_15d > 0:
            rang_15d = (high_15d - low_15d) / low_15d * 100
            if rang_15d < 8:
                scores["LATERAL"] += 50
                
        try:
            lows_15 = hist_data['Low'].tail(15)
            dies_des_minim = len(lows_15) - lows_15.values.argmin() - 1
        except:
            dies_des_minim = 0

        if dies_des_minim >= 10:
            scores["LATERAL"] += 30
        if drop_pct >= 0.10:
            scores["LATERAL"] += 20
            
        for k in scores:
            scores[k] = min(100, int(scores[k]))
            
        return scores

    def _perpendicular_distance(self, pt, line_start, line_end):
        x0, y0 = pt
        x1, y1 = line_start
        x2, y2 = line_end
        numerator = abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1)
        denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        if denominator == 0:
            return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)
        return numerator / denominator
