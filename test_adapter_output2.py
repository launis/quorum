from backend_v2.models.v2_core import OutputProfile, OutputLayoutBlock, I18nText
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_graphs_adapter import MatrixGraphsAdapter

layout = OutputLayoutBlock(
    preset_view="text_only",
    text_delivery_mode="full",
    title=I18nText(default_locale="en", translations={"en": "Title", "fi": "Title"}),
    target_blocks=["*"]
)
profile = OutputProfile(
    id='prf_1234567890abcdef',
    slug='test',
    workflow_id='test',
    name=I18nText(default_locale='en', translations={'en': 'Test'}),
    layouts=[layout]
)
context = AdapterContext(execution=None, locale='en', penalties_applied=[], mcp_audit_map=None, global_score=None, profile=profile, profile_cache=None, parsed_matrices={})
blocks = MatrixGraphsAdapter.build(context)
print(f'Blocks: {len(blocks)}')
if blocks:
    print(f'Block type: {getattr(blocks[0], "block_type", "")}')
