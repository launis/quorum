# Quorumin Tieteellinen ja Kaupallinen Positiointi (2024–2026)

Tämä dokumentti kuvaa Quorum-arkkitehtuurin suhteen tuoreimpaan kansainväliseen tekoälytutkimukseen (State-of-the-Art) ja kaupalliseen markkinakenttään.

---

## 1. Yhteenveto ja Strateginen Positio

Quorumin arkkitehtuuri sijoittuu suoraan vuosien 2023–2026 kansainvälisen tekoälytutkimuksen ja kaupallisen kentän kärkilinjalle. Se yhdistää kolme toisiaan täydentävää pilaria:
1. **Faktuaalinen ja looginen tarkkuus (FActScore & SAFE -evoluutio):** Tekstin dynaaminen lohkotus ja leksikaalinen ankkurointi.
2. **Kausaalinen graafirakenne (Graph of Thoughts & DAG Engine):** Syy-seuraussuhteiden, ehtolauseiden ja päätösketjujen matemaattinen mallinnus.
3. **Psykometrinen kognitiivinen diagnostiikka (CDM & BARS Guttman Waterfall):** Arvosanojen ja kompetenssipisteiden deterministinen laskenta ilman tekoälyn subjektiivista "mustan laatikon" arpomista.

---

## 2. Vertailu Tuoreimpaan Tieteelliseen Tutkimukseen (State-of-the-Art)

| Tutkimus / Teoria | Alkuperäinen Tutkimuslöydös | Miten Quorum Vie Tätä Eteenpäin |
| :--- | :--- | :--- |
| **FActScore**<br>*(Stanford & Univ. of Washington, EMNLP 2023)* | Purki tekstin atomisiksi faktoiksi ja laski yksinkertaisen tosi/epätosi-faktaprosentin tietolähdettä vasten. | FActScore tutkii vain lineaarisia yksittäisiä faktoja. Quorum lisäsi **kausaalisen DAG-verkon, ehdolliset N/A-tilat ja normatiiviset BARS-matriisit (Toulmin, Bloom, Kahneman)**. |
| **SAFE (Search-Augmented Factuality)**<br>*(Google DeepMind, 2024)* | Käytti kielimallia väitteiden pilkkomiseen ja automaattiseen validointiin hakukoneen avulla. | SAFE käyttää mustan laatikon enemmistöäänestystä. Quorum käyttää **bipartiittia graafia (`[B0]...[B53]` $\longleftrightarrow$ `tda_...`), Popperilaista falsifikaatiota ja nollahypoteesia**. |
| **Graph of Thoughts (GoT)**<br>*(Besta et al., 2024)* | Mallinsi kielimallin omaa päättelyprosessia suunnatulla verkolla (Tree of Thoughts -evoluutio). | GoT mallintaa vain LLM:n *omaa sisäistä ajattelua*. Quorum mallintaa **arvioitavan ihmisen ja tekoälyn vuorovaikutuksen kausaalisen rakenteen (`[B47]` $\rightarrow$ `[B48]`)**. |
| **System 2 Attention**<br>*(Meta AI / Weston et al., 2023)* | Karsi epäolennaisen kontekstin ennen päättelyä vähentääkseen attention dilution -häiriötä. | Quorum vie tämän arviointiin: **Paholaisen asianajaja -itsekritiikki ja epäsuorien havaintojen validointi** suoritetaan omassa erillisessä asiantuntijavaiheessaan. |
| **Cognitive Diagnostic Models (CDM / DINA)**<br>*(Psykometriikan teoria)* | Moniulotteinen taitojen ja riippuvuuksien mittaaminen koulutus- ja arviointijärjestelmissä. | Yhdistää LLM:n laadullisen analyysin **deterministiseen Guttman Waterfall -matematiikkaan ja neliöjuurivaimennukseen (`Square Root Dampening`)**. |

---

## 3. Vertailu Kaupalliseen Toimijakenttään

Kaupallinen kenttä jakautuu tällä hetkellä kahteen pääryhmään, joiden väliin Quorum luo täysin uuden kategorian:

