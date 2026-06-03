# EPIC 71: TDA Rule Disambiguation & Measurement Reliability Hardening

## 1. Yhteenveto & Tavoite (Executive Summary)

Quorum V2:n kahden identtisen ajon vertailu (N=185 atomia, M=2 ajoa) paljasti **87% Self-Consistency** ja **Cohen's κ = 0.72** ("Substantial Agreement"). Vaikka tulos on akateemisesti hyvä, 24 epävakaata atomia (13% varianssi) ryhmittyvät **kolmeen systemaattiseen juurisyyluokkaan**, jotka ovat korjattavissa TDA-sääntöjen disambiguaatiolla.

**Tavoite:** Nostaa mittauksen luotettavuus κ ≥ 0.85 ("Almost Perfect Agreement") eliminoimalla systemaattiset tulkintaepäselvyydet TDA-säännöistä.

### Empiirinen Pohja

| Mittari | Nykytila | Tavoite |
|---------|---------|---------|
| Cohen's κ | 0.7195 | ≥ 0.85 |
| Self-Consistency | 87.03% | ≥ 93% |
| Mismatch-atomit | 24/185 (13%) | ≤ 10/185 (5.4%) |
| Avg. Shannon Entropy | 0.1297 | ≤ 0.06 |

### Datalähteet

- **Analyysiskripti:** `scratch/diff_executions.py`
- **Raakadata:** `scratch/mismatch_traces_raw.md`

---

## 2. Juurisyyanalyysi — Kolme Systemaattista Klusteria

### Klusteri A: Sääntely-Viittausten Domain-Scope (5 atomia, 21%)

**Ongelma:** Useat TDA-säännöt flippasivat, koska ne käsittelivät samaa sääntely-viittausta lähdedokumentissa, mutta eivät osanneet päättää, lasketaanko se "methodology link":ksi, "benchmark":ksi, "formal citation":ksi vai "security standard":ksi.

**Seuraus:** LLM tulkitsee saman regulaatioviittauksen eri käsitteenä eri kerroilla, koska TDA-säännöt eivät rajaa, minkä tyyppinen viittaus täyttää kunkin extraction condition -ehdon.

| Sääntöjen lukumäärä | Vaikutus |
|---------------------|----------|
| 5 atomia | Sama sääntely-viittaus tulkitaan eri käsitteenä eri ajoissa |

**Korjaus — `<disambiguation>` -protokolla:**

Lisätään sääntöihin domain-scope -rajaava disambiguaatiolohko:

```xml
<disambiguation>
  Regulatory framework references count as formal citations ONLY if a 
  specific sub-article, clause, or numbered principle is cited (e.g., 
  "Article 29b(2)", "ISO 27001 §6.1.2"). Generic regulatory mentions 
  without sub-clause specificity DO NOT satisfy methodology link, benchmark, 
  formal citation, or security standard extraction conditions.
</disambiguation>
```

---

### Klusteri B: Retorinen Reframing-Pattern (6 atomia, 25%)

**Ongelma:** Useat atomit flippasivat, koska ne käsittelivät samaa retorista rakennetta, jossa konsepti uudelleenkehystetään negatiivisesta positiiviseksi ("not just X, but Y").

Tämä **retorinen reframing** (uudelleenkehystäminen) EI ole:
- Vasta-argumentti (counter-argument)
- Dialektinen synteesi (thesis + antithesis → synthesis)
- Vaihtoehtoisen mallin kumoaminen (model dismantling)
- Absoluuttinen johtopäätös (absolute conclusion)

Mutta LLM tulkitsee sen jokaisena näistä satunnaisesti eri ajoissa.

| Sääntöjen lukumäärä | Vaikutus |
|---------------------|----------|
| 6 atomia | Sama reframing-rakenne laukaisee eri sääntöjä eri ajoissa |

**Korjaus — Reframing-disambiguaatioprotokolla:**

```xml
<disambiguation>
  REFRAMING EXCLUSION: Rhetorical reframing patterns where a concept is 
  repositioned from negative to positive framing ('not just X, but Y') are 
  STYLISTIC DEVICES, not argumentative structures. Do NOT extract them as:
  - counter-arguments (they do not argue AGAINST anything)
  - dialectical syntheses (they do not reconcile two opposing theses)
  - alternative model dismantling (they do not present a separate model)
  - absolute conclusions (they are framing choices, not logical claims)
  If a reframing pattern is the ONLY candidate match, return JSON null.
</disambiguation>
```

---

### Klusteri C: Moniosumatilanteen Priorisointi (3 atomia, 13%) — EI KORJATTAVISSA

**Ongelma:** LLM saa koko syötetekstin ja skannaa kaiken. Kun pitkässä dokumentissa on **useita kandidaattiosumia** eri kohdissa, LLM:n valinta minkä osuman se raportoi `exact_quote`:na on ei-deterministinen. Eri osumien ympäristökonteksti voi johtaa eri TRUE/FALSE -tulokseen.

