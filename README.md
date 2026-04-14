# RadarCore (Swing Trading Intelligence)

An autonomous assistant designed to scan the stock market (S&P 500, NASDAQ 100, and more), identify parametric "Buy the Dip" swing trading opportunities, and explain the market context by combining technical analysis with personal investment knowledge (RAG).

## Features

* **Market Scanner:** Automatic scanning of technical conditions for filtering. Supports S&P 500, NASDAQ 100, IBEX 35, DAX 40, and more.
* **Anti-Blocking Architecture:** Industrial-grade data ingestion with persistent connections, rate-limit (HTTP 429) detection, exponential backoff, and dual-layer fetch fallbacks to prevent IP bans from Yahoo Finance.
* **Strategy System:** Plug-and-play architecture. Includes a configurable "Buy the Dip" strategy by default with European market-friendly defaults.
* **AI Report Generation:** Multi-provider support. Generate research reports using either **Google Gemini** or **OpenAI (GPT-4o)**. 
* **RAG Engine:** Personalize the AI with your own investment philosophy by uploading PDFs. 
* **Streamlit UI:** Automated SQLite database and an interactive research dashboard with real-time heartbeat scanner feedback and stable selection persistence.
* **Smart Data:** Real-time company name lookup, system vs idiosyncratic market context (SPY tracking), and rich technical metrics.
* **Multi-Language Support:** Full results in English, Spanish, or Catalan.

## Requirements

* Python 3.9+
* API Key:
    * **Google Gemini API Key** (for Gemini models).
    * **OpenAI API Key** (for GPT models).
    * *Set them in `.env` or input them directly into the UI.*

## Installation

```bash
git clone https://github.com/ibelchi/swing_trading.git
cd radarcore
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

1. Create a `.env` file in the root directory and add your key:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

2. Run the application:
   ```powershell
   streamlit run app.py
   ```
   *Alternatively, use the `Start_Assistant.bat` shortcut on Windows.*

## User Documentation

### 📘 Fundamentals & Strategy (Investment Manuals)
Learn how RadarCore thinks and make better investment decisions:

**🇬🇧 English:**
- [Beginner's Guide (Start Here)](docs/en/beginner_guide.md): Learn Swing Trading basics and how to use the algorithm safely.
- [Expert Reference](docs/en/expert_reference.md): Pure mathematical specifications, pattern logic, and alpha generation formulas.

**🇪🇸/🇦🇩 Catalan:**
- [Guia d'Inversió (Principiants)](docs/ca/guia_principiant.md): Aprèn conceptes bàsics de Swing Trading pas a pas sense por.
- [Especificació Tècnica (Experts)](docs/ca/referencia_expert.md): Arquitectura paramètrica, reconeixement de patrons i les matemàtiques darrere les decisions.

### ⚙️ AI Customization
- [RAG Instructions](RAG_INSTRUCTIONS.md): Learn how to personalize the AI with your own PDF investment philosophy.

## Future Roadmap
- **Advanced Backtesting:** Full historical simulation module to validate strategies over multi-year periods.
- **Sentiment Analysis:** Integration with news APIs and social media to gauge market sentiment.
- **Real-time Alerts:** Telegram/Email notifications when a new opportunity is detected.
- **Portfolio Tracking:** Basic module to track the performance of detected opportunities.

---
*Disclaimer: This tool is for educational and research purposes only. It does not constitute financial advice.*
