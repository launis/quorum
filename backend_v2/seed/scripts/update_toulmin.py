import json
import uuid

FILE_PATH = r"c:\src\quorum\backend_v2\seed\seed_data.json"

def gen_tda():
    return f"tda_{uuid.uuid4().hex[:16]}"

updates = {
    # SCALE 1
    "Väite on vailla perusteita.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. The Uses of Argument. A claim without data is merely an unfounded assertion.</epistemic_anchor>\n  <fatal_flaw_context>Target instances where the author presents a definitive assertion as an absolute fact, while shifting to a new topic without offering any grounds.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Find a sentence where the author makes a strong declarative assertion (Claim) and immediately introduces a completely new topic or paragraph, acting as if the assertion is self-evident. Document your step-by-step reasoning on why this transition acts as a substitute for evidence before extracting the exact_quote of the unsupported claim."
            }
        ]
    },
    "Data puuttuu.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Data is the foundation of practical argument.</epistemic_anchor>\n  <fatal_flaw_context>Target instances where an argument is presented, but completely relies on rhetorical fluff instead of empirical or textual evidence.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Locate a section where the author explicitly refuses to provide data or uses evasive language (e.g., 'it is widely known', 'everyone agrees') to bypass the need for evidence. Explain the author's avoidance strategy before extracting the exact_quote."
            }
        ]
    },
    "Oikeutus (warrant) puuttuu.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. The Warrant is the crucial logical bridge connecting Data to Claim.</epistemic_anchor>\n  <fatal_flaw_context>Target a disjointed argument where Data is forcibly jammed next to a Claim without logical connective tissue. Example: 'Sales dropped 20%. Therefore fire the CEO.'</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Find a sentence where the author abruptly forces a conclusion immediately adjacent to raw data, using a transition marker like 'therefore' or 'thus' (in the native language), but utterly fails to explain the underlying mechanism connecting them. Document your step-by-step reasoning on why this logical bridge is broken before extracting the exact_quote."
            }
        ]
    },
    "Esittää olettamuksia absoluuttisina faktoina.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Epistemological humility is required when making practical claims.</epistemic_anchor>\n  <fatal_flaw_context>Target extreme hubris: an unverified assumption or subjective opinion presented with 100% certainty.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Identify an instance where the author uses absolute, commanding language (e.g., 'must', 'is undeniably') to state a conclusion, but relies entirely on subjective rhetoric rather than empirical data. Detail your logical deduction of this rhetorical flaw before extracting the exact_quote."
            }
        ]
    },
    # SCALE 2
    "Väitteen tueksi esitetty data on irrelevanttia.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Data must have a relevant bearing on the Claim.</epistemic_anchor>\n  <fatal_flaw_context>Target disconnected data points that do not logically support the specific claim being made.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Find a section where the author presents specific Data, but explicitly connects it to a Claim that addresses a fundamentally different topic or scope. Document how the data is disconnected from the conclusion before extracting the exact_quote."
            }
        ]
    },
    "Väitteen tueksi esitetty data on riittämätöntä.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Grounds must be sufficient to bear the weight of the Claim.</epistemic_anchor>\n  <fatal_flaw_context>Target sweeping claims based on tiny, anecdotal, or weak data points.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Locate a sweeping, generalized Claim that the author attempts to support using only a single anecdotal example or explicitly narrow data point. Explain the insufficiency of the evidence before extracting the exact_quote."
            }
        ]
    },
    "Looginen silta (warrant) on irrallinen datasta.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Warrants must structurally map the provided Data to the given Claim.</epistemic_anchor>\n  <fatal_flaw_context>Target illogical reasoning where the stated rule/warrant does not apply to the provided data.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Identify a sentence where the author attempts to explain their logic (Warrant), but the explanation contradicts or completely ignores the Data they just presented. Document the logical contradiction before extracting the exact_quote."
            }
        ]
    },
    # SCALE 3
    "Oikeutus (warrant) on hatara.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. The Uses of Argument.</epistemic_anchor>\n  <fatal_flaw_context>Target an argument that relies on logical fallacies or extremely weak bridging principles.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Find an instance where the author explicitly relies on a known logical fallacy (e.g., ad hominem, slippery slope, appeal to authority without substance) as their main logical bridge (Warrant). Explain the fallacy step-by-step before extracting the exact_quote."
            }
        ]
    },
    "Vastaväitteitä (rebuttal) ei ole huomioitu.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. A complete argument must anticipate Rebuttals.</epistemic_anchor>\n  <fatal_flaw_context>Target one-sided arguments that completely ignore obvious counter-viewpoints.</fatal_flaw_context>\n</system_directive>",
        "assertions": [
            {
                "inverse": True, "agg": "EXISTS",
                "desc": "CRITICAL DIRECTIVE: Locate a section where the author explicitly dismisses an opposing viewpoint without providing any evidence, using dismissive language (e.g., 'obviously false', 'nonsense'). Detail the intellectual laziness of this dismissal before extracting the exact_quote."
            }
        ]
    },
    # SCALE 4 (POSITIVE - FLOOR LOGIC)
    "Looginen silta (warrant) on kestävä.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. A robust Warrant explicitly states the underlying principle.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Identify the exact sentence where the author explicitly explains the general rule or principle that makes their evidence relevant to their conclusion. Search for causal lexical markers such as 'which means that' or 'because of this principle' in the native language. Detail the author's logical bridge step-by-step before extracting the exact_quote."
            }
        ]
    },
    "Looginen silta kytkee datan eksplisiittisesti väitteeseen.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Explicit connection between Data and Claim.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Locate where the author actively maps the data points directly into the components of the claim, leaving nothing to the reader's assumption. Explain how the mapping is executed before extracting the exact_quote."
            }
        ]
    },
    "Taustaoletuksia ja poikkeuksia on käsitelty.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Recognizing boundary conditions and exceptions (Rebuttals/Qualifiers).</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Find a sentence where the author explicitly limits the scope of their claim, using lexical markers like 'except when', 'in the case of', or 'provided that'. Document this boundary condition before extracting the exact_quote."
            }
        ]
    },
    "Epävarmuudet on tunnistettu avoimesti.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Epistemological humility via Qualifiers.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Identify where the author acknowledges the probabilistic nature of their argument using lexical markers like 'it is likely', 'suggests', or 'indicates'. Explain their display of epistemological humility before extracting the exact_quote."
            }
        ]
    },
    # SCALE 5 (POSITIVE - FLOOR LOGIC)
    "Väite on vahvasti perusteltu asiantuntijadatalla.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. High-quality Grounds (Data) are verifiable and irrefutable.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Locate the specific empirical data, statistics, or expert citations the author uses as the foundational bedrock of their argument. Document why this data is robust before extracting the exact_quote."
            }
        ]
    },
    "Oikeutus (warrant) on aukoton.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. A watertight Warrant survives adversarial scrutiny.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Find the comprehensive explanation where the author anticipates logical gaps and pre-emptively seals them by explaining the airtight mechanism of their reasoning. Detail this mechanism before extracting the exact_quote."
            }
        ]
    },
    "Argumentti on ankkuroitu ekspliittisesti ulkoisiin asiantuntijalähteisiin.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. External Backing provides authority to the Warrant.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Identify the exact sentence where the author introduces external Backing (e.g., citing a specific study, theory, or expert by name) to validate their underlying rule. Document this external anchor before extracting the exact_quote."
            }
        ]
    },
    "Mahdolliset vastaväitteet on kumottu asiantuntevasti.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Active integration and refutation of Rebuttals.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Locate a section where the author explicitly raises a credible counterargument (using markers like 'Critics might say' or 'On the other hand') and then systematically dismantles it. Explain the author's refutation logic before extracting the exact_quote."
            }
        ]
    },
    "Päätöksentekoprosessi ja kognitiivinen kitka on dokumentoitu.": {
        "ai_description": "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. Demonstration of System 2 reasoning.</epistemic_anchor>\n</system_directive>",
        "assertions": [
            {
                "inverse": False, "agg": "ALL_MUST_COMPLY",
                "desc": "CRITICAL DIRECTIVE: Find where the author explicitly describes their internal decision-making process, highlighting the difficulty, trade-offs, or 'cognitive friction' involved in reaching the conclusion. Detail this friction before extracting the exact_quote."
            }
        ]
    }
}

with open(FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_440a5fef9331451b":
        block["ai_description"] = "<system_directive>\n  <epistemic_anchor>Toulmin, Stephen E. 2003. The Uses of Argument. A robust argument is grounded in data and explicitly justified by a warrant.</epistemic_anchor>\n</system_directive>\n" + block.get("ai_description", "")
        for scale in block.get("scales", []):
            for claim in scale.get("claims", []):
                fi_label = claim.get("label", {}).get("translations", {}).get("fi", "")
                if fi_label in updates:
                    upd = updates[fi_label]
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

print("blk_440a5fef9331451b updated successfully.")
