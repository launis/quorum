
def fix_title_resolve():
    with open("backend_v2/services/sdui/adapters/matrix_graphs_adapter.py", encoding="utf-8") as f:
        content = f.read()

    content = content.replace('f"### {layout_def.title}"', 'f"### {layout_def.title.resolve(locale)}"')

    with open("backend_v2/services/sdui/adapters/matrix_graphs_adapter.py", "w", encoding="utf-8") as f:
        f.write(content)

    with open("backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py", encoding="utf-8") as f:
        content = f.read()

    content = content.replace('f"### {layout_def.title}"', 'f"### {layout_def.title.resolve(locale)}"')

    with open("backend_v2/services/sdui/adapters/matrix_summary_table_adapter.py", "w", encoding="utf-8") as f:
        f.write(content)

fix_title_resolve()
print("Fixed title resolve")
