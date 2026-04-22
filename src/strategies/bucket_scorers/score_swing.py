import pandas as pd
from src.strategies.bucket_scorers.base_scorer import BaseBucketScorer

class SwingScorer(BaseBucketScorer):
    def score(self, hist_data: pd.DataFrame, metrics: dict) -> dict:
        total_score = 0
        close = hist_data['Close'].iloc[-1]
        
        # Upside ATH 3Y
        ath_3y = hist_data['High'].tail(252*3).max()
        upside_ath3y = (ath_3y - close) / close * 100 if close > 0 else 0
        
        if upside_ath3y >= 20:
            total_score += 30
        elif upside_ath3y >= 10:
            total_score += 15
            
        # Dies des del minim (approx 60 dies window)
        idx_min = hist_data['Low'].tail(60).idxmin()
        try:
            dies_des_minim = len(hist_data) - hist_data.index.get_loc(idx_min) - 1
        except:
            dies_des_minim = 0
            
        if 5 <= dies_des_minim <= 30:
            total_score += 25
        elif dies_des_minim > 30:
            total_score += 10
            
        # Volum últim segment (aproximació darrers 5 dies vs 20)
        volum_mitjana_20d = hist_data['Volume'].tail(20).mean()
        volum_ultims_5d = hist_data['Volume'].tail(5).mean()
        vol_confirmat = volum_ultims_5d > volum_mitjana_20d
        if vol_confirmat:
            total_score += 20
            
        # Pendent darrer segment
        pendent = (close - hist_data['Close'].iloc[-5]) / hist_data['Close'].iloc[-5] if len(hist_data) >= 5 else 0
        if pendent > 0:
            total_score += 10
            
        vol_str = "confirmat" if vol_confirmat else "feble"
        reasoning = f"Swing: {upside_ath3y:.1f}% upside, {dies_des_minim} dies des del mínim, volum {vol_str}"
        
        return {
            "score": min(100, total_score),
            "reasoning": reasoning,
            "key_metrics": {
                "upside_pct": upside_ath3y,
                "dies_des_minim": dies_des_minim,
                "volum_ratio": volum_ultims_5d / volum_mitjana_20d if volum_mitjana_20d > 0 else 1
            }
        }
