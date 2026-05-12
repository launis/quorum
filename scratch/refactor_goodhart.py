import json
import uuid

def generate_tda_id():
    return f"tda_{uuid.uuid4().hex[:16]}"

def get_epistemic_anchor(level_desc):
    return f"<epistemic_anchor>Strathern, M. (1997). \"When a measure becomes a target, it ceases to be a good measure\" (Goodhart's Law). {level_desc}</epistemic_anchor>"

def refactor_matrix():
    file_path = "c:/src/quorum/backend_v2/seed/seed_data.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for block in data.get("prompt_blocks", []):
        if block.get("id") == "blk_53f32679aa514fcb":
            # Update the global matrix ai_description
            block["ai_description"] = (
                "<system_directive>\n"
                "  <epistemic_anchor>Strathern, M. (1997). Goodhart's Law: \"When a measure becomes a target, it ceases to be a good measure\". Evaluating performative vs. authentic cognitive driving.</epistemic_anchor>\n"
                "</system_directive>\n"
                "ROLE: ANTAGONISTIC PROSECUTOR (ZERO-TRUST). TASK: Evaluate the user's interaction dynamic (Driver vs. Passenger) and susceptibility to performative optimization. "
                "NULL HYPOTHESIS: Assume the user is a passive passenger, blindly accepting AI outputs, sycophantic buzzwords, or superficial metrics without understanding the true objective. "
                "You must actively search for metric fixation, lack of critical challenge, and blind acceptance of hallucinated structures. "
                "MANDATORY DIRECTIVE: Default all boolean claim evaluations to FALSE. You must never infer, guess, or synthesize compliance. A claim can only be evaluated as TRUE if you can extract direct, undeniable semantic proof from the text."
            )

            # Define refactored data per score and claim index
            refactored_data = {
                1: [
                    {
                        "desc": get_epistemic_anchor("Absolute passive delegation.") + "\n  <fatal_flaw_context>Target passive delegation where the user blindly outsources cognition without constraints.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Locate a prompt where the user completely delegates the logical structure to the AI using passive commands like 'write an essay about' or 'summarize this', without providing any analytical constraints. Explain the user's abdication of control before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Sycophantic acceptance.") + "\n  <fatal_flaw_context>Target unquestioning acceptance of the AI's first output.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Identify where the user accepts an AI output immediately without asking a single follow-up question, or explicitly says 'looks good' without adding new requirements. Document this blind acceptance before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Performative metric fixation.") + "\n  <fatal_flaw_context>Target the acceptance of performative buzzwords masking a lack of substance.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Find an instance where the user accepts or encourages an AI response that is heavily laden with performative corporate buzzwords (e.g., 'synergistic', 'innovative') but lacks concrete data. Detail the performativity before extracting the exact_quote.",
                        "inverse": True
                    }
                ],
                2: [
                    {
                        "desc": get_epistemic_anchor("Superficial optimization.") + "\n  <fatal_flaw_context>Target aesthetic or length tweaks that ignore structural logic.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Locate a prompt where the user requests only stylistic or length modifications (e.g., 'make it shorter', 'fix the tone') without challenging the underlying assumptions or logic. Explain the superficiality before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Unchallenged structural boundaries.") + "\n  <fatal_flaw_context>Target implicit validation of flawed AI reasoning.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Find a prompt where the user explicitly validates the AI's existing structure and only asks for more details on a specific sub-point, leaving the core assumptions unchallenged. Document this failure to challenge before extracting the exact_quote.",
                        "inverse": True
                    }
                ],
                3: [
                    {
                        "desc": get_epistemic_anchor("Reactive alignment.") + "\n  <fatal_flaw_context>Target feedback limited to minor corrections without strategic redirection.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Identify where the user provides feedback by merely correcting minor factual errors or typos, rather than actively redirecting the strategic focus or analytical depth. Detail the reactive nature of the prompt before extracting the exact_quote.",
                        "inverse": True
                    },
                    {
                        "desc": get_epistemic_anchor("Framework capitulation.") + "\n  <fatal_flaw_context>Target the blind adoption of AI-proposed frameworks.</fatal_flaw_context>",
                        "rule": "CRITICAL DIRECTIVE: Locate an instance where the user asks the AI to expand on its own proposed framework without introducing any external theories or constraints of their own. Explain this capitulation before extracting the exact_quote.",
                        "inverse": True
                    }
                ],
                4: [
                    {
                        "desc": get_epistemic_anchor("Demand for empirical grounding."),
                        "rule": "CRITICAL DIRECTIVE: Identify the exact sentence where the user explicitly demands empirical data, real-world examples, or logical justification for an AI's claim. Document the user's demand for grounding before extracting the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Epistemological humility via constraint."),
                        "rule": "CRITICAL DIRECTIVE: Locate where the user actively instructs the AI to highlight edge cases, limitations, or uncertainties in its reasoning. Explain how the user enforces humility before extracting the exact_quote.",
                        "inverse": False
                    }
                ],
                5: [
                    {
                        "desc": get_epistemic_anchor("Antagonistic evaluation."),
                        "rule": "CRITICAL DIRECTIVE: Find the exact prompt where the user acts as an antagonistic evaluator, explicitly pointing out a logical flaw, contradiction, or hallucination in the AI's previous output. Detail the user's falsification logic before extracting the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Core assumption challenge."),
                        "rule": "CRITICAL DIRECTIVE: Locate where the user fundamentally challenges the AI's core assumptions by explicitly introducing a new, competing variable or opposing viewpoint. Explain this structural challenge before extracting the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Structural demolition."),
                        "rule": "CRITICAL DIRECTIVE: Identify the prompt where the user demands a complete structural tear-down and rebuild of the AI's response based on a specific failure mode they identified. Document the rebuild demand before extracting the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("Absolute process control."),
                        "rule": "CRITICAL DIRECTIVE: Find the explicit instruction where the user defines strict, non-negotiable constraints or formatting rules that the AI must follow to prevent performative deviations. Extract the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("System 2 articulation."),
                        "rule": "CRITICAL DIRECTIVE: Locate where the user explicitly articulates their own reasoning or rationale for *why* they are redirecting the AI's focus (demonstrating human System 2 thought). Detail the user's cognitive friction before extracting the exact_quote.",
                        "inverse": False
                    },
                    {
                        "desc": get_epistemic_anchor("External source anchoring."),
                        "rule": "CRITICAL DIRECTIVE: Identify the exact sentence where the user introduces a specific external framework, author, or scientific theory to mathematically or theoretically constrain the AI's generation. Extract the exact_quote.",
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
