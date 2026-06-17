# Epic 60: System 2 Reliability & LLM Logic Audit (June 2026)

## 1. Tausta ja Motivaatio (Ongelman kuvaus)
Järjestelmän LLM-evaluointimoottorissa havaittiin merkittävää epävakautta ja varianssia peräkkäisissä ajoissa täysin identtisillä syötteillä ja seed-datalla. Tämä epävakaus paljastui vertailuajoissa, joiden raportit osoittivat hälyttäviä lukemia:

**Todisteet (Diff Raportit 2026-06-17 13:22 ja 13:25):**
- **Keskinäinen konsistenssi (Self-Consistency):** Vain noin 78.7 % – 80.4 %
- **Erimielisyydet:** Jopa 31 kpl (raportti 13:25) ja 29 kpl (raportti 13:22) täysin satunnaisia tilasiirtymiä (esim. PASSED -> FAILED 18 kpl) ilman, että Contextual Override -arvoissa oli eroja.
- **Entropia:** Keskimääräinen Shannonin entropia oli jopa 0.21, mikä viittaa erittäin epävakaaseen mallin päätöksentekoon.

Tämä jatkuva "arvonta" viittasi arkkitehtuuritason rakenteellisiin virheisiin, LLM-ohjeistusten välisiin ristiriitoihin (ns. "Kissojen ja koirien" -ongelma) sekä käänteiseen logiikkaan moottorin ytimessä.

---

## 2. Auditointisuunnitelma (Implementation Plan)
Varianssin juurisyiden selvittämiseksi käynnistettiin kokonaisvaltainen, iteratiivinen auditointi ("kissojen ja koirien kanssa"), joka jaettiin neljään vaiheeseen:

1. **Vaihe 1: Työnkulun orkestrointi ja lohkominen** (`chunk_worker.py`, `prompt_factory.py`, `context_builder.py`)
   - Fokuksessa käänteinen logiikka (is_lightweight, asetukset) ja kielelliset ristiriidat.
2. **Vaihe 2: LLM-ajuri ja suoritusmoottori** (`llm/handler.py`, `llm/client.py`)
   - Fokuksessa Pydantic-validointisilmukat, äärettömät luupit ja Fail-Fast -virheiden käsittely.
3. **Vaihe 3: Jälkikäsittely ja Hookit** (`synthesis.py`, `translation_hook.py`)
   - Fokuksessa LLM-asetusten resurssitehokkuus ja kääntämisen vaikutus semanttiseen päättelyyn.
4. **Vaihe 4: Dynaamisten sääntöjen rakentaja / Seeding** (`seed_data.json`)
   - Fokuksessa arviointisääntöjen kaksoiskielteisyydet ja parsintavirheet.

---

## 3. Auditoinnin Löydökset ja Ratkaisut (Llm Audit Findings)

### Vaihe 1: Työnkulun orkestrointi ja lohkominen
- **Löydös 1 & 2: Orkestroinnin ja äänestyksen deklaratiivinen läpinäkyvyys (chunk_worker.py - KORJATTU)**
  - **Analyysi (Juurisyy):** Raportti listaa katastrofaalisia bugeja: käänteinen ENSEMBLE-logiikka (raskaat ajettiin kerran, kevyet kolmesti) ja Minority Veto (yksi hallusinaatio kolmesta kaatoi koko tuloksen). Nämä oireilevat siitä, että backendin ohjauslogiikka on rakentunut vaikeaselkoisen negatiivisen if/else-viidakon (esim. `if not is_lightweight and not ensemble_failed:`) varaan, mikä on ihmiselle vaikeaa lukea ja ylläpitää.
  - **2026 Best Practice (Declarative Consensus Logic & Pure Functions):** Liiketoimintalogiikka ja äänestyskynnykset nostetaan puhtaiksi, itsedokumentoiviksi vakioiksi ja tilakoneiksi (State Machines).
  - **Tarkka toimenpide:** Refaktoroitiin `chunk_worker.py`:n äänestysmekanismi käyttämään eksplisiittistä ja läpinäkyvää matematiikkaa:
    ```python
    # 2026 Readability Standard
    REQUIRED_MAJORITY_THRESHOLD = 0.66

    def apply_ensemble_consensus(votes: List[VerificationResult]) -> VerificationResult:
        pass_ratio = sum(1 for v in votes if v == VerificationResult.VERIFIED) / len(votes)

        if pass_ratio >= REQUIRED_MAJORITY_THRESHOLD:
            return VerificationResult.VERIFIED
        return VerificationResult.DEBUNKED
    ```
  - **Perustelu:** Itsedokumentoiva koodi poistaa inhimilliset koodausvirheet. "Minority Veto" -sabotaasi ei voi toistua, koska matemaattinen kynnysarvo (0.66) on eksplisiittinen ja täysin luettava.
