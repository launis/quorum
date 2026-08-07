import re

def revert_and_fix_graph_tests():
    with open("backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Revert empty layouts
    old_test_empty = """    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2"""
    
    new_test_empty = """    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 0"""
    content = content.replace(old_test_empty, new_test_empty, 1)

    # test_matrix_graphs_adapter_success assertions
    old_test_success = """    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], SduiRadarChartBlock)
    assert len(blocks[0].axes) == 3"""
    
    new_test_success = """    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Graph 3D"
    assert isinstance(blocks[1], SduiRadarChartBlock)
    assert len(blocks[1].axes) == 3"""
    content = content.replace(old_test_success, new_test_success)

    # test_matrix_graphs_adapter_graceful_degradation
    # Let's check what it should assert
    # It degraded to 1d_metrics, which outputs MarkdownBlock and SduiMetrics1DBlock
    old_test_graceful = """    # Degrades from 3d_matrix (needs 3) to 1d_metrics (needs 1)
    # 1d_metrics just unpacks inner_sdui_blocks, which are empty here.
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2"""
    
    new_test_graceful = """    # Degrades from 3d_matrix (needs 3) to 1d_metrics (needs 1)
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Graph 3D"
    from backend_v2.models.view.sdui import SduiMetrics1DBlock
    assert isinstance(blocks[1], SduiMetrics1DBlock)"""
    content = content.replace(old_test_graceful, new_test_graceful)

    with open("backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py", "w", encoding="utf-8") as f:
        f.write(content)

revert_and_fix_graph_tests()
print("Fixed graph tests")
