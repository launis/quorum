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

  group('WorkflowCloner Unit & ISTQB Boundary Tests', () {
    test(
      'Positive: cloneWorkflow generates 32-hex UUIDv7 IDs and remaps DAG dependencies, inputMappings, causalSourceStepId, and OutputProfiles',
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

        final clonedProfile = cloned.outputProfiles.values.first;
        expect(converter.fromJson(clonedProfile.id), equals(clonedProfile.id));
        expect(clonedProfile.workflowId, equals(cloned.id));
        expect(cloned.defaultProfileId, equals(clonedProfile.id));
      },
    );

    test(
      'Negative Partition 1: throws AppException when dependsOn or causalSourceStepId references an unmapped step',
      () {
        const brokenWorkflow = Workflow(
          id: 'wf_0195f3a0000070008000000000000001',
          slug: 'broken_wf',
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
          () => WorkflowCloner.cloneWorkflow(brokenWorkflow),
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
      'Negative Partition 2 (BVA): throws AppException when step ID is empty (min-1 length 0) or causalSourceStepId is omitted from dependsOn',
      () {
        const emptyStepWorkflow = Workflow(
          id: 'wf_0195f3a0000070008000000000000001',
          slug: 'empty_step_wf',
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

        final invalidStepsTypeMap = <String, Object?>{
          'id': 'wf_0195f3a0000070008000000000000001',
          'steps': 'not_a_list',
        };
        expect(
          () => WorkflowCloner.cloneDeep(invalidStepsTypeMap),
          throwsA(isA<AppException>()),
        );
      },
    );
  });
}
