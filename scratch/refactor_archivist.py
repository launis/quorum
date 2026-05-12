import json
import uuid

def generate_tda_id():
    return f"tda_{uuid.uuid4().hex[:16]}"

def get_epistemic_anchor(level_desc):
    return f"<epistemic_anchor>Dworkin, R. (1986). Law's Empire (Stare Decisis). {level_desc}</epistemic_anchor>"

def refactor_matrix():
    file_path = "c:/src/quorum/backend_v2/seed/seed_data.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for block in data.get("prompt_blocks", []):
        if block.get("id") == "blk_fb15f8dcf23f4865":
            # Update the global matrix ai_description
            block["ai_description"] = (
                "<system_directive>\n"
                "  <epistemic_anchor>Dworkin, R. (1986). Law's Empire. Evaluating adherence to institutional precedent and organizational integrity.</epistemic_anchor>\n"
                "</system_directive>\n"
                "ROLE: ANTAGONISTIC PROSECUTOR (ZERO-TRUST). TASK: Evaluate the AI's output against the organization's established body of precedent, historical policies, and explicit guidelines. "
                "NULL HYPOTHESIS: Assume the output is a random hallucination, mechanically generated, or entirely untethered from institutional memory. "
                "You must actively search for deviations from precedent, intellectual laziness, missing rebuttals, and statements of absolute certainty without evidence (Hubris). "
                "Do NOT give the benefit of the doubt. True compliance requires documented cognitive friction, systematic testing of boundaries, and explicit source anchoring. "
                "MANDATORY DIRECTIVE: Default all boolean claim evaluations to FALSE. You must never infer, guess, or synthesize compliance. A claim can only be evaluated as TRUE if you can extract direct, undeniable semantic proof from the text."
            )

            # Define refactored data per score and claim index
            refactored_data = {
                1: [
                    {
                        "desc": get_epistemic_anchor("Absolute hallucination without precedent.") + "\n  <fatal_flaw_context>Target outputs that demonstrate zero institutional memory.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Locate the exact sentence where the AI makes a sweeping operational claim without referencing any established guideline, policy, or framework. Explain the absolute lack of grounding before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Complete lack of methodological structure.") + "\n  <fatal_flaw_context>Target unstructured, stream-of-consciousness outputs.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Identify where the text presents a solution as a random, unformatted paragraph, entirely bypassing expected methodological steps or structural constraints. Detail the missing structure before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Total disconnect from operational reality.") + "\n  <fatal_flaw_context>Target solutions that ignore all known system constraints.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Find an instance where the AI proposes an action or framework that contradicts fundamental, known operational limitations (e.g., assuming infinite resources or bypassing security). Document this disconnect before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Extreme hubris and unverified certainty.") + "\n  <fatal_flaw_context>Target assumptions masquerading as absolute facts.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Locate the exact phrase where the AI presents a subjective guess, probabilistic inference, or hallucination using definitive, absolute language (e.g., 'This is universally true', 'It is a proven fact') without providing empirical evidence. Extract the exact_quote.",
                        "inverse": True
                    }
                ],
                2: [
                    {
                        "desc": get_epistemic_anchor("Superficial fragmentation.") + "\n  <fatal_flaw_context>Target name-dropping of policies without applied logic.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Identify where the AI merely mentions a policy name, standard, or guideline without actively applying its specific constraints to the problem at hand. Explain this superficial reference before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Fundamentally unguided logic.") + "\n  <fatal_flaw_context>Target incoherent overall strategy despite localized compliance.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Locate an instance where the AI correctly formats a minor sub-point but fails to connect it to the overarching strategic goal or primary directive, resulting in a fragmented response. Document this incoherence before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Active policy violation.") + "\n  <fatal_flaw_context>Target direct contradictions of standard operating procedures.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Find the exact sentence where the AI recommends an action that directly contradicts a widely known, established best practice or explicit negative constraint within its domain. Detail the violation before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("One-sided argument generation.") + "\n  <fatal_flaw_context>Target the failure to explore alternative models or risks.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Identify where the AI forcefully advocates for a single pathway without once mentioning a valid alternative, trade-off, or competing methodology. Explain the lack of intellectual depth before extracting the exact_quote.",
                        "inverse": True
                    }
                ],
                3: [
                    {
                        "desc": get_epistemic_anchor("Mechanical, literal compliance.") + "\n  <fatal_flaw_context>Target responses that follow instructions like a robot without strategic context.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Locate where the AI fulfills a prompt requirement in the most basic, literal way possible, failing to anticipate implied needs or connect the task to broader organizational objectives. Detail this mechanical execution before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Failure to synthesize core principles.") + "\n  <fatal_flaw_context>Target the inability to read between the lines of precedent.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Find an instance where the AI applies a rule strictly to a situation where a known overarching principle (e.g., user safety) should logically override the strict literal interpretation. Document this lack of synthesis before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Bare minimum execution.") + "\n  <fatal_flaw_context>Target intellectual laziness and lack of thoroughness.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Identify where the AI provides a single-sentence conclusion when a complex, multi-step logical derivation was inherently required by the gravity of the topic. Explain this bare-minimum effort before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Absence of counter-factual thinking.") + "\n  <fatal_flaw_context>Target the complete omission of rebuttals or falsification attempts.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Locate the section where the AI concludes its analysis without ever proposing a 'devil's advocate' position, acknowledging a valid counter-argument, or attempting to falsify its own premise. Extract the exact_quote.",
                        "inverse": True
                    }
                ],
                4: [
                    {
                        "desc": get_epistemic_anchor("Active application of structured steering models."),
                        "rule": "CRITICAL DIRECTIVE: Locate the exact section where the AI explicitly maps its reasoning step-by-step against a known, structured directive or established policy framework. Document this alignment before extracting the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Explicit definition of roles and constraints."),
                        "rule": "CRITICAL DIRECTIVE: Identify where the AI explicitly states the boundaries of its current role, or acknowledges a specific negative constraint it must not cross, before executing the task. Extract the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Process-driven interaction logic."),
                        "rule": "CRITICAL DIRECTIVE: Find the exact sentence where the AI utilizes a clear 'If X, then Y' or 'Step 1, Step 2' systematic methodology that perfectly mirrors an established organizational process. Extract the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Proactive documentation of exceptions."),
                        "rule": "CRITICAL DIRECTIVE: Locate where the AI proactively identifies an edge case, exception, or limitation in its own proposed solution, explicitly noting how the standard framework applies to this anomaly. Detail this oversight before extracting the exact_quote.",
                        "inverse": False
                    }
                ],
                5: [
                    {
                        "desc": get_epistemic_anchor("Flawless synthesis of precedent."),
                        "rule": "CRITICAL DIRECTIVE: Identify the exact phrase where the AI not only applies an explicit rule but seamlessly synthesizes the *underlying intent* of multiple precedents into a novel, flawlessly compliant solution. Extract the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Irrefutable axiomatic compliance."),
                        "rule": "CRITICAL DIRECTIVE: Locate where the AI constructs a logical argument so tightly bound to established organizational axioms that it leaves zero room for misinterpretation or ambiguity. Document this precision before extracting the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Adversarial boundary testing."),
                        "rule": "CRITICAL DIRECTIVE: Find the exact instance where the AI explicitly tests its own proposed solution against a hypothetical worst-case scenario or extreme constraint to validate its robustness. Explain this self-challenge before extracting the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Explicit articulation of System 2 cognitive friction."),
                        "rule": "CRITICAL DIRECTIVE: Locate where the AI explicitly pauses to document the 'how' and 'why' of its decision-making process, making its internal logic and trade-off analysis completely transparent to the auditor. Extract the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Absolute anchoring to verifiable external precedent."),
                        "rule": "CRITICAL DIRECTIVE: Identify the exact sentence where the AI mathematically or theoretically anchors its final conclusion directly to an external, verifiable policy document, expert framework, or strict organizational law. Extract the exact_quote.",
                        "inverse": False
                    }
                ]
            }

            for scale in block.get("scales", []):
                score = scale.get("score")
                if score in refactored_data:
                    ref_list = refactored_data[score]
                    for idx, claim in enumerate(scale.get("claims", [])):
                        if idx < len(ref_list):
                            ref = ref_list[idx]
                            
                            # Build new ai_description
                            claim["ai_description"] = f"<system_directive>\n  {ref['desc']}\n</system_directive>"
                            
                            # Build new tda_assertions
                            claim["tda_assertions"] = [
                                {
                                    "tda_id": generate_tda_id(),
                                    "ai_rule_description": ref["rule"],
                                    "inverse_evidence": ref["inverse"],
                                    "aggregation_mode": "EXISTS" if ref["inverse"] else "ALL_MUST_COMPLY"
                                }
                            ]
            
            # Print success
            print(f"Refactored {block['id']} successfully.")
            break

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Saved seed_data.json.")

if __name__ == "__main__":
    refactor_matrix()
