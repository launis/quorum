import json
import uuid

FILE_PATH = r"c:\src\quorum\backend_v2\seed\seed_data.json"

def gen_tda():
    return f"tda_{uuid.uuid4().hex[:16]}"

updates = {
    # SCALE 1 (Negative - EXISTS)
    "Teksti ainoastaan toistaa annettua tietoa.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Remembering. Rote memorization without processing.</epistemic_anchor>\n  <fatal_flaw_context>Target verbatim regurgitation without synthesis.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Find a sentence that is purely a verbatim copy or a direct, mechanical repetition of the input text without any synthesis. Extract the exact_quote."
            }
        ]
    },
    "Ymmärrystä ei ole eksplisiittisesti osoitettu.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Lack of comprehension.</epistemic_anchor>\n  <fatal_flaw_context>Target circular logic or vague filler words used to mask a lack of understanding.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Find a section where the author attempts to explain a concept but relies entirely on circular logic or vague filler words, demonstrating a lack of actual understanding. Detail the circular logic before extracting the exact_quote."
            }
        ]
    },
    "Tieto esitetään absoluuttisena faktana ilman lähdekritiikkiä.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Uncritical reception of knowledge.</epistemic_anchor>\n  <fatal_flaw_context>Target unverified assumptions presented as 100% absolute facts.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Locate a sentence where the author presents a highly complex or debatable assumption as a 100% absolute fact without providing any source or critical reflection. Extract the exact_quote."
            }
        ]
    },
    # SCALE 2 (Negative - EXISTS)
    "Tieto on muotoiltu uudelleen omin sanoin.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Understanding. Simple paraphrasing without deeper integration.</epistemic_anchor>\n  <fatal_flaw_context>Target surface-level rewrites that add no analytical value.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Identify a paragraph that merely paraphrases a known fact or input text, without adding any new logical deductions or connecting it to a broader context. Extract the exact_quote of this surface-level rewrite."
            }
        ]
    },
    "Käsitteiden väliset syvemmät yhteydet puuttuvat.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Lack of relational understanding.</epistemic_anchor>\n  <fatal_flaw_context>Target disjointed lists of concepts without integration.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Find an instance where the author lists multiple concepts sequentially but completely fails to explain how they interact or relate to each other. Document the missing connection before extracting the exact_quote."
            }
        ]
    },
    # SCALE 3 (Negative - EXISTS)
    "Tietoa sovelletaan uuteen, konkreettiseen tilanteeseen.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Applying. Rigid template application.</epistemic_anchor>\n  <fatal_flaw_context>Target forced application of a rule without contextual adaptation.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Locate a section where the author attempts to apply a concept to a new situation, but does so by rigidly forcing a template without adapting to the specific context. Extract the exact_quote."
            }
        ]
    },
    "Soveltaminen on mekaanista.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Mechanistic execution.</epistemic_anchor>\n  <fatal_flaw_context>Target blind execution of processes.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Find an example where the author executes a known process blindly and mechanistically, ignoring obvious contextual nuances. Detail the mechanical rigidity before extracting the exact_quote."
            }
        ]
    },
    "Vaihtoehtoisia lähestymistapoja ei ole käsitelty.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Lack of multi-perspective reasoning.</epistemic_anchor>\n  <fatal_flaw_context>Target one-sided solutions that dismiss alternatives.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Identify where the author proposes a single solution to a complex problem and explicitly uses dismissive language to ignore alternative approaches. Extract the exact_quote."
            }
        ]
    },
    # SCALE 4 (Positive - ALL_MUST_COMPLY)
    "Kokonaisuus on purettu rakenteellisiin osiin.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Analyzing. Structural decomposition.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Identify the exact sentence where the author explicitly breaks down a complex topic into its distinct structural components. Detail the decomposition before extracting the exact_quote."
            }
        ]
    },
    "Osien väliset piilevät suhteet on paljastettu.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Identifying underlying relationships.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Locate where the author actively maps the underlying causal or structural relationships between the identified components, going beyond the surface level. Extract the exact_quote."
            }
        ]
    },
    "Analyysin taustaoletuksia ei kyseenalaisteta riittävästi.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Questioning foundational axioms.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Find a sentence where the author explicitly identifies the foundational assumptions of their own analysis and actively questions or stress-tests them. Explain their critical reflection before extracting the exact_quote."
            }
        ],
        "new_fi_label": "Analyysin taustaoletukset on tunnistettu ja kyseenalaistettu.",
        "new_en_label": "The underlying assumptions of the analysis are identified and questioned."
    },
    # SCALE 5 (Positive - ALL_MUST_COMPLY)
    "Teksti esittää loogisesti perustellun arvoasetelman teorioiden välillä.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Evaluating. Making defensible judgments.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Locate the specific paragraph where the author compares two or more theories or options and makes a definitive, logically justified value judgment between them. Detail the justification before extracting the exact_quote."
            }
        ]
    },
    "Arviointi nojaa ekspliittisiin sisäisiin ja ulkoisiin kriteereihin.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Tethering to explicit standards.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Find the exact sentence where the author explicitly states the internal or external criteria they are using to perform their evaluation. Extract the exact_quote."
            }
        ]
    },
    "Vastaväitteet ja rajoitteet on käsitelty asiantuntevasti.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Anticipating and dismantling opposing views.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Identify where the author acts as their own prosecutor by raising a strong counterargument and then systematically dismantling it using evidence. Detail the dismantling logic before extracting the exact_quote."
            }
        ]
    },
    # SCALE 6 (Positive - ALL_MUST_COMPLY)
    "Teksti syntetisoi uuden ja alkuperäisen rakenteen tai hypoteesin.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Creating. Genuine intellectual creation.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Locate the exact formulation of the author's entirely novel structure, framework, or hypothesis that was synthesized from the preceding analysis. Extract the exact_quote."
            }
        ]
    },
    "Päätöksentekoprosessi ja kognitiivinen kitka on dokumentoitu.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Documenting cognitive friction and System 2 reasoning.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Find where the author explicitly describes their internal 'cognitive friction'—the difficulty, trade-offs, or deliberate reasoning process they underwent to reach their novel synthesis. Detail this friction before extracting the exact_quote."
            }
        ]
    },
    "Uusi synteesi on ankkuroitu ekspliittisesti asiantuntijalähteisiin.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). External anchoring of novel synthesis.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Identify the specific external expert source, theory, or literature the author uses to epistemologically anchor their novel synthesis. Document the anchor before extracting the exact_quote."
            }
        ]
    }
}

