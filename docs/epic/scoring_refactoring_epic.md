# EPIC: Scoring Hook Refactoring - Dismantling the Math & UI God Object

## 1. Tausta ja Konteksti
`backend_v2/hooks/scoring.py` on yksi backendin suurimmista tiedostoista (~60 KB ja yli 1200 riviä). Vaikka varsinaiset matemaattiset moottorit (kuten `average_engine.py` ja `waterfall_engine.py`) on aiemmin eristetty `utils/scoring`-hakemistoon, itse Scoring Hook on yhä aivan liian massiivinen.

**Ongelma:** `scoring.py` rikkoo raskaasti Single Responsibility Principle (SRP) -sääntöä. Se yrittää olla samanaikaisesti kovan tason datan prosessoija ja käyttöliittymän (UI) rakentaja.

**Nykyiset vastuut:**
1. **Datan louhinta ja reititys:** Purkaa Pydantic DTO:ita (ScoringPayloadWrapper) ja kaivaa esiin `falsifier`, `sanitization_result` ja `evaluative_matrices` -tietoja.
2. **Kovakoodattu AST-evaluointi:** Ajattaa koodin sisällä ehtolauseita (Abstract Syntax Tree) määrittääkseen override-logiikkaa.
3. **Tulosten yhdistely ja matematiikka:** Koostaa lopulliset numeeriset matriisipisteet `utils/scoring`-moottoreiden avulla ja skaalaa niitä (esim. `normalize_score_to_100`).
4. **UI-Formatteri (Käyttöliittymän piirtäjä):** Rakentaa SDUI:ta (Server-Driven UI) varten tekstimuotoisia listoja, "Lainaus:"-blokkeja, kääntää sääntöjen selityksiä ja formatoi värikkäitä lohkoja ruudulle.

Tämä tekee sääntömuutoksista tuskallisia: Jos haluamme muuttaa, miten matemaattinen skaalaus toimii, joudumme muokkaamaan samaa tiedostoa, joka vastaa siitä, piirtyykö käyttöliittymään Markdown-lainausmerkki vai ei.

## 2. Tavoite
Purkaa `scoring.py`:n UI-logiikka täysin irti pistelaskusta ja liiketoimintalogiikasta. Lopputuloksena Hook toimii vain puhtaana putkena (Pipeline), joka liittää asiantuntijaluokat toisiinsa.

## 3. Suunnitellut Arkkitehtuurimuutokset (Uudet Komponentit ja Hakemistot)

### A. Uusi Hakemistorakenne
Jotta God Object -luokkia ei vain siirretä isosta tiedostosta isoon kansioon, koko Scoring ja UI -logiikka tulisi jatkossa jaotella omiin erikoistuneisiin hakemistoihinsa:
* `backend_v2/services/scoring/` (Matematiikka ja säännöt)
* `backend_v2/services/sdui/` (Server-Driven UI:n piirtäminen)

### B. Komponenttien Purkaminen

#### 1. `DataExtractor` / `ScoringContextBuilder`
* **Vastuu:** Ottaa vastaan raa'an HookState-olion ja purkaa siitä tiukan Pydantic-mallin avulla vain tarpeelliset tiedot (Falsifiers, Matrices, Quotes).
* **Rajoitus:** Ei sisällä ehtolauseita eikä laske mitään. Palauttaa vain puhtaan, tyypitetyn `ScoringContext`-olion.

#### 2. `MathOrchestrator` (Sääntömoottorin ohjain)
* **Vastuu:** Vastaa AST-lausekkeiden ajamisesta ja delegoi matemaattisen työn `utils/scoring/` -moottoreille. Laskee lopullisen arvosanan 0-100.
* **Rajoitus:** Ei tiedä MITÄÄN siitä, miten tulos esitetään. Palauttaa vain numeron ja tiedon siitä, mitkä säännöt laukesivat.

#### 3. `SDUIFormatter` / `QuoteRenderer` (UI:n piirtäjä)
* **Vastuu:** Ottaa sisään `MathOrchestratorin` numeeriset tulokset ja rakentaa nätin Server-Driven UI -objektin (`ScoringResultDTO`), jossa on tekstiselitykset, oikeat värit ja oikein formatoidut lainaukset. Sijoitetaan uuteen `backend_v2/services/sdui/` -hakemistoon.

### C. Itse Hook (`scoring.py`)
Jäljelle jäävä tiedosto on maksimissaan 50-100 riviä pitkä ja näyttää tältä:
```python
context = context_builder.build(state)
raw_scores = math_orchestrator.calculate(context)
sdui_payload = sdui_formatter.format_for_ui(raw_scores, language)
return HookResult(state_delta=sdui_payload)
```

## 4. Toteutuksen Askelmerkit
1. **Vaihe 1:** Eristetään UI-formaatit (Lainauksien kokoaminen, Markdownin generointi) omaan `sdui_formatter.py` -tiedostoon.
2. **Vaihe 2:** Eristetään Pydantic-purku (strict fail-fast validointi) `ScoringContextBuilderiin`.
3. **Vaihe 3:** Pienennetään alkuperäinen `scoring.py` pelkäksi putkeksi.
4. **Laatuportti:** Ajetaan Tier 2 Python Audit Loop ja varmistetaan, että kaikki yli 100 vanhaa scoring-testiä (`test_scoring_hooks.py` jne.) menevät yhä läpi muuttumattomina.
