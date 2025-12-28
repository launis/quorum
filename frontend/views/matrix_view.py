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
    
    # --- 1. Fetch and List ---
    try:
        all_components = api_client.get_components()
        matrices = [c for c in all_components if c.get('type') == 'evaluation_matrix']
    except Exception as e:
        st.error(f"Failed to load components: {e}")
        return

    # Selection State
    if "selected_matrix_id" not in st.session_state:
        st.session_state.selected_matrix_id = None

    col_list, col_editor = st.columns([1, 2])
    
    # --- LEFT COLUMN: LIST ---
    with col_list:
        st.subheader("Library")
        
        if st.button("➕ Create New Matrix", use_container_width=True):
            st.session_state.selected_matrix_id = "NEW"
            # Clear editor state
            if "editor_criteria" in st.session_state:
                del st.session_state.editor_criteria
            st.rerun()
            
        st.divider()
        
        for m in matrices:
            label = f"**{m.get('name', m['id'])}**"
            if st.button(m.get('name', m['id']), key=f"btn_{m['id']}", use_container_width=True):
                st.session_state.selected_matrix_id = m['id']
                # Clear editor state so it reloads
                if "editor_criteria" in st.session_state:
                    del st.session_state.editor_criteria
                st.rerun()

    # --- RIGHT COLUMN: EDITOR ---
    with col_editor:
        target_id = st.session_state.selected_matrix_id
        
        if not target_id:
            st.info("👈 Select a matrix from the library or create a new one.")
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

        st.text_input("Component ID (Unique)", key="ed_id", disabled=not is_new)
        st.text_input("Matrix Name", key="ed_name")
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

        criteria_list = st.session_state.editor_criteria
        
        for i, crit in enumerate(criteria_list):
            label = crit.get('label') or f"Dimension {i+1}"
            with st.expander(f"Dimension {i+1}: {label}", expanded=False):
                cc1, cc2 = st.columns([1, 2])
                
                # We set Value (default) but rely on on_change to save to list
                cc1.text_input(f"ID ##{i}", value=crit.get('id', ''), key=f"c_id_{i}", on_change=update_crit_field, args=(i, 'id'))
                cc2.text_input(f"Label ##{i}", value=crit.get('label', ''), key=f"c_label_{i}", on_change=update_crit_field, args=(i, 'label'))
                st.text_area(f"Instruction ##{i}", value=crit.get('instruction', ''), key=f"c_instruction_{i}", height=70, on_change=update_crit_field, args=(i, 'instruction'))
                
                st.markdown("**Proficiency Levels (Anchors)**")
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
        if not is_new:
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
