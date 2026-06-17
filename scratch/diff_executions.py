import glob
import json
import math
import os
import sys
from typing import Any


def get_all_evals(path: str) -> dict[str, dict[str, object]]:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    all_evals: dict[str, dict[str, object]] = {}
    for step in data:
        if 'content' in step and isinstance(step['content'], dict):
            evals = step['content'].get('evaluations')
            if isinstance(evals, list):
                for e in evals:
                    all_evals[e['atom_id']] = e
    return all_evals

def calculate_entropy(states: list[str]) -> float:
    """Laskee Shannonin entropian (base 2) annetuille tiloille."""
    if not states:
        return 0.0
    counts: dict[str, int] = {}
    for s in states:
        counts[s] = counts.get(s, 0) + 1
    total = len(states)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def calculate_pairwise_consistency(states: list[str]) -> float:
    """Laskee kuinka suuri osa parivertailuista on yhtäpitäviä."""
    M = len(states)
    if M < 2:
        return 1.0
    counts: dict[str, int] = {}
    for s in states:
        counts[s] = counts.get(s, 0) + 1
    agreed_pairs = sum(c * (c - 1) / 2 for c in counts.values())
    total_pairs = M * (M - 1) / 2
    return agreed_pairs / total_pairs

def calculate_cohens_kappa(atom_states_list: list[list[str]], categories: list[str]) -> float:
    """Laskee Cohenin kapan tasan kahdelle ajolle (M = 2).
    atom_states_list: lista listoista, joissa jokaisessa on tasan 2 tilaa.
    categories: lista mahdollisista tiloista (esim. ['true', 'false']).
    """
    N = len(atom_states_list)
    if N == 0:
        return 0.0
    if len(atom_states_list[0]) != 2:
        raise ValueError("Cohenin kappa vaatii tasan kaksi arvioijaa (ajoa).")

    cat_to_idx = {cat: idx for idx, cat in enumerate(categories)}
    num_classes = len(categories)

    confusion_matrix = [[0] * num_classes for _ in range(num_classes)]
    for states in atom_states_list:
        idx1 = cat_to_idx.get(states[0])
        idx2 = cat_to_idx.get(states[1])
        if idx1 is not None and idx2 is not None:
            confusion_matrix[idx1][idx2] += 1

    observed_agreement = sum(confusion_matrix[i][i] for i in range(num_classes)) / N

    row_sums = [sum(confusion_matrix[i][j] for j in range(num_classes)) for i in range(num_classes)]
    col_sums = [sum(confusion_matrix[i][j] for i in range(num_classes)) for j in range(num_classes)]

    expected_agreement = sum((row_sums[i] / N) * (col_sums[i] / N) for i in range(num_classes))

    if expected_agreement >= 1.0:
        return 1.0

    kappa = (observed_agreement - expected_agreement) / (1.0 - expected_agreement)
    return kappa

def calculate_fleiss_kappa(atom_states_list: list[list[str]], categories: list[str]) -> float:
    """Laskee Fleissin kapan annetuille syötteille (atomit) ja niiden tiloille eri ajoissa.
    atom_states_list: list of lists, missä jokainen sisempi lista sisältää atomin tilat eri ajoissa.
    categories: lista kaikista mahdollisista kategorioista/tiloista (esim. ['true', 'false']).
    """
    N = len(atom_states_list)
    if N == 0:
        return 0.0
    M = len(atom_states_list[0])
    if M < 2:
        return 1.0

    cat_to_idx = {cat: idx for idx, cat in enumerate(categories)}
    num_classes = len(categories)

    count_matrix = [[0] * num_classes for _ in range(N)]
    for i, states in enumerate(atom_states_list):
        for s in states:
            if s in cat_to_idx:
                count_matrix[i][cat_to_idx[s]] += 1

    # 1. Havaittu yhtäpitävyys per syöte (P_i)
    P_i = []
    for i in range(N):
        sum_sq = sum(count_matrix[i][c] ** 2 for c in range(num_classes))
        P_i.append((sum_sq - M) / (M * (M - 1)))
    P_mean = sum(P_i) / N

    # 2. Odotettu sattumanvarainen yhtäpitävyys (p_j)
    p_j = [0.0] * num_classes
    for j in range(num_classes):
        col_sum = sum(count_matrix[i][j] for i in range(N))
        p_j[j] = col_sum / (N * M)
    P_e = sum(p ** 2 for p in p_j)

    if P_e >= 1.0:
        return 1.0

    kappa = (P_mean - P_e) / (1.0 - P_e)
    return kappa

