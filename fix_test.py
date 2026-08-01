with open('C:/src/quorum/backend_v2/tests/unit/services/test_blueprint.py', 'a', encoding='utf-8') as f:
    f.write('''
@pytest.mark.asyncio
async def test_blueprint_authenticity_evaluation_fallback_trace_extraction(
    mock_repo_transformer: MagicMock,
) -> None:
    """Verify that if step_detector is missing in cv, authenticity_evaluation falls back to folded trace extraction."""
    from backend_v2.models.v2_core import Workflow, StepRule
    
    mock_repo_transformer.get_execution.return_value = ExecutionRecord(
        id="exe_0000000000000097",
        workflow_id="wf_1234abcd1234abcd",
        status=ExecutionStatus.PASSED,
        active_profile_id="prf_dddd1111dddd1111",
        execution_trace=[
            TraceEvent(
                step_name="stp_1234abcd1234abcd",
                event_type="decision",
                content={"blk_mock_id": {"raw_score": 85.0}},
                timestamp=datetime.now(timezone.utc),
                v=1,
                redacted_hash=""
            )
        ],
        context_variables={},
        metadata={"target_locale": "en"},
    )

    mock_repo_transformer.get_workflow.return_value = Workflow.model_construct(
        id="wf_1234abcd1234abcd",
        name="Test WF",
        default_profile_id="prf_dddd1111dddd1111",
        steps=[
            StepRule(id="stp_1234abcd1234abcd", task_blueprint="sp_7f9649114d2344dc")
        ]
    )

    mock_repo_transformer.get_all_output_profiles.return_value = [
        OutputProfile(
            id="prf_dddd1111dddd1111",
            slug="default",
            workflow_id="wf_1234abcd1234abcd",
            name=I18nText(default_locale="en", translations={"en": "Default"}),
            display_scale="original",
            layouts=[
                OutputLayoutBlock(
                    preset_view="1d_metrics",
                    target_blocks=["*"],
                )
            ],
            visible_block_extensions=[],
            visible_workflow_extensions=[XaiExtensionType.AUTHENTICITY_EVALUATION],
            max_extension_items=2,
            strictness_level=85,
        )
    ]

    transformer = BlueprintTransformer(
        exec_repo=mock_repo_transformer,
        workflow_repo=mock_repo_transformer,
        comp_repo=mock_repo_transformer,
        prompt_block_repo=mock_repo_transformer,
        output_profile_repo=mock_repo_transformer,
        identity_repo=mock_repo_transformer,
        system_repo=mock_repo_transformer,
    )

    report_dto = await transformer.build_report_dto("exe_0000000000000097")
    
    assert report_dto is not None
    assert any(
        getattr(axis, "block_id", None) == "auth_metrics_row"
        for layout in report_dto.layouts
        for axis in getattr(layout, "axes", [])
    )
''')