with open(FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_f921c7c0989b47e8":
        if "<system_directive>" not in block.get("ai_description", ""):
            block["ai_description"] = "<system_directive>\n  <epistemic_anchor>Bloom, B. S. (1956). Taxonomy of Educational Objectives. Higher-order thinking requires cognitive friction, structural decomposition, and novel synthesis over rote regurgitation.</epistemic_anchor>\n</system_directive>\n" + block.get("ai_description", "")
        
        for scale in block.get("scales", []):
            for claim in scale.get("claims", []):
                fi_label = claim.get("label", {}).get("translations", {}).get("fi", "")
                if fi_label in updates:
                    upd = updates[fi_label]
                    
                    if "new_fi_label" in upd:
                        claim["label"]["translations"]["fi"] = upd["new_fi_label"]
                        claim["label"]["translations"]["en"] = upd["new_en_label"]

                    claim["ai_description"] = upd["ai_description"]
                    
                    new_assertions = []
                    for ass_upd in upd["assertions"]:
                        new_assertions.append({
                            "tda_id": gen_tda(),
                            "ai_rule_description": ass_upd["desc"],
                            "inverse_evidence": ass_upd["inverse"],
                            "aggregation_mode": ass_upd["agg"]
                        })
                    claim["tda_assertions"] = new_assertions

with open(FILE_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("blk_f921c7c0989b47e8 updated successfully.")
