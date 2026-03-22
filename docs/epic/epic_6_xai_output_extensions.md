# Epic 6: XAI Output Extensions (Proaktiivinen Valmentaja)

**Tila:** Suunniteltu (Maaliskuu 2026)
**Konteksti:** Quorum V2 Backend (Structured Outputs) & Flutter Client V2

## Tavoite
Viedä Quorum V2 perinteisestä *"Kylmästä Auditoijasta"* proaktiiviseksi *"Valmentajaksi"* laajentamalla Explainable AI (XAI) -tietokenttien arkkitehtuuria. Mahdollistetaan joustava ja dynaaminen Pydantic-skeema, johon käyttäjä voi Admin Studiossa valita, mitä kaikkea tekoälyn täytyy palauttaa vastauksen kyljessä.

Tämä korvaa kömpelön `require_justification: bool` on/off -kytkimen uudella `output_extensions: list[str]` -arkkitehtuurilla.

## 1. Soveltamisala ja Tuetut Tyypit
Tämä ominaisuus koskee **KAIKKIA** sellaisia prompteja, joihin tekoäly joutuu antamaan erillisen validoidun vastauksen:
*   `type: float` / `int` (Matriisit)
*   `type: string` (Avoimet kysymykset)
*   *Ei koske: `type: instruction` (koska näihin ei odoteta tekoälyltä vastausta, vain LLM:n lukemista).*

## 2. Modulaariset Output Extensions (Sallitut arvot)
*   **[x] `justification`**: Pakottaa tekoälyn kirjoittamaan `_justification`-kenttään loogisen perustelun sille, miksi se ylipäätään antoi kyseisen arvosanan (esim. 3).
*   **[x] `citation`**: Pakottaa tekoälyn liittämään suoran leikkaa-liimaa -todisteen lähdetekstistä estämään hallusinointia (`_citation`).
*   **[x] `coaching`**: Pakottaa tekoälyn antamaan valmennusvinkin tai parannusehdotuksen. *"Mitä toimenpiteitä lukijan tulisi tehdä nostaakseen tämän kriteerin arvosanan vitoseen ensi kerralla?"* (`_coaching`). Pääasiassa laadullisiin matriiseihin.
*   **[x] `confidence`**: Tekoäly ilmoittaa numeerisen varmuuden (0-100%) arviostaan annetun lähtöaineiston perusteella (`_confidence`). Erittäin hyödyllinen epäselvissä tai ristiriitaisissa dokumenteissa.

## 3. Tietokantamallin Päivitys (`v2_core.py` / `db_v2.json`)
*   Vanha tapa: `"require_justification": true`
*   Uusi tapa: `"output_extensions": ["justification", "citation", "coaching"]`

## 4. Kääntäjän Älykkyys (`prompt_compiler.py`)
Kun kääntäjä muuttaa PromptBlockit tekoälyn Pydantic-skeemaksi, se katsoo uutta listaa: 
1. *"Ahaa, `type: float`. Minun pitää vaatia tekoälyltä vastauskenttä `score_leadership` (numero)."*
2. *"Ahaa, `output_extensions` listassa on 'coaching'. Pakotan lisäksi kentän `coaching_leadership` ja annan tekoälylle tiukan ohjeen: 'Kirjoita tähän konkreettinen valmennusvinkki siitä, miten kohde voi parantaa suoritustaan tässä asiassa'."*

## 5. UI:n Renderöintimoottori (Flutter & PDF)
Arkkitehtuuri ei ole valmis ennen kuin se muuttaa loppukäyttäjän kokemusta! 
*   **Valmennusvinkki:** Jos API-vastaus sisältää kriteerin kohdalla sanan `coaching`, Riverpod/Sdui-moottori maalaa ruudulle automaattisesti vihreän "💡 Valmennusvinkki" -laatikon.
*   **Varmuusvaroitus:** Jos tulos sisältää `confidence: 40%`, Frontendiin syttyy varoitus: **⚠️ Matalan varmuuden arvio - Tarkista lähdeviite**.
*   **PDF:** Raporteista tulee dynaamisia "Toimintasuunnitelmia", jotka ohjaavat työntekijöitä heti iteratiiviseen itsensä kehittämiseen pelkkien virheiden osoittamisen sijaan.
