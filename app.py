import streamlit as st
import pandas as pd
import tempfile
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

def check_password() -> bool:
    if st.session_state.get("authenticated"):
        return True
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Enter", key="login_btn"):
        if pwd == st.secrets.get("passwords", {}).get("admin", ""):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password")
    return False

def is_cloud() -> bool:
    return (
        os.environ.get("STREAMLIT_SHARING_MODE") is not None
        or os.environ.get("IS_CLOUD_DEPLOYMENT", "false").lower() == "true"
    )

if is_cloud():
    if not check_password():
        st.stop()

import google.generativeai as genai

# Load and configure Google AI at the very beginning
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY", "").strip()
if api_key:
    genai.configure(api_key=api_key)
    os.environ["GOOGLE_API_KEY"] = api_key

from src.database.db import SessionLocal, Opportunity, StrategyConfig, get_db, Watchlist
from src.utils.watchlist_utils import get_active_watchlist, should_deep_scan, add_to_watchlist
from src.utils.share_utils import format_opportunity_text, format_scan_summary_text
from src.utils.pdf_utils import generate_minimal_pdf, generate_global_pdf
from src.ui.tradingview_chart import render_tv_chart
from src.scanner.market_scanner import MarketScanner
from src.ai.rag_engine import RAGEngine
from src.ai.report_generator import ReportGenerator
from src.data.ingestion import get_company_info, get_historical_data
from src.logging.scan_logger import ScanLogger
from src.logging.scan_report import generate_scan_report
from src.utils.data_utils import normalize_yfinance_df
from src.data.macro_fetcher import get_macro_context
from src.utils.analysis_utils import is_not_recommended_today
from src.utils.db_migration import backfill_rsi_and_vol
from src.data.news_fetcher import get_company_news
from src.reporting.html_report_builder import generate_html_report
from src.analysis.correlation_matrix import calculate_correlation_matrix


# ═══════════════════════════════════════════════
# PRESETS — defined once, never mutated in place
# ═══════════════════════════════════════════════
PRESETS = {
    "Default": {
        "min_drop_pct": 10.0, "lookback_days": 60,
        "min_rebound_pct": 2.0, "min_market_cap_b": 2.0,
        "min_avg_vol_m": 0.5, "min_relative_drop": 5.0,
        "phase_valley_max": 20.0, "phase_mid_max": 65.0, "phase_mature_max": 85.0,
        "rdp_pivot_min": 6, "rdp_pivot_max": 16,
        "zombie_recovery_pct": 50.0, "zombie_lookback_days": 504,
        "conf_weight_drop": 0.50, "conf_weight_rebound": 0.35, "conf_weight_pattern": 0.15,
    },
    "Conservative": {
        "min_drop_pct": 20.0, "lookback_days": 60,
        "min_rebound_pct": 5.0, "min_market_cap_b": 5.0,
        "min_avg_vol_m": 1.0, "min_relative_drop": 10.0,
        "phase_valley_max": 20.0, "phase_mid_max": 65.0, "phase_mature_max": 85.0,
        "rdp_pivot_min": 6, "rdp_pivot_max": 16,
        "zombie_recovery_pct": 60.0, "zombie_lookback_days": 504,
        "conf_weight_drop": 0.40, "conf_weight_rebound": 0.45, "conf_weight_pattern": 0.15,
    },
    "Aggressive": {
        "min_drop_pct": 7.0, "lookback_days": 90,
        "min_rebound_pct": 1.0, "min_market_cap_b": 1.0,
        "min_avg_vol_m": 0.3, "min_relative_drop": 3.0,
        "phase_valley_max": 25.0, "phase_mid_max": 70.0, "phase_mature_max": 88.0,
        "rdp_pivot_min": 4, "rdp_pivot_max": 20,
        "zombie_recovery_pct": 40.0, "zombie_lookback_days": 756,
        "conf_weight_drop": 0.55, "conf_weight_rebound": 0.30, "conf_weight_pattern": 0.15,
    },
}

# Load persisted custom preset if it exists
_custom_path = ".streamlit/custom_preset.json"
if os.path.exists(_custom_path):
    with open(_custom_path) as _f:
        PRESETS["Custom"] = json.load(_f)

# --- DB BACKFILL ---
if "backfill_done" not in st.session_state:
    db_init = SessionLocal()
    try:
        with st.spinner("Updating historical data..."):
            backfill_rsi_and_vol(db_init)
        st.session_state["backfill_done"] = True
    finally:
        db_init.close()

# --- INITIALIZE HTML REPORT ---
if "last_scan_html" not in st.session_state:
    db_init = SessionLocal()
    try:
        recent_opps = db_init.query(Opportunity).order_by(Opportunity.date_detected.desc()).limit(30).all()
        if recent_opps:
            reports = st.session_state.get("generated_reports", {})
            st.session_state["last_scan_html"] = generate_html_report(
                opportunities=recent_opps,
                macro_data=get_macro_context(),
                reports=reports
            )
    except Exception as e:
        print(f"Error initializing HTML report: {e}")
    finally:
        db_init.close()

# --- GLOBAL LOGGER ---
if "scan_logger" not in st.session_state:
    st.session_state.scan_logger = ScanLogger()
scan_logger = st.session_state.scan_logger

# --- ACTIVE CONFIG (preset system) ---
if "active_config" not in st.session_state:
    st.session_state["active_config"] = PRESETS["Default"].copy()
if "active_preset_name" not in st.session_state:
    st.session_state["active_preset_name"] = "Default"

# --- CONSTANTS ---
VERSION = "1.2.0"
LOGO_PATH = "assets/logo.png"

# --- PAGE CONFIG ---
st.set_page_config(
    page_title=f"radarcore {VERSION}", 
    layout="wide", 
    page_icon=LOGO_PATH
)

# Custom CSS for circular logo and refined header
st.markdown("""
    <style>
    /* Make the logo circular to blend with dark mode */
    [data-testid="stImage"] img {
        border-radius: 50%;
    }
    /* Header styling */
    .header-text {
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        margin-top: -15px !important;
        letter-spacing: -1px;
    }
    </style>
""", unsafe_allow_html=True)

import base64

