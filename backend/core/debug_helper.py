def debug_dump_state(state, step_name):
    try:
        dump_path = "debug_state_trace.txt"
        with open(dump_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- AFTER STEP: {step_name} ---\n")
            # Minimal dump of guard for check
            if state.step_guard:
                f.write(f"Guard: {state.step_guard.model_dump_json(exclude_none=True)}\n")
            else:
                f.write("Guard: None\n")

            if state.step_reporter:
                f.write(f"Reporter: {state.step_reporter.model_dump_json(exclude_none=True)}\n")
            else:
                f.write("Reporter: None\n")

    except Exception:
        pass
