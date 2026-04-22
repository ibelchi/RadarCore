# Desplegament de RadarCore al Núvol

Aquesta guia detalla com posar el RadarCore en producció utilitzant Streamlit Community Cloud (o solucions similars tipus Railway, Heroku o Render) de forma segura i protegint el teu entorn.

## 1. Prerequisits

1. Compta de **GitHub** amb el repositori actualitzat.
2. Un compte gratuït a [Streamlit Community Cloud](https://share.streamlit.io).
3. (Opcional) Una API Key de **Google Gemini** per als informes interactius (RAG).

## 2. Passos de Desplegament (Streamlit Cloud)

1. Accedeix a `share.streamlit.io` i registra't connectant el teu perfil de GitHub.
2. Fes clic a **"New app"**.
3. Selecciona el teu repositori (`radarcore` o similar), la branca `main`, i marca `app.py` com a "Main file path".
4. **NO cliquis a 'Deploy' encara**. Clica al botó inferior que diu **"Advanced settings"** (o en la icona d'engranatge de "Secrets").

## 3. Gestió de Secrets i Contrasenyes

Per tal que l'aplicatiu pugui executar-se de manera protegida *només* per a tu, has d'establir la configuració al núvol, ja que has observat que l'arxiu `.streamlit/secrets.toml` s'ha inclòs al `.gitignore` i no es va pujar.

Dins de l'apartat de **Secrets** a la web de Streamlit on-Deploy (o des de *Settings -> Secrets* si l'has llançat per error), copia aquest text fix:

```toml
[passwords]
# Modifica aquesta contrasenya per la teva pròpia!
admin = "CANVIA_AQUESTA_PASSWORD"

# Això forçarà que l'aplicatiu bloquegi la interfície si no passes la password.
IS_CLOUD_DEPLOYMENT = "true"
```

*Opcionalment, si tens claus de Google, afegeix també `GOOGLE_API_KEY = "la_teva_clau"` allà mateix.*

**Opcions Cloud vs Local:**
L'aplicació conté un algoritme `is_cloud()` incrustat a l'inici d'`app.py` que detectarà automàticament on ets. A l'ordinador local no es demanarà mai cap contrasenya. A Streamlit Sharing, o quan `IS_CLOUD_DEPLOYMENT = "true"`, et bloquejarà fins no validar el secret d'autorització.

## 4. Opcions UI Post-Desplegament

Recordeu que **RadarCore** ve carregat amb un Selector (`Toggle`) lateral sota anomenat "Mode d'Anàlisi". 
Quan et trobis al núvol i executis fons llargs:

* **Mode Automàtic**: Escanejarà l'S&P 500 complet, el que pot sobrecarregar-se si Yahoo repeteix filtres per excés de peticions de xarxa (429 Rate Limit error).
* **Mode Watchlist**: Es cenyirà exclusivament a la teva curació manual privada a la taula de SQLite. Aquesta és la configuració més segura i ràpida un cop al servidor cloud. Si escanegeu llibre obert recomanem processament batch des de local.
