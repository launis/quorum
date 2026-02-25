# CONTEXT & ROLE
Olet tiukka Lead QA Engineer ja Staff-tason ohjelmistoarkkitehti. Olemme juuri saaneet päätökseen laajan Python/FastAPI ja Flutter/Dart -projektin refaktoroinnin. 

Tehtävänäsi on suorittaa koodipohjalle säälimätön "POST-REFACTORING ANTI-HALLUCINATION AUDIT". Etsimme koodista tekoälyn jättämiä hallusinaatioita, keksittyjä metodeja, arkkitehtuuririkkomuksia ja vanhentuneita käytäntöjä, jotka saattavat läpäistä kääntäjän mutta rikkovat tiukat mandaattimme.

ÄLÄ KIRJOITA UUTTA KOODIA TAI TEE MUUTOKSIA VIELÄ. Sinun tehtäväsi on käyttää IDE:n globaaleja hakutyökaluja (grep/search), etsiä alla olevia rikkomuksia ja laatia minulle yksityiskohtainen auditointiraportti. Korjaukset tehdään myöhemmin ja vain silloin, kun olemme 100% varmoja virheestä.

---

# AUDIT PROTOCOL: THE HALLUCINATION TARGETS
Käy koodipohja läpi hakutyökaluilla ja etsi SUURENNUSLASILLA seuraavia tyypillisiä hallusinaatioita:

### 1. Backend Hallusinaatiot & Säännöt (Python)
- **Pydantic V1 vs V2:** Etsi koodista kiellettyjä V1-metodeja.
  - *HAE:* `.dict()`, `.parse_obj()`, `__root__`, `Config:` (class Config). Kaiken on oltava V2-muodossa (`.model_dump()`, `.model_validate()`, `ConfigDict`).
- **Silent Failures (Fail-Fast rikkomus):** Etsi defensiivistä koodausta, joka piilottaa virheitä.
  - *HAE:* `except Exception: pass` tai kohtia ydinlogiikassa, joissa palautetaan hiljaa `return None` tai `return {}`.
- **Vanha FastAPI DI:**
  - *HAE:* `= Depends(`. (Kaikkien injektioiden pitäisi käyttää `Annotated[Type, Depends()]`).

### 2. Frontend Hallusinaatiot & Säännöt (Flutter)
- **Tilanhallinnan Frankenstein-koodi:** Etsi tiedostoja, joissa uutta Riverpod 3.0:aa on vahingossa sekoitettu vanhaan arkkitehtuuriin.
  - *HAE:* `ChangeNotifier`, `StateProvider`, `StateNotifier`, `Provider.of`. (Kaiken pitää olla `@riverpod` Notifiereita).
- **Vanhentuneet Widgetit (Material 2):** 
  - *HAE:* `FlatButton`, `RaisedButton`, `OutlineButton` tai teemoituksen `accentColor`. (Kiellettyjä, käytä `TextButton`, `colorScheme`).
- **Reitityksen merkkijonot (GoRouter):** 
  - *HAE:* `context.push('/` tai `context.go('/`. (Reitityksen on pakko käyttää tyyppiturvallisia `GoRouteData`-luokkia).
- **RenderFlex-ansat (Fysiikkahallusinaatiot):** LLM ei ymmärrä UI:n fysiikkaa. 
  - *ETSI MANUAALISESTI:* Etsi tiedostot, joissa on `ListView`, `GridView` tai `SingleChildScrollView`. Ovatko ne suoraan `Column` tai `Row` sisällä ILMAN `Expanded`/`Flexible` -käärettä? Tämä kaatuu ajonaikana.

### 3. I18N ja Hygienia
- **The "No-String" Policy:** Varmista, ettei backend palauta käyttöliittymän tekstejä (suomeksi/englanniksi), vaan ainoastaan Enum-koodeja tai avaimia.
- **Hardkoodatut käännökset & Pluraalit:** Varmista, ettei Flutter-koodissa ole merkkijonojen yhdistelyä (esim. `"Hello " + name`). Näiden on oltava ICU-muodossa `.arb`-tiedostoissa.

---

# EXECUTION INSTRUCTIONS (Kuinka toimit)
1. Suorita tarkat haut jokaiselle kategorialle (Backend, Frontend, I18N).
2. Jos löydät hallusinaation tai rikkomuksen, listaa raporttiin:
   - **Tiedosto & Rivi:**
   - **Löytynyt ongelma:** (Miksi se on hallusinaatio tai mandaatin vastainen)
   - **Korjausehdotus:**
3. **Varmuus ennen kaikkea:** Älä arvaa. Jos et ole täysin varma onko jokin metodi validi, nosta se esiin kysymyksenä raportissa. Emme tee korjauksia "mutulla".
4. Jos jokin kategoria on täysin puhdas, ilmoita se raportissa selkeästi.

Aloita auditointi nyt ja anna minulle ensimmäinen kattava raporttisi.