
def fix_imports():
    with open("backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py", encoding="utf-8") as f:
        content = f.read()

    # Add MarkdownBlock import
    content = content.replace(
        "from backend_v2.models.view.sdui import SduiRadarChartBlock",
        "from backend_v2.models.view.sdui import SduiRadarChartBlock, MarkdownBlock"
    )

    with open("backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py", "w", encoding="utf-8") as f:
        f.write(content)

fix_imports()
print("Fixed imports")