def get_state(e: dict[str, object]) -> str:
    if 'decision' in e:
        return str(e['decision']).lower()
    if 'mapped_state' in e:
        return str(e['mapped_state']).lower()
    if 'exact_quote' in e or 'exact_quotes' in e:
        eq = e.get('exact_quote', e.get('exact_quotes'))
        if eq is None or eq == []:
            return "false"
        eq_lower = str(eq).strip().lower()
        blacklist = {
            "null", "none", "n/a", "false", "", "ei löydy", "not found", "-", "ei mainittu",
            "none detected", "[]", "{}", "ei sovelleta", "ei lainausta", "no quote", "ei ole"
        }
        return "true" if eq_lower not in blacklist else "false"
    return "unknown"

def get_trace(e: dict[str, object]) -> str:
    if 'context_scan_trace' in e:
        return str(e['context_scan_trace'])
    if 'semantic_reasoning' in e:
        return str(e['semantic_reasoning'])
    if 'reasoning_trace' in e:
        return str(e['reasoning_trace'])
    if 'mechanical_trace' in e:
        return str(e['mechanical_trace'])
    return ""

def uses_contextual_override(e: dict[str, object]) -> bool:
    if e.get('contextual_override') is True:
        return True
    eq = e.get('exact_quote')
    if isinstance(eq, str) and '[INFERRED]' in eq:
        return True
    return False

