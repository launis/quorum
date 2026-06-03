# Analyysi: Vanha vs. Uusi Malli (Steppikohtaiset erot)

Vertailin `step_comparison.md`-raportin tuloksia. Erot "vanhan/hyvän" (Ajo 1) ja "uuden/ankaran" (Ajo 2) mallin välillä ovat huikeita, ja ne selittävät täydellisesti miksi uusi ajo epäonnistui loppusynteesissään.

## 1. Mekaaninen suorittaminen vs. Kognitiivinen analyysi
**Ajo 1 (Vanha malli, esim. Gemini):**
- **Reasoning Trace & Evaluation Notes:** Malli tekee aitoa semanttista analyysia. Se kirjoittaa perusteluihin asioita kuten: *"Käyttäjä osoittaa vahvaa System 2 -ajattelua ohjatessaan tekoälyä aktiivisesti. Erityisesti pyyntö luoda 'supermegatrendejä' on selkeä osoitus analyyttisestä synteesistä"*.
- Se ymmärtää säännöt kognitiivisina ohjeina ja arvioi tekstin **merkitystä**.

**Ajo 2 (Uusi malli, esim. GPT-4o / Claude):**
- **Reasoning Trace & Evaluation Notes:** Malli on täysin jumiutunut mekaaniseen suorittamiseen. Sen perustelut ovat robottimaisia toistoja itse promptista: *"Aloitin käymällä läpi jokaisen atom_id:n säännön... Etsin ensin suomenkielisiä vastineita... asetin exact_quote-kentän nulliksi"*.
- Se ei analysoi tekstiä juuri lainkaan, vaan raportoi ainoastaan **algoritmisista toimenpiteistään** (mitä JSON-kenttiä se täytti ja miten se käänsi englannin suomeksi). Se jopa toistaa näitä samoja mekaanisia lauseita useissa eri `[Chunk]`-lohkoissa.

## 2. Miksi tämä rikkoi Synteesin? (Juuri-syy)
Tämä löydös selittää täydellisesti sen alkuperäisen ongelman (synteesin irrallisuuden ja hallusinoinnit):

1. Synteesi-LLM yrittää rakentaa loppuraportin lukemalla näitä matriisien `evaluation_notes` ja `reasoning_trace` -kenttiä.
2. **Vanhoissa ajoissa** synteesi-LLM luki syvällistä analyysia käyttäjän "System 2 -ajattelusta" ja "Supermegatrendien luomisesta". Tästä oli helppo vetää erinomainen, asiapitoinen loppusynteesi.
3. **Uudessa ajossa** synteesi-LLM luki sivutolkulla robottimaista tekstiä: *"skannasin lähdetekstin", "etsin syntaktisia ankkureita", "asetin kentän nulliksi"*. 
4. Koska uudessa ajossa matriisit **eivät antaneet synteesille mitään asiasisältöä**, ja kaiken lisäksi aito `evaluations`-data (lainaukset) oli suodatettu pois, synteesi-LLM oli täysin tyhjän päällä. Sen oli pakko hallusinoida asiasisältö tyhjästä!

## Johtopäätös
Uusi kielimalli ottaa Quorumin matriisipromptit ("Etsi syntaktinen ankkuri", "Rajauslaatikko") aivan liian kirjaimellisesti ohjelmointikoodina, kun taas vanha malli ymmärsi ne analyyttisenä viitekehyksenä. Uusi malli on niin keskittynyt sääntöjen mekaaniseen noudattamiseen, että siltä unohtuu itse tekstin sisällön analysointi.

Tämä vahvistaa sen, että tekemäni suodattimen poisto (`exact_quote` -lainausten palauttaminen synteesille) pelastaa tilanteen, koska silloin synteesillä on aina raakadata käytössään, vaikka matriisit kirjoittaisivat pelkkää robottikieltä! Voi myös olla, että uuden mallin kanssa matriisien prompteja pitäisi hieman "pehmentää", jotta ne keskittyisivät taas enemmän itse asiasisältöön.
