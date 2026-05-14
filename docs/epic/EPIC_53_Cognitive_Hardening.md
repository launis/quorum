# Epic 53: Cognitive Hardening & Anchor Tuning (TDA Rule V4)

## 1. Yhteenveto ja Tavoite (Objective)
Tämä Epic on suora jatkumo Epic 52:lle. Kun Epic 52 pakotti taustajärjestelmän (Map-Reduce, ChunkAccumulator, TaskGroups) 100% deterministiseksi, huomasimme kahden identtisen ajon välillä **18.9% stokastisen "haamuvarianssin" (Mismatches)**. 

Syväanalyysi paljasti, että varianssi ei johdu koodista, vaan **Epic 51:n aikana luotujen sääntöjen (tda_assertions) semanttisesta epämääräisyydestä**. Kielimalli (LLM) pakotettiin arvaamaan subjektiivisia käsitteitä (kuten "robusti" tai "ylivoimainen"), ja se sekoitti käyttäjän ja tekoälyn roolit toisiinsa. 

**Tavoite:** Tämä dokumentti toimii virallisena korjauksena ja päivityksenä dokumenttiin `epic51_seed_data_tda_refactor.md`. Määrittelemme tässä uudet **"Hardened V4" -säännöt (Säännöt 16, 17 ja 18)**, jotka poistavat viimeisenkin tulkinnanvaraisuuden tekoälyn promptauksesta. Tämän jälkeen päivitämme matriisit (erityisesti ne, joissa varianssi havaittiin) vastaamaan näitä uusia V4-mandaatteja.

---

## 2. Arkkitehtuuriset Mandaatit V4 (Epic 51 Päivitykset)

> [!IMPORTANT]
> **V4 KOGNITIIVINEN FILOSOFIA (Zero-Interpretation Doctrine):** Varmista sääntöjen 16–18 toimivuus käsittelemällä `ai_rule_description` -kenttiä ikään kuin ne olisivat säännöllisiä lausekkeita (Regex) tai Python-funktioita luonnollisen kielen muodossa. Kielimallilta EVÄTÄÄN oikeus tulkita, ja sille annetaan vain oikeus suorittaa tarkka "If-This-Then-That" -tarkistuslista.

Nämä säännöt **täydentävät ja yliajavat** `epic51_seed_data_tda_refactor.md` -dokumentin aiempia ohjeita. Kun tekoäly jatkossa suorittaa refaktorointia, sen on huomioitava alkuperäisten 15 säännön lisäksi nämä kolme uutta absoluuttista V4-mandaattia.

### 16. EHDOTON ROOLIAUTENTIKOINTI JA KENTTÄ-ANKKUROINTI (Strict Role & Field Attribution)
**Ongelma Epic 51:ssä:** Tekoäly luki käyttäjän (User) itsekritiikin ("Ennakoin, että en saa hyvää tulosta") ja tulkitsi sen vahingossa tekoälyn (Assistant) episteemiseksi nöyryydeksi, mikä käänsi atomin `tda_b180a5f8` tuloksen väärinpäin.
**Mandaatti V4 (Negative Prompting & Prefix Targeting):** Säännössä on EHDOTTOMASTI määriteltävä puhujan rooli ja sidottava se suoraan tekstissä käytettäviin roolietuliitteisiin (`user:` ja `ai:`). Älä vain kerro, mitä etsiä, vaan rajaa eksplisiittisesti pois kielletyt etuliitteet. Ota huomioon myös tekstit, joista etuliitteet puuttuvat.
* 🚫 **KIELLETTY:** *"Find a sentence where limits of the analysis are admitted."* (Liian epämääräinen, altis roolisekaannukselle)
* ✅ **SALLITTU:** *"REQUIRED TARGET: Find evidence. If role prefixes (`user:`, `ai:`) exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist (e.g. unified report), you may scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields (e.g. `reflection_text`) are automatically REJECTED."*

