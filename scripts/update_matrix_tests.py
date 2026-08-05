import re

def update_summary_tests():
    with open("backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Add MarkdownBlock import if needed
    if "MarkdownBlock" not in content:
        content = content.replace("from backend_v2.models.view.sdui import SduiMatrixTableBlock", 
                                  "from backend_v2.models.view.sdui import SduiMatrixTableBlock, MarkdownBlock")

    # Replace test 1
    old_test_1 = """    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMatrixTableBlock)
    assert len(blocks[0].axes) == 1
    assert blocks[0].matrix_visible_columns == ["label", "score"]"""
    
    new_test_1 = """    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Table Summary"
    assert isinstance(blocks[1], SduiMatrixTableBlock)
    assert len(blocks[1].axes) == 1
    assert blocks[1].matrix_visible_columns == ["label", "score"]"""
    content = content.replace(old_test_1, new_test_1)

    # Replace test 2
    old_test_2 = """    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMatrixTableBlock)
    assert len(blocks[0].axes) == 1
    assert blocks[0].axes[0].evaluated_atoms == []"""
    
    new_test_2 = """    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], SduiMatrixTableBlock)
    assert len(blocks[1].axes) == 1
    assert blocks[1].axes[0].evaluated_atoms == []"""
    content = content.replace(old_test_2, new_test_2)
    
    # Replace test 3
    old_test_3 = """    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMatrixTableBlock)
    assert len(blocks[0].axes) == 2"""
    
    new_test_3 = """    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], SduiMatrixTableBlock)
    assert len(blocks[1].axes) == 2"""
    content = content.replace(old_test_3, new_test_3)
    
    # Replace test 4
    old_test_4 = """    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 3
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "Test description"
    assert isinstance(blocks[1], MarkdownBlock)
    assert blocks[1].text == "Synthesis markdown content"
    assert isinstance(blocks[2], SduiMatrixTableBlock)"""
    
    new_test_4 = """    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 4
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Table Summary"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "Test description"
    assert isinstance(blocks[2], MarkdownBlock)
    assert blocks[2].text == "Synthesis markdown content"
    assert isinstance(blocks[3], SduiMatrixTableBlock)"""
    content = content.replace(old_test_4, new_test_4)

    with open("backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py", "w", encoding="utf-8") as f:
        f.write(content)

update_summary_tests()
print("Updated matrix summary tests")
