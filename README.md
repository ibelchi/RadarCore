# AI Investment Research Terminal (Swing Trading)

An autonomous assistant designed to scan the stock market (S&P 500, NASDAQ 100, and more), identify parametric "Buy the Dip" swing trading opportunities, and explain the market context by combining technical analysis with personal investment knowledge (RAG).

## Features

* **Market Scanner:** Automatic scanning of technical conditions for filtering. Supports S&P 500, NASDAQ 100, IBEX 35, DAX 40, and more.
* **Strategy System:** Plug-and-play architecture. Includes a configurable "Buy the Dip" strategy by default.
* **AI Report Generation:** Combines calculated technical metrics with specific user knowledge (RAG) uploaded from PDFs using Google Gemini.
* **Streamlit UI:** Automated SQLite database and an interactive, easy-to-use research dashboard.
* **Historical Context:** Ability to evaluate rules against past price action for better decision making.
* **Multi-Language Support:** Generate research reports in English, Spanish, or Catalan.

## Requirements

* Python 3.9+
* Google Gemini API Key (set as `GOOGLE_API_KEY` in `.env`).

## Installation

```bash
git clone https://github.com/ibelchi/swing_trading.git
cd investment_assistant
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
- [RAG Instructions](file:///c:/Users/Belchi/.gemini/antigravity/scratch/investment_assistant/RAG_INSTRUCTIONS.md): Learn how to personalize the AI with your own investment philosophy.

## Future Roadmap
- **Advanced Backtesting:** Full historical simulation module to validate strategies over multi-year periods.
- **Sentiment Analysis:** Integration with news APIs and social media to gauge market sentiment.
- **Real-time Alerts:** Telegram/Email notifications when a new opportunity is detected.
- **Portfolio Tracking:** Basic module to track the performance of detected opportunities.

---
*Disclaimer: This tool is for educational and research purposes only. It does not constitute financial advice.*
