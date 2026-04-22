# RadarCore — Guia Completa per a Principiants
### De zero a entendre el swing trading i com usar el programari

> **Avís important:** Aquest document és exclusivament educatiu. RadarCore és una eina d'aprenentatge i anàlisi tècnica. Res del que trobaràs aquí constitueix consell financer. Invertir comporta risc de pèrdua de capital. Consulta sempre un professional regulat abans de prendre decisions financeres reals.

---

## Com usar aquesta guia

No cal que llegeixis tot d'un cop. Està estructurada com un recorregut: comença des del principi si no saps res de finances, o ves directament a la secció que t'interessa si ja tens alguna base. Cada concepte important apareix en **negreta** la primera vegada que es menciona i s'explica immediatament amb exemples del món real.

---

# PART 1 — El món de les inversions, explicat des de zero

## Capítol 1: Per què la gent inverteix?

Imagina que tens 1.000€ guardats al matalàs. Al cap d'un any, segueixen sent 1.000€. Però els preus han pujat un 3% (el pa, la llum, el lloguer). En termes reals, aquells 1.000€ ara valen menys: amb ells pots comprar menys coses que fa un any.

Això es diu **inflació**: la pèrdua de poder adquisitiu del diner amb el temps. És l'enemic silenciós dels estalvis inactius.

La gent inverteix per intentar que els seus diners creixin a un ritme superior a la inflació. En lloc d'un matalàs, posen els diners a treballar.

### Les tres grans opcions d'inversió

**1. Renda fixa (bons, dipòsits):** Li deixes els diners a un banc o a un govern a canvi d'un interès pactat. Risc baix, rendiment baix. Exemple: un dipòsit al 2% anual.

**2. Renda variable (accions):** Compres una petita part d'una empresa. Si l'empresa va bé, el valor de la teva part puja. Si va malament, baixa. Risc més alt, però potencial de rendiment molt superior.

**3. Actius alternatius (immobles, or, criptomonedes):** Cadascun amb les seves regles pròpies.

RadarCore treballa exclusivament amb **renda variable**, concretament amb **accions** de grans empreses cotitzades en borsa.

---

## Capítol 2: Què és una acció i com funciona la borsa?

### L'acció com a tros d'empresa

Quan una empresa gran vol créixer i necessita diners, en lloc de demanar un préstec al banc pot decidir "vendre trossos de si mateixa" al públic. Cada tros és una **acció** (en anglès, *stock* o *share*).

**Exemple real:** Apple té aproximadament 15.000 milions d'accions en circulació. Si en compres una, ets propietari d'una quinzeavamilionèsima part d'Apple. Poc? Sí. Però si Apple val més demà, el teu tros també val més.

### El ticker: el nom codi de cada empresa

Cada empresa cotitzada té un codi abreujat únic que s'usa a tot el món financer. S'anomena **ticker symbol** o simplement **ticker**.

| Empresa | Ticker |
|---|---|
| Apple Inc. | AAPL |
| Microsoft | MSFT |
| Visa Inc. | V |
| Inditex (IBEX) | ITX.MC |

A RadarCore veuràs sempre els tickers a la columna **Symbol** de la taula de resultats, i pots clicar-los per anar directament a Yahoo Finance.

### La borsa com a mercat

La **borsa** (o mercat de valors) és simplement el lloc on compradors i venedors d'accions es troben. Avui és electrònica: no hi ha cap sala física amb gent cridant. Cada segon, milions d'ordres de compra i venda es creuen automàticament.

El **preu** d'una acció en cada moment és simplement el darrer preu al qual algú va estar disposat a comprar i un altre a vendre. Si avui més gent vol comprar Apple que vendre, el preu puja. Si hi ha més venedors que compradors, baixa.

### OHLCV: les cinc dades de cada dia

Per a cada acció i cada dia de mercat, es registren cinc dades fonamentals. Les trobaràs a qualsevol gràfic professional i a RadarCore:

- **O (Open):** Preu d'obertura. El primer preu del dia.
- **H (High):** Preu màxim assolit durant la sessió.
- **L (Low):** Preu mínim de la sessió.
- **C (Close):** Preu de tancament. L'últim preu del dia. És el més important i el que RadarCore usa per a la majoria de càlculs.
- **V (Volume):** Nombre d'accions que han canviat de mans aquell dia.

**Per què importa el volum?** Un moviment de preu amb volum alt és molt més significatiu que el mateix moviment amb volum baix. Si una acció puja un 5% però poquíssima gent ha comprat, pot ser soroll. Si puja un 5% amb el doble de volum habitual, és una senyal de convicció real del mercat.

---

## Capítol 3: Els índexs de referència

Seguir 500 empreses una per una seria impossible. Per això existeixen els **índexs de mercat**: cestes d'empreses que representen un conjunt més ampli.

### Els principals índexs que usa RadarCore

**S&P 500 (USA):** Les 500 empreses més grans dels Estats Units per capitalització de mercat. És el termòmetre de l'economia americana i, per extensió, de l'economia global. Inclou Apple, Microsoft, Amazon, NVIDIA, JPMorgan, etc.

**NASDAQ 100 (USA):** Les 100 empreses no financeres més grans del NASDAQ, la borsa tecnològica americana. Molt concentrat en tech: Apple, Microsoft, NVIDIA, Meta, Alphabet, Tesla...

**IBEX 35 (Espanya):** Les 35 empreses més líquides de la borsa espanyola. Santander, Inditex, BBVA, Iberdrola, Telefónica...

**DAX 40 (Alemanya):** Les 40 principals empreses alemanyes. SAP, Siemens, Volkswagen, BMW, Allianz...

**EuroStoxx 50 (Europa):** Les 50 empreses més grans de la zona euro, de tots els sectors i països.

**Nikkei 225 (Japó):** 225 empreses líders japoneses. Toyota, Sony, SoftBank...

**Nifty 50 (Índia):** Les 50 empreses principals de la borsa de Bombai.

### Per què l'S&P 500 és el "termòmetre global"?

