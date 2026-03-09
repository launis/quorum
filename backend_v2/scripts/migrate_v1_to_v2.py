import json
import re
import sys
from pathlib import Path
from typing import Any

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend_v2.models.auth import Organization, User
from pydantic import TypeAdapter

from backend_v2.models.v2_core import Observation, OutputConfig, Reference


def slugify(text: str, fallback_index: int) -> str:
    """Creates a clean routing slug from V1 string or falls back to index."""
    if not text:
        return f"item_{fallback_index}"
    # Remove non-alphanumeric, replace spaces with underscores
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip().lower()
    clean = re.sub(r'[\s-]+', '_', clean)
    return clean[:30]


def migrate_seeds() -> None:
    v1_path = Path("data/github_seed_data.json")
    if not v1_path.exists():
        print(f"V1 GitHub seed database not found at {v1_path}")
        return

    with open(v1_path, encoding="utf-8") as f:
        v1_db = json.load(f)

    v2_path = Path("backend_v2/seed/seed_data.json")

    # --- Clean Slate Pledge ---
    # We do NOT read the old v2_seed. We start fresh.
    v2_seed: dict[str, list[Any]] = {
        "system_config": [],
        "matrices": [],
        "workflows": [],
        "components": [],
        "output_configs": [],
        "agents": [],
        "dimensions": [],
        "users": [],
        "organizations": [],
        "references": []
    }

    matrices: list[dict[str, Any]] = [
        {
            "id": "matrix_toulmin",
            "label": {"default_locale": "fi", "translations": {"fi": "Toulminin Argumentaatio"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Arvioi argumentin laatua Toulminin mallin mukaisesti."}},
            "category_id": "scientific_theory",
            "type": "string",
            "allow_decimals": True,
            "strictness_level": 80,
            "require_justification": True,
            "theory_grounding": { "source_url": "https://doi.org/10.1017/CBO9780511802034", "citation_reference": "Toulmin, Stephen E. 2003. The uses of argument." },
            "scales": [
                {"score": 1, "name": {"default_locale": "fi", "translations": {"fi": "Heikko"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Väite on täysin vailla perusteita."}}, {"default_locale": "fi", "translations": {"fi": "Data ja oikeutus (warrant) puuttuvat."}}]},
                {"score": 2, "name": {"default_locale": "fi", "translations": {"fi": "Välttävä"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Väitteen tueksi esitetään jotain ekspliittistä dataa."}}, {"default_locale": "fi", "translations": {"fi": "Looginen silta (warrant) datan ja väitteen välillä puuttuu tai on irrallinen."}}]},
                {"score": 3, "name": {"default_locale": "fi", "translations": {"fi": "Kohtalainen"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Väitteellä on perusteita, mutta oikeutus on hatara."}}, {"default_locale": "fi", "translations": {"fi": "Vastaväitteitä (rebuttal) ei ole huomioitu."}}]},
                {"score": 4, "name": {"default_locale": "fi", "translations": {"fi": "Hyvä"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Looginen silta (warrant) on kestävä ja kytkee datan väitteeseen vahvasti."}}, {"default_locale": "fi", "translations": {"fi": "Taustaoletuksia ja poikkeuksia on puitu jossain määrin."}}]},
                {"score": 5, "name": {"default_locale": "fi", "translations": {"fi": "Vahva"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Väite on vahvasti perusteltu datalla ja kestävällä oikeutuksella."}}, {"default_locale": "fi", "translations": {"fi": "Mahdolliset vastaväitteet on käsitelty uskottavasti ja asiantuntevasti."}}]}
            ],
            "rows": [{"default_locale": "fi", "translations": {"fi": "Argumentaation laatu"}}]
        },
        {
            "id": "matrix_bloom",
            "label": {"default_locale": "fi", "translations": {"fi": "Bloomin Taksonomia"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Arvioi kognitiivista syvyyttä Bloomin taksonomian perusteella."}},
            "category_id": "scientific_theory",
            "type": "string",
            "allow_decimals": True,
            "strictness_level": 60,
            "require_justification": True,
            "theory_grounding": { "source_url": "https://www.jstor.org/stable/j.ctt1v2xv4", "citation_reference": "Anderson, Lorin W. & Krathwohl, David R. (toim.) 2001." },
            "scales": [
                {"score": 1, "name": {"default_locale": "fi", "translations": {"fi": "Muistaminen"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä vain toistaa opittua tietoa implikoimatta ymmärrystä."}}]},
                {"score": 2, "name": {"default_locale": "fi", "translations": {"fi": "Ymmärtäminen"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä osaa hieman soveltaa ja uudelleenmuotoilla omin sanoin."}}]},
                {"score": 3, "name": {"default_locale": "fi", "translations": {"fi": "Soveltaminen"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä käyttää opittua tietoa konkreettisesti uusissa tilanteissa."}}]},
                {"score": 4, "name": {"default_locale": "fi", "translations": {"fi": "Analysointi"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä erittelee osia ja paljastaa piileviä suhteita tiedon välillä."}}]},
                {"score": 5, "name": {"default_locale": "fi", "translations": {"fi": "Arviointi"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä kykenee loogisesti perusteltuihin arvoasetelmiin teorioiden välillä."}}]},
                {"score": 6, "name": {"default_locale": "fi", "translations": {"fi": "Luominen"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä syntetisoi uutta alkuperäistä ajattelua."}}, {"default_locale": "fi", "translations": {"fi": "Tuotos ylittää selvästi annetun koulutusraamin asettaen uuden standardin."}}]}
            ],
            "rows": [{"default_locale": "fi", "translations": {"fi": "Kognitiivinen syvyys"}}]
        },
        {
            "id": "matrix_kahneman",
            "label": {"default_locale": "fi", "translations": {"fi": "Kahnemanin Ajattelumallit"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Arvioi ajattelun hitautta tai nopeutta (System 1 vs System 2)."}},
            "category_id": "scientific_theory",
            "type": "string",
            "allow_decimals": True,
            "strictness_level": 50,
            "require_justification": True,
            "theory_grounding": { "source_url": "https://us.macmillan.com/books/9780374533557", "citation_reference": "Kahneman, Daniel 2011." },
            "scales": [
                {"score": 1, "name": {"default_locale": "fi", "translations": {"fi": "Systeemi 1 (Nopea)"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä tekee tiedostamattomia, intuition ohjaamia havaintoja."}}, {"default_locale": "fi", "translations": {"fi": "Päättely sisältää todennäköisesti vahvistusvinoumaa tai halo-efektiä."}}]},
                {"score": 2, "name": {"default_locale": "fi", "translations": {"fi": "Siirtymä"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä yrittää hidastaa ja kyseenalaistaa intuitiota, mutta saattaa yhä sortua osin heuristiikkaan."}}]},
                {"score": 3, "name": {"default_locale": "fi", "translations": {"fi": "Systeemi 2 (Hidas)"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä analysoi systemaattisesti ja pohtii laiskasti piilotettuja vaihtoehtoja tarkkaan."}}, {"default_locale": "fi", "translations": {"fi": "Kognitiivinen ponnistus ja tietoinen hidastaminen näkyy tekstin laadussa."}}]}
            ],
            "rows": [{"default_locale": "fi", "translations": {"fi": "Ajattelun modaliteetti"}}]
        },
        {
            "id": "matrix_goodhart",
            "label": {"default_locale": "fi", "translations": {"fi": "Performatiivisuus"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Arvioi mittarin ja tavoitteen vääristymää."}},
            "category_id": "scientific_theory",
            "type": "string",
            "allow_decimals": True,
            "strictness_level": 70,
            "require_justification": True,
            "theory_grounding": { "source_url": "https://www.cna.org/reports/2022/09/", "citation_reference": "Stumborg, Michael F. ym. 2022. Goodhart's law." },
            "scales": [
                {"score": 1, "name": {"default_locale": "fi", "translations": {"fi": "Sokea usko"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä uskoo tekoälyn ensimmäiseen analyysiin sokeasti eikä huomaa edes ilmeisiä logiikkavirheitä."}}, {"default_locale": "fi", "translations": {"fi": "Käyttäjä toimii passiivisena matkustajana prosessissa."}}]},
                {"score": 2, "name": {"default_locale": "fi", "translations": {"fi": "Reaktiivinen huomioija"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä korjaa selkeitä faktavirheitä, mutta jatkaa mittareiden ja suoritustapojen uskomista kyseenalaistamatta."}}]},
                {"score": 3, "name": {"default_locale": "fi", "translations": {"fi": "Pintapuolinen"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä huomaa virheet ja pyytää korjausta, mutta tyytyy pintapuoliseen ehostukseen."}}, {"default_locale": "fi", "translations": {"fi": "Ohjaa tekoälyä oireiden, ei juurisyiden, korjaamiseen."}}]},
                {"score": 4, "name": {"default_locale": "fi", "translations": {"fi": "Kriittinen ohjaaja"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä kyseenalaistaa aktiivisesti mittarin luotettavuuden suhteessa perimmäiseen tavoitteeseen."}}]},
                {"score": 5, "name": {"default_locale": "fi", "translations": {"fi": "Aktiivinen haastaja"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä etsii aktiivisesti virheitä, haastaa tekoälyn logiikkaa ja vaatii perustavaa laatua olevia korjauksia ja todisteita."}}, {"default_locale": "fi", "translations": {"fi": "Toimii ehdottomana prosessin ajajana delegoidakseen vain suoritettavan työn."}}]}
            ],
            "rows": [{"default_locale": "fi", "translations": {"fi": "Performativiteetti ja ajaminen"}}]
        },
        {
            "id": "matrix_task_interaction",
            "label": {"default_locale": "fi", "translations": {"fi": "Tehtävävuorovaikutus (Task Interaction)"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Arvioi käyttäjän toimintatapaa ja vastuunottoa suhteessa tekoälyyn."}},
            "category_id": "scientific_theory",
            "type": "string",
            "allow_decimals": True,
            "strictness_level": 50,
            "require_justification": True,
            "theory_grounding": { "source_url": "", "citation_reference": "Covey (Proactivity), Fowler (Pair Programming), Senge (Systems Thinking)" },
            "scales": [
                {"score": 1, "name": {"default_locale": "fi", "translations": {"fi": "Matkustaja (Passenger)"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä on passiivinen ja tekee vain sen mitä erikseen pyydetään."}}, {"default_locale": "fi", "translations": {"fi": "Vaatii jatkuvaa ohjeistusta ja johtamista, eikä ota omistajuutta lopputuloksesta."}}]},
                {"score": 2, "name": {"default_locale": "fi", "translations": {"fi": "Kuljettaja (Driver)"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä on aktiivinen suorittaja, joka keskittyy toimeenpanoon ja maaliin viemiseen."}}, {"default_locale": "fi", "translations": {"fi": "Fokus on välittömässä suorituksessa ison kuvan sijaan, riskinä väärä suunta."}}]},
                {"score": 3, "name": {"default_locale": "fi", "translations": {"fi": "Navigaattori (Navigator)"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä toimii taktisena ohjaajana, joka lukee karttaa ja ennakoi esteitä tiimille."}}, {"default_locale": "fi", "translations": {"fi": "Ylläpitää kokonaiskuvaa ja tukee suoritusta joutumatta itse liialliseen ruohonjuuritason työhön."}}]},
                {"score": 4, "name": {"default_locale": "fi", "translations": {"fi": "Arkkitehti (Architect)"}}, "claims": [{"default_locale": "fi", "translations": {"fi": "Käyttäjä toimii strategisena visionäärinä, joka suunnittelee rakenteet ja prosessit."}}, {"default_locale": "fi", "translations": {"fi": "Keskittyy skaalautuvuuteen, pitkän aikavälin visioon ja systeemin optimointiin."}}]}
            ],
            "rows": [{"default_locale": "fi", "translations": {"fi": "Aloitteellisuus ja systeemitason vastuu"}}]
        }
    ]

    # 1. CREATE MATRICES WITH CLEAN SLUGS
    # Dictionary mapping V1 UUID to the new clean V2 matrix slug
    uuid_to_slug: dict[str, str] = {}

    steps_source = v1_db.get("steps", [])
    if isinstance(steps_source, dict):
        steps_source = list(steps_source.values())

    for idx, step_data in enumerate(steps_source):
        step_id = step_data.get("id", f"missing_id_{idx}")
        v1_name = step_data.get("name") or f"step_{idx}"
        clean_slug = f"matrix_{slugify(v1_name, idx)}"

        # Deduplicate slugs
        original_slug = clean_slug
        counter = 1
        while clean_slug in uuid_to_slug.values():
            clean_slug = f"{original_slug}_{counter}"
            counter += 1

        uuid_to_slug[step_id] = clean_slug

        strictness = 50
        try:
            strictness = int(float(step_data.get("weight", 0.5)) * 100)
        except (ValueError, TypeError):
            pass

        v1_type = step_data.get("type", "")
        explanation = step_data.get("explanation", "")
        if v1_type == "instruction":
            explanation = step_data.get("content", "")

        name_lower = v1_name.lower()
        desc_lower = explanation.lower()

        # Determine if this step is purely an instruction/role rather than a matrix
        raw_scales = step_data.get("scales", [])
        raw_rows = step_data.get("rows", [])
        
        is_instruction = False
        cat_id = "cognitive_evaluation"
        block_type = "string"

        if not raw_scales:
            is_instruction = True
            block_type = "instruction"
            role_keywords = ["analyst", "judge", "coach", "falsifier", "retrieval", "overseer", "interaction", "agent", "profiler"]
            if any(k in name_lower for k in role_keywords):
                cat_id = "agent_role"
            else:
                cat_id = "system_rule"

        # Apply fallback intelligence for V1 agents that were completely empty
        if not explanation.strip():
            if clean_slug == "matrix_retrieval_agent":
                explanation = "Olet tiedonhakuun erikoistunut agentti (Retrieval Agent). Tehtäväsi on käsitellä syöte ja hakea siihen liittyvää luotettavaa ja relevanttia faktaa tukemaan myöhempiä päätöksiä. Etsi kontekstia ilman omia tulkintoja."
            elif clean_slug == "matrix_falsifier":
                explanation = "Olet kriittinen auditoija (Falsifier). Tehtäväsi on yrittää aktiivisesti murtaa, kumota tai löytää loogisia virhepäätelmiä aiemmista argumenteista. Etsi heikkoja oletuksia (Weak Warrants) ja jälkikäteisrationalisointeja (Post-Hoc Rationalization)."
            elif clean_slug in ["matrix_input_processing", "matrix_input_processor"]:
                explanation = "Tehtäväsi on käsitellä raakatiedot ja syötteet (Input Processing). Poista kohina, jäsennä olennaiset väitteet ja valmistele data selkeään, analysoitavaan formaattiin seuraavia vaiheita varten."
            elif clean_slug == "matrix_xai_reporter":
                explanation = "Olet selitettävän tekoälyn raportoija (XAI Reporter). Tehtäväsi on koota kaikkien aiempien analyysivaiheiden löydökset yhdeksi selkeäksi, läpinäkyväksi ja tiiviiksi synteesiksi, joka nostaa esiin tärkeimmät huomiot ja vinoumat."
            elif clean_slug == "matrix_analyst":
                explanation = "Olet Analyytikko (Analyst). Tehtäväsi on käsitellä tietoa puolueettomasti, etsiä syy-seuraussuhteita ja muodostaa selkeä, jäsennelty katsaus käsiteltävästä materiaalista."
            elif clean_slug == "matrix_archivist":
                explanation = "Olet Arkistonhoitaja (Archivist). Tehtäväsi on peilata nykyistä päätöksentekoa organisaation aikaisempiin linjauksiin, ohjeisiin ja turvallisuusprotokolliin. Varmista sääntöjenmukaisuus (Compliance)."
            elif clean_slug == "matrix_causal_analyst":
                explanation = "Olet Kausaalinen Analyytikko (Causal Analyst). Tehtäväsi on tunnistaa syy-seuraussuhteet, rakentaa kontrafaktuaalisia (mitä jos) skenaarioita ja arvioida väitteiden uskottavuutta."
            elif clean_slug == "matrix_coach":
                explanation = "Olet Valmentaja (Coach). Tehtäväsi on antaa rakentavaa palautetta, tukea kognitiivista kehitystä ja ohjata käyttäjää tai toista agenttia kohti parempia ja syvällisempiä ratkaisuja."
            elif clean_slug == "matrix_guard":
                explanation = "Olet Turva-agentti (Guard). Tehtäväsi on valvoa syötteitä ja tulosteita eettisten jännitteiden, tietoturvauhkien ja asenteellisuuksien (bias) varalta."
            elif clean_slug == "matrix_interaction_analyst":
                explanation = "Olet Vuorovaikutusanalyytikko. Tehtäväsi on arvioida käyttäjän ja tekoälyn välistä dynaamikkaa, aloitteellisuutta ja hallintasuhdetta."
            elif clean_slug == "matrix_judge":
                explanation = "Olet Tuomari (Judge). Tehtäväsi on arvioida aiemmin tuotettu todistusaineisto ja analyysit kokonaisuutena. Anna lopullinen, perusteltu ja puolueeton tuomio."
            elif clean_slug == "matrix_logician":
                explanation = "Olet Loogikko (Logician). Tehtäväsi on purkaa argumentit niiden loogisiin osiin (väite, peruste, oikeutus) Toulminin mallin mukaisesti ja arvioida päättelyn pätevyys."
            elif clean_slug == "matrix_overseer":
                explanation = "Olet Valvoja (Overseer). Tehtäväsi on koordinoida muita agentteja, valvoa työnkulun etenemistä ja vastata siitä, että lopullinen tuotos on linjassa alkuperäisen tavoitteen kanssa."
            elif clean_slug == "matrix_panel":
                explanation = "Toimit osana monialaista asiantuntijapaneelia. Kuuntele muiden agenttien argumentteja, haasta niitä tarvittaessa kunnioittavasti ja pyri löytämään resilienssiä korostava synteesi."
            elif clean_slug == "matrix_profiler":
                explanation = "Olet Profiloija (Profiler). Tehtäväsi on analysoida tekstin sävyä, piilomerkityksiä, kirjoittajan intentioita sekä psykologista ja kielenkäytännöllistä profiilia."
            else:
                explanation = f"Huomaa: Olet {cat_id} nimeltään {v1_name}. Toimi annetun roolin mukaisesti tiimin ohjeistuksessa."

        matrix = {
            "id": clean_slug,
            "label": {
                "default_locale": "fi",
                "translations": {"fi": v1_name}
            },
            "description": {
                "default_locale": "fi",
                "translations": {"fi": explanation}
            },
            "category_id": cat_id,
            "type": block_type,  
            "allow_decimals": not is_instruction,
            "strictness_level": strictness,
            "require_justification": not is_instruction,
        }

        # Agent types are no longer guessed or enforced in V2

        is_theory = False
        if "toulmin" in name_lower or "toulmin" in desc_lower or "argument" in desc_lower:
            uuid_to_slug[step_id] = "matrix_toulmin"
            is_theory = True
        elif "bloom" in name_lower or "bloom" in desc_lower or "cognitiv" in name_lower or "kognitiivi" in name_lower:
            uuid_to_slug[step_id] = "matrix_bloom"
            is_theory = True
        elif "kahneman" in name_lower or "kahneman" in desc_lower or "fast and slow" in desc_lower or "system 1" in desc_lower or "system 2" in desc_lower:
            uuid_to_slug[step_id] = "matrix_kahneman"
            is_theory = True
        elif "goodhart" in name_lower or "goodhart" in desc_lower or "performatiivisuus" in name_lower or "performativity" in name_lower:
            uuid_to_slug[step_id] = "matrix_goodhart"
            is_theory = True

        if is_theory:
            continue

        if not is_instruction:
            matrix["scales"] = raw_scales
            
            # Convert simple string rows into the I18nText format if needed
            parsed_rows = []
            if not raw_rows:
                raw_rows = [v1_name]

            for r in raw_rows:
                if isinstance(r, str):
                    parsed_rows.append({"default_locale": "fi", "translations": {"fi": r}})
                else:
                    parsed_rows.append(r)

            matrix["rows"] = parsed_rows if parsed_rows else [{"default_locale": "fi", "translations": {"fi": "Arviointi"}}]

        matrices.append(matrix)

    # 1.B MIGRATE V1 COMPONENTS -> V2 MATRICES (PromptBlocks)
    components_db = v1_db.get("components", [])
    if isinstance(components_db, dict):
        components_list = list(components_db.values())
    else:
        components_list = components_db

    for c_idx, comp_data in enumerate(components_list):
        if not comp_data:
            continue

        c_uuid = comp_data.get("id")
        raw_slug = comp_data.get("slug", "") or comp_data.get("name", "")
        # Standardize Slug
        clean_slug = f"block_{slugify(raw_slug, c_idx)}"

        # Deduplicate
        original_slug = clean_slug
        counter = 1
        while clean_slug in uuid_to_slug.values():
            clean_slug = f"{original_slug}_{counter}"
            counter += 1

        uuid_to_slug[c_uuid] = clean_slug

        c_name = comp_data.get("name") or comp_data.get("slug") or f"LegacyPromptBlock {c_idx}"
        c_desc = comp_data.get("description", "")
        c_content = comp_data.get("content") or comp_data.get("instructions", "")
        # Fallback if both are empty
        if not c_desc and c_content:
            c_desc = c_name

        name_lower = c_name.lower()
        desc_lower = c_desc.lower()

        is_theory = False
        if "toulmin" in name_lower or "toulmin" in desc_lower or "argument" in desc_lower:
            uuid_to_slug[c_uuid] = "matrix_toulmin"
            is_theory = True
        elif "bloom" in name_lower or "bloom" in desc_lower or "cognitiv" in name_lower or "kognitiivi" in name_lower:
            uuid_to_slug[c_uuid] = "matrix_bloom"
            is_theory = True
        elif "kahneman" in name_lower or "kahneman" in desc_lower or "fast and slow" in desc_lower or "system 1" in desc_lower or "system 2" in desc_lower:
            uuid_to_slug[c_uuid] = "matrix_kahneman"
            is_theory = True
        elif "goodhart" in name_lower or "goodhart" in desc_lower or "performatiivisuus" in name_lower or "performativity" in name_lower:
            uuid_to_slug[c_uuid] = "matrix_goodhart"
            is_theory = True

        if is_theory:
            continue

        block_matrix = {
            "id": clean_slug,
            "label": {
                "default_locale": "fi",
                "translations": {"fi": c_name}
            },
            "description": {
                "default_locale": "fi",
                "translations": {"fi": f"{c_desc}\n\n{c_content}".strip()}
            },
            "category_id": "system_rule",
            "type": "instruction",  # V2 BlockDataType INSTRUCTION
            "allow_decimals": False,
            "strictness_level": 50,
            "require_justification": False,
        }
        matrices.append(block_matrix)

    v2_seed["matrices"] = matrices

    # 2. CREATE TASK BLUEPRINTS FROM V1 STEPS
    task_blueprints: list[dict[str, Any]] = []
    
    steps_source = v1_db.get("steps", [])
    if isinstance(steps_source, dict):
        steps_source = list(steps_source.values())
        
    for comp_idx, step_data in enumerate(steps_source):
         step_uuid = step_data.get("id", f"missing_tb_{comp_idx}")
         b_name = step_data.get("name") or f"Task {comp_idx}"
         clean_b_slug = f"task_{slugify(b_name, comp_idx)}"
         
         # Deduplicate TaskBlueprint ID
         original_slug = clean_b_slug
         counter = 1
         while clean_b_slug in [t["id"] for t in task_blueprints]:
             clean_b_slug = f"{original_slug}_{counter}"
             counter += 1
             
         prompt_blocks = []
         
         # 1. Did V1 step reference legacy_prompt_blocks directly?
         inner_uuids = step_data.get("prompts", []) or step_data.get("llm_prompts", [])
         for suuid in inner_uuids:
             if suuid in uuid_to_slug:
                 prompt_blocks.append(uuid_to_slug[suuid])
                 
         # 2. Add itself as a matrix if it was a matrix step
         if step_uuid in uuid_to_slug:
              prompt_blocks.append(uuid_to_slug[step_uuid])
         
         blueprint = {
             "id": clean_b_slug,
             "slug": clean_b_slug,
             "name": {
                 "default_locale": "fi",
                 "translations": {"fi": b_name}
             },
             "description": {
                 "default_locale": "fi",
                 "translations": {"fi": step_data.get("description", "")}
             },
             "prompt_blocks": prompt_blocks,
             "pre_hooks": step_data.get("config", {}).get("pre_hooks", []),
             "model_strategy": step_data.get("config", {}).get("model_strategy", None)
         }
         
         # Register V1 legacy step UUID directly to this new blueprint slug
         uuid_to_slug[step_uuid] = clean_b_slug
         task_blueprints.append(blueprint)

    v2_seed["task_blueprints"] = task_blueprints


    # 3. CREATE WORKFLOWS (DAG ROUTING)
    workflows: list[dict[str, Any]] = []

    workflows_source = v1_db.get("workflows", [])
    if isinstance(workflows_source, dict):
        workflows_source = list(workflows_source.values())

    for wf_idx, wf_data in enumerate(workflows_source):
        v1_wf_name = wf_data.get("name") or f"workflow_{wf_idx}"
        v1_steps_array = wf_data.get("steps", [])
        clean_wf_slug = f"workflow_{slugify(v1_wf_name, wf_idx)}"

        v2_wf = {
            "id": clean_wf_slug,
            "name": {
                "default_locale": "fi",
                "translations": {"fi": v1_wf_name}
            },
            "description": {
                "default_locale": "fi",
                "translations": {"fi": wf_data.get("description", "")}
            },
            "expected_inputs": {
                "chat_log": "string",
            },
            "steps": []
        }

        # Parse workflow steps and map legacy step UUIDs to new TaskBlueprint Slugs
        for comp_idx, comp_uuid in enumerate(v1_steps_array):
            if comp_uuid not in uuid_to_slug:
                continue
                
            blueprint_slug = uuid_to_slug[comp_uuid]
            
            # If a workflow directly referenced a Component/Matrix instead of a Step, 
            # dynamically wrap it in a pseudo-blueprint to satisfy V2 architecture.
            if blueprint_slug.startswith("matrix_") or blueprint_slug.startswith("block_"):
                pseudo_slug = f"task_{blueprint_slug}"
                if pseudo_slug not in [t["id"] for t in task_blueprints]:
                     task_blueprints.append({
                         "id": pseudo_slug,
                         "slug": pseudo_slug,
                         "name": {"default_locale": "fi", "translations": {"fi": f"Auto-Wrapper for {blueprint_slug}"}},
                         "description": None,
                         "prompt_blocks": [blueprint_slug],
                         "pre_hooks": [],
                         "model_strategy": None
                     })
                blueprint_slug = pseudo_slug

            node_slug = f"step_node_{comp_idx}"

            existing_steps = v2_wf["steps"]
            prev_step_id = None
            if isinstance(existing_steps, list) and len(existing_steps) > 0:
                last_step = existing_steps[-1]
                if isinstance(last_step, dict):
                    prev_step_id = last_step.get("id")

            depends_on_list = [prev_step_id] if prev_step_id else []

            input_mappings = {
                "context": "$inputs.chat_log",
                "document": "$inputs.document_text"
            }
            if prev_step_id:
                input_mappings[prev_step_id] = f"${prev_step_id}.output"

            step_rule = {
                "id": node_slug,
                "task_blueprint": blueprint_slug,
                "depends_on": depends_on_list,
                "input_mappings": input_mappings,
                "hook": None
            }
            v2_wf["steps"].append(step_rule)  # type: ignore

        workflows.append(v2_wf)

    v2_seed["workflows"] = workflows

    # 3. GLOBAL CONFIGS (Flattened ModelRegistry)
    v1_sys_cfgs = v1_db.get("system_config", {})
    if isinstance(v1_sys_cfgs, dict):
        v1_sys_cfgs = list(v1_sys_cfgs.values())

    valid_v2_sys_configs = []

    for cfg in v1_sys_cfgs:
        cfg_id = cfg.get("id")
        if cfg_id == "model_registry":
            old_models = cfg.get("models", {})
            flat_models = {}
            # Flatten "google -> deep -> attrs" into "deep -> {provider: google, attrs...}"
            for provider_name, provider_profiles in old_models.items():
                if isinstance(provider_profiles, dict):
                    for profile_key, profile_attrs in provider_profiles.items():
                        if isinstance(profile_attrs, dict):
                            # Deep copy to avoid mutating the original
                            attrs_copy = profile_attrs.copy()
                            attrs_copy["provider"] = provider_name
                            flat_models[profile_key] = attrs_copy

            new_cfg = {
                "id": cfg.get("id"),
                "slug": cfg.get("slug", "config_model_registry"),
                "type": "model_registry",
                "models": flat_models
            }
            valid_v2_sys_configs.append(new_cfg)

    v2_seed["system_config"] = valid_v2_sys_configs

    # 4. TRANSFER REMAINING RAW V1 COLLECTIONS FOR UI DISPLAY MAPPING ONLY
    model_mapping = {
        "output_configs": TypeAdapter(OutputConfig),
        "dimensions": TypeAdapter(Observation),
        "references": TypeAdapter(Reference),
        "users": TypeAdapter(User),
        "organizations": TypeAdapter(Organization)
    }

    for coll_name, adapter in model_mapping.items():
        raw_data = v1_db.get(coll_name, [])
        if isinstance(raw_data, dict):
            raw_data = list(raw_data.values())

        validated_data = []
        for item in raw_data:
            try:
                # V1 models lacked standard timestamps for references vs others, fallback implemented in v2_core.py
                import typing
                parsed = typing.cast(typing.Any, adapter).validate_python(item)
                validated_data.append(parsed.model_dump(mode="json"))
            except Exception as e:
                print(f"[ERROR] Failed to validate {coll_name} item: {item.get('id', 'unknown')}. Error: {e}")
                # We do not fail-fast on migration extraction, we drop invalid data so V2 only gets pure valid ones.
                # Actually, Zero-Compromise pledge means we should fail if data is lost, but V1 legacy data has dirt.
                # We will crash explicitly since it's an ETL script.
                raise e

        v2_seed[coll_name] = validated_data

    with open(v2_path, "w", encoding="utf-8") as f:
        json.dump(v2_seed, f, indent=4, ensure_ascii=False)

    print(f"Successfully generated {len(matrices)} matrices and {len(workflows)} workflows.")

if __name__ == "__main__":
    migrate_seeds()
