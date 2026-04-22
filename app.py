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
    if st.button("Entrar", key="login_btn"):
        if pwd == st.secrets.get("passwords", {}).get("admin", ""):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Password incorrecta")
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

# --- GLOBAL LOGGER ---
if "scan_logger" not in st.session_state:
    st.session_state.scan_logger = ScanLogger()
scan_logger = st.session_state.scan_logger

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
    ai_provider = st.radio("AI Provider", ["Google Gemini", "OpenAI"], index=0)
    
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
        index=0,
        help="Select the language for the AI-generated research reports."
    )

    st.divider()
    if scan_logger.end_time:
        st.subheader("📋 Last Scan Report")
        report_md = generate_scan_report(scan_logger)
        st.download_button(
            "Download Scan Report",
            report_md,
            file_name=f"radarcore_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.divider()
    st.caption(f"RadarCore - Build Version: {VERSION}")

# --- TABS ---
tab_scanner, tab_watchlist, tab_history, tab_knowledge = st.tabs([
    "Market Scanner", 
    "📋 Watchlist",
    "History & Reports", 
    "Investor Knowledge"
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
        manual_research_btn = st.button("Research Ticker", type="primary", key="btn_research_manual")
        
    with col_strat:
        st.subheader("Strategy Parameters")
        # Direct import and strategy config logic moved here
        from src.strategies.buy_the_dip import BuyTheDipStrategy
        btd = BuyTheDipStrategy()
        
        db_conf = SessionLocal()
        try:
            conf_record = db_conf.query(StrategyConfig).filter(StrategyConfig.strategy_name == btd.name).first()
            actual_params = conf_record.parameters if conf_record else btd.default_parameters
            
            # Sync session state with DB on first run if not already set (except if we just reset)
            if "min_drop" not in st.session_state:
                st.session_state["min_drop"] = actual_params.get("min_drop_pct", 5.0)
            if "min_rebound" not in st.session_state:
                st.session_state["min_rebound"] = actual_params.get("min_rebound_pct", 2.0)
            if "min_mkt_cap" not in st.session_state:
                st.session_state["min_mkt_cap"] = actual_params.get("min_market_cap_b", 2.0)
            
            st.write(f"**Current Strategy:** {btd.name}")
            min_drop = st.slider("Minimum Drop (%)", 5.0, 50.0, float(st.session_state["min_drop"]), 0.5, key="min_drop_slider")
            lookback = st.slider("Historical Window (Days)", 20, 250, int(actual_params.get("lookback_days", 60)), 5)
            min_rebound = st.slider("Minimum Rebound (%)", 0.0, 15.0, float(st.session_state["min_rebound"]), 0.5, key="min_rebound_slider")
            
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                mc = st.number_input("Min Mkt Cap (B $)", 0.0, 1000.0, float(st.session_state["min_mkt_cap"]), key="min_mkt_cap_input")
            with col_n2:
                vol = st.number_input("Min Avg Vol (M)", 0.0, 100.0, float(actual_params.get("min_volume_m", 1.0)))
            
            # Update session state immediately (reactive sync)
            st.session_state["min_drop"] = min_drop
            st.session_state["min_rebound"] = min_rebound
            st.session_state["min_mkt_cap"] = mc
            
            st.caption("✨ Settings are applied live to the next scan.")
        finally:
            db_conf.close()

    if start_btn:
        # Auto-save parameters to DB for persistence
        db_save = SessionLocal()
        try:
            new_p = {
                "min_drop_pct": min_drop,
                "lookback_days": lookback,
                "min_rebound_pct": min_rebound,
                "min_market_cap_b": mc,
                "min_volume_m": vol
            }
            conf_record = db_save.query(StrategyConfig).filter(StrategyConfig.strategy_name == btd.name).first()
            if not conf_record:
                db_save.add(StrategyConfig(strategy_name=btd.name, parameters=new_p))
            else:
                conf_record.parameters = new_p
            db_save.commit()
        except Exception as e:
            logger.error(f"Error auto-saving parameters: {e}")
        finally:
            db_save.close()

        with st.spinner(f"Scanning {market_choice} market..."):
            scanner = MarketScanner()
            # Move results_container OUTSIDE status block to ensure visibility
            results_container = st.container()
            with st.status("Scanning in progress...", expanded=True) as status:
                st.write("Checking market symbols and downloading SPY context...")
                
                def live_chart_callback(symbol, hist, result):
                    with results_container:
                        if result.get("is_opportunity"):
                            st.success(f"New Opportunity Found: {symbol}")
                            st.toast(f"Opportunity for {symbol} added to History.", icon="🚀")
                        else:
                            # Log heartbeats/rejections for transparency
                            reason = result.get("reason", "Filtered")
                            st.caption(f"Checked {symbol}: {reason}")
                
                try:
                    # START SCAN LOGGING
                    scan_logger.start_scan({
                        "universe": market_choice,
                        "min_drop_pct": min_drop,
                        "auto_mode": auto_mode
                    })
                    
                    found_count = [0]
                    def live_chart_callback_with_counter(symbol, hist, result):
                        if result.get("is_opportunity"):
                            found_count[0] += 1
                        live_chart_callback(symbol, hist, result)

                    overrides = {
                        "Buy the Recovery (Swing)": {
                            "min_drop_pct": min_drop,
                            "lookback_days": lookback,
                            "min_rebound_pct": min_rebound,
                            "min_market_cap_b": mc,
                            "min_volume_m": vol
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
                    if hist.empty:
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
                        report = gen.generate_report(manual_ticker, "Direct Search", "User Request", curr_p, metrics, language=report_lang)
                        
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
                show_systemic = st.checkbox("🔍 Mostra Sistèmiques", value=False)

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

                data.append({
                    "Symbol": f"https://es.finance.yahoo.com/quote/{op.symbol}/",
                    "Company": op.company_name or op.symbol,
                    "Estat": nou_estat,
                    "Drop %": f"{drop_val:.1f}%",
                    "Rebound %": f"{rebound_val:.1f}%",
                    "Pattern": pattern_label,
                    "Phase": phase_str,
                    "Upside 3Y": upside_str,
                    "Conf.": f"{confidence:.1f}%",
                    "Date": op.date_detected.strftime('%Y-%m-%d'),
                    "id": op.id # Hidden but used for selection
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
            
            # Comptador sota els filtres
            st.caption(f"{len(df_display)} results out of {len(opportunities)}")

            # -----------------------------------------------------------
            # DATAFRAME — accedim a l'estat intern directament via key
            # -----------------------------------------------------------
            st.dataframe(
                df_display,
                key="history_table_df",
                column_config={
                    "id": None,
                    "Symbol": st.column_config.LinkColumn(
                        "Symbol",
                        display_text=r"https://es\.finance\.yahoo\.com/quote/(.*?)/"
                    )
                },
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            # Llegim la selecció directament del session_state del widget
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
                    type="primary", 
                    use_container_width=True
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
                        id_map = {i: row["id"] for i, row in df_display.iterrows()}
                        
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
                                    
                                    if h_data.empty:
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
                                    st.toast(f"AI Analyzing {op.symbol}...", icon="🧠")
                                    content = report_gen.generate_report(
                                        op.symbol, op.strategy_name, op.explanation, 
                                        op.current_price, op.metrics, language=report_lang
                                    )
                                    
                                    h_data = get_historical_data(op.symbol, period="2y")
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
    st.write("Upload books, methods, or notes to educate the AI for your reports.")
    
    pdf_docs = st.file_uploader("Upload PDF books here", accept_multiple_files=True, type=['pdf'])
    if st.button("Process & Inject Knowledge"):
        if pdf_docs:
            with st.spinner("Fragmenting and vectorizing (FAISS + Google Embeddings)..."):
                eng = RAGEngine()
                for pdf_file in pdf_docs:
                    # Save temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(pdf_file.getvalue())
                        tmp_path = tmp.name
                    
                    ok = eng.process_pdf(tmp_path)
                    os.unlink(tmp_path)
                    
                    if ok:
                        st.success(f"Document '{pdf_file.name}' indexed successfully.")
                    else:
                        st.error(f"Failed to index '{pdf_file.name}'.")
        else:
            st.warning("Please select at least one document.")
