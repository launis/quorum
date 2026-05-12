import json
import uuid

def generate_tda_id():
    return "tda_" + uuid.uuid4().hex[:16]

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"

with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

found = False
for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_fb15f8dcf23f4865":
        found = True
        
        # 1. XML + Theory Injection (Anti-Token Bloat)
        block["ai_description"] = (
            "<system_directive>\n"
            "<objective>Evaluate strict adherence to operational guidelines, verifiable provenance, and structural integrity based on established archival frameworks.</objective>\n"
            "<epistemic_anchor>ARMA International. \"Generally Accepted Recordkeeping Principles (The Principles).\" A framework ensuring organizational Accountability, Transparency, Integrity, Protection, Compliance, Availability, Retention, and Disposition. Lexical markers of compliance include 'in accordance with' or 'as mandated by'; failure markers include 'I assumed' or 'we can bypass'.</epistemic_anchor>\n"
            "<rules>\n"
            "<rule>Enforce the Null Hypothesis: Assume all actions are ungrounded hallucinations unless explicit compliance and methodological structure are demonstrated.</rule>\n"
            "</rules>\n"
            "</system_directive>"
        )
        
        # Update Theory Grounding
        block["theory_grounding"] = {
            "source_url": "https://www.arma.org/page/principles",
            "citation_reference": "ARMA International. Generally Accepted Recordkeeping Principles."
        }
        
        # 2. MECE Triangulation (Exactly 3 claims per scale)
        block["scales"] = [
            {
                "score": 1,
                "name": {"default_locale": "fi", "translations": {"fi": "Kriittisesti Poikkeava", "en": "Critically Misaligned"}},
                "ai_label": "CATASTROPHIC FAILURE - BRUTE FORCE HALLUCINATION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Ohjeiden täydellinen sivuuttaminen", "en": "Complete disregard of instructions"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY blatant fabrication where the output contradicts foundational constraints.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY blatant fabrication where the output contradicts foundational constraints or explicitly disregards provided instructions. Look for lexical markers of autonomous hallucination (e.g., 'I created', 'Instead of'). Document the deviation in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Absoluuttinen varmuus ilman lähdeviitettä", "en": "Absolute certainty without provenance"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an assertion presented as absolute truth without verifiable provenance.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an assertion presented as absolute truth without verifiable provenance or structural anchor (ARMA Integrity violation). Look for hubristic markers like 'it is guaranteed' or 'always'. Document the missing provenance in reasoning_trace before quoting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Yksityisyyden tai suojauksen vaarantaminen", "en": "Compromising privacy or protection"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where sensitive or restricted information is exposed or mishandled.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where sensitive, restricted, or private information is mishandled, explicitly violating the ARMA Protection principle. Document the operational breach in reasoning_trace before extracting the violating text.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 2,
                "name": {"default_locale": "fi", "translations": {"fi": "Poikkeava", "en": "Misaligned"}},
                "ai_label": "FUNDAMENTALLY FLAWED - PASSIVE FRAGMENTATION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Irralliset käytännöt ilman rakennetta", "en": "Isolated practices without structure"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of isolated compliance without overarching structural integrity.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of isolated compliance where scattered correct elements exist, but lack overarching structural integrity (ARMA Accountability). Document the fragmented adherence in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Ohjeiden ohittaminen mukavuussyistä", "en": "Bypassing instructions for convenience"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT evidence where a required standard operating procedure is explicitly bypassed.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT evidence where a required standard operating procedure or compliance rule is explicitly bypassed for convenience. Look for dismissive markers (e.g., 'we can skip', 'not strictly necessary'). Document the bypassed rule in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Yksipuolinen ja sokea suorittaminen", "en": "One-sided and blind execution"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an execution that blindly follows one rule while completely ignoring conflicting constraints.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an execution that blindly follows a single rule while actively ignoring known conflicting constraints or alternative models. Map the ignored constraints in reasoning_trace before quoting the tunnel-visioned execution.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 3,
                "name": {"default_locale": "fi", "translations": {"fi": "Neutraali", "en": "Neutral"}},
                "ai_label": "NEUTRAL - MECHANICAL COMPLIANCE",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Mekaaninen perusprosessin noudattaminen", "en": "Mechanical adherence to basic process"}},
                        "ai_description": "CRITICAL DIRECTIVE: FIND evidence that the basic compliance process is followed in a mechanical, literal manner.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: FIND evidence that the basic compliance process is followed in a mechanical, literal manner without strategic synthesis. Document the literal interpretation in reasoning_trace before extracting the compliant text.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Haasteiden ja riskien sivuuttaminen", "en": "Ignoring challenges and risks"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where the author avoids acknowledging operational risks or compliance ambiguities.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where the author avoids acknowledging operational risks, compliance ambiguities, or necessary rebuttals. Look for sweeping generic statements that hide complexity. Explain the hidden risk in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Lähdekritiikin puute", "en": "Lack of source criticism"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY a reliance on undocumented or unverified internal knowledge.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY a reliance on undocumented or unverified internal knowledge rather than established external guidelines (violating ARMA Transparency). Document the missing verifiability in reasoning_trace before quoting the unsupported claim.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 4,
                "name": {"default_locale": "fi", "translations": {"fi": "Linjassa", "en": "Aligned"}},
                "ai_label": "LOGICALLY SOUND - SYSTEMATIC EXECUTION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Jäsennelty ja todistettava ohjausmalli", "en": "Structured and verifiable steering model"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE explicit adherence to structured directives where the chain of reasoning is clearly verifiable.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE explicit adherence to structured directives where the chain of reasoning is clearly verifiable and transparent. Look for lexical markers like 'according to the guidelines' or 'based on the procedure'. Document the structural alignment in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Rajoitteiden ja reunaehtojen tunnistaminen", "en": "Identification of constraints and boundary conditions"}},
                        "ai_description": "CRITICAL DIRECTIVE: FIND epistemological humility where limitations and boundary conditions are explicitly stated.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: FIND epistemological humility where limitations, operational constraints, and boundary conditions are explicitly stated. Look for scoping markers like 'within the scope of' or 'subject to'. Document the bounded context in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Vastaväitteiden ennakoiva käsittely", "en": "Proactive handling of counterarguments"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where potential compliance conflicts are systematically addressed.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where potential compliance conflicts or alternative operational models are systematically addressed and resolved. Document the conflict resolution logic in reasoning_trace before quoting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    }
                ]
            },
            {
                "score": 5,
                "name": {"default_locale": "fi", "translations": {"fi": "Vahvasti Linjassa", "en": "Strongly Aligned"}},
                "ai_label": "THEORETICALLY PERFECT - MASTERFUL INTEGRATION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Kognitiivisen kitkan eksplisiittinen dokumentointi", "en": "Explicit documentation of cognitive friction"}},
                        "ai_description": "CRITICAL DIRECTIVE: FIND evidence of 'System 2' deliberation detailing why specific compliance tradeoffs were made.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: FIND evidence of 'System 2' deliberation detailing exactly why specific compliance tradeoffs were made. Look for complex dialectical reasoning ('we chose X over Y because'). Document the cognitive friction step-by-step in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Täydellinen ulkoinen ankkurointi", "en": "Perfect external anchoring"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE where the execution is fortified by explicit backing from external expert frameworks.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE where the execution is fortified by explicit backing from external expert frameworks (like ARMA Principles or ISO standards). Map the connection to the external anchor in reasoning_trace before extracting the definitively compliant quote.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Tavoitteiden ja riskien mestarillinen tasapainottelu", "en": "Masterful balancing of goals and risks"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT a masterfully constructed resolution that seamlessly balances strict compliance with operational goals.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT a masterfully constructed resolution that seamlessly balances strict compliance (Integrity/Protection) with operational goals (Availability). Document the perfect equilibrium triad in reasoning_trace before extracting the definitive conclusion.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    }
                ]
            }
        ]
        break

if found:
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Successfully refactored blk_fb15f8dcf23f4865 with TDA mandates.")
else:
    print("Error: Block blk_fb15f8dcf23f4865 not found!")
