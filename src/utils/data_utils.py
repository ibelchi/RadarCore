import pandas as pd

def normalize_yfinance_df(df: pd.DataFrame,
                           symbol: str = ""
                           ) -> pd.DataFrame:
    """
    Normalitza un DataFrame de yfinance per garantir
    que les columnes són strings simples (OHLCV)
    independentment de si té MultiIndex o no.
    """
    if df is None or df.empty:
        return df
    
    df = df.copy()
    
    # Cas 1: MultiIndex a les columnes
    # ex: ("Close", "AAPL") → "Close"
    if isinstance(df.columns, pd.MultiIndex):
        # Aplana el MultiIndex agafant el primer nivell
        df.columns = [col[0] if isinstance(col, tuple)
                      else col
                      for col in df.columns]
        # Elimina columnes duplicades si n'hi ha
        df = df.loc[:, ~df.columns.duplicated()]
    
    # Cas 2: Columnes amb espais o capitalització
    # inconsistent
    df.columns = [str(col).strip().capitalize()
                  if str(col).lower() in
                  ['open','high','low','close','volume',
                   'adj close']
                  else str(col)
                  for col in df.columns]
    
    # Assegura columnes OHLCV com a float
    for col in ["Open", "High", "Low", "Close"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )
    
    if "Volume" in df.columns:
        df["Volume"] = pd.to_numeric(
            df["Volume"], errors="coerce"
        ).fillna(0)
    
    # Normalitza l'índex a DatetimeIndex sense timezone
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    
    # Elimina files on Close és NaN
    if "Close" in df.columns:
        df = df.dropna(subset=["Close"])
    
    return df