Quan l'S&P 500 cau fortament, quasi tot el món financer ho nota. Els inversors institucionals (fons de pensions, bancs, asseguradores) mouen bilions de dòlars i quan venen accions americanes, també venen en altres mercats per cobrir les pèrdues. Per això RadarCore usa sempre l'S&P 500 com a referència per detectar si una caiguda és global o específica d'una empresa.

### Capitalització de mercat: la mida d'una empresa

La **capitalització de mercat** (*market cap*) és el valor total d'una empresa en borsa. Es calcula multiplicant el preu d'una acció per totes les accions existents.

```
Market Cap = Preu per acció × Nombre total d'accions
Exemple: Apple a $200 × 15.000M accions = ~$3 bilions
```

| Categoria | Market Cap | Exemples |
|---|---|---|
| Mega-cap | > $200B | Apple, Microsoft, NVIDIA |
| Large-cap | $10B - $200B | Visa, McDonald's, Nike |
| Mid-cap | $2B - $10B | moltes empreses sòlides |
| Small-cap | $300M - $2B | empreses petites |
| Micro-cap | < $300M | molt especulatives |

RadarCore per defecte només analitza empreses amb **Min Mkt Cap ≥ $10B** per evitar el soroll i la manipulació de les empreses petites.

---

# PART 2 — Estratègies d'inversió: com guanya la gent?

## Capítol 4: Les tres filosofies principals

### Buy & Hold (Comprar i mantenir)
La filosofia de Warren Buffett. Compres accions d'empreses excel·lents i les guardes durant anys o dècades sense vendre. Funciona molt bé per a qui té paciència i horitzó llarg. El problema: requereix molt temps i és emocionalment difícil aguantar caigudes del 40-50% sense vendre.

### Day Trading (Operar intradiari)
Compres i vens el mateix dia, aprofitant moviments de minuts o hores. Requereix molt de temps, accés a plataformes professionals, capital important i una tolerància al risc extrema. Estudis mostren que la gran majoria de day traders perden diners a llarg termini.

### Swing Trading (L'estratègia de RadarCore)
El terme mig. **Swing trading** significa aprofitar els "oscil·lacions" (*swings*) del preu d'una acció en un horitzó de **dies a setmanes** (típicament 2-6 setmanes). No estàs davant la pantalla tot el dia, però tampoc compres i oblides durant anys.

La idea central: els preus de les accions no van en línia recta. Pugen, baixen, es consoliden, tornen a pujar. Un swing trader intenta detectar quan una acció ha baixat per motius temporals i comprar-la abans que torni a pujar.

---

## Capítol 5: L'estratègia "Buy the Recovery" de RadarCore

### La intuïció darrere l'estratègia

Imagina una empresa sòlida, diguem Visa (la de les targetes de crèdit). Un trimestre té resultats lleugerament per sota de les expectatives dels analistes, o hi ha un moment de pessimisme general al mercat. El preu cau un 20% en poques setmanes.

Però Visa segueix processant milers de milions de transaccions cada dia. El seu negoci no ha canviat fonamentalment. Aquella caiguda del 20% és una **oportunitat temporal** per comprar una empresa sòlida a preu de descompte.

Això és el que busca RadarCore: empreses que han caigut per motius temporals i que ja mostren senyals d'haver tocat terra i estar recuperant-se.

### Per què "Buy the Recovery" i no "Buy the Dip"?

"Buy the Dip" (comprar la caiguda) seria comprar mentre l'acció segueix baixant. El problema és que ningú sap quan tocarà terra. Podries comprar a -20% i seguir baixant fins a -60%.

"Buy the Recovery" espera la confirmació: l'acció ja ha tocat el mínim i ha rebotant una mica. Perds els primers centímetres de la recuperació, però confirmes que el terra ja és aquí. És menys emocionant però molt més disciplinat.

### El patró que busquem: la forma de "V" o "L"

Visualment, l'estratègia busca dos patrons principals:

**Patró V (V-RECOVERY):**
```
     Màxim
    /       \
   /         \         Recuperació
  /           \       /
 /             \ Mín /
```
Caiguda ràpida i forta seguida d'una recuperació igualment ràpida. Alta volatilitat. Pot ser molt rendible però també arriscat.

**Patró L (L-BASE):**
```
     Màxim
    /       \
   /         \___________  ← Base lateral (acumulació)
  /                       \
 /                         Recuperació lenta però sòlida
```
Caiguda seguida d'un període de consolidació horitzontal. Els inversors institucionals "acumulen" accions sense pressa mentre el preu es manté estable. Quan finalment trenca a l'alça, sol ser un moviment més sòlid.

**Per a RadarCore, L-BASE és considerat de més qualitat que V-RECOVERY** perquè la base lateral suggereix que els grans compradors s'estan posicionant discretament.

---

# PART 3 — Conceptes tècnics fonamentals

## Capítol 6: El Drawdown, el Rebot i la Recuperació

### Drawdown: quant ha caigut una acció

El **drawdown** és la caiguda percentual des d'un màxim fins a un mínim posterior. És la mesura del "dolor" que ha sofert una acció.

```
Càlcul del Drawdown:
Màxim recent: $100
Mínim posterior: $75
Drawdown = (100 - 75) / 100 = 25%
```

A RadarCore, la columna **Drop %** mostra exactament aquest valor: quant ha caigut l'acció des del seu màxim dels últims X dies (configurable amb el paràmetre *Historical Window*) fins al seu mínim.

**Per exemple:** Si Visa tenia un màxim de $360 i va caure fins a $290, el Drop % seria:
```
(360 - 290) / 360 = 19.4%
```

### El Rebot: primera senyal de vida

El **rebot** (*rebound*) mesura quant ha pujat l'acció des del seu mínim fins al preu actual. És la confirmació que la caiguda s'ha aturat.

```
Càlcul del Rebound:
Mínim: $75
Preu actual: $82
Rebound = (82 - 75) / 75 = 9.3%
```

A RadarCore, la columna **Rebound %** mostra aquest valor. El paràmetre *Minimum Rebound (%)* (per defecte 2%) filtra les accions que encara no han mostrat cap senyal de recuperació.

### Per què RadarCore exigeix un rebot mínim?

