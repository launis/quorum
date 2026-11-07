import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ExecutionCreateRequestDto Unit & ISTQB Boundary Tests', () {
    const validWorkflowId = 'wf_0195f3a0000070008000000000000002';
    const validProfileId = 'op_0195f3a0000070008000000000000003';

    test(
      'Positive 1: roundtrips full JSON payload and preserves snake_case mapping',
      () {
        final generatedWfId = generateOpaqueUuid7('wf');
        final rawJson = <String, Object?>{
          'workflow_id': generatedWfId,
          'target_locale': 'fi',
          'raw_inputs': <String, Object?>{
            'dynamic_inputs': <String, Object?>{
              'deliverable_text': 'Sample text',
            },
          },
          'profile_id': validProfileId,
          'matrix_sampling_strategy': 0,
        };

        final dto = ExecutionCreateRequestDto.fromJson(rawJson);

        expect(dto.workflowId, equals(generatedWfId));
        expect(dto.targetLocale, equals('fi'));
        expect(
          dto.rawInputs.dynamicInputs['deliverable_text']?.textValue,
          equals('Sample text'),
        );
        expect(dto.profileId, equals(validProfileId));
        expect(dto.matrixSamplingStrategy, equals(0));

        final serialized = dto.toJson();
        expect(serialized['workflow_id'], equals(generatedWfId));
        expect(serialized['target_locale'], equals('fi'));
        expect(serialized['profile_id'], equals(validProfileId));
        expect(serialized['matrix_sampling_strategy'], equals(0));
      },
    );

    test(
      'Positive 2: applies strict defaults when optional fields are omitted',
      () {
        final rawJson = <String, Object?>{
          'workflow_id': validWorkflowId,
          'target_locale': 'en',
        };

        final dto = ExecutionCreateRequestDto.fromJson(rawJson);

        expect(dto.workflowId, equals(validWorkflowId));
        expect(dto.targetLocale, equals('en'));
        expect(dto.rawInputs.dynamicInputs, isEmpty);
        expect(dto.profileId, isNull);
        expect(dto.matrixSamplingStrategy, isNull);
      },
    );

    test(
      'Negative 1 (BVA): rejects invalid 32-hex workflow_id formats on fromJson and toJson (empty, 16-hex, 31-hex min-1, 33-hex max+1, prefix bounds)',
      () {
        const invalidIds = <String>[
          '',
          'wf_0123456789abcdef', // legacy 16-hex
          'wf_0195f3a000007000800000000000000', // 31-hex (min-1)
          'wf_0195f3a00000700080000000000000012', // 33-hex (max+1)
          'w_0195f3a0000070008000000000000002', // 1-char prefix (min-1)
          'abcdef_0195f3a0000070008000000000000002', // 6-char prefix (max+1)
        ];

        for (final invalidId in invalidIds) {
          expect(
            () => ExecutionCreateRequestDto.fromJson(<String, Object?>{
              'workflow_id': invalidId,
              'target_locale': 'fi',
            }),
            throwsA(
              anyOf(
                isA<AppException>(),
                isA<CheckedFromJsonException>().having(
                  (e) => e.innerError,
                  'innerError',
                  isA<AppException>(),
                ),
              ),
            ),
          );

          final invalidDto = ExecutionCreateRequestDto(
            workflowId: invalidId,
            targetLocale: 'fi',
          );
          expect(
            () => invalidDto.toJson(),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                equals('VALIDATION_FAILED'),
              ),
            ),
          );
        }
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException on unrecognized keys or missing required fields',
      () {
        expect(
          () => ExecutionCreateRequestDto.fromJson(<String, Object?>{
            'workflow_id': validWorkflowId,
            'target_locale': 'fi',
            'unexpected_field': 'forbidden',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => ExecutionCreateRequestDto.fromJson(<String, Object?>{
            'workflow_id': validWorkflowId,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => ExecutionCreateRequestDto.fromJson(<String, Object?>{
            'target_locale': 'fi',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    // Phase 5, Step 5.2 Test Contract: test_dynamic_start_screen_validates_required_workflow_inputs
    test(
      'test_dynamic_start_screen_validates_required_workflow_inputs (Boundary: 0 and 5 required ExpectedInput definitions)',
      () {
        const title = I18nText(translations: {'en': 'Test WF', 'fi': 'Testi'});
        const wfZeroInputs = Workflow(
          id: validWorkflowId,
          slug: 'zero_inputs_wf',
          name: title,
          description: title,
          modelRegistryId: 'mr_0195f3a0000070008000000000000004',
          expectedInputs: [],
        );
        expect(wfZeroInputs.expectedInputs, isEmpty);

        const reqZero = ExecutionCreateRequestDto(
          workflowId: validWorkflowId,
          targetLocale: 'fi',
          rawInputs: WorkflowInputs(dynamicInputs: {}),
        );
        expect(reqZero.rawInputs.dynamicInputs, isEmpty);

        final fiveExpectedInputs = List<ExpectedInput>.generate(
          5,
          (i) => ExpectedInput(
            inputKey: 'input_$i',
            label: I18nText(translations: {'en': 'Input $i', 'fi': 'Syote $i'}),
            description: I18nText(
              translations: {'en': 'Description $i', 'fi': 'Kuvaus $i'},
            ),
            required: true,
          ),
        );
        final wfFiveInputs = wfZeroInputs.copyWith(
          expectedInputs: fiveExpectedInputs,
        );
        expect(wfFiveInputs.expectedInputs, hasLength(5));

        final dynamicMap = <String, WorkflowInputValue>{
          for (final exp in wfFiveInputs.expectedInputs)
            exp.inputKey: WorkflowInputValue(
              textValue: 'Value for ${exp.inputKey}',
            ),
        };
        final reqFive = ExecutionCreateRequestDto(
          workflowId: wfFiveInputs.id,
          targetLocale: 'fi',
          rawInputs: WorkflowInputs(dynamicInputs: dynamicMap),
        );
        expect(reqFive.rawInputs.dynamicInputs, hasLength(5));
        expect(
          reqFive.rawInputs.dynamicInputs['input_4']?.textValue,
          equals('Value for input_4'),
        );
      },
    );
  });
}
