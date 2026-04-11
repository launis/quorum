# EPIC 20: Phase 7 - Cognitive Diagnostic Dampening (CDM/DINA)
**Työtila:** Quorum Backend V2
**Tavoite:** Muuttaa staattisen konjunktiivisen "Hybrid Cap" -leikkurin (Vesiputousmalli) laadusta moderniin tieteelliseen **Progressive Dampening** (Dynaaminen kerroinvaimennus) arkkitehtuuriin. Tämä vastaa DINA-mallia (Deterministic Inputs, Noisy "And" gate).

## 1. Tausta ja Ongelmanmäärittely (Miksi muutetaan)
Nykyinen `waterfall_scoring_hook` käyttää kovaa 75 % vesiputouskynnystä, jolla se määrittää `floor_score`-kattotason. Tästä seuraa arvioinnin ilmiö nimeltä "Floor ceiling effect":
- Jos Taso 2 suoritetaan täysin oikein (100 %) ja Taso 4 & 5 saavat paljon osumia LLM-hallusinaatioiden/jargonin takia (Sycophancy), Painotettu keskiarvo ampuu korkealle (esim. 4.2).
- Mutta jos matkalla Taso 3 sai vain 65 % osumia (Putous murtui lukuun 2.0).
- Järjestelmä leikkaa säälimättömästi `min(4.2, 2.0 + 1.0) = 3.0.`
Tämä tuhoaa jatkuvan desimaalikehityksen ja tuntuu siltä, kuin arvosanat "putoaisivat aina alaspäin tasalukuun". Ylätason tärkeitäkin osumia heitetään pois mielivaltaisen kynnysleikkurin vuoksi.

## 2. Ratkaisuarkkitehtuuri: Progressive Dampening (Kerrannainen Vaimennus)
Poistutaan `min(Weighted, Floor+1)` kaavasta ja siirrytään Markov-ketjumaiseen todennäköisyyskerrotimeen. Jokainen taso (alkaen tasosta 1) laskee oman osumaprosenttinsa (esim. 0.90) ja ohjaa tämän arvon *vahvistimena* (Modifier) seuraavalle tasolle. Mitä heikommin pohjat on rakennettu, sitä raskaammin ylätason ansiot kutistuvat (mutta ne eivät putoa pyöreään nollaan).

### Matemaattinen toteutusmalli
Arvosanan aloitustaso on aina `scale_min` (esim. 1.0).
Kerrannainen virta `modifier` käynnistyy arvosta `1.0`.

```python
# Esimerkki algoritmista
achieved_score = scale_min
modifier = 1.0
prev_level = scale_min

for level in sorted_levels:
    hit_rate = hits / total
    
    if level == scale_min:
        # Alimman tason (esim. 1.0) onnistuminen ei lisää pisteitä,
        # vaan määrittää alkuluottamuksen.
        modifier = hit_rate
    else:
        # Vain alemmilta tasoilta selvinnyt "virta" päästää uudet pisteet läpi
        step_value = (level - prev_level)
        achieved_score += step_value * hit_rate * modifier
        
        # Kerrotaan vahvistin seuraavaa tasoa varten
        modifier = modifier * hit_rate 
        
    prev_level = level
```

## 3. Vaadittavat koodimuutokset (Toteutusaskeleet)

### Askel 3.1: Matematiikkamoduulin laajennus
**Tiedosto:** `c:\src\quorum\backend_v2\utils\math_utils.py`
- [x] Tuo sisään uusi funktio `calculate_progressive_dampening_score(level_stats, scale_min, scale_max)`.
- [x] Varmista, että palautusarvo kiinnitetään turvallisesti rajoihin `max(scale_min, min(scale_max, achieved_score))`.

### Askel 3.2: Hookin pisteytyslogiikan vaihtaminen
**Tiedosto:** `c:\src\quorum\backend_v2\hooks\scoring.py`
- [x] Etsi `waterfall_scoring_hook` ja korvaa askeleen "3. Hybrid Calculation" logiikka.
- [x] Laske yhä `floor_score` ja `weighted_score` **pelkkää lokitusta varten**, jotta XAI-raporteissa voidaan verrata tuloksia: 
  * "Raaka painotettu olisi ollut 4.5, mutta puutteet perusteissa vaimentivat lopullisen tuloksen arvoon 3.42".
- [x] Aseta varsinaiseksi tallennettavaksi uusiarvoksi `capped_score = progressive_dampening_score`.

### Askel 3.3: Selitystekstien (XAI) uudelleenkirjoitus
**Tiedosto:** `scoring.py` (`waterfall_scoring_hook`)
- [x] Muuta lokiin (justification) rakentuva tuloste vastaamaan uutta virtauslaskentaa. Esim:
  - `- **Taso 1:** 15/15 (100% - Kognitiivinen virta: 1.00)`
  - `- **Taso 2:** 13/15 (86% - Kognitiivinen virta heikkenee: 0.86)`
  - `- **Taso 3:** 6/15 (40% - Kognitiivinen virta heikkenee: 0.34)`
  - `- **Taso 4:** 14/15 (93% - Osumia vaimennettiin virran mukaisesti)`
  - `**Lopullinen CDM-Arvosana:** 2.8`

## 4. Testaus ja Validointi (Quality Gates)
- [x] **Fail-Fast Varmistus:** Ei muutoksia Pydantic V2 sääntöihin (tämä on pelkkä kaavapivitys Float-arvoille).
- [x] Yksikkötestit (`tests/backend_v2/test_math_utils.py`): Lisää testi, jossa Level 1 on 10%, Level 5 on 100%. Varmista, että Level 5:n 100% tuottaa arvosanaan vain mikroskooppisen lisän, eikä kaarru 5.0 suuntaan.
- [x] Yritä saavuttaa yli tason 1 tulos ilman tason 1 atomeita. Täytyy matemaattisesti olla mahdotonta.

## 5. UI Parity (Zero-Math sääntö)
Tämä backendin muutos **ei riko Flutterin taulukoita**.
Flutter lukee edelleen pelkkää normalisoitua 0-1 X/Y-arvoa, joka saadaan `.py` skaalauksesta. Tämä muutos ainoastaan poistaa tasalukuputoamiset graafeista sumentamalla siirtymät luonnollisemmin, eli Frontend -päivityksiä ei tarvita!
