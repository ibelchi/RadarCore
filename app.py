import streamlit as st
import pandas as pd
import tempfile
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load and configure Google AI at the very beginning
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY", "").strip()
if api_key:
    genai.configure(api_key=api_key)
    os.environ["GOOGLE_API_KEY"] = api_key

from src.database.db import SessionLocal, Opportunity, StrategyConfig, get_db
from src.scanner.market_scanner import MarketScanner
from src.ui.opportunity_chart import render_opportunity_chart
from src.ai.rag_engine import RAGEngine
from src.ai.report_generator import ReportGenerator
from src.data.ingestion import get_company_info, get_historical_data

# --- PAGE CONFIG ---
st.set_page_config(page_title="RadarCore", layout="wide")
st.title("RadarCore")

# --- CUSTOM THEME (Purple & Red) ---
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
    st.header("Global Settings")
    st.subheader("AI Configuration")
    ai_provider = st.radio("AI Provider", ["Google Gemini", "OpenAI"], index=0)
    
    if ai_provider == "Google Gemini":
        models = ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-2.0-flash-exp"]
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

# --- TABS ---
tab_scanner, tab_history, tab_knowledge = st.tabs([
    "Market Scanner", 
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
            
            with st.form("btd_config"):
                st.write(f"**Current Strategy:** {btd.name}")
                min_drop = st.slider("Minimum Drop (%)", 5.0, 50.0, actual_params.get("min_drop_pct", 15.0), 0.5)
                lookback = st.slider("Historical Window (Days)", 20, 250, actual_params.get("lookback_days", 60), 5)
                min_rebound = st.slider("Minimum Rebound (%)", 0.0, 15.0, actual_params.get("min_rebound_pct", 2.0), 0.5)
                
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    mc = st.number_input("Min Mkt Cap (B $)", 0.0, 1000.0, actual_params.get("min_market_cap_b", 10.0))
                with col_n2:
                    vol = st.number_input("Min Avg Vol (M)", 0.0, 100.0, actual_params.get("min_volume_m", 1.0))
                    
                guardar = st.form_submit_button("Save Strategy", use_container_width=True)
                if guardar:
                    new_p = {
                        "min_drop_pct": min_drop,
                        "lookback_days": lookback,
                        "min_rebound_pct": min_rebound,
                        "min_market_cap_b": mc,
                        "min_volume_m": vol
                    }
                    if not conf_record:
                        conf_record = StrategyConfig(strategy_name=btd.name, parameters=new_p)
                        db_conf.add(conf_record)
                    else:
                        conf_record.parameters = new_p
                    db_conf.commit()
                    st.toast("Configuration saved!", icon="✅")
        finally:
            db_conf.close()

    if start_btn:
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
                            with st.expander(f"View Analysis Chart — {symbol}", expanded=True):
                                render_opportunity_chart(symbol, hist, result["metrics"])
                        else:
                            # Log heartbeats/rejections for transparency
                            reason = result.get("reason", "Filtered")
                            st.caption(f"Checked {symbol}: {reason}")
                
                try:
                    found_count = [0]
                    def live_chart_callback_with_counter(symbol, hist, result):
                        if result.get("is_opportunity"):
                            found_count[0] += 1
                        live_chart_callback(symbol, hist, result)

                    scanner.run_scan(
                        market=market_key, 
                        limit_symbols=limit if limit > 0 else None,
                        on_opportunity_found=live_chart_callback_with_counter
                    )
                    status.update(label="Scan completed!", state="complete", expanded=False)
                    
                    if found_count[0] > 0:
                        st.success(f"Analysis complete. Found {found_count[0]} potential opportunities.")
                        st.toast(f"Scan completed: {found_count[0]} opportunities identified.", icon="✅")
                    else:
                        st.info("Scan completed. No new opportunities met the strategy criteria today.")
                        st.toast("Scan completed (0 results).", icon="ℹ️")
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
        opportunities = db.query(Opportunity).order_by(Opportunity.date_detected.desc()).limit(50).all()
        if not opportunities:
            st.info("No market opportunities detected yet.")
        else:
            # Prepare Data for Table
            data = []
            for op in opportunities:
                m = op.metrics or {}
                drop_val = m.get("drop_from_high_pct") or m.get("drop_pct", 0)
                rebound_val = m.get("rebound_pct", 0)
                confidence = getattr(op, 'confidence', 0.0) or 0.0
                data.append({
                    "Symbol": f"https://es.finance.yahoo.com/quote/{op.symbol}/",
                    "Company": op.company_name or op.symbol,
                    "Drop %": f"{drop_val:.1f}%",
                    "Rebound %": f"{rebound_val:.1f}%",
                    "Pattern": m.get("pattern_type", "N/A"),
                    "Conf.": f"{confidence:.1f}%",
                    "Date": op.date_detected.strftime('%Y-%m-%d'),
                    "id": op.id # Hidden but used for selection
                })
            
            df_display = pd.DataFrame(data)
            
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
                    use_container_width=True,
                    disabled=not selected_indices
                )
            with col_actions:
                generate_batch = st.button(
                    "Generate Reports", 
                    type="primary", 
                    use_container_width=True,
                    disabled=not selected_indices
                )
            with col_del:
                if st.button("Clear History", key="btn_clear_hist", use_container_width=True):
                    db.query(Opportunity).delete()
                    db.commit()
                    st.rerun()

            if show_charts and selected_indices:
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

            if generate_batch and selected_indices:
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
                col_title, col_clear = st.columns([4, 1])
                with col_title:
                    type_title = "Generated Reports & Visual Analysis" if st.session_state['active_analysis_type'] == 'reports' else "Visual Analysis"
                    st.subheader(type_title)
                with col_clear:
                    if st.button("Clear Results"):
                        st.session_state.pop('active_analysis', None)
                        st.session_state.pop('active_analysis_type', None)
                        st.session_state.pop('active_report_merged', None)
                        st.rerun()
                
                for item in st.session_state['active_analysis']:
                    st.markdown(f"### {item['symbol']} - {item['title']}")
                    if st.session_state['active_analysis_type'] == 'reports':
                        st.markdown(item["content"])
                    if not item["hist"].empty:
                        render_opportunity_chart(item['symbol'], item["hist"], item["metrics"])
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
