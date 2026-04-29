import os

path = 'backend_v2/tests/unit/test_studio.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('mock_repo.get.return_value = mock_workflow', 'mock_repo.get_workflow_by_id.return_value = mock_workflow')
c = c.replace('mock_repo.get.return_value = mock_block.model_dump(mode="json")', 'mock_repo.save_prompt_block.side_effect = lambda org, id, data: data\n    mock_repo.get_prompt_block_by_id.return_value = mock_block.model_dump(mode="json")')
c = c.replace('mock_repo.get.side_effect = mock_get', 'mock_repo.save_step.side_effect = lambda org, id, data: data\n    mock_repo.get_step_by_id.side_effect = mock_get')
c = c.replace('mock_repo.get_all.return_value = [mock_workflow]', 'mock_repo.get_all_workflows.return_value = [mock_workflow]')
c = c.replace('mock_repo.get.return_value = None', 'mock_repo.get_step_by_id.return_value = None')
c = c.replace('mock_repo.get.side_effect = mock_get_workflow', 'mock_repo.save_workflow.side_effect = lambda org, id, data: data\n    mock_repo.get_workflow_by_id.side_effect = mock_get_workflow')
c = c.replace('mock_repo.get_all.return_value = [mock_step]', 'mock_repo.get_all_steps.return_value = [mock_step]')
c = c.replace('dumped = dto.model_dump()', 'dumped = dto.model_dump(exclude={"organization_id"})')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
