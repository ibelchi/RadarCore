from dotenv import load_dotenv
import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from src.ai.rag_engine import RAGEngine

# Carregar variables d'entorn des de .env
load_dotenv()

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        # Intentem agafar la clau directament de l'entorn per ser més robusts
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.2,
            api_key=api_key if api_key else None,
            google_api_key=api_key if api_key else None
        )
        self.rag = RAGEngine()
        
    def generate_report(self, symbol: str, strategy_name: str, tech_reason: str, current_price: float, metrics: dict = None, language: str = "Catalan") -> str:
        """Agrupa el coneixement RAG amb la troballa tècnica per oferir un resum en l'idioma seleccionat."""
        
        # Consultem a la bdd de coneixement del RAG quins criteris té l'usuari
        # o consells generals sobre swing trading i l'estratègia en concret.
        user_knowledge = self.rag.similarity_search(f"Criterios de inversión y factores de riesgo para {strategy_name} en accions", k=3)
        
        # Assegurar per defecte diccionari buit per metrics
        metrics = metrics or {}
        
        prompt = PromptTemplate.from_template("""
Ets un Expert Equity Analyst & Data Engineer especialitzat en swing trading.

La teva tasca és generar un informe d'anàlisi fonamental estructurat que acompanyi el senyal de trading detectat.

DADES DEL MERCAT ACTUALS (FRESCUES):
Símbol: {symbol}
Preu actual: {current_price}
Màxim recent ({lookback_days} dies): {period_high}
Mínim recent ({lookback_days} dies): {period_low}
Caiguda: {drop_pct}% | Rebot: {rebound_pct}%
Capitalització: {market_cap} B USD
Volum mitjà: {volume} M
PER (Trailing): {per}
EPS (Forward): {eps}
Dividend Yield: {dividend_yield}%
Propers Resultats: {next_earnings}

CONEIXEMENT TEÒRIC I CRITERIS DE L'USUARI (RAG):
{user_knowledge}

---
INSTRUCCIONS D'ESTRUCTURA:
Genera l'informe exactament amb aquests punts. És CRUCIAL que etiquetis cada origen de dades:

1. Resum Executiu i Puntuació (DADA CONTEXTUAL/SINTÈTICA):
   - Fundamental Score: [0-100]
   - Nivell de Risc Fonamental: [Baix / Mitjà / Alt / Crític]
   - Tesi en una frase.

2. Calendari de Riscos i Catalitzadors (DADA FRESCUA):
   - Pròxims Earnings: {next_earnings} (Alerta si és en < 7 dies).
   - Data Ex-Dividend: {dividend_yield}% (Dividend actual).

3. Salut Financera i Valoració (MESCLA DADES):
   - EPS: {eps} i PER: {per} (DADA FRESCUA).
   - Salut General, Deute i Marges (DADA CONTEXTUAL basada en el model Gemini: Avalua segons el teu coneixement del ticker).

4. Flux de "Diners Intel·ligents" (DADA CONTEXTUAL):
   - Institutional Ownership, Insider Trading i Sentiment d'analistes. 
   - (Aquesta secció es basa exclusivament en dades d'entrenament del model, no en temps real).

5. Context Sectorial (DADA CONTEXTUAL):
   - Força Relativa del Sector i Correlacions macro.

6. Resum Final i Veredicte:
   - Punts a favor i Punts en contra.
   - Veredicte Fonamental: [APROVAT / CAUTELA / DESCARTAT].

---
LÒGICA CRÍTICA:
* Si les dades actuals són dolentes malgrat el gràfic, sigues cautelós.
* Si el context RAG diu que no vols invertir en aquesta empresa, el veredicte ha de ser DESCARTAT.
* Respon sempre en {language}.

---
AVÍS DE TRANSPARÈNCIA AL FINAL DE L'INFORME (en {language}):
Afegeix sempre una nota indicant que les seccions marcades com a 'CONTEXTUAL' es basen en el coneixement del model d'IA i poden no reflectir canvis corporatius d'última hora.
""")
        
        formatted_prompt = prompt.format(
            symbol=symbol,
            strategy_name=strategy_name,
            current_price=metrics.get("current_price", current_price),
            tech_reason=tech_reason,
            user_knowledge=user_knowledge,
            lookback_days=metrics.get("lookback_days", "?"),
            period_high=metrics.get("period_high", "?"),
            period_low=metrics.get("period_low", "?"),
            drop_pct=round(metrics.get("drop_pct", 0), 2) if metrics.get("drop_pct") else "?",
            rebound_pct=round(metrics.get("rebound_pct", 0), 2) if metrics.get("rebound_pct") else "?",
            market_cap=round(metrics.get("market_cap", 0), 2) if metrics.get("market_cap") else "?",
            volume=round(metrics.get("volume", 0), 2) if metrics.get("volume") else "?",
            per=metrics.get("per", "N/A"),
            eps=metrics.get("eps", "N/A"),
            dividend_yield=metrics.get("dividend_yield", "N/A"),
            next_earnings=metrics.get("next_earnings", "N/A"),
            language=language
        )
        
        try:
            response = self.llm.invoke(formatted_prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error a l'invocar LLM per reports: {e}")
            return f"Error des de l'IA per a generar l'informe ({e}). Considereu si la API Key de Google és vàlida."
