# Epic 46: Soft Scoring Engines & Strictness Harmonization

## 1. Tausta ja Ongelman Kuvaus
Järjestelmään aiemmin (Epic 43) rakennettu Guttman Waterfall ja Progressive Dampening (DINA) -laskentalogiikka toteutettiin absoluuttisella matemaattisella tarkkuudella. Tämä tarkoitti, että alemman tason 0-tulos (esim. 0/3 osumaa) loi "kovan seinän" (Hard Threshold), joka kerrottiin nollalla. Tämä johti siihen, että yksittäinen LLM:n laiskuusvirhe nollasi kaikki ylempien tasojen tulokset ja romahdutti arvosanan pohjalukemaan (1.0) riippumatta siitä, oliko UI:n Strictness-asetus "Salliva" vai "Tiukka".

**Tavoite:** 
Muutetaan Scoring-moottoreiden logiikka "Pehmeäksi" (Soft Scaling). Käyttöliittymästä (UI) valittu `strictness_level` (0, 15, 50, 85, 100) ohjaa jatkossa kertoimen kireyttä, ei absoluuttista On/Off -kytkintä. 

## 2. Arkkitehtuurinen Ratkaisu (Best Practice)

### A. Uusi Matemaattinen Käsite: "Benefit of the Doubt" (BoD) -pohjakuvun kerroin
Jos tekoäly antaa tason osumiksi 0/3, osumaprosentti ei putoa nollaan, vaan se putoaa `strictness_level` -arvon määrittämään pohjalukemaan.
* **Täysi joustavuus (0):** Pohjakerroin 1.0 (Ei rangaistusta, toimii kuin Puhdas Keskiarvo)
* **Salliva (15):** Pohjakerroin 0.60 (Vaikka taso olisi 0/3, 60 % ylemmistä pisteistä pääsee läpi)
* **Tasapainoinen (50):** Pohjakerroin 0.30 (30 % pääsee läpi)
* **Tiukka (85):** Pohjakerroin 0.10 (Raskas rangaistus, vain 10 % pääsee läpi)
* **Ehdottomuus (100):** Pohjakerroin 0.00 (Hard Wall - Vanha logiikka, nollaa kaiken)

### B. Moottorikohtaiset Päivitykset

#### 1. Progressive Dampening (DINA) (`dampening_engine.py`)
Nykyinen kaava: `modifier = modifier * math.sqrt(hit_rate)`
Uusi kaava: 
```python
effective_hit_rate = max(hit_rate, base_forgiveness)
modifier = modifier * math.sqrt(effective_hit_rate)
```
Näin `modifier` ei koskaan nollaudu täysin (ellei Strictness ole 100), ja arvosanat skaalautuvat luonnollisesti joustavasti alas/ylös.

#### 2. Hybrid Waterfall (`waterfall_engine.py`)
Nykyinen kaava: `if hit_rate < target_threshold: break` (Pysäyttää laskennan ja lukitsee lattian).
Uusi kaava "Soft Waterfall":
Lasketaan painotettu summa niistä tasoista, jotka tekoäly on saavuttanut, mutta **jokainen taso, joka alittaa kynnyksen (target_threshold), aktivoi rangaistuskertoimen (penalty_multiplier)** kaikkiin ylempien tasojen pisteisiin. 
* Kireillä asetuksilla rangaistuskerroin on 0.0 (toimii kuten nykyinen Guttman).
* Löysillä asetuksilla rangaistuskerroin on esim. 0.5 (ylempien tasojen tulokset puolitetaan, mutta niitä ei nollata).

#### 3. Weighted Average & Pure Average (`average_engine.py`)
Nämä moottorit ovat jo luonnostaan "pehmeitä", koska ne laskevat vain keskiarvoja. 
Päivitys: Kytketään `strictness_level` käyrän skaalaukseen. Jos Strictness on korkea (esim. 85), järjestelmä vaatii korkeamman osumaprosentin saadakseen tason täydet pisteet.

## 3. Toteutuksen Askeleet (Implementation Plan)

1. **`backend_v2/utils/math_utils.py` Refaktorointi:**
   * Päivitetään koodiin uusi logiikka `calculate_soft_dampening_score` ja `calculate_soft_waterfall_score`.
   * Lisätään funktio, joka muuntaa `strictness_level` (0-100) arvon `base_forgiveness` -liukuluvuksi.