if __name__ == '__main__':
    # Automaattinen viimeisimpien ajojen haku
    exe_dirs = glob.glob('data/files/executions/exe_*')
    exe_dirs.sort(key=os.path.getmtime, reverse=True)

    loaded_runs = []
    loaded_paths = []
    evals_list = []

    if len(sys.argv) > 1:
        for exe_id in sys.argv[1:]:
            if os.path.isdir(exe_id):
                path = os.path.join(exe_id, 'execution_trace.json')
                name = os.path.basename(exe_id)
            else:
                path = f'data/files/executions/{exe_id}/execution_trace.json'
                name = exe_id

            if os.path.exists(path):
                evals_list.append(get_all_evals(path))
                loaded_runs.append(name)
                loaded_paths.append(path)
            else:
                print(f"Polkua ei löydy: {path}")
    else:
        for d in exe_dirs[:3]:
            path = os.path.join(d, 'execution_trace.json')
            if os.path.exists(path):
                evals_list.append(get_all_evals(path))
                loaded_runs.append(os.path.basename(d))
                loaded_paths.append(path)

    if len(evals_list) < 2:
        print("Virhe: Vertailuun tarvitaan vähintään kaksi ajoa.")
        if len(exe_dirs) < 2:
            print("Luo uusia ajoja suorittamalla arviointeja ensin.")
        sys.exit(1)

    print(f"Vertailuun ladattiin {len(evals_list)} ajoa:")
    for idx, name in enumerate(loaded_runs):
        print(f"  Run {idx + 1}: {name}")

    # Etsi yhteiset atomit, jotka löytyvät kaikista ladatuista ajoista
    common_atoms = set(evals_list[0].keys())
    for evals in evals_list[1:]:
        common_atoms = common_atoms.intersection(set(evals.keys()))

    if not common_atoms:
        print("Virhe: Ladatuilla ajoilla ei ole yhtään yhteistä atomia.")
        sys.exit(1)

    # Etsi säännön kuvaus tietokannasta
    with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
        seed = json.load(f)
    atom_rules = {}
    atom_to_block = {}
    for block in seed.get('prompt_blocks', []):
        bid = block.get('id')
        for s_idx, scale in enumerate(block.get('scales', [])):
            for c_idx, claim in enumerate(scale.get('claims', [])):
                for tda in claim.get('tda_assertions', []):
                    atom_rules[tda.get('tda_id')] = tda.get('ai_rule_description')
                    if bid:
                        atom_to_block[tda.get('tda_id')] = bid

    # Lasketaan metriikat jokaiselle atomille
    atom_states = {}
    atom_entropies = {}
    atom_consistencies = {}
    all_atom_states = []
    unique_categories = set()

    valid_common_atoms = set()
    for atom in common_atoms:
        traces = [get_trace(evals[atom]) for evals in evals_list]
        if any("[SYSTEM ERROR" in t or "Chunk Processing Failed" in t for t in traces):
            continue
        valid_common_atoms.add(atom)

    common_atoms = valid_common_atoms

    for atom in common_atoms:
        states = [get_state(evals[atom]) for evals in evals_list]
        for s in states:
            unique_categories.add(s)

        entropy = calculate_entropy(states)
        consistency = calculate_pairwise_consistency(states)

        atom_states[atom] = states
        atom_entropies[atom] = entropy
        atom_consistencies[atom] = consistency
        all_atom_states.append(states)

    # Globaalit metriikat
    categories_list = sorted(list(unique_categories))
    global_kappa = calculate_fleiss_kappa(all_atom_states, categories_list)
    global_consistency = sum(atom_consistencies.values()) / len(common_atoms)
    global_entropy = sum(atom_entropies.values()) / len(common_atoms)

    cohen_kappa = None
    if len(evals_list) == 2:
        try:
            cohen_kappa = calculate_cohens_kappa(all_atom_states, categories_list)
        except Exception:
            pass

    # Etsi ne, joissa on vähintään jonkin verran vaihtelua (entropia > 0)
    mismatching_atoms = [atom for atom, entropy in atom_entropies.items() if entropy > 0]
    mismatching_atoms.sort(key=lambda a: atom_entropies[a], reverse=True)

    # Lasketaan 2-way siirtymätilastot kahden ensimmäisen (tuoreimman) ajon välillä yhteensopivuuden vuoksi
    summary_2way = {"PASSED->FAILED": 0, "FAILED->PASSED": 0, "Other": 0}
    evals_1 = evals_list[0]
    evals_2 = evals_list[1]
    passed_states = ['true', 'passed', '1']
    failed_states = ['false', 'failed', '0']

    for atom in common_atoms:
        s1, s2 = get_state(evals_1[atom]), get_state(evals_2[atom])
        if s1 != s2:
            if s1 in passed_states and s2 in failed_states:
                summary_2way["PASSED->FAILED"] += 1
            elif s1 in failed_states and s2 in passed_states:
                summary_2way["FAILED->PASSED"] += 1
            else:
                summary_2way["Other"] += 1

    contextual_override_mismatches = 0
    for atom in mismatching_atoms:
        used_override = False
        for evals in evals_list:
            if atom in evals and uses_contextual_override(evals[atom]):
                used_override = True
                break
        if used_override:
            contextual_override_mismatches += 1

    # Tallenna raportti luettavaan Markdown-muotoon
    os.makedirs('scratch', exist_ok=True)
    import datetime
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    report_path = f'scratch/diff_report_{timestamp_str}.md'

    # Hae Git-konteksti ja ympäristön tila (Epic / Git branch & commit)
    import subprocess
    git_info = "Ei saatavilla"
    try:
        git_branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
        git_commit = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%h - %s (%cd)'], text=True).strip()
        git_info = f"Branch: {git_branch} | Commit: {git_commit}"
    except Exception:
        pass

    # Hae tärkeät Enum-arvot ja järjestelmäkonfiguraatio
    sys_enums = "Ei saatavilla"
    try:
        import sys
        if '.' not in sys.path:
            sys.path.insert(0, '.')
        import backend_v2.models.enums as enums

        EvalRunCount = getattr(enums, 'EvaluationRunCount', None)
        ensemble_val = getattr(EvalRunCount, 'ENSEMBLE', None)
        standard_val = getattr(EvalRunCount, 'STANDARD', None)
        ensemble_v = ensemble_val.value if ensemble_val else 'N/A'
        standard_v = standard_val.value if standard_val else 'N/A'

        VerifResult = getattr(enums, 'VerificationResult', None)
        pass_val = getattr(VerifResult, 'VERIFIED', None)
        fail_val = getattr(VerifResult, 'DEBUNKED', None)
        pass_v = pass_val.value if pass_val else 'N/A'
        fail_v = fail_val.value if fail_val else 'N/A'

        sys_enums = (
            f"  - **EvaluationRunCount**: ENSEMBLE = {ensemble_v}, STANDARD = {standard_v}\n"
            f"  - **VerificationResult**: VERIFIED = {pass_v}, DEBUNKED = {fail_v}"
        )

        SysConcurrency = getattr(enums, 'SystemConcurrency', None)
        if SysConcurrency:
            # Otetaan koko SystemConcurrency-enum dynaamisesti (jotta L227-259 asiat tulostuvat)
            sc_items = []
            for k, v in SysConcurrency.__members__.items():
                sc_items.append(f"{k} = {v.value}")
            sys_enums += "\n  - **SystemConcurrency**:\n    - " + "\n    - ".join(sc_items)

    except Exception as e:
        sys_enums = f"Virhe Enumien luvussa: {e}"

    # Hae ajon tilanne (frozen context)
    frozen_context_info = "Ei saatavilla (frozen_context.json puuttuu)"
    if loaded_paths:
        frozen_path = os.path.join(os.path.dirname(loaded_paths[0]), 'frozen_context.json')
        if os.path.exists(frozen_path):
            try:
                with open(frozen_path, encoding='utf-8') as f:
                    frozen_data = json.load(f)
                hints = frozen_data.get('ui_hints_snapshot', {})
                if hints:
                    # Laske atomien tilat per matriisi KAIKILLE ajoille
                    block_stats_by_run = []
                    for evals in evals_list:
                        block_stats = {}
                        for atom_id, ev in evals.items():
                            bid = atom_to_block.get(atom_id)
                            if bid:
                                if bid not in block_stats:
                                    block_stats[bid] = {'PASS': 0, 'FAIL': 0, 'DLQ': 0, 'OTHER': 0}
                                s = get_state(ev).lower()
                                if s in ['true', 'pass']:
                                    block_stats[bid]['PASS'] += 1
                                elif s in ['false', 'fail']:
                                    block_stats[bid]['FAIL'] += 1
                                elif s == 'dlq':
                                    block_stats[bid]['DLQ'] += 1
                                else:
                                    block_stats[bid]['OTHER'] += 1
                        block_stats_by_run.append(block_stats)

                    frozen_lines = []
                    for block_id, conf in hints.items():
                        opts = conf.get('options', [])
                        label_fi = "Tuntematon"
                        if opts and 'label' in opts[0] and 'translations' in opts[0]['label']:
                            label_fi = opts[0]['label']['translations'].get('fi', opts[0]['label']['translations'].get('en', 'Tuntematon'))

                        run_strs = []
                        total_evaluated = 0
                        for r_idx, stats in enumerate(block_stats_by_run):
                            b_stat = stats.get(block_id, {})
                            pass_c = b_stat.get('PASS', 0)
                            fail_c = b_stat.get('FAIL', 0)
                            dlq_c = b_stat.get('DLQ', 0)

                            if pass_c > 0 or fail_c > 0 or dlq_c > 0:
                                total_evaluated += 1

                            dlq_str = f"|DLQ:{dlq_c}" if dlq_c > 0 else ""
                            run_strs.append(f"[R{r_idx+1}: {pass_c}P/{fail_c}F{dlq_str}]")

                        if total_evaluated == 0:
                            continue

                        stats_str = " ".join(run_strs)
                        frozen_lines.append(f"  - **{label_fi}** (`{block_id}`) - {stats_str}")
                    if frozen_lines:
                        frozen_context_info = "\n" + "\n".join(frozen_lines)
            except Exception as e:
                frozen_context_info = f"Virhe frozen_context.json lukemisessa: {e}"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)\n\n')

        f.write('## Ympäristö ja Konteksti (Execution State)\n')
        f.write(f'- **Git / Epic -tila:** {git_info}\n')
        f.write(f'- **Kriittiset järjestelmäarvot (Enums):**\n{sys_enums}\n')

        f.write('- **Vertailtavat ajot (R1, R2...):**\n')
        for idx, run_name in enumerate(loaded_runs):
            f.write(f'  - **R{idx + 1}:** `{run_name}`\n')

        f.write(f'- **Aktiiviset Säännöt ja Asetukset (Frozen Context):**{frozen_context_info}\n\n')

        f.write('## Ajojen Lähdetiedostot ja Syötteet\n')
        for idx, (run_name, exe_path) in enumerate(zip(loaded_runs, loaded_paths)):
            abs_path = os.path.abspath(exe_path).replace('\\', '/')
            f.write(f'- **Run {idx + 1}:** `{run_name}` (Lähde: [{exe_path}](file:///{abs_path}))\n')

            # Ladataan metatiedot alkuperäisestä tietokannasta (db_v2.json)
            try:
                with open('data/db_v2.json', encoding='utf-8') as db_file:
                    db_data = json.load(db_file)
                execs = db_data.get('executions', {})
                run_record: dict[str, Any] = next((v for v in execs.values() if v.get('id') == run_name), {})

                db_models = run_record.get('models_used', {})
                model_used = ", ".join(db_models.keys()) if db_models else "Ei tallennettu DB"

                duration_ms = run_record.get('duration_ms', 0)
                duration_str = f"{duration_ms / 1000 / 60:.1f} minuuttia" if duration_ms else "Keskeytyi / Tuntematon"

                meta = run_record.get('metadata', {})
                total_tokens = meta.get('total_tokens', 0)
                cost = run_record.get('cost_estimate', 0.0)
            except Exception as e:
                model_used, duration_str, total_tokens, cost = f"Error: {e}", "Error", 0, 0.0

            # Luetaan lokista virheet ja fallback-malli
            with open(exe_path, encoding='utf-8') as exe_f:
                raw_data = exe_f.read()
            error_count = raw_data.count("Chunk Processing Failed") + raw_data.count("SYSTEM ERROR")

            if model_used == "Ei tallennettu DB":
                if "gemini-2.5-pro" in raw_data: model_used = "gemini-2.5-pro (Jälki-loki)"
                elif "gemini-2.5-flash" in raw_data: model_used = "gemini-2.5-flash (Jälki-loki)"
                elif "gpt-4" in raw_data: model_used = "gpt-4 (Jälki-loki)"

            f.write(f'  - **Malli:** `{model_used}`\n')
            f.write(f'  - **Kesto:** `{duration_str}`\n')
            f.write(f'  - **Tokenit (DB):** `{total_tokens}`\n')
            f.write(f'  - **Kustannusarvio:** `${cost:.4f}`\n')
            f.write(f'  - **Tekniset virheet (Crash):** `{error_count}` kpl\n')

            run_dir = os.path.dirname(exe_path)
            inputs_dir = os.path.join(run_dir, 'inputs')
            if os.path.isdir(inputs_dir):
                inputs_files = os.listdir(inputs_dir)
                if inputs_files:
                    f.write('  - **Käytetyt syötetiedostot:**\n')
                    for in_file in inputs_files:
                        in_path = os.path.join(inputs_dir, in_file).replace('\\', '/')
                        abs_in = os.path.abspath(in_path).replace('\\', '/')
                        f.write(f'    - [{in_file}](file:///{abs_in})\n')
        f.write('\n')

        f.write('## Globaalit Metriikat\n')
        f.write(f'- **Arvioitujen ajojen määrä ($M$):** {len(evals_list)}\n')
        f.write(f'- **Yhteisten arvioitujen atomien määrä ($N$):** {len(common_atoms)}\n')
        f.write(f'- **Havaittujen luokkien kirjo:** {", ".join(categories_list)}\n')
        f.write(f'- **Parittainen konsistenssi (Self-Consistency):** {global_consistency * 100:.2f} %\n')
        f.write('  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*\n')
        f.write(f'- **Fleissin Kappa ($\\kappa_{{Fleiss}}$):** {global_kappa:.4f}\n')
        f.write('  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*\n')
        if cohen_kappa is not None:
            f.write(f'- **Cohenin Kappa ($\\kappa_{{Cohen}}$):** {cohen_kappa:.4f}\n')
            f.write('  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*\n')
        f.write(f'- **Keskimääräinen Shannonin Entropia:** {global_entropy:.4f}\n')
        f.write('  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*\n\n')

        f.write('## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)\n')
        f.write(f'- **Erimielisyyttä näiden välillä:** {len([a for a in common_atoms if get_state(evals_1[a]) != get_state(evals_2[a])])} kpl\n')
        f.write(f'- **Contextual Override -lähtöiset erimielisyydet koko setissä:** {contextual_override_mismatches} / {len(mismatching_atoms)}\n')
        f.write(f'- **PASSED -> FAILED:** {summary_2way["PASSED->FAILED"]}\n')
        f.write(f'- **FAILED -> PASSED:** {summary_2way["FAILED->PASSED"]}\n')
        f.write(f'- **Muut siirtymät:** {summary_2way["Other"]}\n\n')

        f.write('## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)\n')
        f.write('Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.\n\n')

        for atom in mismatching_atoms:
            entropy = atom_entropies[atom]
            consistency = atom_consistencies[atom]
            states = atom_states[atom]
            f.write(f'### Atom-ID: `{atom}` (Entropia: {entropy:.3f}, Konsistenssi: {consistency*100:.1f}%)\n')
            f.write(f'**Arviointisääntö:** {atom_rules.get(atom, "Unknown")}\n\n')

            f.write('**Havaitut tilat ajoittain:**\n')
            for run_idx, (run_name, state) in enumerate(zip(loaded_runs, states)):
                eval_item = evals_list[run_idx][atom]
                trace_content = get_trace(eval_item).replace('\n', ' ')
                override_tag = " **[CONTEXTUAL OVERRIDE]**" if uses_contextual_override(eval_item) else ""
                f.write(f'- **Run {run_idx+1} ({run_name}) - [{state.upper()}]{override_tag}:**\n')
                f.write(f'  > *{trace_content}*\n')
            f.write('\n---\n\n')

    print(f'Done! Evaluated {len(common_atoms)} common atoms.')
    print(f'Mismatching atoms: {len(mismatching_atoms)}')
    if len(common_atoms) > 0:
        print(f'Variance: {(len(mismatching_atoms)/len(common_atoms))*100:.1f} %')
    print(f'PASSED->FAILED: {summary_2way["PASSED->FAILED"]}, FAILED->PASSED: {summary_2way["FAILED->PASSED"]}, Other: {summary_2way["Other"]}')
    print(f'Global Self-Consistency: {global_consistency * 100:.2f}%')
    print(f'Fleiss Kappa: {global_kappa:.4f}')
    if cohen_kappa is not None:
        print(f'Cohen\'s Kappa: {cohen_kappa:.4f}')
    print(f'Average Entropy: {global_entropy:.4f}')
    print(f'Report written to: {report_path}')
