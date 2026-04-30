# PROJECTE.md — radarcore (Swing Trading Scanner)

Document de context per a sessions d'IA. Mantingues aquest fitxer actualitzat amb cada decisió important.

## 1. Què és
**radarcore** és un escàner de mercat professional dissenyat per a l'estratègia de Swing Trading. El seu objectiu principal és automatitzar la detecció d'oportunitats basades en correccions tècniques (caigudes i rebots) en índexs globals (S&P 500, NASDAQ, IBEX 35, etc.). 

**Filosofia:**
- **Educativa:** Ajuda l'usuari a entendre el "per què" de cada senyal.
- **Modular:** Arquitectura basada en estratègies i mòduls de dades intercanviables.
- **Robustesa:** Ingesta de dades preparada per evitar bloquejos i garantir la persistència.

## 2. Stack tecnològic
| Capa | Tecnologia | Versió |
| :--- | :--- | :--- |
| **Llenguatge** | Python | 3.9+ |
| **Frontend / UI** | Streamlit | >=1.30.0 |
| **Base de Dades** | SQLite / SQLAlchemy | 2.0+ |
| **Ingesta de dades** | yfinance | 0.2.30+ |
| **Processament** | Pandas / NumPy | 2.0+ |
| **Visualització** | Plotly / TradingView | 6.0+ |
| **IA / LLM** | Google Gemini / OpenAI | Latest |
| **Framework AI** | LangChain | 0.0.6+ |

## 3. Estructura de carpetes
```text
radarcore/
├── app.py                      # Punt d'entrada de l'aplicació Streamlit
├── data/                       # Emmagatzematge persistent
│   └── radarcore.db            # Base de dades SQLite principal
├── src/                        # Codi font modular
│   ├── ai/                     # Motors de RAG i generació d'informes
│   ├── analysis/               # Càlculs avançats (correlacions, etc.)
│   ├── data/                   # Ingesta i neteja de dades
│   ├── database/               # Esquemes i gestió de sessions
│   ├── scanner/                # Lògica de l'escàner de mercat
│   ├── strategies/             # Definicions d'estratègies de trading
│   ├── ui/                     # Components visuals i gràfics
│   └── utils/                  # Utilitats transversals
├── docs/                       # Manuals d'inversió (EN/CA/ES)
└── assets/                     # Recursos visuals (logos, captures)
```

## 4. Model de dades
Esquema principal gestionat via SQLAlchemy a `src/database/db.py`:

- **`Opportunity`**: Registra cada senyal detectat.
    - `metrics` (JSON): Conté dades tècniques (RSI, drop %, rebound %).
    - `market_context` (Text): Anàlisi generat per IA sobre el context macro.
    - `confidence` (Float): Score de 0-100 basat en la qualitat del senyal.
- **`Watchlist`**: Tickers en seguiment actiu.
    - `active` (Boolean): Permet esborrat lògic (soft delete).
- **`StrategyConfig`**: Persisteix els paràmetres de l'escàner (presets).

## 5. Variables d'entorn
Necessàries per a les funcions d'IA (actualment en refactorització):
- `GOOGLE_API_KEY`: Clau per a models Gemini (Principal).
- `OPENAI_API_KEY`: Clau per a models GPT (Opcional).

## 6. Decisions d'arquitectura
- **SQLite + SQLAlchemy**: Triat per la seva simplicitat en desplegaments locals i per evitar la sobrecàrrega de servidors externs.
- **Arquitectura Anti-Bloqueig (YFinance)**: S'ha implementat una capa d'ingesta amb retards exponencials i detecció d'errors 429 per evitar banneigs d'IP.
- **Presets de l'Escàner**: Les configuracions (Conservative, Default, Aggressive) es defineixen com a diccionaris immutables per evitar efectes secundaris durant el runtime.
- **Soft Delete a la Watchlist**: No s'esborren dades físicament per mantenir un històric de l'activitat de l'usuari.

## 7. API Routes
*No s'aplica.* L'aplicació és una SPA (Single Page Application) monolítica amb Streamlit. La comunicació amb el backend és directa a través del codi de Python.

## 8. Fases del projecte
- **Fase 1: Escàner i Estratègies** ✅ Completada
- **Fase 2: Persistència i Històric** ✅ Completada
- **Fase 3: Visualització Avançada** ✅ Completada
- **Fase 4: Motor de RAG i Informes IA** 🔄 En curs (Refactorització)
- **Fase 5: Backtesting Històric** ⏳ Pendent
- **Fase 6: Alertes en Temps Real** ⏳ Pendent

## 9. Workflow de desenvolupament
- **Execució:** `streamlit run app.py` o via `Start_Assistant.bat`.
- **Dependències:** Gestió via `requirements.txt` i entorn virtual `venv`.
- **Logs:** Sistema de diagnòstic a `src/logging/` per traçar errors de l'escàner.