Esimerkki: Sääntö etsii "positiivista arviointia ilman rajoitusmainintaa". LLM löytää kaksi kandidaattia. Run 1 raportoi osuman A (jonka ympäristössä on rajoitusmaininta → FALSE). Run 2 raportoi osuman B (jonka ympäristössä ei ole → TRUE). Molemmat ovat valideja skannauksia — ongelma on priorisoinnissa, ei kattavuudessa.

**Miksi tätä EI voida korjata TDA-säännöissä:** Moniosumatilanteen deterministinen priorisointi vaatisi arkkitehtuuritason muutoksia (esim. "raportoi KAIKKI osumat ja valitse konservatiivisin"), ei sääntötason disambiguaatiota.

**Luokittelu:** Nämä 3 atomia ovat **aitoja rajatapauksia** (Osio 3). Ne ovat hyväksyttävä varianssilähde, johon voidaan puuttua vain arkkitehtuuritasolla, ei sääntötasolla.

## 3. Jäljelle Jäävät Aidot Rajatapaukset (13 atomia, 54%)

Loput 13 mismatchista (ml. Klusteri C:n 3 atomia) ovat **aitoja rajatapauksia**, joissa LLM:n tulkinta on perustellusti eri. Esimerkkityyppejä:

- Syntaktinen ankkuri löytyy viereisestä kappaleesta — kuuluuko "surrounding section":iin?
- Dialektinen päättely ilman eksplisiittistä "hylkäsin A koska B" -rakennetta
- Risk + mitigation samassa kappaleessa mutta eri lauseissa
- Numeroitu lista + synteesiverbit samassa kappaleessa
- Dynaamisten syötetekstien scope-epäselvyys (LLM skannaa eri tekstiosaa eri ajoissa)

Nämä eivät ole korjattavissa ilman TDA-sääntöjen perustavanlaatuista uudelleenkirjoittamista tai arkkitehtuuritason muutoksia. Ne edustavat **mallin luonnollista epävarmuutta** rajatapauksissa ja ovat hyväksyttävä varianssilähde κ = 0.85+ tasolla.

---

## 4. Toteutuksen Vaiheet

### Vaihe 1: Disambiguaatioprotokollien Injektio (Klusteri A + B)
- Muokataan 11 TDA-sääntöä `seed_data.json`:ssa
- Lisätään `<disambiguation>` -lohkot sääntöjen `ai_rule_description` -kenttiin
- Ajetaan `run_seed.py` uudelleen

### Vaihe 2: Verifiointikierros
- Ajetaan sama workflow uudelleen (2 uutta ajoa)
- Verrataan `diff_executions.py`:llä uudet metriikat
- Tavoite: κ ≥ 0.85, mismatch ≤ 13 atomia

### Vaihe 3: Regressiotestaus
- Varmistetaan, että korjaukset eivät muuta olemassaolevien atomien peruslogiikkaa
- Ajetaan kaikki olemassa olevat testikeisit läpi uusilla säännöillä

---

## 5. Onnistumisen Kriteerit

- [ ] Cohen's κ ≥ 0.85 ("Almost Perfect Agreement") kahdella peräkkäisellä ajolla
- [ ] Self-Consistency ≥ 93%
- [ ] Klusteri A (sääntely-scope) mismatchit eliminoitu: 5 → 0
- [ ] Klusteri B (reframing) mismatchit eliminoitu: 6 → 0
- [ ] Jäljelle jäävät mismatchit ≤ 13 (aidot rajatapaukset + scope-puutteet)
- [ ] Olemassaolevat testit eivät regressoidu

---

## 6. Riskit ja Varotoimet

### Riski 1: Over-Disambiguation
Liian tiukka disambiguaatio voi estää oikeat havainnot tapauksissa, joissa viitataan spesifiseen artiklaan tai lausekkeeseen.

**Varotoimenpide:** Disambiguaatio rajataan "generic references" -tasolle. Spesifiset artikkeli/clause-viittaukset hyväksytään edelleen.

### Riski 2: Reframing-Pattern Ylimääräinen Karsintu
Jos reframing-pattern kielletään aina, voidaan menettää aitoja vasta-argumentteja jotka käyttävät samaa rakennetta.

**Varotoimenpide:** Disambiguaatio koskee VAIN tapauksia, joissa reframing on AINOA kandidaattiosuma. Jos muitakin osumia löytyy, reframing-ehto ei aktivoidu.

### Riski 3: Seed Data Mutation
TDA-sääntöjen muokkaus `seed_data.json`:ssa vaatii uudelleenseediä.

**Varotoimenpide:** Noudatetaan Quorum V2:n seed-protokollaa (muokkaa `seed_data.json` → `run_seed.py` → verifioi).
