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
            model="gemini-1.5-flash-latest", 
            temperature=0.2,
            api_key=api_key if api_key else None,
            google_api_key=api_key if api_key else None
        )
        self.rag = RAGEngine()
        
    def generate_report(self, symbol: str, strategy_name: str, tech_reason: str, current_price: float, metrics: dict = None) -> str:
        """Agrupa el coneixement RAG amb la troballa tècnica per oferir un resum."""
        
        # Consultem a la bdd de coneixement del RAG quins criteris té l'usuari
        # o consells generals sobre swing trading i l'estratègia en concret.
        user_knowledge = self.rag.similarity_search(f"Criterios de inversión y factores de riesgo para {strategy_name} en accions", k=3)
        
        # Assegurar per defecte diccionari buit per metrics
        metrics = metrics or {}
        
        prompt = PromptTemplate.from_template("""
Ets un analista professional de mercats especialitzat en swing trading.

Analitza la següent oportunitat detectada automàticament per un sistema d'escaneig de mercat.

DADES
Símbol: {symbol}
Preu actual: {current_price}
Màxim recent ({lookback_days} dies): {period_high}
Mínim recent ({lookback_days} dies): {period_low}
Caiguda des del màxim: {drop_pct} %
Rebot des del mínim: {rebound_pct} %
Capitalització de mercat: {market_cap} B USD
Volum mitjà (10 dies): {volume} M accions

Coneixement teòric proveït per l'usuari recuperat de la seva base de dades (RAG Context): 
{user_knowledge}

---

INSTRUCCIONS
Explica l'oportunitat de forma clara i estructurada.
Has d'analitzar:
* què ha passat recentment amb el preu
* si el patró encaixa amb un "Buy the Dip"
* quins riscos existeixen (usant també el RAG Context)
* la qualitat del senyal detectat

---

FORMAT DE RESPOSTA

📊 Context de mercat
(explicació del moviment recent del preu)

📉 Anàlisi del dip
(explicació de la caiguda i el rebot)

⚠️ Factors de risc
(llista de riscos potencials)

⭐ Qualitat del senyal
(Feble / Moderat / Fort amb explicació)

🧠 Conclusió de l'analista
(resum breu de l'oportunitat en 2 o 3 frases)

---

IMPORTANT
L'anàlisi ha de ser clara, professional i breu. Respon en català.
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
            volume=round(metrics.get("volume", 0), 2) if metrics.get("volume") else "?"
        )
        
        try:
            response = self.llm.invoke(formatted_prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error a l'invocar LLM per reports: {e}")
            return f"Error des de l'IA per a generar l'informe ({e}). Considereu si la API Key de Google és vàlida."
