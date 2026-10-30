import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/causal_discovery_dto.dart';

void main() {
  group('CausalNodeDto Parity & Validation', () {
    test('successfully serializes and deserializes CausalNodeDto', () {
      final json = {
        'node_id': 'claim_node_01',
        'claim': 'Process execution failed due to memory starvation.',
        'source_quotes': ['Out of memory at step 4'],
        'paragraph_ref': 'p_01',
        'status': 'FAILED',
        'blame_parent_ids': ['parent_01'],
        'dependent_child_ids': ['child_01', 'child_02'],
        'tda_score': 15.5,
        'tda_level_key': 'high_severity',
        'source_input_key': 'technical_report',
      };

      final node = CausalNodeDto.fromJson(json);
      expect(node.nodeId, 'claim_node_01');
      expect(node.claim, contains('memory starvation'));
      expect(node.status, ExecutionStatus.failed);
      expect(node.blameParentIds, ['parent_01']);
      expect(node.dependentChildIds, ['child_01', 'child_02']);
      expect(node.tdaScore, 15.5);
      expect(node.sourceInputKey, 'technical_report');

      final serialized = node.toJson();
      expect(serialized['node_id'], 'claim_node_01');
      expect(serialized['status'], 'FAILED');
      expect(serialized['blame_parent_ids'], ['parent_01']);
      expect(serialized['source_input_key'], 'technical_report');
    });

    test('rejects unrecognized keys fail-fast (negative)', () {
      final json = {
        'node_id': 'claim_node_01',
        'claim': 'Test claim',
        'status': 'PASSED',
        'unexpected_forbidden_key': 'fail_fast',
      };

      expect(
        () => CausalNodeDto.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });

  group('CausalEdgeDto Parity & Validation', () {
    test('successfully serializes and deserializes CausalEdgeDto', () {
      final json = {
        'source_id': 'node_a',
        'target_id': 'node_b',
        'reasoning': 'Direct prerequisite causal influence.',
      };

      final edge = CausalEdgeDto.fromJson(json);
      expect(edge.sourceId, 'node_a');
      expect(edge.targetId, 'node_b');
      expect(edge.reasoning, contains('prerequisite'));

      final serialized = edge.toJson();
      expect(serialized['source_id'], 'node_a');
      expect(serialized['target_id'], 'node_b');
    });

    test('rejects missing required fields fail-fast (negative)', () {
      final json = {
        'source_id': 'node_a',
        // missing target_id and reasoning
      };

      expect(
        () => CausalEdgeDto.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });

  group('CausalRootCauseDiagnosisDto Parity & Validation', () {
    test('successfully serializes and deserializes diagnosis DTO', () {
      final json = {
        'failing_node_id': 'fail_01',
        'root_cause_parent_id': 'root_01',
        'paragraph_ref': 'p_03',
        'explanation': 'Root cause originates from invalid configuration.',
        'penalty_points': 12.5,
        'root_cause_type': 'warrant_grounding_failure',
      };

      final dto = CausalRootCauseDiagnosisDto.fromJson(json);
      expect(dto.failingNodeId, 'fail_01');
      expect(dto.rootCauseParentId, 'root_01');
      expect(dto.penaltyPoints, 12.5);
      expect(dto.rootCauseType, CausalRootCauseType.warrantGroundingFailure);

      final serialized = dto.toJson();
      expect(serialized['penalty_points'], 12.5);
      expect(serialized['root_cause_type'], 'warrant_grounding_failure');
    });
  });

  group('AntiFluffAuditDto Parity & Validation', () {
    test(
      'successfully serializes and deserializes anti-fluff DTO with topological ratios',
      () {
        final json = {
          'isolated_concept_count': 3,
          'cycle_detected': false,
          'unsupported_claims_count': 1,
          'logical_cohesion_score': 88.5,
          'largest_component_ratio': 0.85,
          'branch_convergence_ratio': 0.25,
          'steering_coupling_ratio': 0.60,
          'detected_hollow_terms': ['synergy', 'paradigm'],
        };

        final dto = AntiFluffAuditDto.fromJson(json);
        expect(dto.isolatedConceptCount, 3);
        expect(dto.cycleDetected, isFalse);
        expect(dto.unsupportedClaimsCount, 1);
        expect(dto.logicalCohesionScore, 88.5);
        expect(dto.largestComponentRatio, 0.85);
        expect(dto.branchConvergenceRatio, 0.25);
        expect(dto.steeringCouplingRatio, 0.60);
        expect(dto.detectedHollowTerms, ['synergy', 'paradigm']);

        final serialized = dto.toJson();
        expect(serialized['logical_cohesion_score'], 88.5);
        expect(serialized['largest_component_ratio'], 0.85);
        expect(serialized['branch_convergence_ratio'], 0.25);
        expect(serialized['steering_coupling_ratio'], 0.60);
      },
    );

    test('applies topological ratio defaults when omitted in JSON', () {
      final json = {
        'isolated_concept_count': 0,
        'cycle_detected': false,
        'unsupported_claims_count': 0,
        'logical_cohesion_score': 100.0,
      };

      final dto = AntiFluffAuditDto.fromJson(json);
      expect(dto.largestComponentRatio, 1.0);
      expect(dto.branchConvergenceRatio, 0.0);
      expect(dto.steeringCouplingRatio, 0.0);
      expect(dto.detectedHollowTerms, isEmpty);
    });

    test(
      'rejects unrecognized keys on AntiFluffAuditDto fail-fast (negative)',
      () {
        final json = {
          'isolated_concept_count': 1,
          'cycle_detected': false,
          'unsupported_claims_count': 0,
          'logical_cohesion_score': 90.0,
          'unexpected_audit_field': true,
        };

        expect(
          () => AntiFluffAuditDto.fromJson(json),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test('rejects non-numeric topological ratio type fail-fast (negative)', () {
      final json = {
        'isolated_concept_count': 1,
        'cycle_detected': false,
        'unsupported_claims_count': 0,
        'logical_cohesion_score': 90.0,
        'largest_component_ratio': 'invalid_ratio',
      };

      expect(
        () => AntiFluffAuditDto.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });

  group('PrescriptiveRemediationDto Parity & Validation', () {
    test(
      'successfully serializes and deserializes prescriptive remediation DTO',
      () {
        final json = {
          'target_node_id': 'node_fix_01',
          'required_action': 'Refactor database query to eliminate N+1.',
          'unlocks_node_ids': ['node_downstream_01'],
          'potential_score_impact': 18.0,
        };

        final dto = PrescriptiveRemediationDto.fromJson(json);
        expect(dto.targetNodeId, 'node_fix_01');
        expect(dto.potentialScoreImpact, 18.0);
        expect(dto.unlocksNodeIds, ['node_downstream_01']);
      },
    );
  });

  group('FairScoringBreakdownDto Parity & Validation', () {
    test(
      'successfully serializes and deserializes fair scoring breakdown DTO',
      () {
        final json = {
          'independent_error_count': 2,
          'cascading_fault_count': 5,
          'raw_penalty_points': 50.0,
          'deduplicated_penalty_points': 20.0,
          'dampened_savings_points': 30.0,
        };

        final dto = FairScoringBreakdownDto.fromJson(json);
        expect(dto.independentErrorCount, 2);
        expect(dto.cascadingFaultCount, 5);
        expect(dto.dampenedSavingsPoints, 30.0);

        final serialized = dto.toJson();
        expect(serialized['raw_penalty_points'], 50.0);
      },
    );
  });

  group('CounterfactualSimulationResultDto Parity & Validation', () {
    test(
      'successfully serializes and deserializes CounterfactualSimulationResultDto',
      () {
        final json = {
          'retracted_root_id': 'nod_0195f3a0000070008000000000000001',
          'collapsed_node_ids': [
            'nod_0195f3a0000070008000000000000001',
            'nod_0195f3a0000070008000000000000002',
          ],
          'surviving_node_ids': ['nod_0195f3a0000070008000000000000003'],
          'collapse_ratio': 0.6667,
          'max_cascade_depth': 2,
        };

        final dto = CounterfactualSimulationResultDto.fromJson(json);
        expect(dto.retractedRootId, 'nod_0195f3a0000070008000000000000001');
        expect(dto.collapsedNodeIds, [
          'nod_0195f3a0000070008000000000000001',
          'nod_0195f3a0000070008000000000000002',
        ]);
        expect(dto.survivingNodeIds, ['nod_0195f3a0000070008000000000000003']);
        expect(dto.collapseRatio, 0.6667);
        expect(dto.maxCascadeDepth, 2);

        final serialized = dto.toJson();
        expect(
          serialized['retracted_root_id'],
          'nod_0195f3a0000070008000000000000001',
        );
        expect(serialized['collapsed_node_ids'], [
          'nod_0195f3a0000070008000000000000001',
          'nod_0195f3a0000070008000000000000002',
        ]);
        expect(serialized['surviving_node_ids'], [
          'nod_0195f3a0000070008000000000000003',
        ]);
        expect(serialized['collapse_ratio'], 0.6667);
        expect(serialized['max_cascade_depth'], 2);
      },
    );

    test('applies defaults when optional fields are omitted', () {
      final json = {
        'retracted_root_id': 'nod_0195f3a0000070008000000000000001',
      };

      final dto = CounterfactualSimulationResultDto.fromJson(json);
      expect(dto.retractedRootId, 'nod_0195f3a0000070008000000000000001');
      expect(dto.collapsedNodeIds, isEmpty);
      expect(dto.survivingNodeIds, isEmpty);
      expect(dto.collapseRatio, 0.0);
      expect(dto.maxCascadeDepth, 0);
    });

    test('rejects missing required retracted_root_id fail-fast (negative)', () {
      final json = <String, dynamic>{
        'collapse_ratio': 0.5,
        'max_cascade_depth': 1,
      };

      expect(
        () => CounterfactualSimulationResultDto.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test(
      'rejects unrecognized keys on CounterfactualSimulationResultDto fail-fast (negative)',
      () {
        final json = {
          'retracted_root_id': 'nod_0195f3a0000070008000000000000001',
          'unknown_simulation_key': 123,
        };

        expect(
          () => CounterfactualSimulationResultDto.fromJson(json),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