### 17. SUBJEKTIIVISTEN ADJEKTIIVIEN KIELTO (The Ban of Subjectivity)
**Ongelma Epic 51:ssä:** Säännöissä käytettiin laatusanoja ("robusti kausaalisuhde", "ylivoimainen päättely", "mestarillinen suoritus"). LLM:n Ajo 1 piti tekstiä "robustina", mutta Ajo 2 päätti, ettei se ollut "tarpeeksi robusti".
**Mandaatti V4 (Operaationalisointi & Kynnykset):** Kaikki subjektiiviset laatusanat ja epämääräiset adjektiivit on EHDOTTOMASTI KIELLETTY mikrosäännöissä. Mielipiteet on muutettava boolen logiikaksi (True/False) tai määrällisiksi kriteereiksi (Thresholds). Kun arvioit tekstin yleispätevyyttä, älä sido sääntöä yksittäisen ajon sanastoon, vaan käytä yleisiä muuttujia. Voit myös nimenomaisesti kieltää mallia arvioimasta laatua.
* 🚫 **KIELLETTY (Subjektiivinen):** *"Find a robust causal relationship or a generic argument."*
* ✅ **SALLITTU (Fysikaalinen/Kvantitatiivinen):** *"Extract a causal chain containing at least three distinct steps (e.g. A -> B -> C). Reject if only two steps exist."*
* ✅ **SALLITTU (Asiasanaluettelot / Yleiskäyttöiset):** *"Extract reasoning that DOES NOT contain any domain-specific proper nouns (e.g. specific organizations, years, names). If it contains them -> REJECT. If absent -> ACCEPT."*
* ✅ **SALLITTU (Toiminnallinen rajaus / Action Boundary):** *"BANNED CONCEPTS: Do not evaluate 'flawlessness' or 'mastery'. STEP 1: Find a command that creates a new conceptual architecture. STEP 2: If it creates a new top-level concept -> ACCEPT. If it is merely a mechanical style correction -> REJECT."*
* ✅ **SALLITTU (Implisiittisen käsitteen operationaalistaminen / Banned Logic):** *"BANNED LOGIC: Do not wait for explicit dismissive language (e.g. 'regardless'). STEP 1 (Lexical Anchor): Find an absolute sentence (e.g. 'the only way'). STEP 2 (Bounding Box): Scan the paragraph. If the absolute claim is presented without refuting alternatives with data in the same paragraph -> ACCEPT (interpreted as dismissal). Otherwise -> REJECT."*

### 18. EKSPLISIITTISEN LAISKUUDEN TORJUNTA (Bounding Boxes & Lexical Anchors)
**Ongelma Epic 51:ssä:** Atomi `tda_8b03f091` ("Eettisesti kyseenalaiset AI-ratkaisut...") hyväksyttiin Ajossa 1, mutta Ajossa 2 LLM sivuutti koko lauseen ja jätti kentän tyhjäksi (FAILED). LLM iski laiskuus ja se lopetti tekstin haravoimisen kesken.
**Mandaatti V4:** Kun haetaan tiettyä harvinaista lausetta isosta massasta, LLM:lle on annettava rakenteelliset rajauslaatikot (Bounding Boxes), jotka pakottavat mallin navigoimaan fyysisessä dokumenttirakenteessa. Käytä lexikaalisia skannausankkureita ennen semanttista hakua.
* 🚫 **KIELLETTY:** *"Find a mention of an ethical constraint."*
* ✅ **SALLITTU (Vaiheistettu skannaus):** 
  *"STEP 1: Locate the Markdown header `## Evolution to Conflict`. STEP 2: Scan the text downwards from this header until the next header. STEP 3: Find the exact term 'irreversible' within this Bounding Box. Matches outside are rejected."*
* ✅ **SALLITTU (Yhdistetty V4-Mandaatti dynaamisilla kentillä):** 
  *"REQUIRED TARGET: Scan ONLY the Target Data, regardless of its format or dynamic field name. BANNED SOURCES: Never read matches from user input fields, instructions or reflections. STEP 1: Find absolute anchor words ('always', '100%'). STEP 2: If found, check if the same paragraph contains empirical measurement data. If no data exists -> ACCEPT (flaw proven). If anchor word is missing -> REJECT."*

---

## 3. Toteutuksen Vaiheet (Epic 53 Työnkulku)

### Phase 1: Varianssimatriisien Täsmällinen Eristäminen ja Trackerin Luonti
* Epic 53 koskee **vain ja ainoastaan** `seed_data.json` -tiedoston sisällön (TDA-sääntöjen) refaktorointia. Kaikki arkkitehtuuriset muutokset kuuluvat muihin epiceihin.
* Luodaan skripti (esim. `scratch/diff_executions.py`), joka lukee läpi kolme aiempaa ajoa (`exe_fd76e0...`, `exe_a9168c...`, `exe_e3b7bc...`).
* Skripti poimii tarkalleen ne 43 atomia (ja niiden emo-matriisit), joissa tulokset heittivät (mismatches).
* Skripti generoi automaattisesti uuden seurantatiedoston `epic53_matrix_tracker.md`, jonne nämä 43 ongelmatapausta kirjataan tilalla `[NOK-V4]`.

### Phase 2: "V4-Kovetus" (Cognitive Friction Refactor)
* Vastaava Generaattori-Kriitikko -looppi kuin Epic 51:ssä, mutta nyt tekoäly analysoi vanhan matriisin säännöt ja etsii niistä **V4-sääntörikkomuksia** (subjektiivisia adjektiiveja, puuttuvia roolimäärittelyjä).
* Tekoäly ajaa Python-skriptin (`scratch/refactor_v4.py`), joka siivoaa säännöistä adjektiivit ja korvaa ne laskettavilla/fyysisillä kriteereillä ja lisää ehdottomat roolikiellot (BANNED: User).

