import sys
import re

with open(r'c:\src\quorum\docs\epic\system2_variance_analysis_report.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Liite 1.2
target_liite1_2 = r'> \*\*System 2 -Analyysi\*\*: Koodin nykytilassa `reasoning_steps` on rajoitettu erittäin tiukasti: \*\"Max 1 short sentence focusing purely on structural evidence\.\"\* Tämä on jäänne aiemmasta \*\*output token -optimoinnista\*\* \(Epic 85\)\. Vaikka optimointi säästää rahaa ja latenssia, se tuhoaa mallin Chain-of-Thought \(CoT\) -kyvyn\. Pakottamalla malli suoraan binääriseen päätökseen \(tai yhteen lauseeseen\) pitkässä 76 000 tokenin kontekstissa, kasvatamme merkittävästi \"hallusinaatiovarianssia\"\. Kolmen askeleen rakenteellinen CoT maksaa muutamia kymmeniä tokeneita lisää per ajo, mutta on \*\*tieteellisesti todistettu keino\*\* vähentää varianssia \(Wei et al\. 2022\)\. Tämä on kannattava kompromissi\.'

new_liite1_2 = '''> **System 2 -Analyysi**: Koodin nykytilassa Flash-ensemblet on pakotettu käyttämään `StepDTOStrict`-skeemaa, jonka `reasoning_steps` on rajoitettu erittäin tiukasti: *"Max 1 short sentence focusing purely on structural evidence."* Raportin osio 9.4 paljastaa, että järjestelmässä on jo olemassa laajempi `AtomEvaluationItemDTO`-skeema natiivilla 4-vaiheisella CoT:lla, mutta sitä ei hyödynnetä ensemble-stepeissä. Tämä on jäänne aiemmasta **output token -optimoinnista** (Epic 85). Vaikka optimointi säästää rahaa ja latenssia, se tuhoaa nimenomaan herkkien Flash-mallien Chain-of-Thought (CoT) -kyvyn. Jotta osion 9.4 löydös ratkaistaan, meidän tulee joko laajentaa `StepDTOStrict`-kenttää yllä esitetyllä tavalla, tai migroida ensemble-stepit käyttämään `AtomEvaluationItemDTO`:ta. Kolmen askeleen rakenteellinen CoT maksaa muutamia kymmeniä tokeneita lisää per ajo, mutta on **tieteellisesti todistettu keino** vähentää varianssia (Wei et al. 2022).'''

text = re.sub(target_liite1_2, new_liite1_2, text, flags=re.MULTILINE)

# 2. Add Section 11.8 for CONTESTED + Inversio
target_section_11 = r'3\. \*\*Käsittelyn symmetrisyys\*\*: Positiivisten ja negatiivisten sääntöjen välinen Guttman Waterfall -kuilu tasoittuu, koska rangaistus suhteutetaan suoraan kyseisessä matriisissa havaittujen epävarmuuksien määrään\.'

new_section_11 = '''3. **Käsittelyn symmetrisyys**: Positiivisten ja negatiivisten sääntöjen välinen Guttman Waterfall -kuilu tasoittuu, koska rangaistus suhteutetaan suoraan kyseisessä matriisissa havaittujen epävarmuuksien määrään.

### 11.8 CONTESTED + Inversio -paradoksi (Kriittinen löydös)

Vaikka CONTESTED-tila saataisiin revitalisoitua pistelaskussa (Osiot 11.5 ja 11.7), järjestelmässä on syvempi arkkitehtuurinen ansa, joka liittyy osiossa 10 käsiteltyyn käänteiseen logiikkaan (`inverse_evidence = true`).

**Matemaattinen ongelma**:
Jos atomi on käänteinen (esim. "Ei virheitä löydy") ja malli palauttaa "CONTESTED" (esim. "löysin sekä hyvää että huonoa"), kooditason inversio-operaatio tuhoaa tuloksen:
1. `CONTESTED` tulkitaan alustavasti "löytyneeksi evidenssiksi" (jotta waterfall ei katkea heti lokaalin sakon saavaan epävarmuuteen).
2. Koska `inverse_evidence = true`, koodi invertoi tuloksen: `NOT True = False`.
3. Tulos `calculate_rule_satisfied = False` laukaisee Guttman Waterfall -arkkitehtuurissa välittömän **fail-fast hylkäyksen** koko matriisilohkolle.

**Johtopäätös**: Jos CONTESTED-tila aktivoidaan ohjaamaan epävarmuutta, backendin inversio-logiikka (`lightweight_matrix.py`) on päivitettävä siten, että `CONTESTED`-tilaa **ei koskaan invertoida** matemaattisesti. CONTESTED on epistemologinen tila ("epävarma"), ei looginen väittämä ("löytyi"), ja sen invertointi ("epä-epävarma") on looginen virhe, joka johtaa tuplasanktioon. Tämä muodostaa perustan Liitteen 3 korjauksille.'''

text = re.sub(target_section_11, new_section_11, text, flags=re.MULTILINE)

# 3. Add to Section 14 to justify Liite 2.1
target_section_14 = r'> 1\. ⚡ \*\*Testaa temperature-diversiteetti\*\* \(0\.0, 0\.1, 0\.3\) nykyisellä arkkitehtuurilla — ei koodimuutoksia majority voteen'

new_section_14 = '''> 0. 🧠 **Kognitiivinen reititys**: Ennen ensemble-kikkailuja, siirrä puhtaat "älykkyyssolmut" (Analyst, Falsifier, Logician, Overseer, Judge) pysyvästi `strict`-strategiaan (Pro-malli). Flashin jättäminen vastuuseen näistä aiheuttaa semanttista varianssia, jota mikään prompt-engineering ei korjaa (perustelee Liitteen 2.1).
> 1. ⚡ **Testaa temperature-diversiteetti** (0.0, 0.1, 0.3) nykyisellä arkkitehtuurilla — ei koodimuutoksia majority voteen'''

text = re.sub(target_section_14, new_section_14, text, flags=re.MULTILINE)

with open(r'c:\src\quorum\docs\epic\system2_variance_analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
