import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/utils/workflow_cloner.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('WorkflowCloner - Causal Source Remapping & Validation', () {
    test('successfully remaps causal_source_step_id to new step ID', () {
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
            'depends_on': <String>['step_causal_1'],
            'causal_source_step_id': 'step_causal_1',
            'input_mappings': <String, Object?>{
              'causal_graph': r'$steps.step_causal_1.outputs.graph',
            },
          },
        ],
      };

      final cloned = WorkflowCloner.cloneDeep(original);

      expect(cloned['id'], isNot(equals('wf_original_123')));
      final steps = cloned['steps'] as List<dynamic>;
      expect(steps.length, equals(2));

      final clonedCausal = steps[0] as Map<String, Object?>;
      final clonedSpecialist = steps[1] as Map<String, Object?>;

      final newCausalId = clonedCausal['id'] as String;
      final newSpecialistId = clonedSpecialist['id'] as String;

      expect(newCausalId, isNot(equals('step_causal_1')));
      expect(newSpecialistId, isNot(equals('step_specialist_2')));

      expect(clonedSpecialist['depends_on'], equals([newCausalId]));
      expect(clonedSpecialist['causal_source_step_id'], equals(newCausalId));
      expect(
        (clonedSpecialist['input_mappings']
            as Map<String, Object?>)['causal_graph'],
        equals('\$steps.$newCausalId.outputs.graph'),
      );
    });

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
  });
}
