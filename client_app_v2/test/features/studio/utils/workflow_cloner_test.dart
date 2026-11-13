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
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: wfId,
          slug: 'exec_coaching_v2',
          name: sampleTitle,
          description: sampleDesc,
          version: 3,
          modelRegistryId: mrId,
          defaultProfileId: opId,
          outputProfiles: {
            opId: OutputProfile(
              organizationId: 'org_0195f3a0000070008000000000000001',
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
          organizationId: 'org_0195f3a0000070008000000000000001',
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
          organizationId: 'org_0195f3a0000070008000000000000001',
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
          organizationId: 'org_0195f3a0000070008000000000000001',
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
}
