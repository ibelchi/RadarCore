import yfinance as yf
import pandas as pd
import requests
from io import StringIO
import logging

logger = logging.getLogger(__name__)

# Redundant function removed for stability - S&P 500 now in hardcoded_markets


def get_market_symbols(market: str) -> list:
    """
    Gets symbol list based on the selected market.
    Uses hardcoded lists where scraping is fragile to maintain maximum simplicity.
    """
    market = market.lower()
    
    hardcoded_markets = {
        "sp500": ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "BRK-B", "TSLA", "V", "UNH", "LLY", "JPM", "AVGO", "MA", "XOM", "JNJ", "HD", "PG", "COST", "ABBV", "ORCL", "MRK", "AMD", "CRM", "BAC", "CVX", "ADBE", "NFLX", "TMO", "WMT", "WFC", "PEP", "DIS", "ACN", "CSCO", "LIN", "ABT", "INTC", "INTU", "MCD", "VZ", "PYPL", "CMCSA", "TXN", "PM", "CAT", "PFE", "COP", "AMAT", "MDLZ", "QCOM", "UNP", "LOW", "IBM", "SPGI", "HON", "GE", "AMGN", "INTU", "NOW", "PLD", "AXP", "T", "ELV", "SYK", "GS", "ISRG", "BLK", "TJX", "DE", "LRCX", "GILD", "VRTX", "BKNG", "MDLZ", "TJX", "MMC", "REGN", "LMT", "ADI", "SCHW", "ZTS", "PGR", "C", "MO", "CB", "PANW", "FI", "CI", "MU", "BSX", "CI", "HUM", "DELL", "LRCX", "ADI"],
        "ibex35": ["ANA.MC", "ACX.MC", "ACS.MC", "AENA.MC", "AMS.MC", "MTS.MC", "SAB.MC", "SAN.MC", "BKT.MC", "BBVA.MC", "CABK.MC", "CLNX.MC", "ENG.MC", "ELE.MC", "FER.MC", "FDR.MC", "GRIF.MC", "IAG.MC", "IBE.MC", "ITX.MC", "IDR.MC", "COL.MC", "LOG.MC", "MAP.MC", "MEL.MC", "MRL.MC", "NTGY.MC", "PUI.MC", "REP.MC", "ROVI.MC", "SCYR.MC", "SOL.MC", "TEF.MC", "UNI.MC"],
        "dax40": ["ADS.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE", "CBK.DE", "CON.DE", "1COV.DE", "DTG.DE", "DBK.DE", "DB1.DE", "DPW.DE", "DTE.DE", "EOAN.DE", "FRE.DE", "HNR1.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MRK.DE", "MBG.DE", "MTX.DE", "MUV2.DE", "PAH3.DE", "PUM.DE", "QIA.DE", "RHM.DE", "RWE.DE", "SAP.DE", "SRT.DE", "SIE.DE", "ENR.DE", "SHL.DE", "SY1.DE", "VOW3.DE", "VNA.DE", "ZAL.DE"],
        "eurostoxx50": ["ADS.DE", "ADYEN.AS", "AD.AS", "AI.PA", "ALV.DE", "ABI.BR", "ASML.AS", "CS.PA", "BAS.DE", "BAYN.DE", "BBVA.MC", "SAN.MC", "BMW.DE", "BNP.PA", "CRG.IR", "DTE.DE", "DPW.DE", "ENEL.MI", "ENI.MI", "FLTR.IR", "EL.PA", "RMS.PA", "IBE.MC", "ITX.MC", "IFX.DE", "INGA.AS", "ISP.MI", "KER.PA", "OR.PA", "MC.PA", "MBG.DE", "MUV2.DE", "PHIA.AS", "PRX.AS", "SAF.PA", "SAN.PA", "SAP.DE", "SU.PA", "SIE.DE", "STE.PA", "STMPA.PA", "TTE.PA", "VCI.PA", "VOW3.DE", "VNA.DE", "NOKIA.HE"],
        "nifty50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", "BAJFINANCE.NS", "KOTAKBANK.NS", "AXISBANK.NS", "HCLTECH.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS", "TATASTEEL.NS", "CIPLA.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "GRASIM.NS", "DIVISLAB.NS", "BAJAJFINSV.NS", "BPCL.NS", "BRITANNIA.NS", "COALINDIA.NS", "DRREDDY.NS", "HINDALCO.NS", "INDUSINDBK.NS", "ONGC.NS", "TATAMOTORS.NS", "UPL.NS", "JSWSTEEL.NS", "HDFCLIFE.NS", "SBILIFE.NS", "APOLLOHOSP.NS", "ADANIPORTS.NS", "TECHM.NS"]
    }
    
    if market in hardcoded_markets:
        return hardcoded_markets[market]
        
    if market == "nasdaq100":
        try:
            url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            tables = pd.read_html(StringIO(res.text), match='Ticker')
            return tables[0]['Ticker'].str.replace('.', '-', regex=False).tolist()
        except Exception as e:
            logger.error(f"Error scraping NASDAQ: {e}")
            return ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA", "AVGO", "COST", "PEP", "CSCO"]
            
    if market == "nikkei225":
        try:
            url = 'https://en.wikipedia.org/wiki/Nikkei_225'
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            tables = pd.read_html(StringIO(res.text))
            for df in tables:
                if 'Ticker' in df.columns or 'Code' in df.columns:
                    col = 'Ticker' if 'Ticker' in df.columns else 'Code'
                    return (df[col].astype(str) + ".T").tolist()
            return []
        except Exception as e:
            logger.error(f"Error scraping Nikkei 225: {e}")
            return ["7203.T", "6758.T", "9984.T", "8306.T", "9432.T", "7974.T", "8035.T"]
            
    return []