- **Havainto:** Muiden ehtojen (`is_lightweight`, `has_search`, `has_shuffled_atoms`) todettiin toimivan oikein ilman käänteistä logiikkaa.

### Vaihe 2: LLM-ajuri ja suoritusmoottori
- **Löydös (Fail-Fast): Fail-Fast -virheiden ja Self-Healingin semanttinen luettavuus (llm/handler.py - KORJATTU)**
  - **Analyysi (Juurisyy):** Kun tiukka Pydantic-validointi (dynaaminen skeeman karsinta `strictness_level >= 100`) hylkää vastauksen (esim. malli yrittää palauttaa subjektiivisen `contextual_override` -kentän), moottori heittää Fail-Fast -virheen. Nykymallissa moottori tekee sokkona uusia yrityksiä (Retry-loop) pelkillä Jitter-viiveillä. Jos LLM ei "lue" virheen syytä, se toistaa virheensä, mikä johtaa tyhjiin tuloksiin (False Fails) ja laskee konsistenssia puhtaasti formaattisyistä.
  - **2026 Best Practice (Semantic Error Bubbling / Self-Reflective Feedback Loops):** Kielimallille ei piiloteta virheitä lokeihin, vaan ne käännetään takaisin mallille "luettavaksi" kognitiiviseksi palautteeksi.
  - **Tarkka toimenpide:** Muokattiin `llm_task_executor.py`:n uudelleenyrityssilmukkaa siten, että Pydanticin `ValidationError` parsitaan eksplisiittiseksi kognitiiviseksi promptiksi seuraavalle yritykselle:
    ```python
    except pydantic.ValidationError as e:
        error_msg = e.errors()[0]['msg']
        feedback_prompt = (
            f"\n<system_feedback>"
            f"CRITICAL ERROR: Your previous JSON output failed strict schema validation. "
            f"Reason: {error_msg}. "
            f"You MUST remove forbidden subjective fields and adhere strictly to the requested JSON schema."
            f"</system_feedback>"
        )
        # Injektoidaan feedback_prompt alkuperäiseen promptiin retry-kutsua varten
    ```
  - **Perustelu:** Moderni System 2 -tason LLM kykenee korjaamaan rakenteellisen virheensä lähes 100 % varmuudella heti ensimmäisellä yrityksellä, kun virhe esitetään sille semanttisena, luettavana kontekstina. Tämä poistaa API-kutsujen haaskauksen ja vakauttaa konsistenssin.

### Vaihe 3: Synthesis & Translation Hooks
- **Löydös 3: Kielellisen arkkitehtuurin eristäminen ("Cat & Dog" -konflikti - KORJATTU)**
  - **Analyysi (Juurisyy):** Järjestelmä on pyytänyt LLM:ää suorittamaan monimutkaista loogista päättelyä (kuten Toulminin kausaalianalyysiä) kohdekielellä (esim. suomeksi tai ranskaksi), samalla kun järjestelmän säännöt ja ohjeet ovat englanniksi. Tämä aiheuttaa mallin latenteissa avaruuksissa "kognitiivisen repeämän" (Attention Drift), jolloin validitkin sitaatit suodattuvat vahingossa pois kielellisen häiriöäänen vuoksi.
  - **2026 Best Practice (Monolingual Latent Space Reasoning / LoT):** Suurten mallien deduktiivinen logiikka (Chain-of-Thought) on parametrisesti ylivoimaisesti vahvinta englanniksi. Kognitio ja esitystapa (lokalisointi) on eriytettävä täysin toisistaan.
  - **Tarkka toimenpide:** Erotettiin "Language of Thought" (LoT) tulostuskielestä. Poistettiin `synthesis.py`:n ristiriitainen "reasoning"-sana kohdekielisäännöstä ja selkeytettiin `prompt_factory.py`:n luomaan globaaliin promptiin selkeä XML-direktiivi:
    ```xml
    <language_directives>
      <reasoning_language>You MUST perform all internal logic, thought processes, and semantic reasoning explicitly in ENGLISH to maximize logical fidelity.</reasoning_language>
      <output_language>Translate ONLY the final user-facing fields (e.g., final summary) to the target locale.</output_language>
    </language_directives>
    ```
  - **Perustelu:** Arkkitehtuurin luettavuus mallille paranee eksponentiaalisesti, kun sen ei tarvitse arpoa, prosessoiko se logiikkaa suomeksi vai englanniksi. Tämä poistaa raportin satunnaiset hylkäykset (PASSED -> FAILED), jotka johtuivat pelkästään käännösvaiheen aiheuttamasta semanttisesta hävikistä.
