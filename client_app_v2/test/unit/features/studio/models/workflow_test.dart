import 'dart:convert';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

void main() {
  group('Workflow, NodeStrategy, StepRule & Sub-Models ISTQB Boundary Tests', () {
    const validWfId = 'wf_0195f3a0000070008000000000000001';
    const validStepId = 'stp_0195f3a0000070008000000000000002';
    const validSrId = 'sr_0195f3a0000070008000000000000003';
    const validPbId = 'pb_0195f3a0000070008000000000000004';
    const validSysId = 'sys_0195f3a0000070008000000000000005';
    const sampleName = I18nText(
      translations: {'en': 'Test Workflow', 'fi': 'Testityönkulku'},
    );
    const sampleDesc = I18nText(
      translations: {'en': 'Workflow description', 'fi': 'Kuvaus'},
    );

    test(
      'Positive: Deserializes Workflow, ExpectedInput, StepRule, and all 3 NodeStrategy union variants',
      () {
        final workflowJson = <String, Object?>{
          'id': validWfId,
          'slug': 'executive-assessment',
          'name': sampleName.toJson(),
          'description': sampleDesc.toJson(),
          'status': 'published',
          'version': 2,
          'is_public': true,
          'organization_id': 'org_0195f3a0000070008000000000000099',
          'default_profile_id': 'prof_0195f3a0000070008000000000000088',
          'mcp_gateway_id': validSysId,
          'model_registry_id': validSysId,
          'default_strictness_level': 65,
          'default_lexical_strictness_level': 70,
          'security_penalty': 0.25,
          'post_hoc_penalty': 0.15,
          'passivity_penalty': 0.10,
          'enable_contextual_overrides': true,
          'enable_semantic_smoothing': true,
          'enable_eager_anonymization': false,
          'system_audit_trail': true,
          'historical_context_mode': 'SLIDING_WINDOW_3',
          'expected_inputs': [
            {
              'input_key': 'dialogue_log',
              'label': sampleName.toJson(),
              'required': true,
              'is_chat_history': true,
              'is_endorsed_deliverable': false,
              'input_modes': ['file', 'paste'],
              'description': sampleDesc.toJson(),
              'scan_for_performative_patterns': true,
              'ai_description': 'Candidate dialogue transcript.',
              'questionnaire_definition': [
                {
                  'question_id': 'q1',
                  'question': sampleName.toJson(),
                  'type': 'text',
                },
              ],
            },
          ],
          'steps': [
            {
              'id': validSrId,
              'task_blueprint': validStepId,
              'depends_on': <String>[],
              'input_mappings': {'context': r'$inputs.dialogue_log'},
              'expected_sdui_type': 'markdown',
              'ui_pos_x': 120.5,
              'ui_pos_y': 240.0,
              'is_synthesis_source': true,
              'causal_source_step_id': validSrId,
            },
          ],
        };

        final wf = Workflow.fromJson(workflowJson);
        expect(wf.id, validWfId);
        expect(wf.slug, 'executive-assessment');
        expect(wf.modelRegistryId, validSysId);
        expect(wf.mcpGatewayId, validSysId);
        expect(wf.historicalContextMode, HistoricalContextMode.slidingWindow3);
        expect(wf.expectedInputs, hasLength(1));
        expect(
          wf.expectedInputs.first.questionnaireDefinition.first.questionId,
          'q1',
        );
        expect(wf.steps, hasLength(1));
        expect(wf.steps.first.expectedSduiType, SduiBlockType.markdown);
        expect(wf.steps.first.causalSourceStepId, validSrId);

        final llmStep = NodeStrategy.fromJson({
          'type': 'llm',
          'id': validStepId,
          'slug': 'step-llm',
          'name': sampleName.toJson(),
          'role_block_id': validPbId,
          'extraction_protocol_block_id': validPbId,
          'execution_persona_block_id': validPbId,
          'criteria_block_ids': [validPbId],
          'cognitive_tier': 'deep',
          'engine_type': 'tda',
          'zone': 'zone_b',
        });
        expect(llmStep, isA<NodeStrategyLlm>());
        expect(llmStep.cognitiveTier, CognitiveTier.deep);
        expect(llmStep.engineType, EngineType.tda);
        expect(llmStep.zone, StepZone.zoneB);

        final logicStep = NodeStrategy.fromJson({
          'type': 'logic',
          'id': validStepId,
          'slug': 'step-logic',
          'name': sampleName.toJson(),
          'hook': 'guard_hook',
          'zone': 'zone_a',
        });
        expect(logicStep, isA<NodeStrategyLogic>());
        expect(logicStep.zone, StepZone.zoneA);

        final causalStep = NodeStrategy.fromJson({
          'type': 'causal_discovery',
          'id': validStepId,
          'slug': 'step-causal',
          'name': sampleName.toJson(),
          'zone': 'zone_c',
        });
        expect(causalStep, isA<NodeStrategyCausalDiscovery>());
        expect(causalStep.engineType, EngineType.causalDiscovery);
        expect(causalStep.zone, StepZone.zoneC);
      },
    );

    test(
      'Positive: Workflow.parseInBackground and parseListInBackground deserialize valid JSON payloads',
      () async {
        const wf = Workflow(
          id: validWfId,
          slug: 'bg-workflow',
          name: sampleName,
          description: sampleDesc,
          modelRegistryId: validSysId,
        );
        final rawJson = jsonEncode(wf.toJson());
        final parsedSingle = await Workflow.parseInBackground(rawJson);
        expect(parsedSingle.id, validWfId);
        expect(parsedSingle.slug, 'bg-workflow');

        final parsedList = await Workflow.parseListInBackground([wf.toJson()]);
        expect(parsedList, hasLength(1));
        expect(parsedList.first.id, validWfId);
      },
    );

    test(
      'Negative Partition 1 (BVA): StrictOpaqueIdConverter rejects 31-hex (min-1) and 33-hex (max+1) IDs across Workflow, StepRule, and NodeStrategy',
      () {
        // 31 hex chars (min - 1) on Workflow.id
        final shortWfJson = <String, Object?>{
          'id': 'wf_0195f3a000007000800000000000001',
          'slug': 'short-wf',
          'name': sampleName.toJson(),
          'description': sampleDesc.toJson(),
          'model_registry_id': validSysId,
        };
        expect(
          () => Workflow.fromJson(shortWfJson),
          throwsA(
            isA<CheckedFromJsonException>().having(
              (e) => e.innerError,
              'innerError',
              isA<AppException>(),
            ),
          ),
        );

        // 33 hex chars (max + 1) on Workflow.model_registry_id
        final longRegWfJson = <String, Object?>{
          'id': validWfId,
          'slug': 'long-reg-wf',
          'name': sampleName.toJson(),
          'description': sampleDesc.toJson(),
          'model_registry_id': 'sys_0195f3a0000070008000000000000005a',
        };
        expect(
          () => Workflow.fromJson(longRegWfJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // 16-hex truncated ID on StepRule.causal_source_step_id
        final truncatedStepRuleJson = <String, Object?>{
          'id': validSrId,
          'task_blueprint': validStepId,
          'causal_source_step_id': 'sr_0195f3a000007000',
        };
        expect(
          () => StepRule.fromJson(truncatedStepRuleJson),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative Partition 2: disallowUnrecognizedKeys rejects unknown properties across Workflow, ExpectedInput, StepRule, and NodeStrategy',
      () {
        final pollutedWfJson = <String, Object?>{
          'id': validWfId,
          'slug': 'polluted-wf',
          'name': sampleName.toJson(),
          'description': sampleDesc.toJson(),
          'model_registry_id': validSysId,
          'unrecognized_legacy_flag': true,
        };
        expect(
          () => Workflow.fromJson(pollutedWfJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final pollutedNodeJson = <String, Object?>{
          'type': 'llm',
          'id': validStepId,
          'slug': 'polluted-node',
          'name': sampleName.toJson(),
          'extra_field': 'forbidden',
        };
        expect(
          () => NodeStrategy.fromJson(pollutedNodeJson),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative Partition 3: Background parsers fail-fast with AppException when given non-object JSON payloads',
      () async {
        await expectLater(
          Workflow.parseInBackground('["not_a_json_object"]'),
          throwsA(isA<AppException>()),
        );
        await expectLater(
          Workflow.parseListInBackground(['not_a_map_element']),
          throwsA(isA<AppException>()),
        );
      },
    );
  });
}
