# EPIC 82: System Audit Trail and XAI Transparency (Faktantarkistuksen Läpinäkyvyys)

## 1. Ydinongelma (The Problem)
Quorum V2 on saavuttanut tason, jossa järjestelmä ei enää suorita vain Lexical-tarkistuksia (sanojen löytymistä tekstistä), vaan se kykenee kumoamaan (falsifioimaan) keksittyjä väitteitä ulkoisten MCP-työkalujen (kuten Tavily-haun) avulla. Jos käyttäjä esimerkiksi väittää, että "Työterveyslaitos suosittelee x", ja haku paljastaa tämän valheeksi, käyttäjän pisteet romahtavat oikeutetusti nolliin.

Nykyinen ongelma on **läpinäkyvyys (Explainable AI, XAI)** loppukäyttäjälle. Vaikka synteesimalli (`gemini-2.5-pro`) kirjoittaa PDF-raporttiin tiukan yhteenvedon ("Ehdotuksesi ei ole linjassa tutkimustiedon kanssa"), **kova todistusaineisto** – eli mitä hakusanoja kone käytti, miltä URL-osoitteilta se tiedon haki, ja mikä oli tarkka ristiriita – jää piiloon backendin `MCPAuditTrace` -objekteihin tai tietokannan uumeniin. Asiakas saattaa luulla saamaansa rangaistusta tekoälyn "hallusinaatioksi", vaikka taustalla on tehty aukoton faktantarkistus.

## 2. Tavoite (The Goal)
Tehdä järjestelmän suorittamasta faktantarkistuksesta täysin läpinäkyvää ja tuoda se ylpeydenaiheena osaksi lopullista tuotosta. Kun käyttäjä jää kiinni performatiivisesta "nimien pudottelusta" (keksityt viittaukset), raportin on näytettävä hänelle tarkka "kuitti" siitä, miten järjestelmä todensi väitteen valheelliseksi.

## 3. Ratkaisuvaihtoehdot & Toteutustavat (Proposed Solutions)

**Toteutustapa A: "Konepellin alta" -osion injektointi loppuraporttiin (Backend/Prompting)**
1. `backend_v2.services.orchestrator.context_router` kerää jo nyt XAI-laajennuksia (`COACHING`, `FALSIFICATION`). Tätä keruulogiikkaa laajennetaan siten, että se poimii `MCPAuditTrace` -luokan sisällöt (kyselyt, työkalun nimi, URL-osoitteet, tulos).
2. Tämä data syötetään loppusynteesin (`gemini-2.5-pro`) promptin kontekstiin.
3. Päivitetään `seed_data.json` -tiedostosta synteesivaiheen (esim. `blk_synthesis_...`) ohjeistus (PromptBlock). Sille annetaan tiukka sääntö: *"Jos kontekstissa on MCPAuditTrace-dataa faktantarkistuksista, lisää raportin aivan loppuun osio 'Järjestelmän Faktantarkistusloki', johon listaat tehdyt haut ja paljastuneet ristiriidat."*

**Toteutustapa B: Suora renderöinti Käyttöliittymään (Flutter)**
1. Laajennetaan "Paholaisen asianajaja" (`FALSIFICATION`) -komponenttia Frontendissä.
2. Jos kyseiseen vasta-argumenttiin liittyy `source_urls` tai `tool_id`, UI renderöi argumentin alle pienen "Faktantarkistettu lähteistä:" -tägin, josta linkki aukeaa alkuperäiseen lähteeseen.

## 4. Hyväksymiskriteerit (Acceptance Criteria)
* [ ] Suorituskansioon generoitava `raportti.md` ja siitä käännetty `report.pdf` sisältävät erillisen osion (System Audit), jossa avataan järjestelmän tekemät ulkoiset haut.
* [ ] XAI-keräin (`context_router`) osaa paketoida `MCPAuditTrace` -tiedot suoraan synteesimallin syötteeseen ilman, että konteksti-ikkuna rikkoutuu.
* [ ] Käyttäjälle syntyy välitön ymmärrys siitä, että Quorumia ei voi huijata keksityillä lähteillä, ja Goodhartin laki on selätetty.

## 5. Riippuvuudet ja Riskit (Dependencies & Risks)
* **Konteksti-ikkunan koko:** `MCPAuditTrace` saattaa tuoda paljon roskaa (raakaa HTML-tekstiä). Kontekstin kasaajan on osattava tiivistää tulos (pelkkä URL ja Summary) ennen synteesiin syöttämistä, ettei 185k tokenin raja räjähdä käsiin.
* Toteutus vaatii `seed_data.json` -päivitystä ja mahdollisesti koodimuutosta `context_builder.py` tai `context_router.py` -tiedostoihin.