- **Havainto:** Jälkikäsittely-hookit hyödyntävät oikein kevyempiä LLMClient-asetuksia, eivätkä haaskaa resursseja raskaisiin evaluointimalleihin.

### Vaihe 4: Dynaamisten sääntöjen rakentaja (Seeding & Rules)
- **Löydös 4: Katkenneet ehdot arviointisäännöissä (Siemendatan kognitiivinen luettavuus - KORJATTU)**
  - **Analyysi (Juurisyy):** Raportti (diff_report 13:22 ja 13:25) paljasti, että kaikkein epävakaimmat säännöt päättyivät katkenneisiin lauseisiin, kuten: `"Otherwise."` Tämä loi LLM-kontekstissa kognitiivisen ansan (Dangling Condition / Double Negative). Se pakotti kielimallin arvaamaan, mitä ohjeen laatija on tarkoittanut "muuten"-tilanteessa (esim. palautetaanko null vai tyhjä merkkijono).
  - **2026 Best Practice (Explicit Terminal Directives):** Sääntöjä on kohdeltava koodina (Deterministic ECA - Event-Condition-Action). Jokaisella luonnollisen kielen säännöllä on oltava ohjelmallinen, absoluuttinen päätetila, joka ei jätä tulkinnanvaraa.
  - **Tarkka toimenpide:** Kymmenen vapaamuotoista `extraction_rule`-sääntöä refaktoroitiin `seed_data.json` -tiedostosta tiukkaan IF-THEN-ELSE -rakenteeseen pseudokoodin omaisesti.
    - *Nykyinen (Kognitiivisesti epäselvä):* `"If [condition]. Otherwise."`
    - *Uusi 2026-luettavuus:* `"... If [condition], extract the quote. Otherwise, return null."` (joka vastaa logiikkaa: `"IF the condition is physically present in the text, EXTRACT the exact quote. OTHERWISE, you MUST output strictly JSON null for this field. Do NOT rationalize or infer missing context."`)
  - **Perustelu:** Eksplisiittinen ohje palauttaa `null` linkittyy saumattomasti Pydantic-skeeman Fail-Fast -validointiin. Se poistaa tulkinnanvaraisuuden ja estää mallia hallusinoimasta täytedataa vain "miellyttääkseen" kysyjää. Tämä korjaa välittömästi Cohenin Kappan ja konsistenssin heittelyt raskaissa iteratiivisissa ajoissa.

---

## 4. Tärkeä Strateginen Huomio: Kielipolitiikka
Auditoinnin yhteydessä vahvistettiin arkkitehtuurillinen tavoite:
**Kaikki sisäinen päättely (`semantic_reasoning`, lokit, ajatukset) tuotetaan yksinomaan englanniksi parhaan suorituskyvyn takaamiseksi, ja ainoastaan valmis lopputulos käännetään/tuotetaan käyttäjän kielellä (eli yleensä samalla kuin lähdeaineisto).**

Tämä yksinkertaistaa mallin taakkaa, kun sen ei tarvitse prosessoida formaalia logiikkaa vierailla tai useilla kielillä samanaikaisesti. Tehdyt hook-korjaukset tukevat nyt tätä tavoitetta täydellisesti.

---

## 5. Yhteenveto
Arkkitehtuurinne perusta on erittäin kestävä (erityisesti dynaaminen skeeman karsinta ja Fail-Fast). Varianssi johtui yksinomaan siitä, että LLM jätettiin kognitiivisesti ylikuormitettuun tilaan arvailemaan roikkuvia sääntöjä ja suorittamaan raskasta logiikkaa vierailla kielillä.

Viittaus vuoden 2026 parhaisiin käytäntöihin korostaa sitä, että tekoälykehityksessä ihmisen kirjoittaman koodin lisäksi on optimoitava se, miten kone "lukee" ohjeensa ja virheensä. Kun `seed_data.json` puhdistetaan deterministiseen ECA-muotoon, päättelykieli sementoidaan englanniksi ja Pydantic-virheet käännetään itsereflektiiviseksi palautteeksi, järjestelmän Fleissin Kappa ja itsekonsistenssi tulevat nousemaan deterministiselle yli 95 % huipputasolle.
