import pandas as pd
import numpy as np

class UniverseFilter:
    """
    Filtre universal previ a qualsevol escaneig de compra.
    Elimina accions no aptes per falta de liquiditat, historial, market cap, o recuperació de preu.

    NOTA DIVERSIFICACIÓ SECTORIAL:
    Implementar a l'orquestrador: després de filtrar tot l'univers, agrupar per info_data['sector'],
    ordenar per score i tallar a 25 per grup.
    """

    def _check_zombie_criterion(self,
                                 hist_data: pd.DataFrame
                                 ) -> dict:
        """
        Retorna {"passes": bool, "reason": str}
        
        Un ticker és zombie si NO té cap episodi de:
          - drawdown >= 20% des d'un màxim local
          - seguit d'un rebote >= 50% d'aquell drawdown
          - ocorregut en els últims 24 mesos (504 sessions)
        
        Si té aquest episodi recentment: PASSA (swing vàlid)
        Si només té episodis antics (>24m): ZOMBIE
        Si no té cap episodi: ZOMBIE
        """
        import numpy as np
        
        try:
            # Finestra màxima: últims 5 anys o tot l'historial
            max_window = min(252 * 5, len(hist_data))
            data = hist_data.tail(max_window).copy()
            
            # Finestra recent: últims 24 mesos
            recent_window = min(504, len(data))
            
            passes_recent = False
            passes_old = False
            
            # Analitza finestres rodants de 252 dies
            window_size = 252
            step = 63  # cada trimestre
            
            for start in range(0, len(data) - window_size,
                               step):
                window = data.iloc[start:start + window_size]
                
                # Màxim de la primera meitat
                first_half = window.iloc[:126]
                max_price = first_half["High"].max()
                max_idx = first_half["High"].idxmax()
                
                # Mínim de la segona meitat
                second_half = window.iloc[126:]
                min_price = second_half["Low"].min()
                min_idx = second_half["Low"].idxmin()
                
                if max_price <= 0:
                    continue
                    
                drawdown = (max_price - min_price) / max_price
                
                if drawdown < 0.20:
                    continue
                
                # Preu al final de la finestra
                end_price = window["Close"].iloc[-1]
                recovery_range = max_price - min_price
                
                if recovery_range <= 0:
                    continue
                    
                recovery = (end_price - min_price) / recovery_range
                
                if recovery >= 0.50:
                    # És un episodi vàlid — és recent?
                    # Comprova si el mínim és dins dels últims 24m
                    position_from_end = len(data) - (
                        data.index.get_loc(min_idx)
                        if min_idx in data.index
                        else len(data)
                    )
                    
                    if position_from_end <= 504:
                        passes_recent = True
                        break  # Trobat episodi recent vàlid
                    else:
                        passes_old = True
            
            if passes_recent:
                return {
                    "passes": True,
                    "reason": "Recent swing recovery detected"
                }
            elif passes_old:
                return {
                    "passes": False,
                    "reason": "Zombie: only old recoveries (>24m ago)"
                }
            else:
                return {
                    "passes": False,
                    "reason": "Zombie: no swing recovery found"
                }
        
        except Exception as e:
            # En cas d'error, benefici del dubte
            return {
                "passes": True,
                "reason": f"Zombie check skipped (error: {str(e)[:50]})"
            }

    def is_eligible(self, symbol: str, hist_data: pd.DataFrame, info_data: dict) -> dict:
        from src.utils.data_utils import normalize_yfinance_df
        hist_data = normalize_yfinance_df(hist_data)
        
        result = {
            "eligible": False,
            "reason": "",
            "passed_criteria": []
        }

        # Comprovació de seguretat bàsica
        if hist_data is None or hist_data.empty:
            result["reason"] = "Poca o cap data històrica disponible"
            return result
        
        current_price = hist_data['Close'].iloc[-1]

        # 1. VOLUM
        try:
            vol_20d = hist_data['Volume'].tail(20).mean()
            if vol_20d >= 500_000 or (vol_20d * current_price) >= 20_000_000:
                result["passed_criteria"].append("Volum i liquiditat aptes")
            else:
                result["reason"] = "Volum insuficient"
                return result
        except Exception as e:
            result["passed_criteria"].append(f"Volum (ignorat per error: {e})")

        # 2. HISTORIAL
        try:
            # Mínim 6 mesos de dades (molt més permissiu)
            if len(hist_data) < 126:
                result["reason"] = "Insufficient history (<6 months)"
                return result
            
            result["passed_criteria"].append("Historial suficient (>= 6 mesos)")
        except Exception as e:
            result["passed_criteria"].append(f"Historial (ignorat per error: {e})")

        # 3. MARKET CAP
        try:
            mcap = info_data.get("market_cap", 0)
            if mcap >= 2_000_000_000:
                result["passed_criteria"].append("Market cap apte")
            else:
                result["reason"] = "Market cap insuficient (<2B$)"
                return result
        except Exception as e:
            result["passed_criteria"].append(f"Market cap (ignorat per error: {e})")

        # 4. PREU MÍNIM
        try:
            if current_price > 5.0:
                result["passed_criteria"].append("Preu > $5")
            else:
                result["reason"] = "Penny stock"
                return result
        except Exception as e:
            result["passed_criteria"].append(f"Preu mínim (ignorat per error: {e})")

        # 5. CRITERI ZOMBIE (clau de Trazo)
        zombie_check = self._check_zombie_criterion(hist_data)
        if not zombie_check["passes"]:
            result["reason"] = zombie_check["reason"]
            return result
        result["passed_criteria"].append("zombie_check")

        # 6. PREU VS ATH HISTÒRIC
        try:
            ath = hist_data['High'].max()
            if current_price >= ath * 0.10:
                result["passed_criteria"].append("Preu vs ATH apte")
            else:
                result["reason"] = "Preu >90% per sota del màxim històric"
                return result
        except Exception as e:
            result["passed_criteria"].append(f"Preu vs ATH històric (ignorat per error: {e})")

        # Si supera tots els filtres, esdevé elegible
        result["eligible"] = True
        return result