# Shared session to avoid being blocked by Yahoo Finance and improve performance
_SHARED_SESSION = requests.Session()
_SHARED_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
})

class RateLimitException(Exception):
    pass

def get_historical_data(symbol: str, period: str = "1y", retries: int = 1) -> pd.DataFrame:
    """
    Gets EOD (End of Day) historical data for a specific symbol with retry logic.
    """
    for attempt in range(retries + 1):
        try:
            ticker = yf.Ticker(symbol, session=_SHARED_SESSION)
            df = ticker.history(period=period)
            
            if not df.empty:
                return df
                
            # If empty, try fallback download
            df = yf.download(symbol, period=period, progress=False, timeout=10)
            if not df.empty:
                return df

        except Exception as e:
            err_msg = str(e).lower()
            if "too many requests" in err_msg or "429" in err_msg or "ratelimit" in err_msg:
                if attempt == retries:
                    raise RateLimitException(f"Yahoo Finance blocked your connection (Rate Limited) on {symbol}")
                time.sleep(5)
            else:
                logger.error(f"Error obtaining data for {symbol}: {str(e)}")
            
            if attempt < retries:
                continue
            else:
                break
                
    return pd.DataFrame()

def get_company_info(symbol: str) -> dict:
    """Gets basic company information (market cap, sector, etc.)."""
    try:
        # Using Ticker with shared session
        ticker = yf.Ticker(symbol, session=_SHARED_SESSION)
        info = ticker.info
        
        if not info or len(info) < 5:
            logger.warning(f"No sufficient info data for {symbol}")
            return {}
            
        # Extra fundamental metrics
        earnings_date = info.get("nextEarningsDate")
        if earnings_date:
            try:
                # Convert timestamp to readable string (YYYY-MM-DD)
                earnings_str = pd.to_datetime(earnings_date, unit='s').strftime('%Y-%m-%d')
            except:
                earnings_str = "Unknown"
        else:
            earnings_str = "Unknown"

        return {
            "market_cap": info.get("marketCap", 0),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "short_name": info.get("shortName") or info.get("longName") or symbol,
            "currency": info.get("currency", "USD"),
            "per": info.get("trailingPE", 0),
            "eps": info.get("forwardEps", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "next_earnings": earnings_str
        }
    except Exception as e:
        logger.error(f"Error obtaining company information for {symbol}: {e}")
        return {}
