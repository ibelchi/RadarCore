import pandas as pd
from src.strategies.bucket_scorers.base_scorer import BaseBucketScorer

class RiseScorer(BaseBucketScorer):
    def score(self, hist_data: pd.DataFrame, metrics: dict) -> dict:
        total_score = 0
        close = hist_data['Close'].iloc[-1]
        
        # Era segments
        era_sequence = metrics.get('era_sequence', [])
        last_3 = era_sequence[-3:]
        up_count = last_3.count("UP")
        
        if up_count == 3:
            total_score += 40
        elif up_count == 2:
            total_score += 20
            
        # EMAs
        try:
            ema50 = hist_data['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
            ema200 = hist_data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
            ema_aligned = close > ema50 > ema200
            if ema_aligned:
                total_score += 30
        except:
            ema_aligned = False

        # Upside fins ATH 3Y
        ath_3y = hist_data['High'].tail(252*3).max()
        upside_ath3y = (ath_3y - close) / close * 100 if close > 0 else 0
        
        if upside_ath3y > 15:
            total_score += 30
            
        forca = "fort" if total_score >= 60 else "moderat"
        reasoning = f"Rise {forca}, {upside_ath3y:.1f}% fins ATH 3Y"
        
        return {
            "score": min(100, total_score),
            "reasoning": reasoning,
            "key_metrics": {
                "ema_alignment": ema_aligned,
                "upside_ath3y": upside_ath3y,
                "era_strength": up_count
            }
        }
