import pytest
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.v2_core import I18nText, ExtensionMetricsDTO, ExecutionRecord, RenderedSynthesisCache, OutputProfile
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.variance_adapter import VarianceAdapter
from backend_v2.exceptions import AppException
from backend_v2.models.enums import XaiExtensionType

def test_variance_adapter_metric_mappings_strip_crash():
    """
    Test that proves the bug where metric_mappings are stripped by exclude=True 
    when the profile passes through worker JSON boundaries via .model_dump().
    """
    # Create valid profile with metric mappings
    mappings = {
        "variance_mechanical": I18nText(default_locale="en", translations={"en": "Mechanical"}),
        "variance_cognitive": I18nText(default_locale="en", translations={"en": "Cognitive"}),
        "variance_total": I18nText(default_locale="en", translations={"en": "Total Variance"}),
        "alignment_verdict": I18nText(default_locale="en", translations={"en": "Verdict"}),
        "alignment_aligned": I18nText(default_locale="en", translations={"en": "Aligned"}),
        "alignment_misaligned": I18nText(default_locale="en", translations={"en": "Misaligned"}),
        "variance_fallback_explanation": I18nText(default_locale="en", translations={"en": "Explanation {0} {1}"})
    }
    profile = OutputProfileResponseDTO(
        id="out_1234567890abcdef",
        slug="test",
        workflow_id="wor_1234567890abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test"}),
        metric_mappings=mappings, 
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        extension_labels={XaiExtensionType.VARIANCE_VALIDATION: I18nText(default_locale="en", translations={"en": "Variance"})},
        max_extension_items=5,
        layouts=[]
    )
    
    # Simulate Arq Worker serialization boundary (where model_dump is called)
    dumped_data = profile.model_dump()
    rehydrated_profile = OutputProfile(**dumped_data)
    
    # Setup Variance Adapter context
    metrics = ExtensionMetricsDTO(
        authenticity_score=85.0,
        performative_phrases_count=3,
        variance_score=15.0,
        alignment_verdict="ALIGNED"
    )
    cache = RenderedSynthesisCache(extension_metrics=metrics, row_explanations={"variance_validation": "Test Explanation"})
    exe = ExecutionRecord(
        id="exe_1234567890123456", 
        workflow_id="wor_1234567890123456", 
        output_profile_id="out_12345678", 
        status="PENDING"
    )
    
    context = AdapterContext(
        profile=rehydrated_profile,
        profile_cache=cache,
        execution=exe,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        user_name=None,
        org_name=None
    )
    
    # This should fail because metric_mappings are stripped
    with pytest.raises(AppException) as exc:
        VarianceAdapter.build(context)
        
    assert "Missing metric_mappings translation for 'variance_mechanical'" in str(exc.value.message)
