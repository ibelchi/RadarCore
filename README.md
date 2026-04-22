<p align="center">
  <img src="assets/logo.png" width="120" alt="radarcore logo">
</p>

# radarcore (Swing Trading Intelligence)

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
- [**Beginner's Guide (Start Here)**](docs/en/beginner_guide.md): Learn Swing Trading basics and how to use the algorithm safely.
- [RAG Instructions](docs/en/rag_instructions.md): Personalize the AI with your own PDF investment philosophy.

**🇪🇸/🇦🇩 Catalan:**
- [**Guia d'Inversió (Principiants)**](docs/ca/guia_principiant.md): Aprèn conceptes bàsics de Swing Trading pas a pas sense por.
- [Instruccions RAG (Personalització)](docs/ca/instruccions_rag.md): Aprèn a personalitzar la IA amb la teva pròpia filosofia en PDF.

**🇪🇸 Spanish:**
- [**Guía de Inversión (Principiantes)**](docs/es/guia_principiante.md): Aprende conceptos básicos de Swing Trading paso a paso sin miedo.
- [Instrucciones RAG (Personalización)](docs/es/instrucciones_rag.md): Aprende a personalizar la IA con tu propia filosofía en PDF.

## Future Roadmap
- **Advanced Backtesting:** Full historical simulation module to validate strategies over multi-year periods.
- **Sentiment Analysis:** Integration with news APIs and social media to gauge market sentiment.
- **Real-time Alerts:** Telegram/Email notifications when a new opportunity is detected.
- **Portfolio Tracking:** Basic module to track the performance of detected opportunities.

---

### Acknowledgments and Credits
This software has been developed thanks to the inspiration from the work of Dani Sánchez-Crespo (https://www.skool.com/decodecore) and David Bastidas (https://www.davidbastidas.com/) in addition to their collaboration.
This software has been programmed with a pedagogical intention and thanks to Gemini and Claude.

*Disclaimer: This tool is for educational and research purposes only. It does not constitute financial advice.*
