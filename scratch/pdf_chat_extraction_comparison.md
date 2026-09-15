# Keskustelulogien Roolijakauma ja Erotteluraportti: Alkuperäiset Tuotanto-ohjelmistot

**Päivämäärä:** 2026-09-15  
**Ajotapa:** Testattu Quorumin aidoilla tuotantokomponenteilla:
1. `scripts/run_e2e_variance_test.py` (`load_inputs_from_path`)
2. `backend_v2.services.ingress.multi_channel_ingress_service.MultiChannelIngressService` (Kaikki kanavat 1–5)
3. `backend_v2.services.chat_normalizer.ChatNormalizerService`
4. `backend_v2.services.ingress.pdf_chat_extractor.PdfChatExtractorService`

---

## 1. Yhteenveto ja Perusmetatiedot Aidoilla Tuotantoputkilla

| Ominaisuus | SITRA (`data/test_inputs_sitra`) | JWDATAT (`docs/jwdatat`) |
| :--- | :--- | :--- |
| **Pääasiallinen keskustelutiedosto** | `keskusteluhistoria SITRA.pdf` (16 sivua) | `keskusteluhistoria.pdf` (17 sivua) |
| **Muut hakemiston syötteet** | `lopputuote sitra.pdf`, `Reflektiodokumentti sitra.pdf`, `Tehtävä 3 - sitra.pdf` | `lopputuote.pdf`, `reflektiodokumentti.pdf` |
| **PDF Title** | `Google Gemini` | `Etätyön vaikutukset: Talous, HR, Strategia - Google Gemini` |
| **Alkuperä** | Chrome Skia / Google Gemini | Chrome Skia / Google Gemini |
| **Tuotantoputken vuorot yhteensä** | **21 vuoroa** | **14 vuoroa** |
| **Käyttäjän vuorot (USER)** | 10 kpl | 7 kpl |
| **Tekoälyn vuorot (AI)** | 11 kpl | 7 kpl |
| **Käyttäjän sanamäärä (`user_only.md`)** | **113 sanaa** (1,9 % kokonaissanoista) | **211 sanaa** (6,1 % kokonaissanoista) |
| **Tekoälyn sanamäärä (`ai_only.md`)** | **5 334 sanaa** (`variance_test` -putki) / **5 710 sanaa** (suora PDF-muisti) | **3 254 sanaa** (100 % muuttumaton molemmilla tavoilla) |
| **Vuoro 0** | ⚠️ `[AI]: Gemini Chat` (2 sanaa, haamuvuoro) | ✅ `[USER]: Olen tekemässä selvitystä...` (68 sanaa) |

---

## 2. Läpimurtohavainto: 376 Sanan Eron Juurisyy Löydetty

Vertailussa `diff_report_2026-09-14_1319.md` todettiin, että ajossa 1 tekoälyvuoroissa oli **5 334 sanaa** ja ajossa 2 **5 710 sanaa** (+376 sanaa).

Kun ajoimme tiedoston täsmälleen tuotanto-ohjelmistoilla, syy selvisi kiistattomasti:
- `scripts/run_e2e_variance_test.py` kutsuu rivillä 285 kirjastoa `pymupdf4llm.use_layout(False)`.
- Tämä globaali asetus muuttaa PyMuPDF:n taulukkolukijan tilaa siten, että taulukoiden solujen sisällä sanojen välit tiivistyvät ilman välilyöntejä (esim. `Luonnonkantokyky` sanan `Luonnon kantokyky` sijaan).
- Tämän seurauksena `run_e2e_variance_test.py` tuottaa täsmälleen **5 334 sanaa**!
- Kun taas `MultiChannelIngressService` lukee PDF-tiedoston suoraan binäärinä ilman `pymupdf4llm`-kutsun sivuvaikutusta, välilyönnit säilyvät ja sanamäärä on täsmälleen **5 710 sanaa**.
- **Käyttäjän sanamäärä (`user_only.md`) on molemmissa tapauksissa täsmälleen identtinen 113 sanaa.**

---

