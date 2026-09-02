import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  group('MatrixSynthesisGroup JSON Parsing', () {
    test('Should parse MatrixSynthesisGroup with valid fields', () {
      final jsonPayload = {
        'id': 'grp_1111111111111111',
        'title': {
          'translations': {'fi': 'Otsikko', 'en': 'Title'},
        },
        'target_blocks': ['blk_1', 'blk_2'],
        'view_type': '2d_compare',
      };

      final group = MatrixSynthesisGroup.fromJson(jsonPayload);

      expect(group, isNotNull);
      expect(group.id, 'grp_1111111111111111');
      expect(group.title.translations['en'], 'Title');
      expect(group.targetBlocks, ['blk_1', 'blk_2']);
      expect(group.viewType, PresetView.compare2d);
    });

    test('Should throw on unrecognized keys in MatrixSynthesisGroup', () {
      final jsonPayload = {
        'id': 'grp_1111111111111111',
        'title': {
          'translations': {'en': 'Title'},
        },
        'target_blocks': ['blk_1'],
        'extra_field': 'forbidden',
      };

      expect(
        () => MatrixSynthesisGroup.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test(
      'Should throw when legacy synthesis_directive is in MatrixSynthesisGroup',
      () {
        final jsonPayload = {
          'id': 'grp_1111111111111111',
          'title': {
            'translations': {'en': 'Title'},
          },
          'target_blocks': ['blk_1'],
          'synthesis_directive': 'forbidden',
        };

        expect(
          () => MatrixSynthesisGroup.fromJson(jsonPayload),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });

  group('OutputProfile JSON Parsing', () {
    test('Should parse fully populated OutputProfile with all fields', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'slug': 'test-profile',
        'workflow_id': 'wf_9d68c573802341db',
        'organization_id': 'org_123',
        'name': {
          'translations': {'en': 'Test Profile'},
        },
        'description': {
          'translations': {'en': 'Description'},
        },
        'user_role_label': {
          'translations': {'en': 'Role'},
        },
        'custom_preface': {
          'translations': {'en': 'Preface'},
        },
        'visible_metadata': ['date', 'user'],
        'visible_block_extensions': ['citation', 'coaching'],
        'visible_workflow_extensions': ['risk_flag'],
        'max_extension_items': 5,
        'display_scale': 'custom',
        'custom_scale_min': 0.0,
        'custom_scale_max': 100.0,
        'strictness_level': 85,
        'scoring_strategy': 'WATERFALL',
        'synthesis_length_constraint': 300,
        'max_quotes_per_matrix': 5,
        'max_unmet_criteria': 3,
        'tone_instruction': {
          'translations': {'en': 'Formal'},
        },
        'matrix_1d_synthesis_directive': {
          'translations': {'en': '1D Directive'},
        },
        'matrix_2d_synthesis_directive': {
          'translations': {'en': '2D Directive'},
        },
        'matrix_3d_synthesis_directive': {
          'translations': {'en': '3D Directive'},
        },
        'matrix_text_synthesis_directive': {
          'translations': {'en': 'Text Directive'},
        },
        'language': 'en',
        'matrix_synthesis_groups': [
          {
            'id': 'grp_1111111111111111',
            'title': {
              'translations': {'en': 'Group 1'},
            },
            'target_blocks': ['blk_1', 'blk_2'],
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
        'performativity_detector_step_id': 'step_perf_1',
      };

      final profile = OutputProfile.fromJson(jsonPayload);
      expect(profile.id, 'op_1234567890abcdef');
      expect(profile.displayScale, DisplayScale.custom);
      expect(profile.maxExtensionItems, 5);
      expect(profile.scoringStrategy, ScoringStrategy.waterfall);
      expect(profile.synthesisLengthConstraint, 300);
      expect(profile.maxQuotesPerMatrix, 5);
      expect(profile.maxUnmetCriteria, 3);
      expect(
        profile.matrix1dSynthesisDirective?.translations['en'],
        '1D Directive',
      );
      expect(
        profile.matrix2dSynthesisDirective?.translations['en'],
        '2D Directive',
      );
      expect(
        profile.matrix3dSynthesisDirective?.translations['en'],
        '3D Directive',
      );
      expect(
        profile.matrixTextSynthesisDirective?.translations['en'],
        'Text Directive',
      );
      expect(profile.targetBlockOrder.length, 12);
      expect(profile.targetBlockOrder.first, TargetBlockType.metadataBlock);
      expect(profile.targetBlockOrder.last, TargetBlockType.auditTrailBlock);
      expect(profile.matrixSynthesisGroups.length, 1);
      expect(profile.matrixSynthesisGroups.first.id, 'grp_1111111111111111');
      expect(profile.visibleBlockExtensions, [
        XaiExtensionType.citation,
        XaiExtensionType.coaching,
      ]);
      expect(profile.visibleWorkflowExtensions, [XaiExtensionType.riskFlag]);
      expect(profile.language, SystemLocale.en);
    });

    test('test_output_profile_language_enum_parsing', () {
      final basePayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'translations': {'en': 'Test Profile'},
        },
      };

      // Language null
      final profileNull = OutputProfile.fromJson(basePayload);
      expect(profileNull.language, isNull);

      // Language fi
      final profileFi = OutputProfile.fromJson({
        ...basePayload,
        'language': 'fi',
      });
      expect(profileFi.language, SystemLocale.fi);
      expect(profileFi.toJson()['language'], 'fi');

      // Invalid language throws
      expect(
        () => OutputProfile.fromJson({
          ...basePayload,
          'language': 'invalid_locale',
        }),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('test_output_profile_unknown_display_scale_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'translations': {'en': 'Test Profile'},
        },
        'display_scale': 'invalid_scale',
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('test_output_profile_unknown_target_block_type_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'translations': {'en': 'Test Profile'},
        },
        'target_block_order': ['invalid_block'],
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('test_output_profile_extra_root_key_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'translations': {'en': 'Test Profile'},
        },
        'include_diagnostic_scorecard': true,
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('test_output_profile_purged_layouts_key_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'translations': {'en': 'Test Profile'},
        },
        'layouts': [],
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('test_output_profile_purged_metric_mappings_key_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'translations': {'en': 'Test Profile'},
        },
        'metric'
                '_mappings':
            {},
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('test_output_profile_purged_synthesis_key_throws', () {
      final jsonPayload = {
        'id': 'op_1234567890abcdef',
        'workflow_id': 'wf_9d68c573802341db',
        'name': {
          'translations': {'en': 'Test Profile'},
        },
        'synthesis': {},
      };

      expect(
        () => OutputProfile.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test(
      'Should parse and serialize OutputProfile with custom_scale_min and custom_scale_max',
      () {
        final jsonPayload = {
          'id': 'op_1234567890abcdef',
          'workflow_id': 'wf_9d68c573802341db',
          'name': {
            'translations': {'en': 'Test Profile'},
          },
          'display_scale': 'custom',
          'custom_scale_min': 4.0,
          'custom_scale_max': 10.0,
        };

        final profile = OutputProfile.fromJson(jsonPayload);
        expect(profile.displayScale, DisplayScale.custom);
        expect(profile.customScaleMin, 4.0);
        expect(profile.customScaleMax, 10.0);

        final serialized = profile.toJson();
        expect(serialized['display_scale'], 'custom');
        expect(serialized['custom_scale_min'], 4.0);
        expect(serialized['custom_scale_max'], 10.0);
      },
    );
  });
}
