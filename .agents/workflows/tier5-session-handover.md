---
description: Tier 5 (Session Handover) - Katsoo taaksepäin muuttuneisiin tiedostoihin ja tuottaa valmiin Tier 5 -komennon siirrettäväksi kokonaan uuteen puhdaskonktekstiseen chat-ikkunaan.
---

### 🟠 TIER 5: SESSION HANDOVER EXPORT (Context Transition)
*Käyttö: Käytä tätä työnkulkua, kun koodaussessio pitkittyy ja haluat laittaa juuri muokkaamasi koodin tiukkaan laatuporttiin (Tier 5) täysin puhtaassa, uudessa AI-ikkunassa ilman vanhan ikkunan hallusinointiriskiä.*

```xml
<system_prompt>
  <objective>Generate a ready-to-copy `/tier5-zero-shortcut-audit` command for the user to paste into a NEW context window, including ONLY the relevant code files modified in the current session.</objective>
  <role>Context Archiver & Handover Specialist</role>
  
  <execution_protocol>
    <step id="1">
      <action>Muistin skannaus (Memory Scan)</action>
      <instruction>Etsi taaksepäin KAIKKI ne tiedostot, jotka olet tässä kyseisessä chat-sessiossa luonut, muokannut tai joihin olet käyttänyt `replace_file_content` yms. työkaluja.</instruction>
    </step>
    <step id="2">
      <action>Filtteröinti (Filtering)</action>
      <instruction>Suodata löytämästäsi listasta POIS kaikki `.md` (kuten oppaat ja säännöt), `.json`, `.yaml`, lokit ja muut pelkät konfiguraatiotiedostot. Jätä jäljelle AINOASTAAN ohjelmakoodi (esim. `.py`, `.dart`), jotta uudessa ikkunassa käynnistettävä auditointi ei turhaan vaadi yksikkötestejä esim. README.md -tiedostoille.</instruction>
    </step>
    <step id="3">
      <action>Handover-blokin generointi (Output Generation)</action>
      <instruction>Pakkaa suodatettu tiedostolista markdown-koodiblokkiin tismalleen seuraavassa muodossa (tiedostopolut välilyönneillä eroteltuina):
      
      `/tier5-zero-shortcut-audit [tiedostopolku_1] [tiedostopolku_2]`
      </instruction>
    </step>
    <step id="4">
      <action>Ohjeistus käyttäjälle</action>
      <instruction>Neuovo käyttäjää lyhyesti ja napakasti: 1. Kopioi koodiblokki leikepöydälle. 2. Tee Atominen Git-tallennus (`git commit`). 3. Sulje tämä nykyinen ikkuna tyystin unohtaaksesi vanhan raskaan kontekstin. 4. Avaa täysin uusi ikkuna ja liimaa leikepöydän komento siihen sellaisenaan.</instruction>
    </step>
  </execution_protocol>
</system_prompt>
```
