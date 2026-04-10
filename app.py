import streamlit as st
import pandas as pd
import tempfile
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Carregar i configurar Google AI al principi de tot
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY", "").strip()
if api_key:
    genai.configure(api_key=api_key)
    os.environ["GOOGLE_API_KEY"] = api_key

from src.database.db import SessionLocal, Opportunity, StrategyConfig
from src.scanner.market_scanner import MarketScanner
from src.ai.rag_engine import RAGEngine
from src.ai.report_generator import ReportGenerator
from src.data.ingestion import get_company_info, get_historical_data

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Investment Research Terminal", layout="wide")
st.title("📈 AI Investment Research Terminal")

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("Global Settings")
    report_lang = st.selectbox(
        "AI Report Language",
        ["Catalan", "Spanish", "English"],
        index=0,
        help="Select the language for the AI-generated research reports."
    )

# --- TABS ---
tab_config, tab_scanner, tab_history, tab_knowledge = st.tabs([
    "⚙️ Strategy Settings",
    "🔍 Market Scanner", 
    "📚 History & Reports", 
    "🧠 Investor Knowledge (RAG)"
])

# --- TAB SCANNER ---
with tab_scanner:
    st.header("Daily Market Scanning")
    st.write("Find opportunities based on active swing trading strategies.")
    
    col1, col2 = st.columns([1, 4])
    with col1:
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
        
        if market_key in ["ibex35", "dax40", "eurostoxx50", "nifty50"]:
            st.caption("ℹ️ Internal fixed list for stability. Last review: **April 2026**.")
        else:
            st.caption("🟢 **Live** scanning against internet directories.")
            
        limit = st.number_input("Symbol limit (0 for full market)", min_value=0, max_value=4000, value=0)
        start_btn = st.button("Run Scanner", type="primary")
        
    with col2:
        if start_btn:
            with st.spinner(f"Scanning {market_choice} market... This may take a moment."):
                scanner = MarketScanner()
                try:
                    scanner.run_scan(market=market_key, limit_symbols=limit if limit > 0 else None)
                    st.success("Scan completed! Check the History tab for new opportunities.")
                    st.balloons()
                except Exception as e:
                    st.error(f"⚠️ Critical error during scan: {e}")

    st.divider()
    st.subheader("🔍 On-Demand Analysis")
    st.write("Generate a professional AI report for any ticker immediately.")
    
    c1, c2 = st.columns([1, 4])
    with c1:
        manual_ticker = st.text_input("Enter Ticker (e.g., TSLA, SAN.MC, 7203.T):").upper()
        if st.button("Generate Report Now", type="primary"):
            if not manual_ticker:
                st.warning("Please enter a valid ticker.")
            else:
                with st.spinner(f"Fetching data and analyzing {manual_ticker}..."):
                    try:
                        info = get_company_info(manual_ticker)
                        hist = get_historical_data(manual_ticker)
                        
                        if hist.empty:
                            st.error("Could not find data for this ticker.")
                        else:
                            curr_p = hist['Close'].iloc[-1]
                            high_60 = hist['High'].tail(60).max()
                            low_60 = hist['Low'].tail(60).min()
                            
                            metrics = {
                                "current_price": curr_p,
                                "period_high": high_60,
                                "period_low": low_60,
                                "drop_pct": ((high_60 - curr_p) / high_60) * 100,
                                "rebound_pct": ((curr_p - low_60) / low_60) * 100,
                                "lookback_days": 60,
                                "market_cap": info.get("market_cap", 0) / 1e9,
                                "volume": hist['Volume'].tail(10).mean() / 1e6,
                                "per": info.get("per", "N/A"),
                                "eps": info.get("eps", "N/A"),
                                "dividend_yield": info.get("dividend_yield", "N/A"),
                                "next_earnings": info.get("next_earnings", "N/A")
                            }
                            
                            gen = ReportGenerator()
                            report = gen.generate_report(
                                symbol=manual_ticker,
                                strategy_name="On-Demand Analysis",
                                tech_reason="Manual user request.",
                                current_price=curr_p,
                                metrics=metrics,
                                language=report_lang
                            )
                            
                            st.session_state['manual_report'] = report
                            st.session_state['manual_ticker_status'] = manual_ticker

                    except Exception as e:
                        st.error(f"Error analyzing {manual_ticker}: {e}")

    with c2:
        if 'manual_report' in st.session_state:
            st.markdown(f"### Research Report: {st.session_state['manual_ticker_status']}")
            st.markdown(st.session_state['manual_report'])
            st.download_button(
                label=f"📥 Download Report ({st.session_state['manual_ticker_status']})",
                data=st.session_state['manual_report'],
                file_name=f"report_{st.session_state['manual_ticker_status']}.md",
                mime="text/markdown"
            )

    with st.expander("🗑️ Danger Zone"):
        if st.button("Delete All History", type="secondary"):
            db = SessionLocal()
            try:
                db.query(Opportunity).delete()
                db.commit()
                st.warning("The opportunities database has been cleared.")
            finally:
                db.close()

