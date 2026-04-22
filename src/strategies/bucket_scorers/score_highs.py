import pandas as pd
from src.strategies.bucket_scorers.base_scorer import BaseBucketScorer

class HighsScorer(BaseBucketScorer):
    def score(self, hist_data: pd.DataFrame, metrics: dict) -> dict:
        total_score = 0
        close = hist_data['Close'].iloc[-1]
        
        # Preu dins 2% màxim 60d
        high_60d = hist_data['High'].tail(60).max()
        dist_maxim_pct = (high_60d - close) / close * 100 if close > 0 else 0
        if dist_maxim_pct <= 2:
            total_score += 50
            
        # RSI 14 simple
        delta = hist_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        try:
            rs = gain.iloc[-1] / loss.iloc[-1]
            rsi = 100 - (100 / (1 + rs))
        except:
            rsi = 50
            
        if rsi > 70:
            total_score += 30
            
        # Volum decreixent 5 dies respecte la de 20
        vol_5d = hist_data['Volume'].tail(5).mean()
        vol_20d = hist_data['Volume'].tail(20).mean()
        vol_decreixent = vol_5d < vol_20d
        
        if vol_decreixent:
            total_score += 20
            
        rsi_str = "sobrecomprat" if rsi > 70 else "neutre"
        reasoning = f"En màxims, RSI {rsi:.1f} - {rsi_str}"
        
        return {
            "score": min(100, total_score),
            "reasoning": reasoning,
            "key_metrics": {
                "dist_maxim_pct": dist_maxim_pct,
                "rsi": rsi,
                "volum_trend": "decreixent" if vol_decreixent else "creixent"
            }
        }