```
                      【 KAUPALLINEN KENTTÄ 】
                                 │
     ┌───────────────────────────┴───────────────────────────┐
     ▼                                                       ▼
【 LLM-ARVIOINTITYÖKALUT 】                     【 AI COACHING & JOHTAMISALUSTAT 】
(Ragas, DeepEval, Arize Phoenix)                (BetterUp, CoachHub, Retorio)
• Keskittyvät RAG-teknisiin metriikoihin        • Keskittyvät yleiseen palautteeseen
  (esim. "faithfulness 0.85")                     (esim. "olit empaattinen")
• Eivät ymmärrä argumentaation rakennetta       • "Musta laatikko": ei todennettavaa
• Pisteet perustuvat usein arvaavaan              auditointiketjua tai kausaalisuutta
  kosinisamankaltaisuuteen                      • Ei sovellu viralliseen arviointiin
```

### Quorumin Erottavat Tekijät:

1. **Neuro-symbolinen arkkitehtuuri (LLM = Sensori, Python = Tuomari):**  
   Kaupalliset työkalut antavat usein LLM:n arpoa suoraan kokonaisarvosanan. Quorumissa kielimalli toimii vain **havainnoivana sensorina**, ja kaikki pisteytys, kynnysarvot ja logiikka ajetaan puhtaalla, deterministisellä Python-koodilla.
2. **Forensinen todennettavuus (EU AI Act Art. 13 & 14 -yhteensopivuus):**  
   Yksikään kaupallinen AI Coaching -alusta ei pysty osoittamaan, miksi tietty arvosana annettiin. Quorum pystyy tulostamaan **jokaisen pisteen kohdalta tarkan tekstilohkon (`[B47]`), asiantuntijaperustelun ja kriteerin**.
3. **FinOps & Prompt Caching -ylivoima:**  
   Siinä missä monimutkaiset moniagenttijärjestelmät (CrewAI, LangGraph) räjäyttävät API-kustannukset toistamalla samoja kyselyitä, Quorumin staattisen prefiksin kätkötys (**Prompt Caching**) mahdollistaa 12 syväasiantuntijan ajamisen murto-osalla tavanomaisista kustannuksista.

---

## 4. Arkkitehtuurin Ydinkomponentit

```
┌──────────────────────────────────────────┐       ┌──────────────────────────────────────────┐
│        DYNAAMINEN LÄHDETEKSTI            │       │        NORMATIIVINEN BARS-GRAAFI         │
│     (Purettu dynaamisiksi lohkoiksi)     │       │       (Toulmin / Bloom / Kahneman)       │
├──────────────────────────────────────────┤       ├──────────────────────────────────────────┤
│ [B35] Kontrafaktuaalinen lause           │◄─────►│ tda_6e53... (Kontrafaktuaalinen päättely)│
│ [B47] Käyttäjän korjauskehote            │◄──┐   │ tda_18fd... (Syötteen ja tuotoksen linkki│
│ [B48] Tekoälyn korjattu vastaus          │◄──┴──►│              - Overseer Taso 3)          │
│ [B53] Itsekritiikki ja reflektio         │◄─────►│ tda_9a08... (System 2 -deliberaatio)     │
└──────────────────────────────────────────┘       └──────────────────────────────────────────┘
                      │                                                  │
                      └────────────────────────┬─────────────────────────┘
                                               │
                                               ▼
                                 【 DETERMINISTINEN PISTEYTYS 】
                                 • Pythonin `TopologicalEvaluator`
                                 • Guttman Waterfall -laskenta
```

---

## 5. Johtopäätökset ja Kilpailuetu ("Unfair Advantage")

Quorumin arkkitehtuuri ratkaisee **tekoälypohjaisen arvioinnin suurimman ongelman: luotettavuuden, todennettavuuden ja kausaalisen läpinäkyvyyden**.

- **Tieteellisesti:** Se yhdistää FActScoren atomisen tarkkuuden, Graph of Thoughtsin kausaalisuuden ja psykometrisen CDM-matematiikan.
- **Kaupallisesti:** Se luo täysin uuden kategorian: **Auditoitavan kognitiivisen arvioinnin ja johtamisanalytiikan alustan**, jollaista suuretkaan toimijat (OpenAI, Google) eivät tarjoa suoraan laatikosta.
