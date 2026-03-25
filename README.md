# Quantitative Trading Assistant

Aplicació de terminal i Streamlit per al filtratge de valors en dues etapes: Geomètrica i Sentiment per IA.

## Característiques

### 1. Motor Geomètric (Core)
- **Ingesta de dades**: Descàrrega automàtica de dades històriques (2 anys) via `stooq`.
- **Simplificació de corba**: Algorisme de pivots (mínims i màxims locals) usant `PIP/ZigZag`.
- **Pattern Matching**: Detecció de patrons "Bullish Swing" (Low -> Higher High -> Higher Low -> Breakout) mitjançant **Dynamic Time Warping (DTW)**.
- **Ranking**: Classificació dels top 10 valors que millor s'ajusten al patró.

### 2. Anàlisi de Sentiment (IA)
- **Catalitzadors**: Cerca de notícies recents i detecció de Buybacks, Insider Buying, Upgrades, etc.
- **Sentiment Score**: Puntuació de -1 a +1 generada per un LLM.
- **Factor Earnings**: Avís crític si falten menys de 3 dies per als resultats.
- **Fail-Safe**: L'aplicació funciona de manera degradada si la IA no està disponible.

## Instal·lació

1. **Baixar el projecte**:
   Si tens Git: `git clone https://github.com/ibelchi/swing_trading.git`
   Si no, descarrega el ZIP de GitHub i descomprimeix-lo.

2. **Instal·lar llibreries**:
   Obre una terminal a la carpeta i executa:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar l'API**:
   - Edita el fitxer `.env` a la carpeta arrel.
   - Selecciona el teu proveïdor a `LLM_PROVIDER` ('gemini', 'openai' o 'ollama').
   - Posa la teva clau d'API a la línia corresponent (`GEMINI_API_KEY` o `OPENAI_API_KEY`).

## Ús

1. **Llista de valors**: Modifica el fitxer `tickers.csv` per afegir els símbols que vulguis analitzar.
2. **Execució**:
   - Windows: Fes doble clic a `run_app.bat`.
   - General: `streamlit run app.py`


## Arquitectura

- `app.py`: Interfície d'usuari amb Streamlit i Plotly.
- `core/geometric_engine.py`: Lògica de processament de preus i DTW.
- `intelligence/sentiment_analysis.py`: Integració amb LLMs i anàlisi de notícies.
- `tickers.csv`: Llista personalitzable de valors a analitzar.
