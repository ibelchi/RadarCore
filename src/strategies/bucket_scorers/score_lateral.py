import pandas as pd
from src.strategies.bucket_scorers.base_scorer import BaseBucketScorer

class LateralScorer(BaseBucketScorer):
    def score(self, hist_data: pd.DataFrame, metrics: dict) -> dict:
        total_score = 0
        
        high_15d = hist_data['High'].tail(15).max()
        low_15d = hist_data['Low'].tail(15).min()
        rang_15d = (high_15d - low_15d) / low_15d * 100 if low_15d > 0 else 0
        
        if rang_15d < 5:
            total_score += 40
        elif rang_15d < 8:
            total_score += 20
            
        # Estimació de dies en lateral (aproxem per quan porta sense trencar el canal)
        # Utilitzem l'históric fins on el rang estava per sota del 10%
        # Això és complex, calculem simple com el nombre de dies des que el preu està contingut
        dies_en_lateral = 15 # Minim els 15 de dalt si els supera
        try:
            for i in range(16, min(60, len(hist_data))):
                h = hist_data['High'].tail(i).max()
                l = hist_data['Low'].tail(i).min()
                r = (h - l) / l * 100
                if r < 10:
                    dies_en_lateral = i
                else:
                    break
        except:
            pass
            
        if dies_en_lateral >= 20:
            total_score += 30
            
        vol_5d = hist_data['Volume'].tail(5).mean()
        vol_20d = hist_data['Volume'].tail(20).mean()
        vol_decreixent = vol_5d < vol_20d
        
        if vol_decreixent:
            total_score += 30
            
        vol_str = "decreixent" if vol_decreixent else "estable"
        reasoning = f"Base lateral {dies_en_lateral}d, rang {rang_15d:.1f}%, volum {vol_str}"
        
        return {
            "score": min(100, total_score),
            "reasoning": reasoning,
            "key_metrics": {
                "dies_lateral": dies_en_lateral,
                "rang_pct": rang_15d,
                "volum_trend": "decreixent" if vol_decreixent else "creixent"
            }
        }
