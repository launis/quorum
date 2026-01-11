"""Builder Help Component."""
import streamlit as st


def show_help_sidebar():
    """Renders the 'Workflow Builder Guide' in the sidebar."""
    with st.sidebar:
        with st.expander("📘 Workflow Builder Guide", expanded=False):
            st.markdown("""
            ### 🛠️ General Usage

            **1. Dashboard (The List)**
            * **Create New**: Start by copying a "Seed Workflow" (e.g., *Courtroom 2.0*).
              This ensures you have a valid foundation.
            * **Active vs Draft**: Only active workflows appear in the runner selection.
              Keep experiments in Draft if possible (naming convention).

            **2. The Editor (Visual Chain)**
            * **Selection**: Click any step card to view its details in the **Properties Panel** (Right).
            * **Reordering**: Use the **Move Up ⬆️** and **Move Down ⬇️** buttons to change execution order.
            * **Deleting**: The 🗑️ icon removes a step from this workflow *only*.
              It does not delete the step definition from the database.

            **3. Customizing Steps (Properties)**
            * **Shared Steps**: Steps like `step_logician` are shared across workflows.
            * **Forking**: To edit a shared step (e.g., change its prompts), click **✨ Customize (Fork Step)**.
              This creates a unique copy (e.g., `step_logician_custom_123`) just for this workflow. Safe to edit!
            * **Prompt Editor**: Once forked, you can add/remove specific prompt Instructions
              (e.g., `MANDATE_1`) to change the Agent's behavior.

            ---

            ### 🚀 Prompt Fusion (Optimization)

            Merge multiple "Narrow Agents" into a single "Panel Agent" call to save time and tokens.

            1. Create a dedicated workflow (e.g., "Courtroom Fused").
            2. Select the consecutive steps you want to merge (e.g., Steps 5-9: Logician through Overseer).
            3. In the Properties panel, under **Prompt Fusion**, select these steps.
            4. Click **🔥 Compile Fused Prompt**.
            5. The Builder replaces them with a single `step_panel`.
            **Tip:** Ensure you assign a capable model (Gemini Pro/Ultra or GPT-4)
            to `step_panel` as the task complexity increases.

            ---

            ### ✅ Verification & Safety

            **"How do I know I didn't break it?"**

            1. **Never Edit Master**: Always work on a copy ("Courtroom Test A").
            2. **Incremental Changes**: Change one thing (e.g., prompt or fusion) at a time.
            3. **A/B Testing**:
               - Run "Courtroom 2.0" (Baseline)
               - Run "Courtroom Test A" (Modified)
               - Compare the final `XAI Report` and `Score` in the History tab.
            4. **Data Integrity**: The system automatically validates data flow.
               If you remove a step that produces critical data (e.g., `step_analyst` produces Evidence),
               subsequent steps (e.g., `step_judge`) will warn or fail.
            """)
