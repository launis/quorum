import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/utils/workflow_cloner.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const converter = StrictOpaqueIdConverter();
  const sampleTitle = I18nText(
    translations: {'en': 'Original Workflow', 'fi': 'Alkuperäinen työnkulku'},
  );
  const sampleDesc = I18nText(
    translations: {'en': 'Workflow description', 'fi': 'Kuvaus'},
  );

  group('WorkflowCloner.cloneWorkflow (Typed Freezed Domain Model)', () {
    test(
      'Positive: clones Workflow with 32-hex UUIDv7 IDs and remaps dependencies, inputMappings, causalSourceStepId, and OutputProfiles',
      () {
        const wfId = 'wf_0195f3a0000070008000000000000001';
        const srCausalId = 'sr_0195f3a0000070008000000000000010';
        const srSpecialistId = 'sr_0195f3a0000070008000000000000020';
        const bpCausalId = 'st_0195f3a0000070008000000000000100';
        const bpSpecialistId = 'st_0195f3a0000070008000000000000200';
        const opId = 'op_0195f3a0000070008000000000000300';
        const mrId = 'mr_0195f3a0000070008000000000000400';

        const original = Workflow(
          id: wfId,
          slug: 'exec_coaching_v2',
          name: sampleTitle,
          description: sampleDesc,
          version: 3,
          modelRegistryId: mrId,
          defaultProfileId: opId,
          outputProfiles: {
            opId: OutputProfile(
              id: opId,
              slug: 'exec_profile',
              workflowId: wfId,
              name: sampleTitle,
            ),
          },
          steps: [
            StepRule(
              id: srCausalId,
              taskBlueprint: bpCausalId,
              dependsOn: [],
              inputMappings: {},
            ),
            StepRule(
              id: srSpecialistId,
              taskBlueprint: bpSpecialistId,
              dependsOn: [srCausalId],
              causalSourceStepId: srCausalId,
              inputMappings: {
                'causal_graph': '\$steps.$srCausalId.outputs.graph',
                'raw_res': '\$results.$srCausalId.summary',
              },
            ),
          ],
        );

        final cloned = WorkflowCloner.cloneWorkflow(original);

        expect(cloned.id, isNot(equals(wfId)));
        expect(converter.fromJson(cloned.id), equals(cloned.id));
        expect(cloned.slug, equals('exec_coaching_v2_copy'));
        expect(cloned.version, equals(1));
        expect(cloned.steps, hasLength(2));

        final newCausalStep = cloned.steps[0];
        final newSpecialistStep = cloned.steps[1];

        expect(newCausalStep.id, isNot(equals(srCausalId)));
        expect(newSpecialistStep.id, isNot(equals(srSpecialistId)));
        expect(converter.fromJson(newCausalStep.id), equals(newCausalStep.id));
        expect(
          converter.fromJson(newSpecialistStep.id),
          equals(newSpecialistStep.id),
        );

        expect(newSpecialistStep.dependsOn, equals([newCausalStep.id]));
        expect(newSpecialistStep.causalSourceStepId, equals(newCausalStep.id));
        expect(
          newSpecialistStep.inputMappings['causal_graph'],
          equals('\$steps.${newCausalStep.id}.outputs.graph'),
        );
        expect(
          newSpecialistStep.inputMappings['raw_res'],
          equals('\$results.${newCausalStep.id}.summary'),
        );

        expect(cloned.outputProfiles, hasLength(1));
        final clonedProfile = cloned.outputProfiles.values.first;
        expect(clonedProfile.id, isNot(equals(opId)));
        expect(converter.fromJson(clonedProfile.id), equals(clonedProfile.id));
        expect(clonedProfile.workflowId, equals(cloned.id));
        expect(cloned.defaultProfileId, equals(clonedProfile.id));
      },
    );

    test(
      'Negative 1: throws AppException when StepRule dependsOn references an unmapped step',
      () {
        const original = Workflow(
          id: 'wf_0195f3a0000070008000000000000001',
          slug: 'broken_dep_wf',
          name: sampleTitle,
          description: sampleDesc,
          modelRegistryId: 'mr_0195f3a0000070008000000000000400',
          steps: [
            StepRule(
              id: 'sr_0195f3a0000070008000000000000010',
              taskBlueprint: 'st_0195f3a0000070008000000000000100',
              dependsOn: ['sr_0195f3a0000070008000000000000999'],
            ),
          ],
        );

        expect(
          () => WorkflowCloner.cloneWorkflow(original),
          throwsA(
            isA<AppException>().having(
              (e) => e.extensions['error_code'],
              'error_code',
              equals('WORKFLOW_CLONE_FAILED'),
            ),
          ),
        );
      },
    );

    test(
      'Negative 2 (Boundary): throws AppException when StepRule has empty ID or causalSourceStepId is omitted from dependsOn',
      () {
        const emptyStepWorkflow = Workflow(
          id: 'wf_0195f3a0000070008000000000000001',
          slug: 'empty_step_id_wf',
          name: sampleTitle,
          description: sampleDesc,
          modelRegistryId: 'mr_0195f3a0000070008000000000000400',
          steps: [
            StepRule(
              id: '',
              taskBlueprint: 'st_0195f3a0000070008000000000000100',
            ),
          ],
        );

        expect(
          () => WorkflowCloner.cloneWorkflow(emptyStepWorkflow),
          throwsA(isA<AppException>()),
        );

        const missingCausalDepWorkflow = Workflow(
          id: 'wf_0195f3a0000070008000000000000001',
          slug: 'missing_causal_dep_wf',
          name: sampleTitle,
          description: sampleDesc,
          modelRegistryId: 'mr_0195f3a0000070008000000000000400',
          steps: [
            StepRule(
              id: 'sr_0195f3a0000070008000000000000010',
              taskBlueprint: 'st_0195f3a0000070008000000000000100',
            ),
            StepRule(
              id: 'sr_0195f3a0000070008000000000000020',
              taskBlueprint: 'st_0195f3a0000070008000000000000200',
              dependsOn: [],
              causalSourceStepId: 'sr_0195f3a0000070008000000000000010',
            ),
          ],
        );

        expect(
          () => WorkflowCloner.cloneWorkflow(missingCausalDepWorkflow),
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('depends_on'),
            ),
          ),
        );
      },
    );
  });

  group('WorkflowCloner.cloneDeep - Causal Source Remapping & Validation', () {
    test(
      'successfully remaps causal_source_step_id and output_profiles to new 32-hex UUIDv7 step ID',
      () {
        final original = <String, Object?>{
          'id': 'wf_0195f3a0000070008000000000000001',
          'slug': 'wf_original',
          'name': 'Original Workflow',
          'steps': [
            <String, Object?>{
              'id': 'step_causal_1',
              'task_blueprint': 'bp_causal_1',
              'depends_on': <String>[],
              'input_mappings': <String, Object?>{},
            },
            <String, Object?>{
              'id': 'step_specialist_2',
              'task_blueprint': 'bp_specialist_2',
              'depends_on': <String>['step_causal_1'],
              'causal_source_step_id': 'step_causal_1',
              'input_mappings': <String, Object?>{
                'causal_graph': r'$steps.step_causal_1.outputs.graph',
              },
            },
          ],
          'output_profiles': <String, Object?>{
            'op_1': <String, Object?>{
              'binding': r'$results.step_causal_1.data',
            },
          },
        };

        final cloned = WorkflowCloner.cloneDeep(original);

        final newWfId = cloned['id'] as String;
        expect(newWfId, isNot(equals('wf_0195f3a0000070008000000000000001')));
        expect(converter.fromJson(newWfId), equals(newWfId));
        expect(cloned['slug'], equals('wf_original_copy'));

        final steps = cloned['steps'] as List<Object?>;
        expect(steps.length, equals(2));

        final clonedCausal = steps[0] as Map<String, Object?>;
        final clonedSpecialist = steps[1] as Map<String, Object?>;

        final newCausalId = clonedCausal['id'] as String;
        final newSpecialistId = clonedSpecialist['id'] as String;

        expect(newCausalId, isNot(equals('step_causal_1')));
        expect(newSpecialistId, isNot(equals('step_specialist_2')));
        expect(converter.fromJson(newCausalId), equals(newCausalId));
        expect(converter.fromJson(newSpecialistId), equals(newSpecialistId));

        expect(clonedSpecialist['depends_on'], equals([newCausalId]));
        expect(clonedSpecialist['causal_source_step_id'], equals(newCausalId));
        expect(
          (clonedSpecialist['input_mappings']
              as Map<String, Object?>)['causal_graph'],
          equals('\$steps.$newCausalId.outputs.graph'),
        );

        final profiles = cloned['output_profiles'] as Map<String, Object?>;
        final op1 = profiles['op_1'] as Map<String, Object?>;
        expect(op1['binding'], equals('\$results.$newCausalId.data'));
      },
    );

    test(
      'throws AppException when causal_source_step_id points to unmapped step',
      () {
        final original = <String, Object?>{
          'id': 'wf_original_123',
          'name': 'Original Workflow',
          'steps': [
            <String, Object?>{
              'id': 'step_specialist_2',
              'task_blueprint': 'bp_specialist_2',
              'depends_on': <String>['missing_causal_step'],
              'causal_source_step_id': 'missing_causal_step',
              'input_mappings': <String, Object?>{},
            },
          ],
        };

        expect(
          () => WorkflowCloner.cloneDeep(original),
          throwsA(
            isA<AppException>().having(
              (e) => e.extensions['error_code'],
              'error_code',
              equals('WORKFLOW_CLONE_FAILED'),
            ),
          ),
        );
      },
    );

    test(
      'throws AppException when causal_source_step_id is not in depends_on',
      () {
        final original = <String, Object?>{
          'id': 'wf_original_123',
          'name': 'Original Workflow',
          'steps': [
            <String, Object?>{
              'id': 'step_causal_1',
              'task_blueprint': 'bp_causal_1',
              'depends_on': <String>[],
              'input_mappings': <String, Object?>{},
            },
            <String, Object?>{
              'id': 'step_specialist_2',
              'task_blueprint': 'bp_specialist_2',
              'depends_on': <String>[],
              'causal_source_step_id': 'step_causal_1',
              'input_mappings': <String, Object?>{},
            },
          ],
        };

        expect(
          () => WorkflowCloner.cloneDeep(original),
          throwsA(
            isA<AppException>().having(
              (e) => e.extensions['error_code'],
              'error_code',
              equals('WORKFLOW_CLONE_FAILED'),
            ),
          ),
        );
      },
    );

    test(
      'Negative Boundary: throws AppException when step has empty ID or malformed step entry',
      () {
        final emptyStepIdPayload = <String, Object?>{
          'id': 'wf_original_123',
          'steps': [
            <String, Object?>{'id': '', 'task_blueprint': 'bp_1'},
          ],
        };

        expect(
          () => WorkflowCloner.cloneDeep(emptyStepIdPayload),
          throwsA(isA<AppException>()),
        );

        final nonMapStepPayload = <String, Object?>{
          'id': 'wf_original_123',
          'steps': ['invalid_step_entry'],
        };

        expect(
          () => WorkflowCloner.cloneDeep(nonMapStepPayload),
          throwsA(isA<AppException>()),
        );
      },
    );
  });
}
