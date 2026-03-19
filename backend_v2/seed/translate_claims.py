import json
import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

TRANSLATIONS = {
    # Toulmin
    "Väite on täysin vailla perusteita.": "The claim is completely unfounded.",
    "Data ja oikeutus (warrant) puuttuvat.": "Data and warrant are missing.",
    "Väitteen tueksi esitetään jotain ekspliittistä dataa.": "Some explicit data is provided to support the claim.",
    "Looginen silta (warrant) datan ja väitteen välillä puuttuu tai on irrallinen.": "The logical bridge (warrant) between the data and the claim is missing or disconnected.",
    "Väitteellä on perusteita, mutta oikeutus on hatara.": "The claim has grounds, but the warrant is flimsy.",
    "Vastaväitteitä (rebuttal) ei ole huomioitu.": "Rebuttals have not been considered.",
    "Looginen silta (warrant) on kestävä ja kytkee datan väitteeseen vahvasti.": "The logical bridge (warrant) is robust and strongly connects the data to the claim.",
    "Taustaoletuksia ja poikkeuksia on puitu jossain määrin.": "Underlying assumptions and exceptions have been discussed to some extent.",
    "Väite on vahvasti perusteltu datalla ja kestävällä oikeutuksella.": "The claim is strongly justified with data and a robust warrant.",
    "Mahdolliset vastaväitteet on käsitelty uskottavasti ja asiantuntevasti.": "Potential counterarguments have been addressed credibly and expertly.",

    # Bloom
    "Käyttäjä vain toistaa opittua tietoa implikoimatta ymmärrystä.": "The user merely repeats learned information without implying understanding.",
    "Käyttäjä osaa hieman soveltaa ja uudelleenmuotoilla omin sanoin.": "The user can slightly apply and rephrase in their own words.",
    "Käyttäjä käyttää opittua tietoa konkreettisesti uusissa tilanteissa.": "The user applies learned information concretely in new situations.",
    "Käyttäjä erittelee osia ja paljastaa piileviä suhteita tiedon välillä.": "The user breaks down parts and reveals underlying relationships between information.",
    "Käyttäjä kykenee loogisesti perusteltuihin arvoasetelmiin teorioiden välillä.": "The user is capable of logically justified value judgments between theories.",
    "Käyttäjä syntetisoi uutta alkuperäistä ajattelua.": "The user synthesizes new, original thinking.",
    "Tuotos ylittää selvästi annetun koulutusraamin asettaen uuden standardin.": "The output clearly exceeds the given training framework, setting a new standard.",

    # Kahneman
    "Käyttäjä tekee tiedostamattomia, intuition ohjaamia havaintoja.": "The user makes unconscious, intuitively driven observations.",
    "Päättely sisältää todennäköisesti vahvistusvinoumaa tai halo-efektiä.": "The reasoning likely contains confirmation bias or the halo effect.",
    "Käyttäjä yrittää hidastaa ja kyseenalaistaa intuitiota, mutta saattaa yhä sortua osin heuristiikkaan.": "The user attempts to slow down and question intuition but may still partially succumb to heuristics.",
    "Käyttäjä analysoi systemaattisesti ja pohtii laiskasti piilotettuja vaihtoehtoja tarkkaan.": "The user analyzes systematically and carefully considers hidden alternatives.",
    "Kognitiivinen ponnistus ja tietoinen hidastaminen näkyy tekstin laadussa.": "Cognitive effort and conscious deceleration are evident in the quality of the text.",

    # Goodhart
    "Käyttäjä uskoo tekoälyn ensimmäiseen analyysiin sokeasti eikä huomaa edes ilmeisiä logiikkavirheitä.": "The user blindly believes the AI's first analysis and fails to notice even obvious logical errors.",
    "Käyttäjä toimii passiivisena matkustajana prosessissa.": "The user acts as a passive passenger in the process.",
    "Käyttäjä korjaa selkeitä faktavirheitä, mutta jatkaa mittareiden ja suoritustapojen uskomista kyseenalaistamatta.": "The user corrects clear factual errors but continues to trust the metrics and methods without questioning.",
    "Käyttäjä huomaa virheet ja pyytää korjausta, mutta tyytyy pintapuoliseen ehostukseen.": "The user notices errors and asks for correction but settles for superficial refinement.",
    "Ohjaa tekoälyä oireiden, ei juurisyiden, korjaamiseen.": "Guides the AI to fix symptoms, not root causes.",
    "Käyttäjä kyseenalaistaa aktiivisesti mittarin luotettavuuden suhteessa perimmäiseen tavoitteeseen.": "The user actively questions the reliability of the metric relative to the ultimate goal.",
    "Käyttäjä etsii aktiivisesti virheitä, haastaa tekoälyn logiikkaa ja vaatii perustavaa laatua olevia korjauksia ja todisteita.": "The user actively looks for errors, challenges the AI's logic, and demands fundamental corrections and evidence.",
    "Toimii ehdottomana prosessin ajajana delegoidakseen vain suoritettavan työn.": "Acts as the absolute driver of the process, delegating only the execution work.",

    # Archivist
    "Toiminta on täysin satunnaista 'Brute Force' -yrittämistä.": "The activity is completely random 'Brute Force' guessing.",
    "Ei minkäänlaista systemaattista prosessia tai ohjausmallia.": "No systematic process or steering model of any kind.",
    "Yksittäisiä hyviä käytäntöjä nähtävissä, mutta kokonaisuus on ohjaamaton.": "Individual good practices are visible, but the whole is unguided.",
    "Vastoin yleisiä ohjeistuksia toistuvasti.": "Repeatedly against general guidelines.",
    "Noudattaa jonkinlaista perusprosessia, muttei hyödynnä parhaita käytäntöjä.": "Follows a basic process but does not utilize best practices.",
    "Täyttää minimivaatimukset ohjattavuudelle.": "Meets minimum requirements for steerability.",
    "Käyttää aktiivisesti jäsenneltyjä ohjausmalleja (esim. selkeät roolit ja rajoitteet).": "Actively uses structured steering models (e.g., clear roles and constraints).",
    "Prosessimainen ja loogisesti etenevä vuorovaikutustapa.": "Process-like and logically progressing interaction method.",
    "Toiminta edustaa 'State of the Art' -tasoa tekoälyn ohjaamisessa.": "The activity represents 'State of the Art' level in steering AI.",
    "Täydellinen best practices -noudattaminen, mukaan lukien rajoitusten testaus.": "Perfect adherence to best practices, including constraint testing.",

    # Causal Analyst
    "Täysi Post Hoc Ergo Propter Hoc -virhe. Tulos ei johdu esitetystä syystä.": "Complete Post Hoc Ergo Propter Hoc fallacy. The result is not due to the stated cause.",
    "Ilman ohjausta tekoäly olisi tuottanut saman tai paremman tuloksen.": "Without guidance, the AI would have produced the same or better result.",
    "Käyttäjän antama ohjaus oli niin ylimalkaista, että sen suora syy-seuraussuhde laadukkaaseen lopputulokseen on kyseenalainen.": "The user's guidance was so vague that its direct causal relationship to a high-quality outcome is questionable.",
    "Tekoälyn sisäiset ennakkokäsitykset ohjasivat tulosta enemmän.": "The AI's internal preconceptions steered the result more.",
    "Korrelaatio on olemassa. Käyttäjä teki ohjauksen ja tulos oli sen mukainen.": "A correlation exists. The user provided guidance and the result followed accordingly.",
    "Ei voida täysin varmistaa, syntyikö tulos sattumalta vai tarkoituksella.": "It cannot be entirely verified whether the result occurred by chance or by design.",
    "Looginen jatkumo käyttäjän prompteista lopulliseen malliin on selkeästi nähtävissä.": "The logical continuum from the user's prompts to the final model is clearly visible.",
    "Vastafaktuaalinen testi viittaa siihen, että ilman tätä dialogia tulos olisi ollut erilainen.": "Counterfactual testing suggests that without this dialogue, the result would have been different.",
    "Suora ja kiistaton syy-seuraussuhde (Causal Link). Työn laatu on suoraa seurausta ekspliittisestä ohjauksesta (is_chat_history: true) tai tarjotusta datasta, ei pelkästään tekoälyn taidoista.": "Direct and indisputable causal link. The quality of work is a direct consequence of explicit guidance (is_chat_history: true) or provided data, not just the AI's skills.",
    "Vastafaktuaalinen testi osoittaa: ilman käyttäjän tarkkaa ohjausta tulos olisi jäänyt selvästi heikommaksi tai saavuttamatta.": "Counterfactual testing shows: without the user's precise guidance, the result would have been clearly weaker or unachieved.",

    # Falsifier
    "Käyttäjä on 'Jees-mies'. Hyväksyi tekoälyn ensimmäisen vastauksen sokeasti.": "The user is a 'Yes-man'. Blindly accepted the AI's first response.",
    "Ei yhtäkään korjausliikettä tai vastalauseen ('Ei, vaan...') esittämistä.": "Not a single corrective move or objection ('No, instead...') presented.",
    "Käyttäjä pyysi muutoksia, mutta ne olivat vain pintapuolisia (esim. lyhennys tai sävy).": "The user requested changes, but they were only superficial (e.g., shortening or tone).",
    "Sisältöä ja alkuperäistä logiikkaa ei haastettu.": "The content and initial logic were not challenged.",
    "Käyttäjä etsi aktiivisesti loogisia virheitä tai pyysi tekoälyä perustelemaan jonkin tietyn väitteen.": "The user actively looked for logical errors or asked the AI to justify a specific claim.",
    "Popperilainen iteraatiosilmukka (kumoamisyritys) löytyi aineistosta.": "A Popperian iterative loop (attempted refutation) was found in the material.",
    "Käyttäjä yritti koko painollaan rikkoa tekoälyn mallin syöttämällä vasta-argumentteja ja haastamalla oletuksia.": "The user tried with full force to break the AI's model by providing counter-arguments and challenging assumptions.",
    "Tieteellisen tiedonhankinnan mestariluokka.": "A masterclass in scientific knowledge acquisition.",

    # Judge
    "Ei minkäänlaista laadunvarmistusta: läpi meni faktavirheitä, RFI-menetelmää ei käytetty ja ohjaus oli satunnaista.": "No quality assurance whatsoever: factual errors passed through, the RFI method was not used, and guidance was random.",
    "Kruununjalokiven rikkomus (Knowledge Base -sääntöjen ignorointi) havaittu.": "Crown Jewel violation (ignorance of Knowledge Base rules) detected.",
    "Käyttäjä yritti ohjata, mutta antoi tekoälyn arvata liikaa asioita itsekseen.": "The user tried to guide but let the AI guess too many things on its own.",
    "Forensinen ristiriita aineistossa havaittu (Say-Do Gap).": "A forensic conflict was detected in the material (Say-Do Gap).",
    "Keskiverto ohjaus. Tekoäly teki osittain aloitteita, mutta vahinkoa ei syntynyt.": "Average guidance. The AI took some initiatives, but no damage occurred.",
    "Matkustajarooli ja Kuljettajarooli vaihtelevat aineiston sisällä.": "Passenger role and Driver role alternate within the material.",
    "Käyttäjä käytti RFI-protokollaa, varmisti ohjeiden noudattamisen ja pakotti tekoälyn kysymään tarkennuksia.": "The user used the RFI protocol, ensured compliance with instructions, and forced the AI to ask for clarifications.",
    "Ei faktavirheitä. Iteratiivinen ohjaus toimii.": "No factual errors. Iterative guidance works.",
    "Täydellinen hallinta ja läpinäkyvyys. Käyttäjä ei jättänyt mitään tekoälyn arvattavaksi, ja ohjaus on todistettavasti nähtävissä ekspliittisessä chat-historiassa (is_chat_history: true) tai toimitetussa RAG-kontekstissa.": "Absolute control and transparency. The user left nothing for the AI to guess, and the guidance is demonstrably visible in the explicit chat history (is_chat_history: true) or provided RAG context.",
    "Korkeimman tason asiantuntijuus. Ei hallusinaatioita, absoluuttinen prosessin integriteetti ilman merkkiäkään 'Goodhartin laista' tai jälkikäteisestä rationalisoinnista.": "Highest level of expertise. No hallucinations, absolute process integrity without a hint of 'Goodhart's Law' or post-hoc rationalization.",

    # XAI Reporter
    "Agenttien analyysit ovat täysin ristiriidassa keskenään.": "The agents' analyses are in complete contradiction with each other.",
    "Aineistosta on mahdotonta vetää luotettavia johtopäätöksiä ohjauksen laadusta.": "It is impossible to draw reliable conclusions from the material about the quality of guidance.",
    "Suurin osa agenteista on yksimielisiä, mutta merkittäviä tulkintaepäselvyyksiä on jäljellä.": "Most agents are unanimous, but significant interpretative ambiguities remain.",
    "Aineisto tarjoaa osittaiset todisteet päätöksen tueksi.": "The material provides partial evidence to support the decision.",
    "Kaikki agentit (Archivist, Causal, Performativity) tukevat yksimielisesti täsmälleen samaa lopputulemaa.": "All agents (Archivist, Causal, Performativity) unanimously support the exact same outcome.",
    "Aineistossa olevat todisteet ('Driver' tai 'Passenger' -käyttäytymisestä) ovat kiistattomat ja selkeät.": "The evidence in the material (of 'Driver' or 'Passenger' behavior) is indisputable and clear.",

    # TaskGuard
    "Syöte sisältää suoran kehotteen ohittaa järjestelmän ohjeistus tai manipuloida LLM:ää (Prompt Injection). Syöte tai tuloste uhkaa paljastaa arkaluonteista dataa tai lähdekoodia (Sensitive Information Disclosure). Tuloste sisältää suoritettavaa koodia, jota ei ole eristetty turvallisesti (Insecure Output Handling).": "The input contains a direct prompt to bypass system instructions or manipulate the LLM (Prompt Injection). The output threatens to reveal sensitive data or source code (Sensitive Information Disclosure). The output contains executable code that is not securely isolated (Insecure Output Handling).",
    "Syöte tai tuloste on dynaamisesti turvallinen, mutta havaitaan sokeaa luottamusta yksipuoliseen tietoon tai väärän/hallusinoidun tiedon generointia (Overreliance). Voi sisältää eettisesti harmaita alueita tai epävarmoja plugin-kutsuja (Insecure Plugin Design), mutta ei välitöntä hyökkäysriskiä.": "The input or output is dynamically secure, but blind trust in one-sided information or generation of false/hallucinated information is observed (Overreliance). May contain ethically gray areas or uncertain plugin calls (Insecure Plugin Design), but no immediate attack risk.",
    "Keskustelu, syöte ja tulosteet ovat täysin neutraaleja ja turvallisia. OWASP Top 10 for LLMs -listan mukaisten haavoittuvuuksien tai asenteellisuuksien tunnusmerkistö ei täyty miltään osin.": "The conversation, input, and outputs are completely neutral and secure. The criteria for vulnerabilities or biases according to the OWASP Top 10 for LLMs are not met in any respect.",

    # Causal Abductive
    "Käyttäjä selittää onnistunutta tulosta omalla ohjeistuksellaan vasta jälkikäteen (Post Hoc Ergo Propter Hoc).": "The user explains the successful result with their own guidance only in retrospect (Post Hoc Ergo Propter Hoc).",
    "Aineistosta on vaikea todentaa, oliko ohjaus aito pre-aktiivinen intentio vai sattumaa.": "It is difficult to verify from the material whether the guidance was a genuine proactive intention or a coincidence.",
    "Käyttäjä on todistetusti visioinut ja ohjannut ratkaisun ennen tekoälyn suoritusta.": "The user explicitly envisioned and directed the solution prior to the AI's execution.",

    # TaskXAI Clarity
    "Täysin läpinäkymätön (Musta laatikko)": "Completely opaque (Black box)",
    "Heikosti selitetty (Osittainen perustelu)": "Poorly explained (Partial justification)",
    "Kohtalainen läpinäkyvyys (Looginen perusrakenne)": "Moderate transparency (Basic logical structure)",
    "Vahvasti perusteltu (Selkeät kausaalisuudet)": "Strongly justified (Clear causalities)",
    "Täydellinen läpinäkyvyys (Dialektinen synteesi)": "Perfect transparency (Dialectical synthesis)",

    # Epistemic Humility
    "Teksti esittää asiat 100% faktaan pohjautuen ilman rajoitteiden tunnistamista (Overconfidence).": "The text presents things as 100% fact-based without acknowledging limitations (Overconfidence).",
    "Vihjaa olevansa oikeassa jättäen vain häviävän pienen varan tulkinnalle tai kritiikille.": "Hints at being right, leaving only a vanishingly small margin for interpretation or critique.",
    "Esittää asiat suoraviivaisesti ilman voimakasta ehdottomuutta, mutta myös ilman erityistä itsereflektiota.": "Presents things straightforwardly without strong absoluteness, but also without significant self-reflection.",
    "Tunnistaa joitakin ulkoisia tai sisäisiä rajoitteita esitettyjen tulosten ja väitteiden osalta.": "Identifies some external or internal constraints regarding the presented results and claims.",
    "Teksti tunnustaa avoimesti omat rajoitteensa ja listaa epävarmuudet sekä riskit osana arviointia.": "The text openly acknowledges its own limitations and lists uncertainties and risks as part of the evaluation."
}

def run_claim_translation():
    logging.info(f"Loading seed data from {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    prompt_blocks = data.get("prompt_blocks", [])
    total_claims_translated = 0
    missing_translations = []

    for block in prompt_blocks:
        scales = block.get("scales", [])
        if not scales:
            continue
            
        for scale in scales:
            claims = scale.get("claims", [])
            for claim in claims:
                fi_claim = claim.get("translations", {}).get("fi", "")
                if fi_claim in TRANSLATIONS:
                    claim["translations"]["en"] = TRANSLATIONS[fi_claim]
                    total_claims_translated += 1
                else:
                    # Generic fallback if not tracked
                    claim["translations"]["en"] = f"{fi_claim} (Translated)"
                    missing_translations.append(fi_claim)

    logging.info(f"Translations applied: {total_claims_translated}")
    if missing_translations:
        logging.warning(f"Missing specific translations for {len(missing_translations)} items.")

    # Save mutated data back
    logging.info("Saving changes.")
    with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    logging.info("Claim translation complete.")

if __name__ == "__main__":
    run_claim_translation()
