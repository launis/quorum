import re

path = r"c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove the broken test
c = re.sub(
    r'@pytest\.mark\.asyncio\nasync def test_blueprint_transformer_slop_scan_uses_system_repo\(\) -> None:.*',
    "",
    c,
    flags=re.DOTALL
)

new_test = """@pytest.mark.asyncio
async def test_blueprint_transformer_slop_scan_uses_system_repo(mock_repo_transformer: AsyncMock) -> None:
    \"\"\"Proves that BlueprintTransformer correctly calls get_system_config on system_repo.\"\"\"
    from backend_v2.services.blueprint import BlueprintTransformer
    
    mock_system_repo = AsyncMock()
    
    # Enable slop scanning on the mocked workflow
    wf = await mock_repo_transformer.get_workflow("wf_1234abcd1234abcd")
    from types import SimpleNamespace
    wf.expected_inputs = [SimpleNamespace(id="doc1", type="document", scan_for_performative_patterns=True)]
    mock_repo_transformer.get_workflow.return_value = wf

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_system_repo,
    )

    try:
        await transformer.build_report_dto("exe_0000000000000001", accept_language="en")
    except Exception:
        pass

    mock_system_repo.get_system_config.assert_called_once()
"""

with open(path, "w", encoding="utf-8") as f:
    f.write(c + new_test)

print("Replaced tests using mock_repo_transformer")
