# Epic 11: Absolute Data Purity (Zero "Before" Validators)

**Epic Status:** Suunniteltu / Odottaa suoritusta
**Tavoite:** Pydantic V2 "Strict Nirvana" – Kaikkien ajonaikaisten tekohengitys-validaattorien (`before`) poistaminen malliestamme ja siemendatan kovettaminen absoluuttisesti puhdastyypitetyksi JSON:ksi.
**Arkkitehtuurimandaatti:** Fail-Fast ja Zero-Trust Datakerrokseen. API ja tietokantakerros lukevat vain täydellistä dataa. Ne eivät korjaile huonoa dataa (eivät yritä arvata aikavyöhykkeitä tai parsia stringejä AST-kirjastolla).

---

## Vaihe 1: Siemendatan (`seed_data.json`) Puhdistaminen

Ennen kuin koskemme koodiin, `backend_v2/seed/seed_data.json` on korjattava vastaamaan tiukkoja tietotyyppejä. Tiedosto on tarkistettava ja korjattava seuraavien sääntöjen mukaisesti:

### 1. Korjaa `ast.literal_eval` -ongelma (Stringifioidut JSON-objektit)
Kaikki (erityisesti `ExecutionRecord` tai `TraceEvent` -objekteissa) sijaitsevat sisäkkäiset datat, jotka on tallennettu heittomerkeillä varustettuna merkkijonona ("stringified JSON"), on purettava natiiveiksi JSON-objekteiksi.
- ❌ VÄÄRIN: `"results": "{'score': 5, 'text': 'hyvä'}"` (Pakotti käyttämään hidasta `ast.literal_eval` -purkkaa)
- ✅ OIKEIN: `"results": {"score": 5, "text": "hyvä"}` (Puhdas, esijäsennelty JSON-objekti)

### 2. Korjaa Enum-arvot täsmällisiksi
Kaikki kentät, jotka viittaavat `BlockDataType` tai `ExecutionStatus` -enumeihin, on muutettava täsmälleen oikeaan kirjainkokoon, jotta ne vastaavat tarkasti `backend_v2/models/enums.py` -määrittelyitä.
- ❌ VÄÄRIN: `"type": "STRING", "status": "Done"`
- ✅ OIKEIN: `"type": "string", "status": "completed"`

### 3. Varmista puhtaat ISO 8601 -aikaleimat
Pydantic V2 ymmärtää natiivisti 'Z'-merkin (Zulu time, UTC). Manuaalista `.replace("Z", "+00:00")` -purkkaa ei tarvita koodissa, joten datan itsessään on taattava rakenteen eheys.
- ❌ VÄÄRIN: `"created_at": "2026-03-25 12:00:00"` (Puuttuu T ja aikavyöhyke)
- ✅ OIKEIN: `"created_at": "2026-03-25T12:00:00Z"`

---

## Vaihe 2: Koodin Puhdistaminen (Delete the Hacks)

Kun siemendata on siivottu (Vaihe 1), poistetaan väliaikaiset tekohengitykset `backend_v2/models/v2_core.py` -tiedostosta. Poista seuraavat lohkot kokonaan:

### A. Poista PromptBlockin Enum-purkka
Etsi ja poista kokonaan tämä lohko `PromptBlock`-luokasta:
```python
    @model_validator(mode="before")
    @classmethod
    def pre_validate_type_enum(cls, data: Any) -> Any:
        # Pysytetään tyyppiparsinta
        ...
```
*(Huom. Tämä poistetaan myös `DataDictionaryField`-luokasta tai mistä tahansa muualta, mihin se on levinnyt.)*

### B. Poista ExecutionRecordin massiivinen parseri
Etsi ja poista kokonaan tämä lohko `ExecutionRecord`-luokasta (sekä vastaavat `MCPAuditTrace`-luokasta):
```python
    @model_validator(mode="before")
    @classmethod
    def pre_validate_type_enums(cls, data: Any) -> Any:
        # Tämä poistaa ast.literal_evalin, datetime-replacen 
        # ja status-enumin try-except -hidasteet.
        ...
```

