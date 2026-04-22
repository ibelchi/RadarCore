import pandas as pd
from src.strategies.bucket_scorers.base_scorer import BaseBucketScorer

class DescendingScorer(BaseBucketScorer):
    def score(self, hist_data: pd.DataFrame, metrics: dict) -> dict:
        total_score = 0
        close = hist_data['Close'].iloc[-1]
        
        era_sequence = metrics.get("era_sequence", [])
        last_3 = era_sequence[-3:]
        
        consecutive_down = 0
        for era in reversed(last_3):
            if era == "DOWN":
                consecutive_down += 1
            else:
                break
                
        if consecutive_down >= 2:
            total_score += 40
            
        try:
            ema50 = hist_data['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
            ema200 = hist_data['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
            below_emas = close < ema50 < ema200
            if below_emas:
                total_score += 40
        except:
            below_emas = False
            
        vol_5d = hist_data['Volume'].tail(5).mean()
        vol_20d = hist_data['Volume'].tail(20).mean()
        vol_confirma = vol_5d > vol_20d # pujada de volum confirmant baixada
        
        if vol_confirma:
            total_score += 20
            
        forca = "forta" if total_score >= 60 else "moderada"
        reasoning = f"Baixada {forca} - evitar entrada"
        
        return {
            "score": min(100, total_score),
            "reasoning": reasoning,
            "key_metrics": {
                "consecutive_down": consecutive_down,
                "below_emas": below_emas,
                "volum_confirma": vol_confirma
            }
        }
