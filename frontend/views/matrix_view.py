import streamlit as st
import pandas as pd
import requests
import json
import uuid

def render_matrix_view(api_client, backend_url):
    """
    Renders the No-Code Evaluation Matrix Builder.
    Refactored to avoid nested st.form issues.
    """
    st.header("⚖️ Audit Matrix Builder")
    st.markdown("Create and manage dynamic evaluation matrices (e.g., Cognitive BARS, Compliance Checks). These matrices can be attached to **Judge Agents** in any workflow.")
    
    # --- INIT STATE ---
    if "selected_matrix_id" not in st.session_state:
        st.session_state.selected_matrix_id = None

    # --- SIDEBAR: Navigation ---
    sb_tabs = st.sidebar.tabs(["Matrix Editor", "Ontology Manager"])
    
    # === TAB 2: ONTOLOGY MANAGER ===
    with sb_tabs[1]:
        st.subheader("Ontology Manager")
        
        # 1. Create New
        with st.expander("➕ Define New Dimension"):
            with st.form("new_dim_form"):
                new_d_id = st.text_input("ID (System Key)", placeholder="e.g. 'security'").strip().lower()
                new_d_lbl = st.text_input("Label (Default Display)", placeholder="e.g. Security & Privacy")
                new_d_desc = st.text_area("Description")
                if st.form_submit_button("Create Dimension"):
                    if not new_d_id:
                        st.error("ID is required.")
                    else:
                        try:
                            payload = {
                                "id": new_d_id,
                                "label": new_d_lbl,
                                "description": new_d_desc,
                                "is_system": False
                            }
                            res = requests.post(f"{backend_url}/config/ontology/dimensions", json=payload)
                            if res.status_code == 200:
                                st.success(f"Created '{new_d_id}'")
                                st.rerun()
                            else:
                                st.error(f"Error: {res.text}")
                        except Exception as e:
                            st.error(f"Connection Error: {e}")

        st.markdown("---")
        st.caption("Existing Dimensions")
        
        # 2. List & Delete
        try:
            full_onto = requests.get(f"{backend_url}/config/ontology/dimensions/full").json()
            for d in full_onto:
                with st.container():
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"**{d['label']}** (`{d['id']}`)")
                    if d.get('description'):
                        c1.caption(d['description'])
                    
                    if c2.button("🗑️", key=f"del_dim_{d['id']}", help=f"Delete {d['id']}"):
                        try:
                            res = requests.delete(f"{backend_url}/config/ontology/dimensions/{d['id']}")
                            if res.status_code == 200:
                                st.success(f"Deleted {d['id']}")
                                st.rerun()
                            else:
                                st.error(f"Cannot Delete: {res.json().get('detail')}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    st.divider()
        except Exception as e:
            st.error(f"Failed to load ontology: {e}")


    # === TAB 1: MATRIX EDITOR ===
    with sb_tabs[0]:
        st.subheader("Matrix Selection")
        
        def reset_selection():
            st.session_state.selected_matrix_id = None
            
        c_mode = st.radio("Mode", ["Edit Existing", "Create New"], key="mode_select", on_change=reset_selection)

        existing_matrices = []
        try:
            # Fetch 'components' where type='evaluation_matrix'
            resp = requests.get(f"{backend_url}/config/components")
            if resp.status_code == 200:
                all_comps = resp.json()
                existing_matrices = [c for c in all_comps if c.get('type') == 'evaluation_matrix']
        except:
             st.error("Failed to fetch existing matrices.")

        if c_mode == "Edit Existing":
            if existing_matrices:
                opts = {m['id']: f"{m.get('name', m['id'])} ({m['id']})" for m in existing_matrices}
                keys = list(opts.keys())
                
                # Determine Index
                curr = st.session_state.selected_matrix_id
                idx = 0
                if curr in keys:
                    idx = keys.index(curr)
                
                def on_change_sel():
                    st.session_state.selected_matrix_id = st.session_state.matrix_selector_sb
                    if "editor_criteria" in st.session_state: del st.session_state.editor_criteria

                st.selectbox(
                    "Select Matrix", 
                    keys, 
                    format_func=lambda x: opts[x], 
                    key="matrix_selector_sb", 
                    index=idx,
                    on_change=on_change_sel
                )
                
                # Force init if needed
                if st.session_state.selected_matrix_id not in keys:
                     st.session_state.selected_matrix_id = keys[0]
                     st.rerun()
            else:
                st.info("No existing matrices found. Create a new one!")
                c_mode = "Create New"

        if c_mode == "Create New":
            if st.session_state.selected_matrix_id != "NEW":
                st.session_state.selected_matrix_id = "NEW"
                if "editor_criteria" in st.session_state: del st.session_state.editor_criteria
            st.info("Creating a new blank matrix.")

    # --- 1. Fetch and List ---
    # This section is now driven by the sidebar selection
    try:
        all_components = api_client.get_components()
        matrices = [c for c in all_components if c.get('type') == 'evaluation_matrix']
    except Exception as e:
        st.error(f"Failed to load components: {e}")
        return

    # --- MAIN EDITOR AREA ---
    target_id = st.session_state.selected_matrix_id
    
    if not target_id:
        st.info("👈 Select a matrix from the sidebar library or create a new one.")
        return

    st.subheader("Matrix Editor")
    
    # Determine Data
    if target_id == "NEW":
        base_data = {
            "id": f"matrix_new_{uuid.uuid4().hex[:8]}",
            "name": "New Audit Matrix",
            "description": "",
            "type": "evaluation_matrix",
            "content": {
                "name": "New Matrix",
                "description": "",
                "role_description": "Toimit Järjestelmän Tuomarina.",
                "scale": {"min": 1, "max": 4},
                "criteria": []
            }
        }
        is_new = True
    else:
        base_data = next((m for m in matrices if m['id'] == target_id), None)
        is_new = False
        
    if not base_data:
        st.error("Matrix not found.")
        return

    # --- INITIALIZE STATE ---
    # We need a robust way to handle edits without losing focus
    if "editor_criteria" not in st.session_state or st.session_state.get("editor_matrix_id") != target_id:
        content = base_data.get('content', {})
        if isinstance(content, str):
            try: content = json.loads(content)
            except: content = {}
        
        st.session_state.editor_matrix_id = target_id
        st.session_state.editor_criteria = content.get('criteria', [])
        # Also helper fields
        st.session_state.ed_id = base_data.get('id')
        st.session_state.ed_name = base_data.get('name')
        st.session_state.ed_desc = base_data.get('description')
        st.session_state.ed_role = content.get('role_description', '')
        st.session_state.ed_min = content.get('scale', {}).get('min', 1)
        st.session_state.ed_max = content.get('scale', {}).get('max', 4)

    # --- METADATA ---
    c1, c2 = st.columns(2)
    
    def update_meta(key):
        # No-op needed, values are in st.session_state[key]
        pass

    c1.text_input("Component ID (Unique)", key="ed_id", disabled=not is_new)
    c2.text_input("Matrix Name", key="ed_name")
    st.text_area("Description", key="ed_desc")
    
    st.divider()
    st.markdown("#### Evaluation Logic")
    
    gc1, gc2 = st.columns(2)
    gc1.text_input("Role Persona", key="ed_role")
    
    gc2.number_input("Min Score", 0, 10, key="ed_min")
    gc2.number_input("Max Score", 1, 100, key="ed_max")
    
    # --- CRITERIA BUILDER ---
    st.markdown("#### Criteria Dimensions")
    
    # Helper callbacks
    def update_crit_field(idx, field):
        val = st.session_state[f"c_{field}_{idx}"]
        st.session_state.editor_criteria[idx][field] = val
        
    def update_anchor_field(idx, level):
            val = st.session_state[f"c_a{level}_{idx}"]
            if 'anchors' not in st.session_state.editor_criteria[idx]:
                st.session_state.editor_criteria[idx]['anchors'] = {}
            st.session_state.editor_criteria[idx]['anchors'][str(level)] = val

    # Fetch Ontology from API (Dynamic)
    KNOWN_DIMENSIONS_MAP = {}
    try:
        resp = requests.get(f"{backend_url}/config/ontology/dimensions/full")
        if resp.status_code == 200:
            data = resp.json()
            # Sort by is_system first, then id
            data.sort(key=lambda x: (not x.get('is_system', False), x['id']))
            KNOWN_DIMENSIONS_MAP = {d['id']: d for d in data}
        else:
            st.error(f"Fatal Error: Could not load ontology from Backend. Status: {resp.status_code}")
            st.stop()
    except Exception as e:
            st.error(f"Fatal Error: Could not connect to backend API. {e}")
            st.stop()

    criteria_list = st.session_state.editor_criteria
    
    for i, crit in enumerate(criteria_list):
        label = crit.get('label') or f"Dimension {i+1}"
        with st.expander(f"Dimension {i+1}: {label}", expanded=False):
            cc1, cc2 = st.columns([1, 2])
            
            # ID Selection with Ontology Enforcement
            curr_id = crit.get('id', '')
            
            options = list(KNOWN_DIMENSIONS_MAP.keys()) + ["Custom..."]
            
            # Determine initial index for selectbox
            sel_index = len(options) - 1 # Default Custom
            if curr_id in KNOWN_DIMENSIONS_MAP:
                sel_index = options.index(curr_id)
            
            def update_id_from_select(idx):
                val = st.session_state[f"c_id_sel_{idx}"]
                if val != "Custom...":
                    st.session_state.editor_criteria[idx]['id'] = val
                    # Auto-fill Label/Instruction if empty and we picked a system dimension
                    dim_data = KNOWN_DIMENSIONS_MAP.get(val)
                    if dim_data:
                         if not st.session_state.editor_criteria[idx].get('label'):
                             st.session_state.editor_criteria[idx]['label'] = dim_data['label']
                         # We could autofill instruction too if we had a default one in DB, but descriptions are short.
                # If Custom, we wait for text input update
            
            # Format Function for Rich Display
            def format_dim_option(opt):
                if opt == "Custom...": return opt
                obj = KNOWN_DIMENSIONS_MAP.get(opt)
                if not obj: return opt
                # Return "Label (Description snippet)"
                desc = obj.get('description', '')
                # Ensure it's not too long
                if len(desc) > 40: desc = desc[:37] + "..."
                return f"{obj['label']} ({desc})"
            
            sel_val = cc1.selectbox(
                "Category (System ID)", 
                options, 
                index=sel_index, 
                key=f"c_id_sel_{i}", 
                on_change=update_id_from_select, 
                format_func=format_dim_option,
                args=(i,), 
                help="Determines where this score appears in comparisons and analytics (e.g. 'agency' scores are grouped together)."
            )
            
            if sel_val == "Custom...":
                def update_id_custom(idx):
                    val = st.session_state[f"c_id_custom_{idx}"]
                    st.session_state.editor_criteria[idx]['id'] = val
                    
                cc1.text_input("Custom ID", value=curr_id if curr_id not in KNOWN_DIMENSIONS_MAP else "", key=f"c_id_custom_{i}", on_change=update_id_custom, args=(i,), label_visibility="collapsed", placeholder="Enter ID...")

            # Contextual Help for ID
            help_map = {
                "analyysi": "Strategia & Ymmärrys (Driver)",
                "agency": "Toimijuus & Hallinta",
                "arviointi": "Validointi & Tekniikka (Engineering)",
                "engineering": "Tekninen Toteutus",
                "synteesi": "Luovuus & Kritiikki (Falsification)",
                "falsification": "Virheiden etsintä & Iterointi"
            }
            
            final_id = st.session_state.editor_criteria[i].get('id', '')
            if final_id in help_map:
                cc1.caption(f"ℹ️ {help_map[final_id]}")

            cc2.text_input("Display Name", value=crit.get('label', ''), key=f"c_label_{i}", on_change=update_crit_field, args=(i, 'label'))
            st.text_area(f"Instruction ##{i}", value=crit.get('instruction', ''), key=f"c_instruction_{i}", height=70, on_change=update_crit_field, args=(i, 'instruction'))
            
            st.markdown("**Proficiency Levels (Anchors)**")
            # Pills removed by user request
            
            ac1, ac2 = st.columns(2)
            ac3, ac4 = st.columns(2)
            
            anchors = crit.get('anchors', {})
            
            ac1.text_area(f"Level 1 ##{i}", value=anchors.get('1', ''), key=f"c_a1_{i}", height=100, on_change=update_anchor_field, args=(i, 1))
            ac2.text_area(f"Level 2 ##{i}", value=anchors.get('2', ''), key=f"c_a2_{i}", height=100, on_change=update_anchor_field, args=(i, 2))
            ac3.text_area(f"Level 3 ##{i}", value=anchors.get('3', ''), key=f"c_a3_{i}", height=100, on_change=update_anchor_field, args=(i, 3))
            ac4.text_area(f"Level 4 ##{i}", value=anchors.get('4', ''), key=f"c_a4_{i}", height=100, on_change=update_anchor_field, args=(i, 4))
            
            if st.button(f"🗑️ Remove Dimension {i+1}", key=f"del_c_{i}"):
                st.session_state.editor_criteria.pop(i)
                st.rerun()

    if st.button("➕ Add Dimension"):
        st.session_state.editor_criteria.append({
            "id": f"dim_{len(criteria_list)+1}",
            "label": "New Dimension",
            "instruction": "",
            "anchors": {"1": "", "2": "", "3": "", "4": ""}
        })
        st.rerun()
        
    st.divider()
    
    st.divider()
    
    # SAVE ACTION
    if st.button("💾 Save Matrix", type="primary"):
        try:
            # Force updates from metadata fields (they are in state but lets be sure)
            final_id = st.session_state.ed_id
            final_name = st.session_state.ed_name
            final_desc = st.session_state.ed_desc
            
            final_content = {
                "name": final_name,
                "description": final_desc,
                "role_description": st.session_state.ed_role,
                "scale": {"min": st.session_state.ed_min, "max": st.session_state.ed_max},
                "criteria": st.session_state.editor_criteria
            }
            
            payload = {
                "id": final_id,
                "name": final_name,
                "description": final_desc,
                "type": "evaluation_matrix",
                "content": final_content
            }
            
            if is_new:
                requests.post(f"{backend_url}/config/components", json=payload).raise_for_status()
                st.success("Matrix Created!")
                st.session_state.selected_matrix_id = final_id
                st.session_state.editor_matrix_id = final_id # Sync
                st.rerun()
            else:
                requests.put(f"{backend_url}/config/components/{final_id}", json=payload).raise_for_status()
                st.success("Matrix Updated!")
                st.session_state.editor_matrix_id = final_id # Sync
                st.rerun()
                
        except Exception as e:
            st.error(f"Error saving matrix: {e}")

    # Delete Button (Outside form)
    if not is_new: # Render delete button directly after save logic
        if st.button("🗑️ Delete This Matrix", key="del_mat_btn"):
            try:
                requests.delete(f"{backend_url}/config/components/{st.session_state.ed_id}").raise_for_status()
                st.success("Deleted!")
                st.session_state.selected_matrix_id = None
                if "editor_criteria" in st.session_state:
                        del st.session_state.editor_criteria
                st.rerun()
            except Exception as e:
                st.error(f"Delete failed: {e}")