Per evitar comprar "ganivets que cauen". Si una acció ha baixat un 30% però segueix baixant, el rebot és 0%. No hi ha confirmació de gir. RadarCore espera que el preu hagi demostrat que el mínim ja ha quedat enrere.

---

## Capítol 7: La Caiguda Idiosincràtica vs. la Caiguda Sistèmica

Aquesta distinció és **la més important de tota l'estratègia**. Entenent-la triplicaràs la qualitat de les teves decisions.

### Caiguda Sistèmica: el mercat explica la caiguda

Si el mercat sencer (l'S&P 500) cau un 20%, és normal que moltes empreses caiguin un 20-25%. En aquest cas, la caiguda no és culpa de l'empresa: és el context global. Comprar en un entorn de caiguda general és arriscat perquè no hi ha un "terra" clar.

### Caiguda Idiosincràtica: l'empresa cau sola

Si el mercat puja un 5% però una empresa cau un 25%, aquella caiguda és **idiosincràtica** (és a dir, específica d'aquella empresa). Pot ser per resultats decebedors, canvi de directiu, problema regulatori temporal o simplement por exagerada dels inversors.

Aquestes caigudes idiosincràtiques en empreses fonamentalment sòlides són les **millors oportunitats de swing trading**, perquè:
1. L'empresa no ha caigut perquè el món estigui malament.
2. Quan la por passa, el preu tendeix a recuperar-se cap al nivell anterior.

**A RadarCore veuràs:** `✅ Idiosyncratic drop (+16.6% vs SPY)` als resultats de l'escaneig. Significa que l'empresa ha caigut un 16.6% MÉS que el mercat, confirmant que la seva caiguda és específica seva.

### Com ho calcula RadarCore?

```
Caiguda relativa = Drawdown de l'empresa - Drawdown del SPY
                   en el mateix període de temps

Si Caiguda relativa > 5% → Caiguda idiosincràtica ✅
Si Caiguda relativa ≤ 5% → Caiguda sistèmica ⚠️
```

---

## Capítol 8: Mitjanes Mòbils (EMA)

### Què és una mitjana mòbil?

Imagina que vols saber si una persona té febre. No mires la temperatura d'un segon: la mesures al llarg del temps. Les **mitjanes mòbils** fan el mateix amb el preu d'una acció: suavitzen el soroll diari per mostrar la tendència real.

Una **EMA (Exponential Moving Average)** és una mitjana mòbil exponencial que dona més pes als preus recents que als antics. Reacciona més ràpid als canvis que una mitjana simple.

### EMA 50 i EMA 200: les més importants

**EMA 50:** La mitjana dels últims 50 dies de cotització. Representa la tendència a mitjà termini.

**EMA 200:** La mitjana dels últims 200 dies. Representa la tendència a llarg termini. Molts inversors institucionals consideren que una acció és "en tendència alcista" quan cotitza per sobre de la seva EMA 200.

### La Cruïlla Daurada i la Cruïlla de la Mort

**Cruïlla Daurada (Golden Cross):** Quan l'EMA 50 supera per sobre l'EMA 200. Senyal alcista fort. Molts algoritmes automàtics compren en aquest moment.

**Cruïlla de la Mort (Death Cross):** Quan l'EMA 50 cau per sota l'EMA 200. Senyal baixista.

```
Preu > EMA50 > EMA200 → Tendència alcista sòlida (RISE)
Preu < EMA50 < EMA200 → Tendència baixista (DESCENDING)
Preu oscil·la al voltant de EMA50 → Possible SWING o LATERAL
```

---

## Capítol 9: RSI — L'índex de força relativa

### Què mesura el RSI?

El **RSI (Relative Strength Index)** és un indicador que mesura la velocitat i magnitud dels moviments de preu recents en una escala de 0 a 100. El van crear als anys 70 i segueix sent un dels més usats del món.

**Interpretació clàssica:**
- RSI > 70 → L'acció pot estar **sobrecomprada** (ha pujat massa ràpid, possible correcció)
- RSI < 30 → L'acció pot estar **sobrevenda** (ha baixat massa ràpid, possible rebot)
- RSI entre 40-60 → Zona neutral

**Com l'usa RadarCore:** El RSI al mínim del suelo és un confirmador de qualitat. Si una acció arriba al seu mínim amb RSI < 30 i després el RSI comença a recuperar-se cap a 40-50, és una senyal que la sobrevenda s'ha esgotat i que el rebot pot tenir continuïtat.

**Important:** El RSI per si sol mai és suficient per prendre decisions. És un confirmador, no un predictor.

---

## Capítol 10: ATR — La volatilitat real de cada acció

### Què és l'ATR?

L'**ATR (Average True Range)** mesura quant es mou una acció de mitjana cada dia. No diu la direcció (si puja o baixa), sinó la magnitud típica del moviment.

**Exemple:**
- Si Apple té un ATR de $5, significa que de mitjana cada dia el preu oscil·la $5 entre el mínim i el màxim.
- Si una empresa de $10 té un ATR de $2, és enormement volàtil (20% diari!).

### Per a què serveix l'ATR a RadarCore?

**Per calcular el Stop Loss de manera intel·ligent.** En lloc de posar un stop fix (per exemple, "venc si baixa un 8%"), usem l'ATR per adaptar el stop a la volatilitat real de cada acció:

```
Stop Loss = Mínim del sòl - (ATR × 1.5)
```

Per a una acció molt volàtil, el stop serà més ampli (per evitar ser "esquitxat" per moviments normals). Per a una acció tranquil·la, el stop serà més estret.

---

## Capítol 11: El concepte de Pivot i l'Algorisme RDP

### Què és un pivot?

Un **pivot** (o punt de gir) és un màxim local o un mínim local en el gràfic d'una acció. En un gràfic de dos anys, pot haver-hi desenes de moviments, però els pivots són els "moments clau": els pics i les valls estructurals del preu.

- **Peak (Pic, marcat com P1, P2...):** Un màxim local, des d'on el preu va girar a la baixa.
- **Trough (Vall, marcat com T1, T2...):** Un mínim local, des d'on el preu va girar a l'alça.

### L'Algorisme RDP: filtrar el soroll del mercat

El mercat financer és ple de soroll. Cada dia el preu puja i baixa per centenars de motius trivials. El repte és separar el moviment meaningful (estructural) del soroll irrellevant.

**RDP (Ramer-Douglas-Peucker)** és un algorisme matemàtic dissenyat originalment per simplificar línies en cartografia digital. Si tens una costa amb mil petites badies, el RDP t'ajuda a dibuixar-la amb 20 punts essencials en lloc de 1.000, mantenint la forma global.

RadarCore l'aplica al preu d'una acció: simplifica els dos anys de cotització a entre 6 i 16 punts clau (els pivots), eliminant el soroll de dies concrets per revelar l'estructura real del moviment.

**Visualment a RadarCore:** A la vista "Pivots" del gràfic, veus la línia discontínua blanca (els pivots RDP) sobre la línia daurada (el preu real). La línia blanca et mostra la "narrativa" de l'acció, sense soroll.

---

## Capítol 12: Les Eres — la narrativa del preu

### Segments i Eres

Un cop l'algorisme RDP ha identificat els pivots, RadarCore classifica cada segment entre dos pivots consecutius:

- **UP:** El segment puja més d'un 3%.
- **DOWN:** El segment baixa més d'un 3%.
- **FLAT:** El canvi és inferior al 3% (consolidació lateral).

Una seqüència de segments és el que RadarCore anomena les **Eres** d'una acció. La seqüència d'eres és la "história" de l'acció explicada en paraules simples.

**Exemples de seqüències:**
```
UP-UP-UP               → Tendència alcista clara (RISE)
DOWN-DOWN-UP-DOWN-UP   → Oscil·lació amb potencial de swing (SWING)
DOWN-FLAT-FLAT-FLAT    → Caiguda i base lateral (L-BASE / LATERAL)
UP-DOWN-UP-DOWN        → Swing regular (SWING)
```

**A la UI veuràs:** `Last segment FLAT (-0.6%) · Second-to-last UP (+3.8%) · Recovery at 24% of peak-valley range · Valley 0 days ago`

Això et diu: l'últim moviment estructural és lateral (consolidació), l'anterior va ser una pujada del 3.8%, i l'acció ha recuperat el 24% del camí des del seu mínim fins al màxim previ.

---

# PART 4 — El sistema de classificació de RadarCore

## Capítol 13: Els Cinc Buckets (Categories)

RadarCore classifica cada acció en una de les cinc categories estructurals. No és un sistema binari (oportunitat sí/no), sinó una classificació de quin "estat" es troba l'acció.

### SWING 🔄
L'acció mostra un patró d'oscil·lació: ha pujat, ha baixat, i potencialment tornarà a pujar. És el patró més buscant per a swing trading. La condició essencial és que hagi caigut prou des d'un màxim recent i hagi demostrat que el mínim ja ha quedat enrere amb un rebot inicial.

**Subtipus de SWING:**
- **SWING → BREAKOUT:** L'acció acaba de superar el seu últim màxim local significatiu. Senyal de força, però cal vigilar que no sigui una trampa.
- **SWING → PULLBACK:** Desprès d'un breakout, l'acció ha retrocedit una mica. Si el retrocés es manté per sobre del suport, pot ser una segona oportunitat d'entrada millor que el breakout original.
- **SWING → RETEST:** L'acció ha tornat a testar el nivell del seu mínim anterior (sense trencar-lo). Si el suport aguanta, és una confirmació molt potent.

### RISE 📈
L'acció està en una tendència alcista clara i sostinguda. No hi ha grans oscil·lacions: simplement puja de manera consistent. Per a swing trading pur és menys interessant (ja no té la caiguda prèvia), però indica una empresa amb fort momentum que pot seguir pujant.

**Subtipus de RISE:**
- **RISE → BREAKOUT:** Superant nous màxims anuals. Molt fort, però pot estar "massa car".
- **RISE → PULLBACK:** Retrocés dins d'una tendència alcista. Pot ser un punt d'entrada per als que creuen en la continuació de la tendència.

### LATERAL 〰️
L'acció no fa res: es mou en un rang estret sense tendència clara ni amunt ni avall. Pot estar "acumulant" (preparant-se per pujar) o simplement dormida. Per si sol no és una senyal d'acció, però si ve precedit d'una caiguda és el que RadarCore anomena **L-BASE**.

### HIGHS 🔝
L'acció cotitza prop del seu màxim recent. Alt risc de correcció. RadarCore la marca per informació però no la considera una oportunitat de "Buy the Recovery" (no hi ha caiguda prèvia des d'on recuperar-se).

### DESCENDING 📉
L'acció està en una tendència baixista clara. El mercat li dona l'esquena. Evitar-la per a compres. Pot ser interessant per a vendes en curt (*short selling*), però això és una estratègia avançada fora de l'abast d'aquesta guia.

---

## Capítol 14: Les Fases de Trazo — On ets dins del recorregut?

Saber que una acció és SWING és útil, però no et diu si estàs entrant al principi de la recuperació o quan ja s'ha mogut molt. Les **fases** responen exactament aquesta pregunta.

### La fórmula del Progress

```
Progress % = (Preu actual - Mínim del Pivot) 
             / (ATH 3 anys - Mínim del Pivot) × 100
```

Aquesta fórmula mesura quant del recorregut possible ja s'ha recorregut. Si el màxim dels últims 3 anys és $100 i el mínim del pivot va ser $60, i ara l'acció és a $70:

```
Progress = (70 - 60) / (100 - 60) × 100 = 25%
```

L'acció ha recorregut el 25% del camí possible entre el seu mínim i el seu màxim anterior.

### Les quatre fases

**🟢 VALLEY (< 20% de progress)**
L'acció acaba de rebotar del mínim. Tens la màxima distància per recórrer fins al màxim anterior (el màxim upside possible). Però també el màxim risc: no saps si el rebot és real o un dead cat bounce (rebot temporal abans de continuar baixant).

*Quan és bona opció:* Quan el patró és L-BASE, el volum acompanya i la caiguda és idiosincràtica.

**🟡 MID (20%-65% de progress)**
La recuperació ja porta un cert camí. La tendència alcista comença a estar confirmada pels mercats. Et queda recorregut fins al màxim anterior però has perdut la part inicial. És el **"sweet spot"** que Trazo i RadarCore consideren el millor equilibri entre risc i oportunitat.

*Quan és bona opció:* Quasi sempre. La relació risc/recompensa és la millor d'aquestes quatre.

**🟠 MATURE (65%-85% de progress)**
L'acció ha recuperat la major part del terreny perdut. El recorregut restant fins al màxim és limitat. El risc d'una nova correcció és elevat perquè molts inversors que van comprar a preus alts ara tenen l'oportunitat de "recuperar el que havien perdut" i venen.

*Quan tenir cura:* Observa el volum. Si la pujada es fa amb volum decreixent, pot ser una trampa.

**🔴 LATE (> 85% de progress)**
L'acció ja ha tornat quasi al màxim anterior. Poc marge de pujada addicional, molta pressió vendedora. RadarCore la mostra per informació però no la considera candidata per a una nova entrada.

### Upside: quant li queda per pujar

A la taula de resultats veuràs **Upside 3Y** i **Upside 5Y**. Aquests percentatges indiquen quant podria pujar l'acció si tornés al seu màxim dels últims 3 o 5 anys.

```
Upside 3Y = (ATH 3 anys - Preu actual) / Preu actual × 100
```

Una acció amb Phase VALLEY i Upside 3Y del 40% és molt més interessant que una amb Phase LATE i Upside 3Y del 5%.

---

## Capítol 15: La Confiança (Confidence) — com es calcula?

El **Confidence %** que veus a la columna **Conf.** és una puntuació composta que RadarCore calcula per ordenar les oportunitats de millor a pitjor. No és màgia: és la suma ponderada de quatre factors.

### Les quatre components de la Confiança

**1. Qualitat de la Caiguda (30% del total)**
Com més propera al 40% sigui la caiguda real (de màxim a mínim), major puntuació. Una caiguda del 20% rep menys punts que una del 35%. Perquè caigudes majors impliquen "descomptes" majors i potencial de recuperació superior.

```
Puntuació = min(Drop% / 40%, 1.0) × 0.30
```

**2. Qualitat del Rebot (20% del total)**
Un rebot entre el 5% i el 10% des del mínim és el més valorat. Massa poc (<2%) no confirma el gir. Massa (>15%) pot significar que ja hem perdut la millor entrada.

```
Puntuació = min(Rebound% / 10%, 1.0) × 0.20
```

**3. Forma del Patró (25% del total)**
- **L-BASE o LATERAL:** Màxima puntuació (0.25). La base lateral suggereix acumulació institucional.
- **V-RECOVERY o SWING:** Puntuació mitja (0.15). La recuperació ràpida és menys predictible.
- **EARLY:** Puntuació baixa (0.05). Massa incipient per confiar.

**4. Context de Mercat (25% del total)**
- **Caiguda idiosincràtica confirmada:** 0.25 punts. La caiguda és específica de l'empresa.
- **Dades de mercat no disponibles:** 0.10 punts. Benefici del dubte.
- **Caiguda sistèmica:** 0 punts. El mercat ho explica tot.

**Exemple pràctic:**
```
MSFT: Drop 26% → 0.195 | Rebound 17% → 0.20 | 
      Patró V-RECOVERY → 0.15 | Idiosincràtica ✅ → 0.25
      
Confidence = (0.195 + 0.20 + 0.15 + 0.25) × 100 = 79.5%
```

---

## Capítol 16: Stop Loss, Targets i el Ratio R/R

### Stop Loss: protegint el capital

El **Stop Loss (SL)** és l'ordre automàtica de venda que posem per limitar les pèrdues si ens equivoquem. No és una derrota: és una part integral de qualsevol estratègia professional.

**Regla fonamental del trading:** Preservar el capital és prioritat absoluta. Una pèrdua del 50% requereix un guany del 100% per recuperar-se. Una pèrdua del 10% només necessita un guany d'l'11%.

```
Stop Loss = Mínim del Pivot - (ATR × 1.5)
```

Usem 1.5 vegades l'ATR perquè el preu pot fer moviments normals dins de la seva volatilitat habitual sense que la tesi d'inversió s'hagi trencat. Si el stop estigués massa ajustat, saltaria per soroll normal.

**El nivell d'invalidació:** Si el preu cau per sota del Stop Loss, la tesi "Buy the Recovery" ja no és vàlida. El preu ha trencat el suport on s'havia format el patró. Sortir ràpid i buscar la propera oportunitat.

### Targets: recollint guanys

**T1 (Target 1 — Objectiu Conservador):**
El primer punt de presa de beneficis. A RadarCore sol estar marcat al voltant del 85% de la distància entre el mínim i el màxim anterior. En aquest punt, molts swing traders venen la meitat de la posició per assegurar guanys i deixen la resta "córrer" cap al T2.

**T2 (Target 2 — Objectiu Ideal):**
El màxim anterior a la caiguda. És l'objectiu natural de "Buy the Recovery": si l'empresa recupera tot el terreny perdut, el preu tornaria a on era abans. En practiques, moltes recuperacions no arriben al 100% però sí al 70-80%.

### El Ratio Risc/Recompensa (R/R)

Aquest és el concepte **més important** per a la supervivència financera a llarg termini.

```
Ratio R/R = (Target - Entrada) / (Entrada - Stop Loss)
```

**Exemple:**
```
Entrada: $100
Stop Loss: $92  → Risc = $8
Target (T2): $125 → Recompensa = $25
Ratio R/R = 25 / 8 = 3.1x
```

Un ratio de 3.1x significa que per cada dòlar que arrisques, pots guanyar 3.1$. RadarCore considera com a mínim acceptable un R/R de 2.0x.

**La màgia del R/R:** Imagina que fas 10 operacions amb R/R de 2x:
- 6 surten malament: perds 6 × $1 = -$6
- 4 surten bé: guanyes 4 × $2 = +$8
- Resultat net: +$2 **sense haver encertat ni la meitat!**

Amb un bon R/R, pots ser rentable fins i tot encertant menys del 50% de les operacions.

---

## Capítol 17: Els Earnings — el risc més important del swing trading

### Què són els Earnings?

Cada trimestre (quatre vegades a l'any), les empreses cotitzades publiquen els seus resultats financers oficials. Ingressos, beneficis, perspectives futures... Aquesta publicació s'anomena **Earnings Report** (informe de resultats).

El mercat sol tenir expectatives sobre els resultats. Si l'empresa les supera → el preu pot pujar un 10-20% en un dia. Si les defrauda → pot caure un 10-20% en un dia.

### Per què els Earnings són perillosos per al swing trading?

Perquè **la direcció del moviment és imprevisible fins a l'últim moment**, inclús per als professionals. Ni l'anàlisi tècnica ni el pattern del gràfic et pot dir si els resultats seran millors o pitjors que les expectatives.

Si tens una posició oberta i surten els Earnings mentre la tens, estàs apostant sense saber ni cara ni creu. Això és especulació pura, no swing trading.

### Com gestiona RadarCore els Earnings?

RadarCore mostra a la UI el badge d'avís:
- **⚠️ EARN Xd (vermell):** Earnings en menys de 14 dies. Risc molt alt. Considera esperar.
- **📅 EARN Xd (groc):** Earnings en 15-30 dies. Avís. Vigila el timing.
- **earn Xd (gris):** Earnings en 31-60 dies. Informació per planificar.

**Estratègia recomanada:** Si una oportunitat té Earnings en menys de 14 dies, tens dues opcions:
1. **No entrar** fins que els Earnings hagin passat (i el preu s'hagi estabilitzat).
2. **Entrar amb posició molt reduïda** (menys del que hi posaries normalment) per limitar l'exposició a la incertesa.

---

# PART 5 — Usar RadarCore pas a pas

## Capítol 18: La Sidebar — configuració global

La **sidebar** (panell lateral esquerre) conté les configuracions globals que afecten com la IA analitza les oportunitats.

**AI Provider:** Tria entre Google Gemini (per defecte i recomanat) o OpenAI (GPT-4o). Afecta la qualitat i l'estil dels informes generats.

**Model:** El model específic dins de cada proveïdor. Per a ús habitual, el model per defecte és suficient.

**API Key Settings:** Si tens les teves pròpies claus d'API, les pots introduir aquí. No és obligatori per a les funcions bàsiques.

**AI Report Language:** L'idioma en el qual la IA redactarà els informes: Català, Castellà o Anglès.

**Analysis Mode:**
- **Automatic mode (ON):** Totes les oportunitats detectades passen automàticament per l'anàlisi avançada de patrons. Recomanat mentre aprens.
- **Automatic mode (OFF):** Activa el Mode Watchlist. Només s'analitzen en profunditat els tickers que tu has seleccionat manualment a la pestanya Watchlist.

**Pre-filter universe:** Activa un filtre addicional que elimina empreses zombie (sense historial de recuperació) i empreses amb liquiditat insuficient. Recomanat tenir-lo desactivat mentre aprens per veure més resultats; activar-lo quan vulguis resultats de més qualitat.

---

## Capítol 19: Pestanya Market Scanner — fent el primer escaneig

Aquesta és la pantalla principal. Aquí configures els paràmetres i llances l'escaneig.

### Seleccionar el Mercat (Market to Scan)

Tria entre els set mercats disponibles:

| Mercat | Recomanat per a... |
|---|---|
| S&P 500 (USA) | Primer aprenentatge. Empreses molt conegudes. |
| NASDAQ 100 (USA) | Interessat en tecnologia |
| IBEX 35 (Spain) | Empreses espanyoles properes |
| DAX 40 (Germany) | Empreses europees industrials |
| EuroStoxx 50 | Diversificació europea |
| Nikkei 225 | Exposició a Japó |
| Nifty 50 | Mercat emergent, Índia |

**Recomanació per a principiants:** Comença amb S&P 500. Les empreses et seran familiars (Apple, Microsoft, Visa...) i hi ha molta informació disponible per aprendre.

### Symbol Limit

Posa 0 per analitzar totes les empreses del mercat, o un número petit (20-50) per fer proves ràpides. Amb 0 i el S&P 500 l'escaneig pot trigar 30-60 segons.

### Strategy Parameters — els sliders de l'estratègia

**Minimum Drop (%) — per defecte 15%:**
Quant ha de haver caigut l'acció des del seu màxim recent. Amb 15%, busques empreses que hagin perdut almenys un 15% del seu valor. Si poses molt alt (>30%), veuràs poques empreses però en situació de "gran descompte". Si poses baix (<10%), veuràs moltes empreses però algunes amb caigudes poc significatives.

*Recomanació inicial:* 15% és un bon punt de partida. En mercats alcistes potser cal baixar a 10%. En mercats baixistes, les oportunitats apareixeran naturalment a 20-30%.

**Historical Window (Days) — per defecte 60:**
En quants dies enrere mirem el màxim de referència. Amb 60 dies, el màxim és el més alt dels últims 2 mesos. Amb 252 dies (un any), el màxim és l'anual. Finestres més llargues detecten caigudes estructurals majors; finestres curtes detecten caigudes recents menors.

*Recomanació inicial:* 60 dies per a swing trading de 2-6 setmanes. 120-252 dies per a posicions de recuperació a llarg termini.

**Minimum Rebound (%) — per defecte 2%:**
El rebot mínim des del mínim que confirma que la caiguda s'ha aturat. Amb 2%, és molt permissiu (qualsevol petit gir). Amb 8-10%, exigeixes una recuperació ja en marxa però et perds l'entrada inicial.

*Recomanació inicial:* 2-5% per capturar oportunitats en fase VALLEY. 5-10% si prefereixes més confirmació i no importa perdre part del moviment inicial.

**Min Mkt Cap (B $) — per defecte $10B:**
Filtra per capitalització de mercat mínima. $10B elimina la majoria de small-caps especulatives. Per als que volen explorar empreses més petites (amb més risc), es pot baixar a $2-5B.

**Min Avg Vol (M) — per defecte 1M accions/dia:**
Volum mitjà mínim. La liquiditat és essencial: necessites poder comprar i vendre sense que el teu ordre mogui el preu. 1M accions/dia és el mínim raonable per a empreses large-cap.

### El botó Run Scan

En prémer **Run Scan**, RadarCore:
1. Descarrega les dades de preu de cada empresa del mercat seleccionat.
2. Aplica el filtre d'univers (si és actiu).
3. Calcula el Drop % i el Rebound % per a cada empresa.
4. Aplica els filtres de Strategy Parameters.
5. Per a les que passen els filtres, executa el PatternClassifier (RDP + Eres + Buckets).
6. Calcula la Fase (VALLEY, MID, MATURE, LATE).
7. Detecta els Earnings pròxims.
8. Guarda els resultats a la base de dades i mostra'ls a la UI.

---

## Capítol 20: Pestanya History & Reports — interpretant els resultats

Aquí és on veus, analitzes i gestiones les oportunitats detectades.

### La taula de resultats

Cada fila és una empresa que ha passat tots els filtres. Les columnes:

**Symbol:** Codi de l'empresa. Clica per anar a Yahoo Finance i veure la seva informació completa.

**Company:** Nom complet de l'empresa.

**Drop %:** La caiguda real des del màxim recent fins al mínim. *Regla pràctica: a més drop, més "descompte" però també més risc que la tesi no es compleixi.*

**Rebound %:** Quant ha pujat des del mínim fins avui. *Un rebound del 5-15% en un VALLEY és ideal. Més del 30% en VALLEY pot ser excessiu (potser ja hem perdut l'entrada).*

**Pattern:** El tipus de patró detectat. Recordatori ràpid:
- SWING / L-BASE / V-RECOVERY → Candidats per a Buy the Recovery
- RISE → Tendència alcista, no és "Buy the Recovery" però pot ser interessant
- LATERAL → Acumulació possible, vigilar
- DESCENDING / HIGHS → Evitar per ara

**Phase:** On estem dins del recorregut. 🟢 VALLEY és el millor moment, 🔴 LATE és massa tard.

**Upside 3Y:** Quant podria pujar si tornés al màxim dels últims 3 anys. Més del 20% és interessant.

**Conf.:** La puntuació composta de qualitat. Ordena per aquesta columna de major a menor per veure les millors oportunitats primer.

**Date:** Quan es va detectar l'oportunitat. Oportunitats de fa molts dies poden haver canviat de situació.

### Els gràfics

Selecciona una o més files i prem **View Charts** per veure la representació visual.

**Vista Mountain:** La línia daurada del preu sobre fons negre. Ideal per veure la tendència global de manera neta.

**Vista Eras:** Zones acolorides que mostren cada segment de l'algorisme RDP:
- Zones verdes → Segments UP
- Zones vermelles → Segments DOWN
- Zones grises → Segments FLAT

**Vista Pivots:** La línia discontínua blanca dels punts clau (P1, P2... pels pics; T1, T2... per les valls) sobre la línia de preu. Et permet veure l'estructura sense soroll.

**Vista Candles:** El gràfic de veles japoneses tradicional (OHLCV complet). Cada vela representa un dia: verda si el preu ha pujat, vermella si ha baixat.

**La capçalera del gràfic** (text petit sobre el gràfic): Et dona informació contextual important com ara `Last segment UP (+3.8%) · Recovery at 24% of peak-valley range · Valley 0 days ago · RETEST`. Llegeix-la sempre com a primer resum.

**El panell Trazo Phase Analysis:** Mostra la Phase, el Progress %, l'Upside 3Y, l'Upside 5Y i el preu del Pivot (el mínim del patró). Usa'l per entendre immediatament on ets dins del recorregut possible.

---

## Capítol 21: Pestanya Watchlist — curant manualment les oportunitats

La **Watchlist** és el pas de curació manual que Trazo considera essencial. Funciona així:

1. L'escaneig et dóna, per exemple, 25 oportunitats.
2. Mires ràpidament els gràfics de cadascuna (30 segons per gràfic = 12 minuts).
3. Les que visualment et convenencen (bon patró, bona forma) les afegeixes a la Watchlist.
4. Sobre les de la Watchlist, fas l'anàlisi profunda: generes l'informe d'IA, mires els fonamentals a Yahoo Finance, comproves el context sectorial.

### Mode Automàtic vs. Mode Watchlist

**Mode Automàtic (recomanat per a principiants):** Totes les oportunitats passen per l'anàlisi completa. Ideal mentre estàs aprenent i vols veure com funciona el sistema.

**Mode Watchlist (recomanat quan tinguis experiència):** Separes la detecció (algorisme) de la selecció final (tu). Warren (l'autor del sistema que ha inspirat part de RadarCore) diu que ell passa 1 hora a Yahoo Finance sobre les que el seu bucketer selecciona. Trazo fa una primera tria visual manual. Tots dos coincideixen que l'ull humà afegeix valor sobre l'algorisme.

---

## Capítol 22: Pestanya Investor Knowledge — personalitzant la IA

Aquí pots pujar els teus propis PDFs de filosofia inversora per entrenar la IA. Si tens un llibre de Warren Buffett, un article d'anàlisi que t'ha agradat, o els teus propis apunts d'inversió, la IA els incorporarà als seus informes per donar-te respostes més alineades amb la teva filosofia.

Exemples de documents que pots pujar:
- Resums d'estratègies de swing trading
- Notes sobre sectors que t'interessen
- Criteris personals d'entrada i sortida
- Articles sobre empreses específiques

---

# PART 6 — Posant-ho tot junt: el flux complet d'una operació

## Capítol 23: Del escaneig a la decisió

### Pas 1: Configuració (5 minuts)

Obre RadarCore. A la sidebar, verifica que l'idioma és el que vols i que el mode és Automàtic. A Market Scanner, selecciona S&P 500. Deixa els paràmetres per defecte la primera vegada.

### Pas 2: L'escaneig (30-60 segons)

Prem Run Scan. Mira els logs que apareixen mentre escaneja. Veuràs les empreses que passen o fallen els filtres. Quan acabi, vés a History & Reports.

### Pas 3: Primera revisió de la taula (5-10 minuts)

Ordena per Conf. descendent. Mira les primeres 10 files. Filtra per SWING o LATERAL si vols concentrar-te en els patrons de recuperació.

Elimina mentalment:
- Qualsevol cosa amb Phase LATE o MATURE (ja ha pujat massa)
- Les que tinguin ⚠️ EARN en menys de 14 dies (si no vols assumir el risc)
- Les DESCENDING (evitar per a compres)

### Pas 4: Revisió visual dels gràfics (2 minuts per empresa)

Per a cadascuna de les candidates que queden, prem View Charts. Mira:
1. Vista Mountain: La tendència general. Puja o baixa de manera neta?
2. Vista Pivots: El patró és clar? Es veu la V o la L?
3. Capçalera: Quin segment és el darrer? FLAT és bo (base), DOWN és dolent.
4. Trazo Phase Analysis: On és el Progress? L'Upside 3Y és atractiu?

### Pas 5: Anàlisi profunda de les candidates (10-20 minuts)

Per a les 3-5 empreses que han superat la revisió visual, genera un **informe d'IA** (Generate Reports). La IA t'explicarà el context fonamental, els riscos no tècnics (deute, competència, regulació) i si hi ha raons per no entrar.

Alhora, clica el Symbol a la taula per anar a Yahoo Finance. Mira:
- La secció de notícies recents: hi ha alguna raó clara per la caiguda?
- El "Summary" de la pàgina: la capitalització, el P/E ratio, el dividend.
- Els Earnings: quan és el proper? Coincideix amb el que RadarCore ha marcat?

### Pas 6: La decisió (tu, no l'algoritme)

RadarCore detecta. Tu decideixes. Fes-te aquestes preguntes:
1. Entenc per què ha caigut aquesta empresa?
2. Crec que els motius de la caiguda són temporals?
3. L'empresa seguirà existint i prosperant d'aquí a 6 mesos? I a 2 anys?
4. El Ratio R/R (de Stop Loss a Target) justifica el risc?
5. Si cau fins al Stop Loss, estaré còmode havent-ho perdut?

Si les respostes a tot això són sí, tens una tesi d'inversió sòlida. Si dubtes en alguna, és millor esperar.

---

## Capítol 24: La Regla d'Or — Gestió del risc i diversificació

Cap sistema de detecció és perfecte. RadarCore et dóna probabilitats, no certeses. Per sobreviure (i prosperar) a llarg termini, la gestió del risc és més important que qualsevol senyal concreta.

### Regla 1: Mai tot en una sola posició

Si poses tot el teu capital en una empresa i surt malament, has perdut tot. Si el distribuïdes en 10 operacions i una surt malament (i salta el Stop Loss), has perdut el 10% d'una part del capital.

**Recomanació:** Entre 8 i 15 posicions simultànies. Màxim un 10-15% del capital total en una sola empresa.

### Regla 2: Defineix el Stop Loss ABANS d'entrar

Decideix on sortiràs si et trobes equivocat ABANS de comprar. Si no ho fas, la psicologia del mercat t'ho farà impossible un cop estàs dins. "Esperaré que reboti" és la frase que ha arruïnat molts inversors.

### Regla 3: El R/R mínim és 2x

Si l'operació no té almenys el doble de recompensa possible respecte al risc assumit, no és una bona operació per a swing trading.

### Regla 4: Accepta les pèrdues ràpid, deixa córrer els guanys

Salta el Stop Loss? Surt sense dubtar. El mercat mai et deu una recuperació. Però si una posició va a favor, no la tanquis per por: deixa que arribi al T1 i decideix llavors.

### Regla 5: No inverteixis el que no pots permetre't perdre

Tots els conceptes anteriors no valen de res si el capital que inverteixes és el que necessites per pagar el lloguer del mes vinent. La pressió emocional de necessitar els diners pren les pitjors decisions possibles.

---

## Glossari ràpid

| Terme | Definició simplificada |
|---|---|
| Acció | Tros de propietat d'una empresa cotitzada |
| ATH | All-Time High. El preu màxim històric d'una acció |
| ATR | Average True Range. Mesura de la volatilitat diària típica |
| Borsa | Mercat electrònic on es compren i venen accions |
| Bucket | Categoria estructural d'una acció (SWING, RISE, etc.) |
| Caiguda idiosincràtica | Caiguda específica d'una empresa, no del mercat general |
| Drawdown | Caiguda percentual des d'un màxim fins a un mínim posterior |
| Earnings | Resultats financers trimestrals d'una empresa |
| EMA | Exponential Moving Average. Mitjana mòbil que dona més pes als preus recents |
| Era | Segment del gràfic classificat com UP, DOWN o FLAT |
| Índex | Cistella d'empreses que representa un mercat (S&P 500, IBEX 35...) |
| Inflació | Pèrdua de poder adquisitiu del diner amb el temps |
| L-BASE | Patró de caiguda seguida de base lateral. Signe d'acumulació |
| Liquiditat | Facilitat per comprar o vendre una acció sense moure el preu |
| Market Cap | Capitalització de mercat. Valor total d'una empresa en borsa |
| OHLCV | Open, High, Low, Close, Volume. Les cinc dades diàries d'una acció |
| Pivot | Punt clau de gir en el gràfic (Peak o Trough) |
| Ratio R/R | Ràtio Risc/Recompensa. Quantifica si una operació val la pena |
| RDP | Ramer-Douglas-Peucker. Algorisme per simplificar el gràfic eliminant soroll |
| Rebot | Pujada del preu des del seu mínim. Confirma el gir |
| RSI | Relative Strength Index. Indicador de sobrecompra/sobrevenda (0-100) |
| Stop Loss | Ordre automàtica de venda per limitar pèrdues |
| Swing Trading | Estratègia d'inversió en horitzó de dies a
---

### Agra�ments i M�rits
Aquest software ha estat elaborat gr�cies a la inspiraci� en la feina de Dani S�nchez-Crespo (https://www.skool.com/decodecore) i David Bastidas (https://www.davidbastidas.com/) a m�s de la seva col�laboraci�.
Aquest software ha estat programat amb una intenci� pedag�gica i gr�cies a Gemini i Claude.
