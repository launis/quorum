import sys
import re

with open(r'c:\src\quorum\docs\epic\system2_variance_analysis_report.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the note in 9.4
target_note = r'> \[\!NOTE\]\n  > \*\*Tärkeä korjaus\*\*: Alkuperäinen väite "ZERO-REASONING MANDATE on suurin yksittäinen syy varianssille" on \*\*empiirisesti väärä\*\* koodianalyysin perusteella\. ZERO-REASONING koskee vain lightweight-steppejä \(1× ajo\), jotka eivät ole osa ensemble-arviointia\. Todellinen CoT-deprivaatio tapahtuu output-skeeman `reasoning_steps`-kentän yhden lauseen rajoituksessa, joka koskee \*\*kaikkia\*\* ensemble-steppejä \(3× Flash-ajo\)\. Tämä on korjattavissa ilman arkkitehtuurimuutoksia — pelkkä skeeman description-kentän päivitys riittää\.'

new_note = '''> [!NOTE]
  > **Tärkeä korjaus ja System 2 -Löydös**: Alkuperäinen väite "ZERO-REASONING MANDATE on suurin yksittäinen syy varianssille" on koodianalyysin perusteella **empiirisesti väärä**. ZERO-REASONING koskee vain lightweight-steppejä (1× ajo), jotka eivät ole osa ensemble-arviointia.
  >
  > Todellinen kooditason sokea piste liittyy **kaksijakoiseen CoT-skeemaan**: Järjestelmä käyttää raskaampia malleja (`AtomEvaluationItemDTO`) varten täyttä 4-vaiheista `ReasoningStepDTO` -rakennetta, jolla on natiivisti valtavasti "ajatteluaikaa". Kuitenkin, juuri ne **Flash-ensemblet** jotka ovat kaikkein herkkiä varianssille, pakotetaan käyttämään `StepDTOStrict`-skeemaa, jonka `reasoning_steps` salli vain 1 lauseen. Varianssin ratkaisu ei siis ole pelkkä kentän lisäys, vaan sen ymmärtäminen, miksi raskaampi natiivi-CoT on deaktivoitu ensemblen osalta. Oikea interventio on joko laajentaa `StepDTOStrict`-kenttää (kuten ehdotettu) tai migroida ensemble käyttämään täysimittaista `AtomEvaluationItemDTO`-skeemaa.'''

text = re.sub(target_note, new_note, text, flags=re.MULTILINE)

# Add CONTESTED warning to Liite 3
target_liite3 = r'elif contested_votes >= pass_votes and contested_votes >= fail_votes:\n          chosen\["status"\] = "CONTESTED"\n      elif pass_votes > fail_votes:\n          chosen\["status"\] = "PASS"\n      else:\n          chosen\["status"\] = "FAIL"\n  ```\n  \n  > \*\*System 2 -Analyysi\*\*: Koodin nykytilan tutkinta vahvistaa, että tällä hetkellä esim\. 1 PASS, 1 FAIL, 1 CONTESTED -äänestys menee `else`-lohkoon ja palauttaa satunnaisen FAILin\. Confidence on järjestelmässä dormoiva signaali\. Aktivoimalla kynnysarvon \(`<= 0\.67`\) poistamme LLM:n pakotetun Group Thinkin: kun mallit ovat eri mieltä semanttisessa rajatapauksessa \(Tyyppi 3\), järjestelmä hyväksyy ambivalenssin ja välittää sen eteenpäin\. Tämä on ehdoton edellytys Tyypin 3 varianssin korjaamiselle\.'

new_liite3 = '''elif contested_votes >= pass_votes and contested_votes >= fail_votes:
          chosen["status"] = "CONTESTED"
      elif pass_votes > fail_votes:
          chosen["status"] = "PASS"
      else:
          chosen["status"] = "FAIL"
  ```
  
  > **System 2 -Analyysi**: Koodin nykytilan tutkinta vahvistaa, että tällä hetkellä esim. 1 PASS, 1 FAIL, 1 CONTESTED -äänestys menee `else`-lohkoon ja palauttaa satunnaisen FAILin. Confidence on järjestelmässä dormoiva signaali. Aktivoimalla kynnysarvon (`<= 0.67`) poistamme LLM:n pakotetun Group Thinkin: kun mallit ovat eri mieltä semanttisessa rajatapauksessa (Tyyppi 3), järjestelmä hyväksyy ambivalenssin ja välittää sen eteenpäin. Tämä on ehdoton edellytys Tyypin 3 varianssin korjaamiselle.
  
  > [!WARNING]
  > **System 2 -Kriittinen Huomio (CONTESTED + Inversio -paradoksi)**: CONTESTED-tila palauttaa mallista `calculate_rule_satisfied = False`. Inverse-atomeille (esim. "Ei virheitä", 43.4% kaikista) tämä `False` tarkoittaa, että "ongelma havaittiin". Tämä laukaisee automaattisen waterfall-hylkäyksen koko blokille, vaikka CONTESTEDin pitäisi viestiä "epävarma, tarvitsee ihmistä". Jos reititämme epävarmuuden CONTESTED-tilalla, meidän on lisättävä poikkeus logiikkaan: CONTESTED ei saa triggeröidä fail-fast waterfallia invertoiduissa säännöissä, tai rankaisemme mallia tuplana sen rehellisestä epävarmuudesta.'''

text = re.sub(target_liite3, new_liite3, text, flags=re.MULTILINE)

with open(r'c:\src\quorum\docs\epic\system2_variance_analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