## 3. OpenAI (ChatGPT) vs. Google Gemini -Tekstimuotojen Vertailu Tuotantoputkessa

Ajoimme `MultiChannelIngressService`:n läpi myös molempien tekoälyjen vakiomuotoiset leikepöytäsyötteet:

### 3.1 OpenAI (ChatGPT) Leikepöytämuoto
```text
You:
Miten sitra tämän näkee raporttien perusteella?

ChatGPT:
Sitran megatrendiraporttien perusteella näkymä tulevaisuuteen on siirtynyt kohti kasautuvia kriisejä.
```
- **Tuotantokanava:** Kanava 4 (`ChatNormalizerService.try_parse_fast_path`).
- **Tulos:** **Osuu välittömästi (Fast-Path Match: TRUE)**.
- **Latenssi:** < 1 ms (deterministinen muistijäsennys).
- **Vuorot:** Täsmälleen 4 vuoroa (2 USER, 2 AI).

### 3.2 Google Gemini Leikepöytämuoto
```text
Keskustelu Geminin kanssa

Miten sitra tämän näkee raporttien perusteella?

Gemini
Sitran megatrendiraporttien perusteella näkymä tulevaisuuteen on siirtynyt kohti kasautuvia kriisejä.
```
- **Tuotantokanava:** Kanava 4 epäonnistuu kaksoispisteiden puuttuessa (**Fast-Path Match: FALSE**).
- **Fallback:** Putoaa kanavalle 5 (`ChatParserService.parse_pasted_chat`), joka tekee LLM-kutsun Gemini Flashille.
- **Seuraus:** Aiheuttaa verkkoviiveen ja mahdollisen lämpötila-/poimintavaihtelun.

---

## 4. Miksi Tekoälymallit Lukevat Tämän Eri Tavoilla Arviointivaiheessa?

Kun nämä erotellut virrat syötetään matriisin arviointiputkeen (`prompt_compiler.py` -> LLM):
1. **OpenAI GPT-4o:**
   - Kärsii "Echo Parroting" -ilmiöstä. Kun käyttäjä antaa lyhyen ohjeen (*"koosta raportti, jossa supermegatrendit ovat pääosassa"*), GPT-4o attribusoi aiheen monimutkaisuuden käyttäjän omaksi Systeemi 2 -kognitioksi ja Bloomin taksonomian hallinnaksi.
2. **Google Gemini (1.5/2.0):**
   - Noudattaa järjestelmäkehotteen XML-rajoja (`<user_payload>` vs. `<ai_draft_context>`) kirjaimellisesti. Koska käyttäjä kirjoitti vain 113 sanaa lyhyitä ohjauskomentoja, Gemini katsoo aiheellisesti, ettei käyttäjän puheessa ole itsenäistä analyyttistä näyttöä, ja hylkää käyttäjään kohdistetut väitteet.

---

## 5. Yhteenvetotaulukko

| Testattu syöte / ohjelmisto | Kanava | Vuoroja | Käyttäjän sanat | AI:n sanat | Huomiot |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SITRA (`run_e2e_variance_test.py`)** | `load_inputs_from_path` | 21 | 113 | 5 334 | `pymupdf4llm`-kutsu tiivisti taulukkosanoja |
| **SITRA (`MultiChannelIngressService`)** | Direct PDF Channel 1 | 21 | 113 | 5 710 | Täysi sanavälillinen suora PDF-poiminta |
| **JWDATAT (`run_e2e_variance_test.py`)** | `load_inputs_from_path` | 14 | 211 | 3 254 | 100 % stabiili, ei taulukkotiivistymää |
| **JWDATAT (`MultiChannelIngressService`)** | Direct PDF Channel 1 | 14 | 211 | 3 254 | 100 % stabiili |
| **OpenAI Leikepöytäteksti** | Fast-Path Regex (Kanava 4) | 4 | 10 | 17 | 0 ms deterministinen muistijäsennys |
| **Gemini Leikepöytäteksti** | LLM Fallback (Kanava 5) | - | - | - | Regex ei osu kaksoispisteettömään muotoon |