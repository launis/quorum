import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  group('OutputLayoutBlock JSON Parsing', () {
    test('Should parse OutputLayoutBlock with valid enums and fields', () {
      final jsonPayload = {
        'preset_view': 'default',
        'title': {
          'default_locale': 'en',
          'translations': {'fi': 'Otsikko', 'en': 'Title'},
        },
        'text_delivery_mode': 'full',
        'is_synthesis_enabled': true,
      };

      final block = OutputLayoutBlock.fromJson(jsonPayload);

      expect(block, isNotNull);
      expect(block.presetView, PresetView.defaultView);
      expect(block.textDeliveryMode, TextDeliveryMode.full);
      expect(block.isSynthesisEnabled, isTrue);
    });

    test('Should parse empty JSON and default maps to {}', () {
      final jsonPayload = <String, dynamic>{};

      final block = OutputLayoutBlock.fromJson(jsonPayload);

      expect(block, isNotNull);
      expect(block.presetView, PresetView.defaultView);
      expect(block.textDeliveryMode, TextDeliveryMode.full);
      expect(block.matrixColumnLabels, isEmpty);
    });

    // Contract: test_output_layout_block_unknown_preset_view_throws
    test('test_output_layout_block_unknown_preset_view_throws', () {
      final jsonPayload = {
        'preset_view': 'unknown_preset',
        'text_delivery_mode': 'full',
      };

      expect(
        () => OutputLayoutBlock.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    // Contract: test_output_layout_block_unknown_text_delivery_mode_throws
    test('test_output_layout_block_unknown_text_delivery_mode_throws', () {
      final jsonPayload = {
        'preset_view': 'default',
        'text_delivery_mode': 'invalid_mode',
      };

      expect(
        () => OutputLayoutBlock.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });

  group('SynthesisConfigDTO JSON Parsing', () {
    test(
      'Should parse SynthesisConfigDTO with synthesis_block_id and row_explanations_block_id',
      () {
        final jsonPayload = {
          'synthesis_block_id': 'blk_8f7e6d5c4b3a2019',
          'row_explanations_block_id': 'blk_row_explanation_rules',
          'length_constraint': 300,
        };

        final dto = SynthesisConfigDTO.fromJson(jsonPayload);
        expect(dto.synthesisBlockId, 'blk_8f7e6d5c4b3a2019');
        expect(dto.rowExplanationsBlockId, 'blk_row_explanation_rules');
        expect(dto.lengthConstraint, 300);
      },
    );

    test(
      'Should parse SynthesisConfigDTO with max_quotes_per_matrix and max_unmet_criteria',
      () {
        final jsonPayload = {
          'synthesis_block_id': 'blk_8f7e6d5c4b3a2019',
          'row_explanations_block_id': 'blk_row_explanation_rules',
          'max_quotes_per_matrix': 5,
          'max_unmet_criteria': 3,
        };

        final dto = SynthesisConfigDTO.fromJson(jsonPayload);
        expect(dto.synthesisBlockId, 'blk_8f7e6d5c4b3a2019');
        expect(dto.maxQuotesPerMatrix, 5);
        expect(dto.maxUnmetCriteria, 3);
      },
    );

    // Contract: test_synthesis_config_dto_purged_enable_pii_masking_throws
    test('test_synthesis_config_dto_purged_enable_pii_masking_throws', () {
      final jsonPayload = {'enable_pii_masking': false};

      expect(
        () => SynthesisConfigDTO.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    // Contract: test_synthesis_config_dto_purged_historical_context_mode_throws
    test('test_synthesis_config_dto_purged_historical_context_mode_throws', () {
      final jsonPayload = {'historical_context_mode': 'DISABLED'};

      expect(
        () => SynthesisConfigDTO.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    // Contract: test_synthesis_config_dto_purged_allowed_exports_throws
    test('test_synthesis_config_dto_purged_allowed_exports_throws', () {
      final jsonPayload = {
        'allowed_exports': ['pdf'],
      };

      expect(
        () => SynthesisConfigDTO.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });

  group('OutputProfile JSON Parsing', () {
    test('Should parse strict ID for system workflows and valid language', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'language': 'fi',
        'content_blocks': [
          {'id': 'blk_123', 'block_type': 'markdown', 'text': 'test'},
        ],
      };

      final profile = OutputProfile.fromJson(jsonPayload);
      expect(profile.workflowId, 'wf_9d68c573802341db');
      expect(profile.language, 'fi');
      expect(profile.displayScale, DisplayScale.original);
      expect(profile.maxExtensionItems, 3);
    });

    test('Should parse OutputProfile with synthesis object', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'synthesis': {
          'synthesis_block_id': 'blk_1a2b3c4d5e6f7a8b',
          'row_explanations_block_id': 'blk_row_explanation_rules',
          'length_constraint': 250,
        },
      };

      final profile = OutputProfile.fromJson(jsonPayload);
      expect(profile.synthesis, isNotNull);
      expect(profile.synthesis?.synthesisBlockId, 'blk_1a2b3c4d5e6f7a8b');
      expect(
        profile.synthesis?.rowExplanationsBlockId,
        'blk_row_explanation_rules',
      );
      expect(profile.synthesis?.lengthConstraint, 250);
    });

    // Contract: test_output_profile_valid_deserialization
    test('test_output_profile_valid_deserialization', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'slug': 'test-profile',
        'workflow_id': 'wf_9d68c573802341db',
        'organization_id': 'org_123',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Complete Valid Profile'},
        },
        'description': {
          'default_locale': 'en',
          'translations': {'en': 'Valid Description'},
        },
        'user_role_label': {
          'default_locale': 'en',
          'translations': {'en': 'Lead'},
        },
        'custom_preface': {
          'default_locale': 'en',
          'translations': {'en': 'Preface'},
        },
        'visible_metadata': ['date', 'organization'],
        'visible_block_extensions': ['citation', 'coaching'],
        'visible_workflow_extensions': ['risk_flag'],
        'max_extension_items': 5,
        'display_scale': 'custom',
        'strictness_level': 85,
        'scoring_strategy': 'WATERFALL',
        'tone_instruction': {
          'default_locale': 'en',
          'translations': {'en': 'Formal'},
        },
        'language': 'en',
        'user_role_mappings': {
          'role_1': {
            'default_locale': 'en',
            'translations': {'en': 'Role One'},
          },
        },
        'extension_labels': {
          'ext_1': {
            'default_locale': 'en',
            'translations': {'en': 'Extension One'},
          },
        },
        'metric_mappings': {
          'metric_1': {
            'default_locale': 'en',
            'translations': {'en': 'Metric One'},
          },
        },
        'layouts': [
          {
            'preset_view': '1d_metrics',
            'title': {
              'default_locale': 'en',
              'translations': {'en': 'Layout 1'},
            },
            'text_delivery_mode': 'titles_only',
            'is_synthesis_enabled': true,
          },
        ],
        'content_blocks': [
          {'id': 'blk_123', 'block_type': 'markdown', 'text': 'Content'},
        ],
        'target_block_order': [
          'metadata_block',
          'executive_summary_block',
          'synthesis_text_block',
          'matrix_graphs_block',
          'grouped_extensions_block',
          'penalties_block',
          'matrix_summary_table_block',
          'variance_validation_block',
          'authenticity_evaluation_block',
          'printable_sources_block',
          'global_score_block',
          'audit_trail_block',
        ],
        'synthesis': {
          'synthesis_block_id': 'blk_syn_1',
          'length_constraint': 300,
        },
        'performativity_detector_step_id': 'step_perf_1',
      };

      final profile = OutputProfile.fromJson(jsonPayload);
      expect(profile.id, 'op_1234567890abcdef');
      expect(profile.displayScale, DisplayScale.custom);
      expect(profile.maxExtensionItems, 5);
      expect(profile.scoringStrategy, ScoringStrategy.waterfall);
      expect(profile.targetBlockOrder.length, 12);
      expect(profile.targetBlockOrder.first, TargetBlockType.metadataBlock);
      expect(profile.targetBlockOrder.last, TargetBlockType.auditTrailBlock);
      expect(profile.layouts.first.presetView, PresetView.metrics1d);
      expect(
        profile.layouts.first.textDeliveryMode,
        TextDeliveryMode.titlesOnly,
      );
      expect(profile.synthesis?.synthesisBlockId, 'blk_syn_1');
      expect(profile.synthesis?.lengthConstraint, 300);
      expect(profile.visibleBlockExtensions, [
        XaiExtensionType.citation,
        XaiExtensionType.coaching,
      ]);
      expect(profile.visibleWorkflowExtensions, [XaiExtensionType.riskFlag]);
    });

    // Contract: test_output_profile_unknown_display_scale_throws
    test('test_output_profile_unknown_display_scale_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'display_scale': 'invalid_scale',
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    // Contract: test_output_profile_unknown_target_block_type_throws
    test('test_output_profile_unknown_target_block_type_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'target_block_order': ['invalid_block'],
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    // Contract: test_output_profile_extra_root_key_throws
    test('test_output_profile_extra_root_key_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'include_diagnostic_scorecard': true,
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    // Contract: test_output_profile_extra_key_in_synthesis_config_throws
    test('test_output_profile_extra_key_in_synthesis_config_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'synthesis': {'synthesis_block_id': 'blk_syn_1', 'ghost_key': true},
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    // Contract: test_output_profile_extra_key_in_layout_throws
    test('test_output_profile_extra_key_in_layout_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'default_locale': 'en',
          'translations': {'en': 'Test Profile'},
        },
        'layouts': [
          {'preset_view': 'default', 'ghost_key': true},
        ],
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });
}