### C. Koodikannan systemaattinen haravointi (Scope Sweep)
Vaikka Epic listaa selkeät pääkohteet, kehittäjä saattaa jättää jonkin muun tiedoston huomiotta.
- Varmista puhdistuksen kattavuus ajamalla komentoriviltä haku:
  ```bash
  grep -r '@model_validator(mode="before")' backend_v2/models/
  ```
- Tuhoa absoluuttisesti kaikki osumat, jotka liittyvät tyyppimuunnoksiin (string coercion).

---

## Vaihe 3: Tietokannan Nollaus (The Wipe)

Koska lokaali kanta (esim. TinyDB `data/db_v2.json` tai lokaali Firestore) sisältää vanhaa datamuotoa, se on tuhottava viipymättä, ettei se estä testejä.

1. Pysäytä käynnissä oleva backend.
2. Aja olemassa oleva nollausskripti:
   ```bash
   uv run python backend_v2/seed/wipe_user_data.py
   ```
*(Tai poista kyseinen kanta manuaalisesti).*

---

## Vaihe 4: Uudelleensiemennys ja Fail-Fast-iterointi

Tämä on totuuden hetki Epicille. Aja puhdistettu data armottomien Pydantic-mallien läpi.

1. **Aja siemennysskripti:**
   ```bash
   uv run python backend_v2/seed/run_seed.py local
   ```
2. **Analysoi kaatuminen:**
   On hyvin todennäköistä (ja toivottavaa), että skripti kaatuu heti ensimmäisellä kerralla ja heittää Pydanticin `ValidationError` -virheen. Tämä on Fail-Fast -arkkitehtuurisi toiminnassa. 
3. **Korjaa seed_data.json:**
   Lue virheilmoitus huolella: Pydantic kertoo sinulle täsmälleen, millä rivillä ja missä kentässä `seed_data.json` -tiedostoa on yhä virhe. (Esim. `"1 validation error for PromptBlock... type: input should be 'string', 'float'..."`). Tee vaadittu korjaus JSON-tiedostoon, EI taaksepäin koodiin!
4. **Toista:**
   Aja `run_seed.py` uudelleen, kunnes se menee läpi puhtaasti ilman yhtäkään virhettä.

---

## Vaihe 5: Yksikkötestien ja Mock-datan päivitys (Test Suite Update)

Epic luottaa vahvasti `run_seed.py` -skriptin läpimenoon. On kuitenkin varmaa, että kun Pydantic-mallit tiukentuvat, myös automatisoidut yksikkötestit (pytest) tulevat kaatumaan löyhän testidatan myötä.

1. Aja koko testipatteristo (`uv run pytest`).
2. Etsi ja korjaa kaikki testien käyttämät vanhentuneet Mock-datat ja fixturet, joissa rutiininomaisesti syötettiin vääränlaisia enumeita tai stringifioitua JSONia.

---

## Vaihe 6: Frontend-pariteetin varmistaminen (Flutter Client)

Jos korjaat `seed_data.json` -tiedostossa esimerkiksi enum-arvon `status: "Done"` absoluuttisen oikeaan muotoon `status: "completed"`, on massiivinen vaara, että Flutter-käyttöliittymä lähettää yhä API-kutsun muodossa `"Done"`.

- Varmista, että Flutter-käyttöliittymän (Dart) DTO-mallit ja pyyntöjen payloadit on päivitetty vastaamaan uusia, tiukennettuja Enum- ja päivämääräsääntöjä. 
- Muutoin käyttöliittymä kaataa reitittimen välittömästi `422 Unprocessable Entity` -virheeseen backendin torjuessa datan!

---

## Lopputulos (Definition of Done)

Kun `run_seed.py` ja yksikkötestit menevät vihdoin laakista vihreänä läpi:
- Koodissasi ei ole enää yhtäkään hidasta tai vaarallista "before"-validaattoria.
- Järjestelmä on 100% "Strict Pydantic V2".
- Voit olla varma, että kaikki data, mitä järjestelmään tästä eteenpäin menee (niin käyttöliittymästä kuin tietokannasta), on rakenteellisesti absoluuttisen täydellistä. Koko backend hengittää vapaasti.
