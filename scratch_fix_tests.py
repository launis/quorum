import sys

path1 = 'backend_v2/tests/unit/llm/test_client_schema.py'
content = open(path1, 'r').read()
content = content.replace(
    'with patch("backend_v2.llm.provider.LLMFactory.create_provider") as mock_factory:\n        mock_provider = AsyncMock()\n        mock_factory.return_value = mock_provider',
    'with patch("backend_v2.llm.provider.LLMFactory.create_provider") as mock_factory, \\\n         patch("backend_v2.llm.client.LLMCacheAdapterFactory.get_adapter") as mock_adapter_factory:\n        mock_provider = AsyncMock()\n        mock_factory.return_value = mock_provider\n        mock_adapter_factory.return_value.prepare_provider_kwargs.return_value = {}'
)
open(path1, 'w').write(content)

path2 = 'backend_v2/tests/unit/llm/test_structured_retry.py'
content2 = open(path2, 'r').read()
content2 = content2.replace(
    'with patch("backend_v2.llm.provider.LLMFactory.create_provider", return_value=mock_provider):',
    'with patch("backend_v2.llm.provider.LLMFactory.create_provider", return_value=mock_provider), \\\n         patch("backend_v2.llm.client.LLMCacheAdapterFactory.get_adapter") as mock_adapter_factory:\n        mock_adapter_factory.return_value.prepare_provider_kwargs.return_value = {}'
)
open(path2, 'w').write(content2)

print('Tests fixed.')
