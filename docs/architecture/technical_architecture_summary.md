# Tekninen arkkitehtuuri: Claim-Level Contextual Override & Zero-Variance -suojamuurit

Tämä dokumentti kuvaa Cognitive Quorumin kognitiivisen arviointimoottorin Phase 4 -tason teknistä arkkitehtuuria, joka on suunniteltu varmistamaan absoluuttinen päättelyn luotettavuus, oskilloinnin poisto ja läpinäkyvä XAI-tilannekuva (Explainable AI) loppukäyttäjälle.

---

## 1. Claim-Level Contextual Override (Kontekstuaalinen ohitusventtiili)

Järjestelmä erottaa toisistaan **System 1 (sokea semanttinen tiedonhaku)** ja **System 2 (deterministinen looginen päättely)** -tasot. 

Kun tekoälyagentti arvioi lähdemateriaalia atomitasolla, se saattaa kohdata tilanteen, jossa mekaaninen sääntö epäonnistuu dokumentissa olevan epäsuoran tai lieventävän asiayhteyden vuoksi. Tätä varten arkkitehtuuriin on rakennettu **Claim-Level Contextual Override (ohitusventtiili)**:

1. **Kaksoislukitusvaltuutus (Double-Lock Authorization)**:
   Ohituksen soveltaminen ei ole kielimallin itsenäisesti päätettävissä. Se vaatii poikkeuksetta kahden tason master-kytkinten aktiivisuutta:
   * **Workflow Switch** (`enable_contextual_overrides`): Globaali työnkulun ylätason kytkin.
   * **Assertion Switch** (`allow_contextual_override`): Kyseisen yksittäisen TDA-väitteen oma sääntökohtainen kytkin.
   
   Jos LLM palauttaa vastauksessaan `contextual_override = True`, mutta jompikumpi kytkimistä on `False`, System 2 -suojamuuri **hylkää ohituksen välittömästi** ja pakottaa arvioinnin palaamaan mekaaniseen evidenssitarkistukseen.

2. **Laiskuuden esto (Anti-Laziness Mandate)**:
   Mallin laiskuuden ja oikoteiden estämiseksi jokainen hyväksytty ohitus validoidaan Pydantic-kerroksessa:
   * **Pituusvaatimus**: Perustelutekstin (`semantic_reasoning`) on oltava vähintään 50 merkkiä pitkä.
   * **Spatiaalinen ankkurointi**: Perustelun on sisällettävä eksplisiittinen sijaintiviite lähdetekstiin (kuten *sivu*, *kappale*, *rivi*, *luku* tai *otsikko*).
   
   Mikäli nämä ehdot eivät täyty, Pydantic heittää `ValidationError`-virheen ja käynnistää korjaavan uudelleenyrityksen (`Self-Healing`).

---

## 2. System 2 Zero-Variance -suojamuurit & Shannonin entropia

Tekoälyn tuottaman luonnollisen kielen varianssi (oskillointi) pyritään minimoimaan matemaattisilla System 2 -suodattimilla. Vaikka kielimallin lämpötilaa nostettaisiin (`temperature = 0.3`) luovuuden stimuloimiseksi, järjestelmän deterministisen lopputuomion (PASS/FAIL) **Shannonin entropian on oltava tasan 0.000** ja **Fleissin Kappan tasan 1.0**.

Tämä saavutetaan seuraavilla suojamuureilla:
* **AST-arviointimoottori (`ast_evaluator.py`)**: Siirtää loogisen päättelyn kokonaan pois kielimallilta deterministiseen Python-koodiin.
* **Map-Merge-Evaluate -malli**: Eristää chunk-workerit ja ratkaisee ristiriidat deterministisellä *First-Wins* -törmäyksenestolla.
* **Pessimistinen DLQ-laskenta**: Dead-letter-queue -tilat käsitellään kiinteästi arvolla 0/1 ilman optimistista nimittäjän pienentämistä.

---

## 3. Spatial Slicing (Spatiaalinen paloittelu) ja Kronomnesia

**Kronomnesia (aikahäiriö)** estetään fyysisellä **Spatial Slicing (spatiaalinen paloittelu)** -tekniikalla ennen tekstin syöttämistä kielimallille:

* **Kronologinen tunnistus**: `ContextBuilder` tunnistaa säännöstä aikajanaan sidotun ehdon (esim. *"ennen vaihetta 2"*).
* **Fyysinen leikkaus**: Tekstistä etsitään vastaava rajamerkki (esim. `[PHASE 2]`), ja kaikki tämän rajan jälkeinen aineisto **leikataan mekaanisesti irti**.
* **Kaksikanavainen falsifikointi**: Koska leikatun alueen ulkopuolinen tapahtuma poistetaan fyysisesti, kielimalli raportoi siitä nollahavainnon (`evidence_found = False`). Python-kerroksen Boolean-inversio (`inverse_evidence = True`) kääntää tämän oikein `PASSED`-tilaksi. LLM ei voi nähdä tulevaisuuteen, mikä todistaa kronomnesian eston aukottomasti.

---

## 4. Visuaalinen XAI Audit Trail (Explainable AI) käyttöliittymässä

Jotta tekoälyn tekemät poikkeukselliset päätökset ovat täysin auditoitavissa, frontend-kerros (Flutter) renderöi kontekstuaaliset ohitukset selkeänä ja korostettuna visualisointina:

```
+-------------------------------------------------------------------+
|  💡 Tekoälyn semanttinen perustelu (Kontekstuaalinen ohitus):     |
|                                                                   |
|  "Tämä kriteeri on hyväksytty poikkeuksellisesti, koska sivun 12  |
|   kappaleessa 3 todettu lieventävä seikka kumoaa..."             |
+-------------------------------------------------------------------+
```

* **Mekaanisen sitaatin korvaaminen**: Kun `contextual_override` on `true`, käyttöliittymä poistaa normaalin *"Ote alkuperäisestä tekstistä"* -laatikon ja korvaa sen korostetulla, oranssilla/amber-reunaisella perustelulaatikolla.
* **Lokalisaatiopariteetti**: UI-merkkijonot haetaan täysin lokalisoituna `AppLocalizations`-luokan kautta (`reportSemanticExplanationTitle`), varmistaen Zero-Math ja No-Magic-Strings -vaatimusten ehdottoman toteutumisen.
