# 🚀 Full de Ruta: Futures Millores a Discutir

Aquest document recull idees, reflexions crítiques i possibles funcionalitats per al futur de l'Assistent d'Inversió.

## 📈 Educació i Aprenentatge (Principiant)
Seguint la reflexió sobre l'usuari amb "nul·la idea" d'invertir:

### Glosari de Conceptes Financers
- **Idea**: Enllaçar conceptes tècnics (PER, EPS, Dividend Yield) a definicions externes (Wikipedia/Investopedia).
- **Reflexió**: Evitar el "soroll visual" de massa enllaços blaus dins l'informe. 
- **Proposta**: Crear una secció de "Llegenda Financera" al final de l'informe o una pestanya de "Diccionari de l'Inversor" fixa a l'App.

### Gestió del Risc i Tamany de Posició
- **Problema**: L'usuari pot arruïnar-se si no sap quants diners posar en cada operació (Position Sizing).
- **Proposta**: Afegir una calculadora de "Risc per Operació" que suggereixi quantes accions comprar segons el preu actual i un *Stop Loss* tècnic.

---

## 🛠️ Funcionalitats d'Anàlisi

### Informe "A la Carta" (On-Demand Report)
- **Idea**: Poder escriure un Ticker qualsevol (ex. "TSLA") i demanar un informe immediat sense esperar que l'Escàner el detecti com a oportunitat.
- **Requereix**: Una secció de "Cerca Directa" que descarregui dades fonamentals i tècniques al moment.

### Filtratge per Mercat a l'Historial
- Ara que guardem el camp `market`, seria útil poder filtrar la taula d'Historial per veure només oportunitats del NASDAQ, o només de l'IBEX35.

---

## 🏗️ Reflexions sobre el Model d'IA
- **Dualitat de Dades**: Mantenir sempre la distinció entre **DADA FRESCUA** (actual de Python) i **DADA CONTEXTUAL** (model de l'IA).
- **RAG Ètic**: Fomentar l'ús de la "Llista Negra" per a perfils d'inversió amb valors personals forts.