def get_base64_img(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- HEADER / BRANDING (Ultra-Compact & Centered) ---
try:
    base64_logo = get_base64_img(LOGO_PATH)
    st.markdown(f"""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: -30px; margin-bottom: 20px;'>
            <img src='data:image/png;base64,{base64_logo}' width='60' style='border-radius: 50%;'>
            <h1 style='margin: 0; padding: 0; font-size: 1.8rem; line-height: 1.2;'>radarcore</h1>
        </div>
    """, unsafe_allow_html=True)
except:
    st.markdown("<h1 style='text-align: center;'>radarcore</h1>", unsafe_allow_html=True)

# --- CUSTOM THEME (Purple & Red) ---
# ... (rest of CSS)
# ... (rest of CSS)
st.markdown("""
<style>
    /* Primary buttons as Pastel Purple/Lavender */
    div.stButton > button:first-child {
        background-color: #9b59b6;
        color: white;
        border-radius: 5px;
        border: 1px solid #000000;
    }
    div.stButton > button:first-child:hover {
        background-color: #8e44ad;
        color: white;
        border: 1px solid #000000;
    }
    /* Specific styling for the Delete button (Danger) */
    div.stButton > button[kind="secondary"] {
        background-color: #e74c3c;
        color: white;
        border-radius: 5px;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #c0392b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.title("Settings")
    st.divider()
    st.subheader("Analysis Mode")
    
    auto_mode = st.toggle(
        "Automatic mode",
        value=True,
        help="ON: all opportunities are passed to the scanner. OFF: manual watchlist only."
    )
    st.session_state["auto_mode"] = auto_mode
    
    use_universe_filter = st.toggle(
        "Pre-filter universe",
        value=True,
        key="use_universe_filter",
        help="ON: applies liquidity and zombie filters before scanning (~250 stocks). OFF: scans all tickers directly, the bucketer handles the noise (~500 stocks)."
    )
    
    db_sidebar = SessionLocal()
    try:
        if auto_mode:
            st.caption("✅ All opportunities pass to the Pattern Scanner")
        else:
            n = db_sidebar.query(Watchlist).filter(Watchlist.active == True).count()
            st.caption(f"📋 {n} tickers in manual watchlist")
    finally:
        db_sidebar.close()

    st.divider()

    st.subheader("AI Configuration")
    st.caption("🚧 AI features are under review — these settings have no effect in the current version.")
    ai_provider = st.radio("AI Provider", ["Google Gemini", "OpenAI"], index=0, disabled=True)
    
    if ai_provider == "Google Gemini":
        models = ["gemini-flash-latest", "gemini-pro-latest", "gemini-3.1-pro-preview", "gemini-2.5-flash", "gemini-2.0-flash"]
    else:
        models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
        
    ai_model = st.selectbox("Model", models, index=0)
    
    # Optional API Key override
    with st.expander("API Key Settings (Optional)"):
        user_api_key = st.text_input(f"Override {ai_provider} API Key", type="password")
        if user_api_key:
            st.caption(f"🔑 Specific {ai_provider} key will be used.")

    st.divider()

    report_lang = st.selectbox(
        "AI Report Language",
        ["Catalan", "Spanish", "English"],
        index=2,
        help="Select the language for the AI-generated research reports."
    )

    st.divider()
    st.subheader("📊 Reports & Downloads")
    
    # 1. Regenerate HTML Report
    if st.button("🔄 Refresh HTML Report", use_container_width=True, help="Update the HTML report with the latest database entries"):
        db_sidebar = SessionLocal()
        try:
            recent_opps = db_sidebar.query(Opportunity).order_by(Opportunity.date_detected.desc()).limit(50).all()
            if recent_opps:
                opps_ok = [o for o in recent_opps if not is_not_recommended_today(o.metrics)[0]]
                opps_nok = [o for o in recent_opps if is_not_recommended_today(o.metrics)[0]]
                
                reports = st.session_state.get("generated_reports", {})
                st.session_state["last_scan_html"] = generate_html_report(
                    opportunities=opps_ok,
                    macro_data=get_macro_context(),
                    not_recommended=opps_nok,
                    reports=reports
                )
                st.success("HTML Report updated!")
                st.rerun()
            else:
                st.warning("No opportunities found in database.")
        finally:
            db_sidebar.close()

    # 2. Download Buttons
    if "last_scan_html" in st.session_state:
        st.download_button(
            label="🌐 Download HTML Report",
            data=st.session_state["last_scan_html"],
            file_name=f"radarcore_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            help="Visual HTML report — open in any browser",
            use_container_width=True
        )
    
    if st.session_state.get('active_report_merged'):
        st.download_button(
            "📄 Download AI Analysis (MD)",
            st.session_state['active_report_merged'],
            file_name=f"radarcore_ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
            help="Merged AI research reports for selected tickers"
        )

    if scan_logger.end_time:
        report_md = generate_scan_report(scan_logger)
        st.download_button(
            "📝 Download Scan Log",
            report_md,
            file_name=f"radarcore_scan_log_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
            help="Detailed diagnostic log of the last scan"
        )

    st.divider()
    st.caption(f"RadarCore - Build Version: {VERSION}")

# --- TABS ---
tab_scanner, tab_watchlist, tab_history, tab_knowledge, tab_config = st.tabs([
    "Market Scanner",
    "📋 Watchlist",
    "History & Reports",
    "Investor Knowledge",
    "⚙️ Config",
])

# Utility: Derive provider key
provider_key = "google" if ai_provider == "Google Gemini" else "openai"

# --- TAB SCANNER ---
with tab_scanner:
    st.header("Market Scanning & Strategy")
    st.write("Configure your parameters and find opportunities based on active swing trading strategies.")
    
    # --- ROW 1: SCANNER & STRATEGY CONFIG ---
    col_scan, col_strat = st.columns([1, 1])
    
    with col_scan:
        st.subheader("Scanner")
        market_options = {
            "S&P 500 (USA)": "sp500",
            "NASDAQ 100 (USA)": "nasdaq100",
            "IBEX 35 (Spain)": "ibex35",
            "DAX 40 (Germany)": "dax40",
            "EuroStoxx 50 (Europe)": "eurostoxx50",
            "Nikkei 225 (Japan)": "nikkei225",
            "Nifty 50 (India)": "nifty50"
        }
        market_choice = st.selectbox("Market to Scan:", list(market_options.keys()))
        market_key = market_options[market_choice]
        
        if market_key in ["sp500", "ibex35", "dax40", "eurostoxx50", "nifty50"]:
            st.caption("ℹ️ Internal fixed list/stable source for stability. Last review: **April 2026**.")
        else:
            st.caption("🟢 **Live** scanning against internet directories.")
            
        limit = st.number_input("Symbol limit (0 for full market)", min_value=0, max_value=4000, value=0)

        start_btn = st.button("Run Scan", type="primary", use_container_width=True)
        
        st.divider()
        st.write("Analyze any ticker immediately regardless of current scanner results.")
        manual_ticker = st.text_input("Enter Ticker (e.g., TSLA, SAN.MC):", key="scan_manual_ticker").upper()
        manual_research_btn = st.button("Research Ticker", type="primary", key="btn_research_manual", disabled=True)
        st.caption("🚧 **Under review** — AI research is temporarily unavailable while we improve the analysis quality.", unsafe_allow_html=False)
        
    with col_strat:
        st.subheader("Active Configuration")
        _cfg = st.session_state.get("active_config", PRESETS["Default"])
        _preset = st.session_state.get("active_preset_name", "Default")
        st.info(
            f"⚙️ Active preset: **{_preset}** · "
            f"Drop ≥{_cfg['min_drop_pct']:.0f}% · "
            f"Rebound ≥{_cfg['min_rebound_pct']:.0f}% · "
            f"Market Cap ≥{_cfg['min_market_cap_b']:.1f}B · "
            f"Window {_cfg['lookback_days']}d"
        )
        st.caption("✨ Adjust all parameters in the ⚙️ Config tab.")
        st.markdown(f"""
| Parameter | Value |
|---|---|
| Phase thresholds | Valley<{_cfg['phase_valley_max']:.0f}% · Mid<{_cfg['phase_mid_max']:.0f}% · Mature<{_cfg['phase_mature_max']:.0f}% |
| Confidence weights | Drop {_cfg['conf_weight_drop']:.0%} · Rebound {_cfg['conf_weight_rebound']:.0%} · Pattern {_cfg['conf_weight_pattern']:.0%} |
| Zombie filter | {_cfg['zombie_lookback_days']}d lookback · min {_cfg['zombie_recovery_pct']:.0f}% recovery |
""")

    if start_btn:
        _cfg = st.session_state.get("active_config", PRESETS["Default"])

        with st.spinner(f"Scanning {market_choice} market..."):
            scanner = MarketScanner()
            results_container = st.container()
            with st.status("Scanning in progress...", expanded=True) as status:
                st.write("Checking market symbols and downloading SPY context...")

                def live_chart_callback(symbol, hist, result):
                    with results_container:
                        if result.get("is_opportunity"):
                            st.success(f"New Opportunity Found: {symbol}")
                            st.toast(f"Opportunity for {symbol} added to History.", icon="🚀")
                        else:
                            reason = result.get("reason", "Filtered")
                            st.caption(f"Checked {symbol}: {reason}")

                try:
                    scan_logger.start_scan({
                        "universe": market_choice,
                        "min_drop_pct": _cfg["min_drop_pct"],
                        "auto_mode": auto_mode,
                        "preset": st.session_state.get("active_preset_name", "Default")
                    })

                    found_count = [0]
                    def live_chart_callback_with_counter(symbol, hist, result):
                        if result.get("is_opportunity"):
                            found_count[0] += 1
                        live_chart_callback(symbol, hist, result)

                    overrides = {
                        "Buy the Recovery (Swing)": {
                            "min_drop_pct":     _cfg["min_drop_pct"],
                            "lookback_days":    _cfg["lookback_days"],
                            "min_rebound_pct":  _cfg["min_rebound_pct"],
                            "min_market_cap_b": _cfg["min_market_cap_b"],
                            "min_volume_m":     _cfg["min_avg_vol_m"],
                            "conf_weight_drop":    _cfg["conf_weight_drop"],
                            "conf_weight_rebound": _cfg["conf_weight_rebound"],
                            "conf_weight_pattern": _cfg["conf_weight_pattern"],
                        }
                    }

                    scanner.run_scan(
                        market=market_key, 
                        limit_symbols=limit if limit > 0 else None,
                        on_opportunity_found=live_chart_callback_with_counter,
                        use_universe_filter=st.session_state.get("use_universe_filter", False),
                        scan_logger=scan_logger,
                        strategy_overrides=overrides
                    )
                    
                    # END SCAN LOGGING
                    scan_logger.end_scan()
                    
                    # GENERATE HTML REPORT
                    db_report = SessionLocal()
                    try:
                        all_opps = db_report.query(Opportunity).order_by(Opportunity.date_detected.desc()).limit(100).all()
                        
                        # Separate actionable from non-recommended
                        opps_ok = [o for o in all_opps if not is_not_recommended_today(o.metrics)[0]]
                        opps_nok = [o for o in all_opps if is_not_recommended_today(o.metrics)[0]]
                        
                        reports = st.session_state.get("generated_reports", {})
                        st.session_state["last_scan_html"] = generate_html_report(
                            opportunities=opps_ok,
                            macro_data=get_macro_context(),
                            scan_config=overrides,
                            not_recommended=opps_nok,
                            reports=reports
                        )
                    finally:
                        db_report.close()
                    
                    status.update(label="Scan completed!", state="complete", expanded=False)
                    
                    if found_count[0] > 0:
                        st.success(f"Analysis complete. Found {found_count[0]} potential opportunities.")
                        st.toast(f"Scan completed: {found_count[0]} opportunities identified.", icon="✅")
                    else:
                        st.warning("No opportunities found with current parameters.")
                        
                        with st.expander("🔍 Why? Scan diagnostics"):
                            summary = scan_logger.summary()
                            st.write("**Tickers analyzed:**", summary.get("total_analyzed", 0))
                            st.write("**Discarded by stage:**")
                            
                            skipped = summary.get("skipped_by_stage", {})
                            if skipped:
                                for stage, count in skipped.items():
                                    st.write(f"  - {stage}: {count} tickers")
                            else:
                                st.info(
                                    "Tip: Try reducing Minimum Drop to 10%, "
                                    "Minimum Rebound to 2%, and turning off "
                                    "Pre-filter universe to see more results."
                                )
                            
                            st.divider()
                            if st.button("Apply diagnostic parameters", use_container_width=True):
                                st.session_state["min_drop"] = 10.0
                                st.session_state["min_rebound"] = 2.0
                                st.session_state["min_mkt_cap"] = 2.0
                                st.session_state["use_universe_filter"] = False
                                st.rerun()
                        
                        st.toast("Scan completed (0 results).", icon="⚠️")
                except Exception as e:
                    st.error(f"Critical error during scan: {e}")

    # Manual Research Execution
    if manual_research_btn:
        if not manual_ticker:
            st.warning("Please enter a valid ticker.")
        else:
            with st.spinner(f"Analyzing {manual_ticker}..."):
                try:
                    info = get_company_info(manual_ticker)
                    hist = get_historical_data(manual_ticker)
                    hist = normalize_yfinance_df(hist, manual_ticker)
                    if hist is None or hist.empty:
                        st.error("No data found.")
                    else:
                        curr_p = hist['Close'].iloc[-1]
                        h60, l60 = hist['High'].tail(60).max(), hist['Low'].tail(60).min()
                        metrics = {
                            "current_price": curr_p, "period_high": h60, "period_low": l60,
                            "drop_pct": ((h60 - curr_p) / h60) * 100, "rebound_pct": ((curr_p - l60) / l60) * 100,
                            "lookback_days": 60, "market_cap": info.get("market_cap", 0) / 1e9,
                            "volume": hist['Volume'].tail(10).mean() / 1e6,
                            "per": info.get("per", "N/A"), "eps": info.get("eps", "N/A"),
                            "dividend_yield": info.get("dividend_yield", "N/A"), "next_earnings": info.get("next_earnings", "N/A")
                        }
                        gen = ReportGenerator(
                            provider=provider_key, 
                            model_name=ai_model, 
                            api_key=user_api_key if user_api_key else None
                        )
                        macro = get_macro_context()
                        news = get_company_news(manual_ticker)

                        report = gen.generate_report(
                            manual_ticker, "Direct Search", "User Request", curr_p, metrics, 
                            language=report_lang, macro_context=macro, news_items=news
                        )
                        
                        # Save to reports/ folder
                        os.makedirs("reports", exist_ok=True)
                        filename = f"reports/radarcore_report_{manual_ticker}_{pd.Timestamp.now().strftime('%y%m%d')}.md"
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(report)
                        
                        st.session_state['manual_report'] = report
                        st.session_state['manual_ticker_status'] = manual_ticker
                        st.session_state['manual_report_file'] = filename
                except Exception as e:
                    st.error(f"Error: {e}")

    if 'manual_report' in st.session_state:
        st.divider()
        st.markdown(f"### Research Report: {st.session_state['manual_ticker_status']}")
        st.markdown(st.session_state['manual_report'])
        st.download_button(
            label=f"Download {st.session_state['manual_ticker_status']} Report",
            data=st.session_state['manual_report'],
            file_name= f"radarcore_report_{st.session_state['manual_ticker_status']}_{pd.Timestamp.now().strftime('%y%m%d')}.md",
            mime="text/markdown"
        )

# --- TAB WATCHLIST ---
with tab_watchlist:
    auto_status = st.session_state.get("auto_mode", True)
    if auto_status:
        st.info("🔄 Automatic mode active — watchlist is not used as a filter. Tickers added here will be used when manual mode is activated.")
    else:
        st.success("📋 Watchlist mode active — deep scanner only analyzes these tickers.")
        
    st.header("Watchlist Management")
    
    col_w1, col_w2 = st.columns([3, 1])
    with col_w1:
        manual_tickers = st.text_input("Add ticker", placeholder="e.g., NVDA, MSFT...")
    with col_w2:
        st.write("")
        st.write("")
        add_manual_btn = st.button("➕ Add", use_container_width=True)
        
    db_w = SessionLocal()
    try:
        if add_manual_btn and manual_tickers:
            symbols_to_add = [s.strip() for s in manual_tickers.split(",")]
            added = add_to_watchlist(symbols_to_add, db_w, source='manual')
            if added > 0:
                st.success(f"{added} tickers added to the watchlist.")
            else:
                st.warning("Tickers are already active in the watchlist or input is invalid.")
            
        st.divider()
        st.subheader("Add from recent opportunities")
        recent_ops = db_w.query(Opportunity.symbol).order_by(Opportunity.date_detected.desc()).limit(50).all()
        # Ensure distinct presentation 
        recent_symbols = list(set([r[0] for r in recent_ops]))
        
        selected_recent = st.multiselect("Select recent opportunities to add:", recent_symbols)
        if st.button("➕ Add selected to watchlist"):
            if selected_recent:
                added = add_to_watchlist(selected_recent, db_w, source='scanner')
                if added > 0:
                    st.success(f"{added} tickers added to the watchlist from scanner.")
                else:
                    st.warning("Already active.")
            else:
                st.warning("Select some first.")
                
        st.divider()
        st.subheader("Active Watchlist")
        
        active_items = db_w.query(Watchlist).filter(Watchlist.active == True).all()
        
        if not active_items:
            st.info("The watchlist is empty.")
        else:
            w_data = []
            for item in active_items:
                w_data.append({
                    "Symbol": f"https://es.finance.yahoo.com/quote/{item.symbol}/",
                    "Source": item.source,
                    "Date": item.added_date.strftime('%Y-%m-%d'),
                    "Notes": item.notes or "",
                    "Delete": False,
                    "id": item.id
                })
            
            df_w = pd.DataFrame(w_data)
            
            edited_df = st.data_editor(
                df_w,
                column_config={
                    "id": None,
                    "Symbol": st.column_config.LinkColumn(
                        "Symbol",
                        display_text=r"https://es\.finance\.yahoo\.com/quote/(.*?)/"
                    ),
                    "Source": st.column_config.TextColumn("Source", disabled=True),
                    "Date": st.column_config.TextColumn("Date", disabled=True),
                    "Notes": st.column_config.TextColumn("Notes"),
                    "Delete": st.column_config.CheckboxColumn("Delete (Soft Delete)")
                },
                disabled=["id", "Source", "Date"],
                hide_index=True,
                use_container_width=True,
                key="watchlist_editor"
            )
            
            if st.button("💾 Save changes (Notes / Delete)"):
                for idx, row in edited_df.iterrows():
                    item_id = row['id']
                    db_item = db_w.query(Watchlist).filter(Watchlist.id == item_id).first()
                    if db_item:
                        db_item.notes = row['Notes']
                        if row.get('Delete'):
                            db_item.active = False
                db_w.commit()
                st.rerun()
                
        st.divider()
        st.subheader("Global Actions")
        if st.checkbox("I confirm I want to clear the watchlist (Soft delete)"):
            if st.button("🗑️ Clear watchlist", type="primary"):
                db_w.query(Watchlist).update({"active": False})
                db_w.commit()
                st.success("Watchlist cleared.")
                st.rerun()

    finally:
        db_w.close()

# --- TAB HISTORY ---
with tab_history:
    st.header("Detected Opportunities")
    db = SessionLocal()
    
    # --- MACRO CONTEXT ---
    macro = get_macro_context()
    m_cols = st.columns(5)
    
    indicators = ["SPY", "QQQ", "VIX", "TNX", "DXY"]
    for i, key in enumerate(indicators):
        data = macro.get(key)
        if data and data["value"] is not None:
            m_cols[i].metric(
                label=data["name"],
                value=f"{data['value']:.2f}",
                delta=f"{data['change_pct']:+.2f}%"
            )
        else:
            m_cols[i].metric(label=key, value="N/A")
    
    if macro["alerta_vix"]:
        st.warning("⚠️ VIX > 25 — High volatility market. Consider reducing position size.")
        
    st.caption(f"Macro data updated at {macro['timestamp']}")
    st.divider()
    
    # Auto-migration for confidence column
    try:
        from sqlalchemy import text
        db.execute(text("ALTER TABLE opportunities ADD COLUMN confidence FLOAT"))
        db.commit()
    except Exception:
        db.rollback()

    try:
        opportunities = db.query(Opportunity).order_by(Opportunity.date_detected.desc(), Opportunity.id.desc()).limit(50).all()
        if not opportunities:
            st.info("No market opportunities detected yet.")
        else:
            # FILTRES D'USUARI
            col_filter, col_score, col_sys = st.columns([2, 1, 1])
            with col_filter:
                bucket_filter = st.radio(
                    "",
                    options=["All", "SWING", "RISE", "DESCENDING", "HIGHS", "LATERAL"],
                    horizontal=True,
                    key="bucket_filter",
                    index=0
                )
            with col_score:
                min_score = st.slider(
                    "Min Score",
                    min_value=0, max_value=100,
                    value=0, step=5,
                    key="min_score_filter"
                )
            with col_sys:
                st.write("")
                st.write("")
                show_systemic = st.checkbox("🔍 Show Systemic", value=False)

            # is_not_recommended_today imported from src.utils.analysis_utils


            def matches_bucket_filter(pattern: str, filter_val: str) -> bool:
                mapping = {
                    "SWING":    ["SWING", "V-RECOVERY"],
                    "RISE":     ["RISE"],
                    "DESCENDING": ["DESCENDING", "DOWN"],
                    "HIGHS":    ["HIGHS", "TOP"],
                    "LATERAL":  ["LATERAL", "L-BASE"]
                }
                if filter_val == "All": return True
                terms = mapping.get(filter_val, [filter_val])
                return any(t in pattern for t in terms)

            # Prepare Data for Table
            data = []
            for op in opportunities:
                m = op.metrics or {}
                drop_val = m.get("drop_from_high_pct") or m.get("drop_pct", 0)
                rebound_val = m.get("rebound_pct", 0)
                confidence = getattr(op, 'confidence', 0.0) or 0.0
                
                bucket = m.get("bucket", "N/A")
                if bucket == "N/A" or bucket == "UNKNOWN":
                    bucket = m.get("pattern_type", "N/A")
                    
                subtype = m.get("subtype", "")
                pattern_label = f"{bucket} → {subtype}" if subtype else bucket

                # Aplicar filtres
                if not matches_bucket_filter(pattern_label, bucket_filter):
                    continue
                if confidence < min_score:
                    continue
                if not show_systemic and m.get("is_systemic_new", False) is True:
                    continue

                # Fase antigues del classifier
                phase = m.get("phase", "N/A")
                phase_emojis = {
                    "VALLEY": "🟢", "MID": "🟡", "MATURE": "🟠", "LATE": "🔴", "NO_PATTERN": "⚪"
                }
                emoji = phase_emojis.get(phase, "⚪")
                phase_str = f"{emoji} {phase}" if phase != "N/A" else "N/A"
                
                # Semàfor nou
                nou_semafor = m.get("phase_emoji", "")
                if nou_semafor:
                    fase_nom = m.get("phase_name_new", "")
                    nou_estat = f"{nou_semafor} {fase_nom}"
                else:
                    nou_estat = "-"
                    
                upside_str = "N/A"
                if "upside_to_ath3y" in m:
                    upside_str = f"{m.get('upside_to_ath3y', 0):.1f}%"

                # PART C — Color condicional al RSI
                rsi_val = m.get("rsi_14")
                if rsi_val is not None:
                    if rsi_val >= 70: rsi_display = f"🔴 {rsi_val:.0f}"
                    elif rsi_val <= 30: rsi_display = f"🟢 {rsi_val:.0f}"
                    else: rsi_display = f"⚪ {rsi_val:.0f}"
                else:
                    rsi_display = "N/A"

                # MILLORA 4 — Volum ratio
                vol_ratio = m.get("vol_ratio_3m")
                if vol_ratio is None: 
                    vol_display = "N/A"
                elif vol_ratio >= 2.0:  vol_display = f"🔵 {vol_ratio:.1f}x"
                elif vol_ratio >= 1.5:  vol_display = f"🟡 {vol_ratio:.1f}x"
                elif vol_ratio < 0.5:   vol_display = f"⬜ {vol_ratio:.1f}x"
                else:                   vol_display = f"⚪ {vol_ratio:.1f}x"

                # Millora 3: Classificació recomanació

                not_recommended, reason = is_not_recommended_today(m)

                data.append({
                    "Symbol_raw": op.symbol,
                    "Symbol": f"https://es.finance.yahoo.com/quote/{op.symbol}/",
                    "Company": op.company_name or op.symbol,
                    "Status": nou_estat,
                    "Drop %": f"{drop_val:.1f}%",
                    "Rebound %": f"{rebound_val:.1f}%",
                    "Pattern": pattern_label,
                    "RSI": rsi_display,
                    "Vol": vol_display,
                    "Phase": phase_str,

                    "Upside 3Y": upside_str,
                    "Conf.": f"{confidence:.1f}%",
                    "Date": op.date_detected.strftime('%Y-%m-%d'),
                    "id": op.id, # Hidden but used for selection
                    "_not_recommended": not_recommended,
                    "_not_rec_reason": reason
                })


            
            df_display = pd.DataFrame(data)
            
            if not df_display.empty:
                phase_order = {
                    "🟢 VALLEY": 1, 
                    "🟡 MID": 2, 
                    "🟠 MATURE": 3, 
                    "🔴 LATE": 4, 
                    "⚪ NO PATTERN": 5, 
                    "N/A": 5
                }
                
                df_display["_phase_order"] = df_display["Phase"].map(
                    lambda x: phase_order.get(x, 5)
                )
                df_display["_conf_num"] = df_display["Conf."].str.rstrip("%").astype(float)
                df_display["_upside_num"] = df_display["Upside 3Y"].str.rstrip("%").replace("N/A", "0").astype(float)
                
                df_display = df_display.sort_values(
                    ["_phase_order", "_conf_num", "_upside_num"],
                    ascending=[True, False, False]
                ).drop(columns=["_phase_order", "_conf_num", "_upside_num"]).reset_index(drop=True)
            
            if not df_display.empty:
                df_display["Finviz"] = df_display.apply(
                    lambda row: f"https://finviz.com/quote.ashx?t={row['Symbol_raw']}",
                    axis=1
                )
            
            # Millora 3: Separar DataFrames
            df_ok = df_display[df_display["_not_recommended"] == False].copy()
            df_nok = df_display[df_display["_not_recommended"] == True].copy()
            
            # Results counter
            st.caption(f"{len(df_ok)} actionable opportunities · {len(df_nok)} discouraged today")

            # Taula principal — oportunitats accionables
            st.dataframe(
                df_ok.drop(columns=["_not_recommended", "_not_rec_reason"]),
                key="history_table_df",
                column_config={
                    "id": None,
                    "Symbol_raw": None,
                    "Symbol": st.column_config.LinkColumn(
                        "Symbol",
                        display_text=r"https://es\.finance\.yahoo\.com/quote/(.*?)/"
                    ),
                    "Finviz": st.column_config.LinkColumn(
                        "Finviz",
                        display_text="📊 View",
                        width="small",
                        help="Open in Finviz"
                    ),
                    "RSI": st.column_config.TextColumn("RSI(14)", width="small"),
                    "Vol": st.column_config.TextColumn(
                        "Vol 3M", width="small",
                        help="Today's volume vs 3-month average. 🔵 >2x = possible institutional interest"
                    )
                },

                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            # Separador visual
            if len(df_nok) > 0:
                st.markdown("---")
                with st.expander(
                    f"⚠️ {len(df_nok)} detected but not recommended today (high RSI, LATE phase or imminent earnings)",
                    expanded=True
                ):
                    df_nok_display = df_nok.copy()
                    df_nok_display["Reason"] = df_nok["_not_rec_reason"]
                    
                    st.caption(
                        "Technically detected but with risk factors "
                        "advising against entry today. "
                        "Keep for future monitoring."
                    )
                    st.dataframe(
                        df_nok_display.drop(columns=["_not_recommended", "_not_rec_reason"]),
                        column_config={
                            "id": None,
                            "Symbol_raw": None,
                            "Symbol": st.column_config.LinkColumn(
                                "Symbol",
                                display_text=r"https://es\.finance\.yahoo\.com/quote/(.*?)/"
                            ),
                            "Finviz": st.column_config.LinkColumn(
                                "Finviz",
                                display_text="📊 View",
                                width="small",
                                help="Open in Finviz"
                            ),
                            "RSI": st.column_config.TextColumn("RSI(14)", width="small"),
                            "Vol": st.column_config.TextColumn(
                                "Vol 3M", width="small",
                                help="Today's volume vs 3-month average. 🔵 >2x = possible institutional interest"
                            ),
                            "Reason": st.column_config.TextColumn("Reason", width="medium")

                        },
                        use_container_width=True,
                        hide_index=True
                    )

            # --- PORTFOLIO CORRELATION ANALYSIS ---
            with st.expander("📊 Portfolio Correlation Analysis", expanded=False):
                # Agafa els tickers de les oportunitats mostrades (accionables)
                symbols = df_ok["Symbol_raw"].tolist() if not df_ok.empty else []

                if len(symbols) >= 2:
                    with st.spinner("Calculating correlations..."):
                        corr_data = calculate_correlation_matrix(symbols, period_days=60)

                    if not corr_data["matrix"].empty:
                        # Alerta general
                        level = corr_data["warning_level"]
                        avg = corr_data["avg_portfolio_correlation"]
                        if level == "HIGH":
                            st.warning(f"⚠️ High portfolio correlation ({avg:.2f} avg). Many positions move together — consider diversifying sectors.")
                        elif level == "MEDIUM":
                            st.info(f"📊 Moderate correlation ({avg:.2f} avg). Monitor sector concentration.")
                        else:
                            st.success(f"✅ Good diversification ({avg:.2f} avg).")

                        # Parells problemàtics
                        if corr_data["high_corr_pairs"]:
                            st.markdown("**Highly correlated pairs:**")
                            for pair in corr_data["high_corr_pairs"][:5]:
                                st.markdown(f"{pair['warning']} **{pair['ticker_a']}** ↔ **{pair['ticker_b']}**: {pair['correlation']:.2f}")

                        # Matriu visual (heatmap)
                        import plotly.graph_objects as go
                        matrix = corr_data["matrix"]
                        fig = go.Figure(data=go.Heatmap(
                            z=matrix.values,
                            x=matrix.columns.tolist(),
                            y=matrix.columns.tolist(),
                            colorscale=[
                                [0.0, "#1a1a2e"],
                                [0.5, "#16213e"],
                                [0.75, "#f59e0b"],
                                [1.0, "#ef4444"]
                            ],
                            zmin=-1, zmax=1,
                            text=matrix.values.round(2),
                            texttemplate="%{text}",
                            showscale=True
                        ))
                        fig.update_layout(
                            paper_bgcolor="#0b0d10",
                            plot_bgcolor="#0b0d10",
                            font_color="white",
                            height=400,
                            margin=dict(l=20, r=20, t=20, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Could not calculate correlation matrix. Check connection or tickers.")
                else:
                    st.info("Need at least 2 opportunities to calculate correlation.")

            # Llegim la selecció directament del session_state del widget (només de la taula OK)
            raw_selection = st.session_state.get("history_table_df", {})
            if hasattr(raw_selection, "selection"):
                selected_indices = raw_selection.selection.rows or []
            elif isinstance(raw_selection, dict):
                selected_indices = raw_selection.get("selection", {}).get("rows", [])
            else:
                selected_indices = []

            # Feedback visual
            if selected_indices:
                st.caption(f"Selected: {len(selected_indices)} opportunity(s)")
            else:
                st.caption("Select one or more rows to activate actions.")


            # --- ACTION AREA (Below Dataframe) ---
            col_charts, col_actions, col_del = st.columns([2, 2, 1])
            
            with col_charts:
                show_charts = st.button(
                    "View Charts", 
                    type="primary", 
                    use_container_width=True
                )
            with col_actions:
                generate_batch = st.button(
                    "Generate Reports",
                    type="secondary",
                    use_container_width=True,
                    disabled=True
                )
            with col_del:
                if st.button("Clear History", key="btn_clear_hist", use_container_width=True):
                    db.query(Opportunity).delete()
                    db.commit()
                    st.rerun()

            if show_charts:
                if not selected_indices:
                    st.warning("Please select at least one row from the history table above.")
                else:
                    ops_data = []
                    with st.spinner("Fetching charts..."):
                        # Create a map for reliable lookup within the same rendering cycle
                        id_map = {i: row["id"] for i, row in df_ok.iterrows()}

                        
                        for idx in selected_indices:
                            try:
                                if idx not in id_map:
                                    st.error(f"Selection index {idx} out of range for current view.")
                                    continue
                                    
                                selected_op_id = id_map[idx]
                                op = db.query(Opportunity).filter(Opportunity.id == selected_op_id).first()
                                
                                if op:
                                    st.toast(f"Loading data for {op.symbol}...", icon="📊")
                                    h_data = get_historical_data(op.symbol, period="2y")
                                    h_data = normalize_yfinance_df(h_data, op.symbol)
                                    
                                    if h_data is None or h_data.empty:
                                        st.warning(f"Connection issue or no data available for {op.symbol} via Yahoo Finance.")
                                    else:
                                        ops_data.append({
                                            "symbol": op.symbol, 
                                            "title": op.company_name or op.strategy_name,
                                            "metrics": op.metrics,
                                            "hist": h_data
                                        })
                                else:
                                    st.error(f"Opportunity ID {selected_op_id} not found in database.")
                            except Exception as e:
                                st.error(f"Critical error loading index {idx}: {e}")

                    if ops_data:
                        st.session_state['active_analysis'] = ops_data
                        st.session_state['active_analysis_type'] = 'charts'
                    elif not selected_indices:
                        pass
                    else:
                        st.error("Charts could not be loaded. Please check your internet connection and ticker symbols.")

            if generate_batch:
                if not selected_indices:
                    st.warning("Please select at least one row from the history table above.")
                else:
                    with st.spinner(f"Generating reports for {len(selected_indices)} symbols..."):
                        reports_data = []
                        # Create the same reliable map
                        id_map = {i: row["id"] for i, row in df_display.iterrows()}
                        
                        report_gen = ReportGenerator(
                            provider=provider_key, 
                            model_name=ai_model, 
                            api_key=user_api_key if user_api_key else None
                        )
                        
                        for idx in selected_indices:
                            try:
                                if idx not in id_map:
                                    st.error(f"Selection index {idx} out of range.")
                                    continue
                                    
                                selected_op_id = id_map[idx]
                                op = db.query(Opportunity).filter(Opportunity.id == selected_op_id).first()
                                
                                if op:
                                    macro = get_macro_context()
                                    news = get_company_news(op.symbol)

                                    content = report_gen.generate_report(
                                        op.symbol, op.strategy_name, op.explanation, 
                                        op.current_price, op.metrics, language=report_lang,
                                        macro_context=macro, news_items=news
                                    )
                                    
                                    h_data = get_historical_data(op.symbol, period="2y")
                                    h_data = normalize_yfinance_df(h_data, op.symbol)
                                    full_content = f"# Analysis Report: {op.symbol}\n\n{content}\n\n---"
                                    
                                    reports_data.append({
                                        "symbol": op.symbol, 
                                        "title": op.company_name or op.strategy_name,
                                        "metrics": op.metrics,
                                        "hist": h_data, 
                                        "content": full_content
                                    })
                                else:
                                    st.error(f"Database mismatch for symbol at index {idx}.")
                            except Exception as e:
                                st.error(f"Analysis error for index {idx}: {e}")
                            
                            # Pause to avoid RPM (Requests Per Minute) limits for Google AI
                            import time
                            time.sleep(2.0)
                        
                        if reports_data:
                            merged_report = "\n\n".join([r["content"] for r in reports_data])
                            os.makedirs("reports", exist_ok=True)
                            merged_filename = f"reports/merged_report_{pd.Timestamp.now().strftime('%y%m%d_%H%M')}.md"
                            with open(merged_filename, "w", encoding="utf-8") as f:
                                f.write(merged_report)
                            
                            st.session_state['active_analysis'] = reports_data
                            st.session_state['active_analysis_type'] = 'reports'
                            st.session_state['active_report_merged'] = merged_report
                        else:
                            st.error("Report generation failed. Verify your AI API settings.")

            # --- RENDER RESULTS BELOW ---
            if 'active_analysis' in st.session_state and st.session_state['active_analysis']:
                st.divider()
                col_title, cx1, cx3 = st.columns([2, 1, 1])
                with col_title:
                    type_title = "Generated Reports & Visual Analysis" if st.session_state['active_analysis_type'] == 'reports' else "Visual Analysis"
                    st.subheader(type_title)
                
                with cx1:
                    if st.button("📤 Export Text"):
                        st.session_state['show_global_text'] = format_scan_summary_text(st.session_state['active_analysis'])
                with cx3:
                    if st.button("🗑️ Clear Results"):
                        st.session_state.pop('active_analysis', None)
                        st.session_state.pop('active_analysis_type', None)
                        st.session_state.pop('active_report_merged', None)
                        st.session_state.pop('show_global_text', None)
                        st.rerun()

                if "show_global_text" in st.session_state and st.session_state["show_global_text"]:
                    text_content = st.session_state["show_global_text"]
                    st.markdown(
                        f"""<div style="
                            background-color: #1a1a2e;
                            border: 1px solid #333;
                            border-radius: 8px;
                            padding: 16px;
                            font-family: monospace;
                            font-size: 13px;
                            color: #e0e0e0;
                            line-height: 1.6;
                            white-space: pre-wrap;
                        ">{text_content}</div>""",
                        unsafe_allow_html=True
                    )
                
                for i_idx, item in enumerate(st.session_state['active_analysis']):
                    st.markdown(f"### [{item['symbol']}](https://es.finance.yahoo.com/quote/{item['symbol']}/) - {item['title']}")
                    
                    m = item.get("metrics", {})
                    
                    # EARNINGS BADGES
                    risk_lvl = m.get("earnings_risk_level", "NONE")
                    d_next = m.get("days_to_next_earnings")
                    if risk_lvl == "HIGH":
                        st.error(f"⚠️ EARN {d_next}D")
                    elif risk_lvl == "MEDIUM":
                        st.warning(f"📅 EARN {d_next}D")
                    elif risk_lvl == "LOW":
                        st.caption(f"earn {d_next}d")
                        
                    enote = m.get("earnings_note")
                    if enote:
                        st.info(f"💡 Safety Info: {enote}")
                        
                    phase_status = m.get("phase", "N/A")
                    
                    if phase_status not in ["N/A", "NO_PATTERN", "UNKNOWN"]:
                        phase_label = m.get("phase_label", phase_status)
                        with st.expander("📊 Phase Analysis", expanded=False):
                            phase_emoji_map = {"VALLEY":"🟢","MID":"🟡","MATURE":"🟠","LATE":"🔴"}
                            pe = phase_emoji_map.get(m.get("phase",""), "⚪")
                            st.caption(
                                f"{pe} {m.get('phase','N/A')} · "
                                f"Progress: {m.get('progress_pct',0):.0f}% · "
                                f"Upside 3Y: {m.get('upside_to_ath3y',0):.1f}% · "
                                f"Upside 5Y: {m.get('upside_to_ath5y',0):.1f}% · "
                                f"Pivot: ${m.get('pivot_price',0):.2f}"
                            )
                            
                    if st.session_state['active_analysis_type'] == 'reports':
                        st.markdown(item["content"])
                    
                    # Link Buttons
                    symbol = item["symbol"]
                    col1, col2, col3 = st.columns(3)
                    col1.link_button(
                        "📰 Yahoo Finance News",
                        f"https://finance.yahoo.com/quote/{symbol}/news/",
                        use_container_width=True
                    )
                    col2.link_button(
                        "📊 Finviz",
                        f"https://finviz.com/quote.ashx?t={symbol}",
                        use_container_width=True
                    )
                    col3.link_button(
                        "🏛️ SEC Filings",
                        f"https://www.sec.gov/cgi-bin/browse-edgar"
                        f"?action=getcompany&company={symbol}"
                        f"&type=8-K&dateb=&owner=include&count=10",
                        use_container_width=True
                    )
                    
                    if not item["hist"].empty:
                        render_tv_chart(item['symbol'], item["hist"], item["metrics"], height=500)
                            
                    # BOTONS D'ACCIÓ PER ITEM
                    colA, colC = st.columns([1,1])
                    sym = item['symbol']
                    m = item.get("metrics", {})
                    
                    with colA:
                        if st.button(f"📤 Export Text", key=f"txt_{sym}_{i_idx}"):
                            text_content = format_opportunity_text(sym, m, item)
                            st.markdown(
                                f"""<div style="
                                    background-color: #1a1a2e;
                                    border: 1px solid #333;
                                    border-radius: 8px;
                                    padding: 16px;
                                    font-family: monospace;
                                    font-size: 13px;
                                    color: #e0e0e0;
                                    line-height: 1.6;
                                    white-space: pre-wrap;
                                ">{text_content}</div>""",
                                unsafe_allow_html=True
                            )    
                                
                    with colC:
                        in_wl = db.query(Watchlist).filter(Watchlist.symbol == sym, Watchlist.active == True).first()
                        if in_wl:
                            st.button("✅ In watchlist", disabled=True, key=f"wl_add_{sym}_{i_idx}")
                        else:
                            if st.button("➕ Watchlist", key=f"wl_addbtn_{sym}_{i_idx}"):
                                add_to_watchlist([sym], db, "manual")
                                st.rerun()
                                
                    st.divider()
                
                if st.session_state.get('active_analysis_type') == 'reports':
                    st.download_button(
                        "Download All Reports (.md)", 
                        st.session_state['active_report_merged'], 
                        file_name=f"radarcore_reports_{pd.Timestamp.now().strftime('%y%m%d')}.md"
                    )

    finally:
        db.close()


# --- TAB KNOWLEDGE (RAG) ---
with tab_knowledge:
    st.header("Investor Knowledge Base")
    st.warning(
        "🚧 **Under Review** — The AI Knowledge Base (RAG) is temporarily unavailable "
        "while we improve the quality and accuracy of the document indexing pipeline. "
        "This feature will be re-enabled in a future version."
    )
    st.divider()
    # --- DISABLED UI (preserved for future re-activation) ---
    with st.container():
        pdf_docs = st.file_uploader(
            "Upload PDF books here",
            accept_multiple_files=True,
            type=['pdf'],
            disabled=True
        )
        st.button("Process & Inject Knowledge", disabled=True)

# --- TAB CONFIG ---
with tab_config:
    st.header("⚙️ Scanner Configuration")
    st.write("All parameters configured here are applied on the next scan run.")

    # ── ZONE A: Preset Selector ──
    st.subheader("Configuration Presets")

    col_presets = st.columns(4)
    _preset_names_base = ["Default", "Conservative", "Aggressive"]

    for i, name in enumerate(_preset_names_base):
        with col_presets[i]:
            is_active = (st.session_state["active_preset_name"] == name)
            if st.button(
                f"{'✅ ' if is_active else ''}{name}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                key=f"preset_btn_{name}"
            ):
                st.session_state["active_config"] = PRESETS[name].copy()
                st.session_state["active_preset_name"] = name
                st.rerun()

    with col_presets[3]:
        if "Custom" in PRESETS:
            is_custom_active = (st.session_state["active_preset_name"] == "Custom")
            if st.button(
                f"{'✅ ' if is_custom_active else ''}Custom",
                use_container_width=True,
                type="primary" if is_custom_active else "secondary",
                key="preset_btn_Custom"
            ):
                st.session_state["active_config"] = PRESETS["Custom"].copy()
                st.session_state["active_preset_name"] = "Custom"
                st.rerun()
        if st.button("💾 Save as Custom", use_container_width=True, key="btn_save_custom"):
            PRESETS["Custom"] = st.session_state["active_config"].copy()
            st.session_state["active_preset_name"] = "Custom"
            os.makedirs(".streamlit", exist_ok=True)
            with open(".streamlit/custom_preset.json", "w") as _fout:
                json.dump(PRESETS["Custom"], _fout, indent=2)
            st.success("✅ Custom preset saved!")

    st.divider()

    # ── ZONE B: Detection Parameters ──
    st.subheader("📉 Detection Parameters")
    st.caption(
        "These control which stocks are considered opportunities. "
        "More restrictive = fewer but higher quality signals."
    )

    cfg = st.session_state["active_config"]

    col1, col2 = st.columns(2)
    with col1:
        cfg["min_drop_pct"] = st.slider(
            "Minimum Drop (%)", min_value=5.0, max_value=50.0,
            value=float(cfg["min_drop_pct"]), step=0.5,
            help="Minimum fall from period high to period low. "
                 "Higher = fewer but more significant drops. Default: 10%"
        )
        cfg["min_rebound_pct"] = st.slider(
            "Minimum Rebound (%)", min_value=0.0, max_value=15.0,
            value=float(cfg["min_rebound_pct"]), step=0.5,
            help="Minimum bounce from the low to confirm the turn. "
                 "Higher = more confirmation but later entry. Default: 2%"
        )
        cfg["lookback_days"] = st.slider(
            "Historical Window (days)", min_value=20, max_value=250,
            value=int(cfg["lookback_days"]), step=5,
            help="How far back to look for the high. 60 days = 3 months. Default: 60"
        )
    with col2:
        cfg["min_market_cap_b"] = st.slider(
            "Min Market Cap (B$)", min_value=0.0, max_value=50.0,
            value=float(cfg["min_market_cap_b"]), step=0.5,
            help="Minimum company size. Higher = more stable companies, "
                 "fewer opportunities. Default: 2B$"
        )
        cfg["min_avg_vol_m"] = st.slider(
            "Min Avg Volume (M shares)", min_value=0.0, max_value=10.0,
            value=float(cfg["min_avg_vol_m"]), step=0.1,
            help="Minimum daily trading volume. Ensures you can buy and sell easily. Default: 0.5M"
        )
        cfg["min_relative_drop"] = st.slider(
            "Min Relative Drop vs SPY (%)", min_value=0.0, max_value=20.0,
            value=float(cfg["min_relative_drop"]), step=0.5,
            help="Minimum extra drop vs S&P 500 to consider idiosyncratic. "
                 "Higher = only company-specific drops. Default: 5%"
        )

    st.divider()

    # ── ZONE C: Phase Classification ──
    st.subheader("🎯 Phase Classification")
    st.caption(
        "These thresholds define when a stock transitions from one recovery phase to another."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        cfg["phase_valley_max"] = st.slider(
            "VALLEY upper limit (%)", min_value=10.0, max_value=35.0,
            value=float(cfg["phase_valley_max"]), step=1.0,
            help="Progress% below this = VALLEY phase. Early entry, max upside, max risk. Default: 20%"
        )
    with col2:
        cfg["phase_mid_max"] = st.slider(
            "MID upper limit (%)", min_value=40.0, max_value=80.0,
            value=float(cfg["phase_mid_max"]), step=1.0,
            help="Progress% below this (above VALLEY) = MID phase. Sweet spot. Default: 65%"
        )
    with col3:
        cfg["phase_mature_max"] = st.slider(
            "MATURE upper limit (%)", min_value=70.0, max_value=95.0,
            value=float(cfg["phase_mature_max"]), step=1.0,
            help="Progress% below this (above MID) = MATURE. Above this = LATE. Default: 85%"
        )

    # Phase preview
    st.markdown("**Phase boundaries preview:**")
    _v = cfg["phase_valley_max"]
    _m = cfg["phase_mid_max"]
    _ma = cfg["phase_mature_max"]
    st.markdown(
        f"🟢 VALLEY: 0–{_v:.0f}% · "
        f"🟡 MID: {_v:.0f}–{_m:.0f}% · "
        f"🟠 MATURE: {_m:.0f}–{_ma:.0f}% · "
        f"🔴 LATE: {_ma:.0f}–100%"
    )

    st.divider()

    # ── ZONE D: Confidence Weights ──
    st.subheader("📊 Confidence Score Weights")
    st.caption(
        "The confidence score is a weighted sum of three components. "
        "Weights should sum to 1.0."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        cfg["conf_weight_drop"] = st.slider(
            "Drop quality weight", min_value=0.10, max_value=0.80,
            value=float(cfg["conf_weight_drop"]), step=0.05,
            help="How much the size of the drop contributes to confidence. Default: 50%"
        )
    with col2:
        cfg["conf_weight_rebound"] = st.slider(
            "Rebound quality weight", min_value=0.10, max_value=0.80,
            value=float(cfg["conf_weight_rebound"]), step=0.05,
            help="How much the rebound strength contributes to confidence. Default: 35%"
        )
    with col3:
        cfg["conf_weight_pattern"] = st.slider(
            "Pattern weight", min_value=0.05, max_value=0.40,
            value=float(cfg["conf_weight_pattern"]), step=0.05,
            help="How much the detected pattern contributes to confidence. Default: 15%"
        )

    total_weight = (
        cfg["conf_weight_drop"] +
        cfg["conf_weight_rebound"] +
        cfg["conf_weight_pattern"]
    )
    if abs(total_weight - 1.0) > 0.01:
        st.warning(
            f"⚠️ Weights sum to **{total_weight:.2f}**, not 1.0. "
            f"Results may be unexpected. Adjust until sum = 1.0."
        )
    else:
        st.success(f"✅ Weights sum correctly to **{total_weight:.2f}**")

    st.divider()

    # ── ZONE E: Advanced Parameters ──
    with st.expander("🔬 Advanced Parameters", expanded=False):
        st.caption(
            "Advanced parameters. Only modify if you understand their impact. "
            "Default values are recommended for most use cases."
        )
        col1, col2 = st.columns(2)
        with col1:
            cfg["rdp_pivot_min"] = st.slider(
                "RDP Min Pivots", min_value=3, max_value=10,
                value=int(cfg["rdp_pivot_min"]), step=1,
                help="Minimum number of pivot points in the chart. Fewer = simpler chart. Default: 6"
            )
            cfg["rdp_pivot_max"] = st.slider(
                "RDP Max Pivots", min_value=10, max_value=30,
                value=int(cfg["rdp_pivot_max"]), step=1,
                help="Maximum pivot points before simplifying further. Default: 16"
            )
        with col2:
            cfg["zombie_recovery_pct"] = st.slider(
                "Zombie filter: min recovery (%)", min_value=20.0, max_value=80.0,
                value=float(cfg["zombie_recovery_pct"]), step=5.0,
                help="Minimum historical recovery needed to not be classified as zombie. Default: 50%"
            )
            cfg["zombie_lookback_days"] = st.slider(
                "Zombie filter: lookback (days)", min_value=252, max_value=1260,
                value=int(cfg["zombie_lookback_days"]), step=63,
                help="How far back to look for zombie check. 504 = 2 years. Default: 504"
            )

        if st.button("🔄 Reset ALL to Default", type="secondary", key="btn_reset_config"):
            st.session_state["active_config"] = PRESETS["Default"].copy()
            st.session_state["active_preset_name"] = "Default"
            st.rerun()

    # Persist changes back to session state
    st.session_state["active_config"] = cfg