2. **Moottoreiden Päivitys (`backend_v2/utils/scoring/`):**
   * Päivitetään `waterfall_engine.py` käyttämään joustavaa Soft Waterfall -laskentaa absoluuttisen Break-käskyn sijaan.
   * Päivitetään `dampening_engine.py` käyttämään `effective_hit_rate` ja `base_forgiveness` muuttujia, jotta 0-osuma ei tee kerrointa nollaksi.

3. **Logituksen ja XAI:n (Explainable AI) Päivitys:**
   * Päivitetään moottoreiden generoima `calculation_log` (Markdown), jotta se selittää selkeästi frontendiin: *"Tasolta X saatiin 0 osumaa. Käytetään Strictness 50:n mukaista joustokerrointa (0.30), joten pisteitä vaimennettiin pehmeästi."*

## 4. Frontendin Toteutus ja Laatuporttivaatimukset (Flutter Desktop)

Käyttöliittymään toteutetaan Strictness-tason valitsin sekä uuden XAI-lokituksen (Calculation Log) näyttökomponentti. Tämän koodin on läpäistävä absoluuttisesti Tier 2 Frontend Hardening -laatuportti:

* **The Zero Compromise Pledge (Ei purkkapaikkauksia):** Kun UI vastaanottaa taustajärjestelmältä XAI-lokeja tai Strictness-tiloja, DTO-mallien käsittelyssä on **ehdoton kielto** käyttää Dartin null-coalescing (`?? 'default'`) -operaattoreita puuttuvan datan piilottamiseen.
* **Täydellinen tilanhallinta (No `.maybeWhen`):** Riverpod-tilanhallinnassa ja Freezed-malleissa on käsiteltävä kaikki tilat eksplisiittisesti `.when()` -metodilla. Fallback-ratkaisuja (kuten `.maybeWhen()` tai `.orElse()`) ei saa käyttää, jotta rakenteelliset virheet tulevat näkyviin heti (Fail Fast).
* **Frontend Zero DB Hardcoding Mandate:** Käyttöliittymäkomponentit (esim. Strictness-tason valitsin ja Scoring Engine -valitsin) **eivät saa nojata kovakoodattuihin tietokannan ID-tunnisteisiin, taulujen nimiin tai indeksijärjestyksiin** (esim. oletus, että indeksi 50 on aina "Tasapainoinen"). Tilojen on tultava vahvasti tyypitettyinä DTO-malleina (esim. Enum) API:n kautta tai vähintään UI-puolen Enumeina, mutta ei taianomaisina taulukoiden avaimina `Map<int, String> strictnessOptions = {50: 'Tasapainoinen'}`.
* **UI Presentation Fix (Tuplatekstien poisto):** Kuvakaappausten osoittama nykyinen toteutustapa, jossa Strictness-valikko tulostaa arvoja tuplana muodossa `Salliva (15) (15)` (johtuen koodin logiikasta `Text('${entry.value} (${entry.key})')`), on korjattava. Uudessa enum/DTO-pohjaisessa toteutuksessa käyttöliittymän lokalisointitiedostot (esim. `AppLocalizations`) hoitavat näyttötekstin yksinään, jolloin valikossa lukee ammattimaisesti vain `Salliva (15)` tai `Tasapainoinen (50 - Oletus)`.

## 5. Odotettu Lopputulos ja Hyväksymiskriteerit

**Toiminnallinen lopputulos:**
Sama ajokerta ja täysin sama AI-data (esim. 0/3 osumaa alatasolta) tuottaa:
* **Strictness 100:** Arvosana 1.0 (Kova seinä)
* **Strictness 50:** Arvosana esim. 2.7 (Vaimennettu)
* **Strictness 15:** Arvosana esim. 3.8 (Salliva)

**Laadulliset hyväksymiskriteerit (Definition of Done):**
1. **Tier 2 Audit Matrix Passed:** Kaikki Epicissä muokatut tai luodut `.dart`-tiedostot on auditoitava onnistuneesti `Tier 2 Frontend Hardening Loop` -työnkulkua vasten. 
2. Yksikään uusi UI-komponentti ei ohita virheenkäsittelyä hiljaisesti, vaan noudattaa `frontend_zero_leaks` ja `strongly_typed_routing` -mandaatteja.
3. XAI-loki renderöityy oikein Desktop-käyttöliittymässä ilman legacy-ratkaisuja.

Tämä täyttää liiketoiminnan Best Practice -vaatimukset tekoälyn satunnaisuuden hallinnassa, palauttaa UI:n valikoiden tarkoittaman joustavuuden käyttöön, sekä varmistaa Frontendin arkkitehtuurisen eheyden (Zero DB Hardcoding).