# --- TAB HISTORY ---
with tab_history:
    st.header("Detected Opportunities")
    db = SessionLocal()
    try:
        opportunities = db.query(Opportunity).order_by(Opportunity.date_detected.desc()).limit(50).all()
        if not opportunities:
            st.info("No market opportunities detected yet.")
        else:
            # Display summary table with Yahoo Finance links
            data = []
            
            # Currency formatting helper
            def fmt_curr(price, curr_code):
                symbols = {"EUR": "€", "USD": "$", "JPY": "¥", "INR": "₹", "GBP": "£"}
                s = symbols.get(curr_code, curr_code or "$")
                return f"{price:.2f} {s}"

            for op in opportunities:
                data.append({
                    "ID": op.id,
                    "Date": op.date_detected.strftime('%Y-%m-%d %H:%M'),
                    "Market": op.market.upper() if op.market else "S&P500",
                    "Symbol": f"https://es.finance.yahoo.com/quote/{op.symbol}/",
                    "Strategy": op.strategy_name,
                    "Price": fmt_curr(op.current_price, op.currency),
                    "_symbol_real": op.symbol # Used for database lookups
                })
            
            df = pd.DataFrame(data)
            st.dataframe(
                df.drop(columns=["_symbol_real"]),
                column_config={
                    "ID": None,  # Hide ID column
                    "Symbol": st.column_config.LinkColumn(
                        "Symbol",
                        display_text=r"https://es\.finance\.yahoo\.com/quote/(.*?)/"
                    )
                },
                use_container_width=True
            )
            
            st.divider()
            st.subheader("Generate AI Reports")
            
            # Multi-ticker selector
            ticker_list = df["_symbol_real"].unique().tolist()
            selected_symbols = st.multiselect("Select symbols to analyze (choose multiple)", ticker_list)
            
            if st.button("Generate Selected Reports"):
                if not selected_symbols:
                    st.warning("Please select at least one symbol.")
                else:
                    all_reports = ""
                    progress_bar = st.progress(0)
                    
                    for idx, sym in enumerate(selected_symbols):
                        with st.status(f"Analyzing {sym}...", expanded=True) as status:
                            op = db.query(Opportunity).filter(Opportunity.symbol == sym).order_by(Opportunity.date_detected.desc()).first()
                            if op:
                                gen = ReportGenerator()
                                informe = gen.generate_report(
                                    symbol=op.symbol, 
                                    strategy_name=op.strategy_name, 
                                    tech_reason=op.explanation, 
                                    current_price=op.current_price,
                                    metrics=op.metrics,
                                    language=report_lang
                                )
                                
                                st.markdown(f"### Research Report: {sym}")
                                st.markdown(informe)
                                
                                # Accumulate for download
                                all_reports += f"# MARKET REPORT: {sym}\n\n{informe}\n\n---\n\n"
                                
                            progress_bar.progress((idx + 1) / len(selected_symbols))
                            status.update(label=f"Analysis of {sym} completed", state="complete")
                    
                    st.divider()
                    st.download_button(
                        label="📥 Download all reports (.md)",
                        data=all_reports,
                        file_name="investment_reports.md",
                        mime="text/markdown"
                    )
    finally:
        db.close()

# --- TAB CONFIG ---
with tab_config:
    st.header("Strategy Configuration")
    st.write("Adjust strategy parameters without touching the code.")
    
    # Direct import trick
    from src.strategies.buy_the_dip import BuyTheDipStrategy
    btd = BuyTheDipStrategy()
    
    db = SessionLocal()
    try:
        conf_record = db.query(StrategyConfig).filter(StrategyConfig.strategy_name == btd.name).first()
        actual_params = conf_record.parameters if conf_record else btd.default_parameters
        
        with st.form("btd_config"):
            st.subheader(btd.name)
            
            col1, col2 = st.columns(2)
            with col1:
                min_drop = st.slider("Minimum Drop (%)", 5.0, 50.0, actual_params.get("min_drop_pct", 15.0), 0.5)
                lookback = st.slider("Historical Window (Days)", 20, 250, actual_params.get("lookback_days", 60), 5)
                min_rebound = st.slider("Minimum Rebound (%)", 0.0, 15.0, actual_params.get("min_rebound_pct", 2.0), 0.5)
            
            with col2:
                mc = st.number_input("Min Market Cap (B $)", 0.0, 1000.0, actual_params.get("min_market_cap_b", 10.0))
                vol = st.number_input("Min Average Volume (M)", 0.0, 100.0, actual_params.get("min_volume_m", 1.0))
                
            guardar = st.form_submit_button("Save Changes")
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
                    db.add(conf_record)
                else:
                    conf_record.parameters = new_p
                db.commit()
                st.success("Configuration saved and applied for the next scan.")
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
