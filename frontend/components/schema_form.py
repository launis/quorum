"""Generic Schema-Driven Form Component for Streamlit."""

import streamlit as st

def render_schema_form(schema: dict, current_values: dict = None, key_prefix: str = "sdui"):
    """Renders a Streamlit form based on a JSON Schema.

    Args:
        schema (dict): The JSON Schema (Pydantic .model_json_schema() output).
        current_values (dict): Optional dictionary of current values to populate.
        key_prefix (str): Unique prefix for widget keys to avoid collisions.
    
    Returns:
        dict: The updated values from the form widgets.
    """
    if not current_values:
        current_values = {}

    form_data = {}
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    for field_name, props in properties.items():
        field_title = props.get("title", field_name).replace("_", " ").title()
        field_desc = props.get("description", "")
        field_type = props.get("type", "string")

        # Get existing value or default
        val = current_values.get(field_name, props.get("default", None))

        # Handle Read-Only / System Fields (simple heuristic based on name)
        # In a real SDUI, we'd use a custom "ui:readonly" annotation in the schema.
        # For now, we hardcode common non-editable fields.
        if field_name in ["id", "created_at", "updated_at", "uid"]:
           st.text_input(field_title, value=val, disabled=True, help=field_desc)
           continue

        key = f"{key_prefix}_{field_name}"


        # 1. Booleans (Checkbox)
        if field_type == "boolean":
            form_data[field_name] = st.checkbox(
                field_title, 
                value=bool(val) if val is not None else False, 
                help=field_desc,
                key=key
            )

        # 2. Enums (Selectbox)
        elif "enum" in props:
            # If value is NOT in enum (e.g. data drift), add it temporarily or specific logic?
            # We assume strict adherence for now.
            options = props["enum"]
            # Try to find index
            try:
                idx = options.index(val) if val in options else 0
            except ValueError:
                idx = 0
            
            form_data[field_name] = st.selectbox(
                field_title,
                options=options,
                index=idx,
                help=field_desc,
                key=key
            )

        # 3. Integers/Numbers
        elif field_type == "integer":
            # Check min/max
            min_v = props.get("minimum")
            max_v = props.get("maximum")
            form_data[field_name] = st.number_input(
                field_title,
                value=int(val) if val is not None else 0,
                min_value=min_v,
                max_value=max_v,
                step=1,
                help=field_desc,
                key=key
            )
        elif field_type == "number":
             min_v = props.get("minimum")
             max_v = props.get("maximum")
             form_data[field_name] = st.number_input(
                field_title,
                value=float(val) if val is not None else 0.0,
                min_value=min_v,
                max_value=max_v,
                help=field_desc,
                key=key
            )

        # 4. Strings (Text Input / Text Area)
        elif field_type == "string":
            # Heuristic: Is it a password?
            is_password = "password" in field_name.lower()
            
            form_data[field_name] = st.text_input(
                field_title,
                value=str(val) if val is not None else "",
                help=field_desc,
                type="password" if is_password else "default",
                key=key
            )
        
        # Fallback
        else:
             st.warning(f"Unsupported field type: {field_type} for {field_name}")

    return form_data
