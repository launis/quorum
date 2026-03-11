import json

def analyze_theoretical_flaws_deep():
    with open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    pb_dict = {pb['id']: pb for pb in data.get('prompt_blocks', [])}
    
    print("=== DEEP AI AUDIT ROUND 2: ISOLATED CONCEPTS & THEORETICAL HOLES ===\n")
    
    # Check 1: Illusion of Validity (Kahneman)
    # Are we forcing the Judge to average out scores? Averaging categorical/cognitive biases is a known mathematical fallacy.
    judge_prompt = pb_dict.get('block_taskjudge', {}).get('description', {}).get('translations', {}).get('fi', '')
    if 'keskiarvo' in judge_prompt.lower() or 'average' in judge_prompt.lower():
        print("[FLAW DETECTED] Judge is instructed to calculate averages. Cognitive biases cannot be mathematically averaged.")
    else:
        print("[CLEAN] Judge is not explicitly forced into the mathematical fallacy of averaging cognitive states.")

    # Check 2: Synthesis vs Aggregation (Hegel vs Taylorism)
    # Does the XAI Reporter just list what others said (Aggregation), or does it explain WHY the Judge made the call (Synthesis)?
    xai_prompt = pb_dict.get('block_taskxai', {}).get('description', {}).get('translations', {}).get('fi', '')
    if 'yhteenveto' in xai_prompt.lower() or 'listaa' in xai_prompt.lower():
        print("[WARNING] XAI Reporter might be acting as a simple aggregator ('listaa', 'yhteenveto') rather than a true Explainer (Why).")
    else:
        print("[CLEAN] XAI Reporter seems focused on synthesis.")
        
    print("XAI Prompt snippet:", xai_prompt[:400])

    # Check 3: The Performativity Paradox 
    # If Performativity Detector flags "High Performativity" (Bad), does it invert the score so it looks "Good" to simple math aggregators?
    perf_prompt = pb_dict.get('block_taskperformativity', {}).get('description', {}).get('translations', {}).get('fi', '')
    if 'käänteinen' in perf_prompt.lower() or 'inverse' in perf_prompt.lower():
        print("[WARNING] Does Performativity score correctly map 5 = Good (Low performativity) and 1 = Bad (High performativity)?")
    else:
        print("[POTENTIAL FLAW] Performativity Detector might output 5 for 'Highly Performative' (which is actually a negative trait). Check numeric scale logic.")

    print("\nPerformativity Prompt snippet:", perf_prompt[:400])

if __name__ == "__main__":
    analyze_theoretical_flaws_deep()