### Phase 3: Determinismin Verifikaatio (Test Driven Regression)
* Kun ongelmallisten matriisien säännöt on refaktoroitu V4-tasolle, ajetaan täsmälleen sama dokumentti läpi vähintään kaksi kertaa uudelleen.
* Tavoitteena on nostaa determinismi-aste nykyisestä 76.76%:sta yli **95.0%**.

## 4. Definition of Done (DoD)
- Automaattisesti generoitu `epic53_matrix_tracker.md` on luotu ja se sisältää tarkalleen ne 43 ongelma-atomia/matriisia.
- Näiden matriisien `tda_assertions` -kentistä on auditoitu ja poistettu kaikki subjektiiviset adjektiivit (Rule 17).
- Rooleja koskevat säännöt on sidottu eksplisiittisesti (AI vs. User) (Rule 16).
- Sääntöjen kontekstiankkurit on vahvistettu laiskuuden estämiseksi (Rule 18).
- Ristiinajotestin determinismi-aste ylittää 95.0%.

## 5. Ristiinajon Juurisyyanalyysi (RCA)

Tässä on kolme todellista esimerkkiä äskeisestä 3-way ristiinajosta (`fd7`, `a91`, `e3b`), jotka todistavat V4-mandaattien absoluuttisen tarpeen.

### RCA 1: Subjektiiviset adjektiivit murtavat determinismin (Rule 17)
* **Atomi:** `tda_de0afa003e6740ce`
* **Vanha sääntö:** *"EXTRACT definitive evidence of 'System 2' oversight where the user enforces systemic architectural rules flawlessly..."*
* **Mitä tapahtui:** 
  * Ajo 1 sanoi [FAILED], koska käyttäjän ohjaus oli "strategista mutta ei syvällistä System 2 -tasoa".
  * Ajo 2 sanoi [PASSED], koska käyttäjä "asetti selkeän systeemisen säännön komennollaan".
  * Ajo 3 sanoi [FAILED], koska käyttäjän prosessi ei ollut "virheetön" (flawless).
* **Diagnoosi:** Kielimalli joutui arvuuttelemaan, mitä subjektiiviset sanat "flawlessly" ja "definitive" tarkoittavat. V4 Sääntö 17 (Subjektiivisten adjektiivien kielto) korjaa tämän korvaamalla sanan "flawless" fyysisellä vaatimuksella (esim. "Sisältää suoran komennon, joka eksplisiittisesti kieltää tekoälyn oletuskäytöksen").

### RCA 2: Kognitiivinen tulkintaero epämääräisissä konsepteissa (Rule 17)
* **Atomi:** `tda_0ea6db6e838946f4` (Bounty Hunter)
* **Vanha sääntö:** *"Scan for non-specific justifications. Locate a sentence where the explanation could apply to any generic situation..."*
* **Mitä tapahtui:** 
  * Ajo 1 sanoi [FAILED], koska se löysi mielestään yleispätevän lauseen ("edellyttää tulevaisuusajattelua ja muutoskykyä").
  * Ajot 2 ja 3 sanoivat [PASSED], koska ne kokivat saman lauseen "ankkuroiduksi raportin otsikoihin".
* **Diagnoosi:** Mikä on "yleispätevää" (generic)? Se on mielipide. V4 Sääntö 17 pakottaa muuttamaan tämän fyysiseksi säännöksi: *"Etsi perustelu, joka ei sisällä yhtäkään domain-spesifiä erisnimeä"*. Tämä ei jätä tulkinnanvaraa.

### RCA 3: Puhujan roolin sekoittuminen (Rule 16)
* **Ilmiö useissa atomeissa:** Säännössä käsketään etsimään "episteemistä nöyryyttä" tai "virheen myöntämistä". Tekoäly lukee ihmisen (User) kirjoittaman promptin ja tulkitsee sen tekoälyn (Assistant) tuottamaksi lauseeksi.
* **Diagnoosi:** V4 Sääntö 16 korjaa tämän pakottamalla jokaisen tällaisen säännön alkuun: *"REQUIRED: Etsi tekoälyn (Assistant) tuottamasta tekstistä... BANNED: Älä koskaan poimi ihmisen (User) omia lauseita"*.

Näiden todisteiden valossa on selvää, että 18.9% varianssi ei johdu lämpötilasta, vaan promptien sisältämästä semanttisesta joustovarasta. Epic 53 (V4-Kovetus) korjaa tämän rautalangalla.
