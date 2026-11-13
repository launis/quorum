import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/prompt_block_simulation.dart';
import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late StudioClient client;
  late MockDio mockDio;
  late MockLoggerService mockLogger;

  setUp(() {
    mockDio = MockDio();
    mockLogger = MockLoggerService();
    client = StudioClient(mockDio, mockLogger);
  });

  group('StudioClient Unit & ISTQB Boundary Tests', () {
    const testBlockId = 'blk_0195f3a0000070008000000000000001';
    const testWorkflowId = 'wf_0195f3a0000070008000000000000002';
    const testStepId = 'stp_0195f3a0000070008000000000000003';
    const testRegistryId = 'mrg_0195f3a0000070008000000000000004';
    const testGatewayId = 'mcp_0195f3a0000070008000000000000005';
    const testProfileId = 'op_0195f3a0000070008000000000000006';

    final validBlockJson = <String, Object?>{
      'category_id': 'system_rule',
      'id': testBlockId,
      'slug': 'test_rule',
      'label': <String, Object?>{
        'translations': <String, Object?>{'en': 'Test Rule'},
      },
      'description': <String, Object?>{
        'translations': <String, Object?>{'en': 'Test Description'},
      },
      'is_evaluative': false,
      'type': 'instruction',
      'allow_decimals': false,
      'output_extensions': <String>[],
      'is_lightweight_protocol': false,
      'instruction_text': 'Follow rule',
    };

    final validWorkflowJson = <String, Object?>{
      'id': testWorkflowId,
      'slug': 'test_workflow',
      'name': <String, Object?>{
        'translations': <String, Object?>{'en': 'Test Workflow'},
      },
      'description': <String, Object?>{
        'translations': <String, Object?>{'en': 'Test Workflow Description'},
      },
      'model_registry_id': testRegistryId,
    };

    final validStepJson = <String, Object?>{
      'type': 'llm',
      'id': testStepId,
      'slug': 'test_step',
      'name': <String, Object?>{
        'translations': <String, Object?>{'en': 'Test Step'},
      },
    };

    final validConfigJson = <String, Object?>{
      'id': testRegistryId,
      'name': 'Default Model Registry',
      'default_provider': 'ai_studio',
      'tier_definitions': <String, Object?>{},
    };

    final validGatewayJson = <String, Object?>{
      'id': testGatewayId,
      'organization_id': 'org_0195f3a0000070008000000000000001',
      'name': 'Default MCP Gateway',
      'slug': 'default_mcp_gateway',
      'endpoint_url': 'https://mcp.example.com/v1',
      'transport_type': 'streamable_http',
      'auth_type': 'none',
      'timeout_seconds': 30,
      'tools': <Object?>[],
    };

    final validProfileJson = <String, Object?>{
      'id': testProfileId,
      'slug': 'test_profile',
      'workflow_id': testWorkflowId,
      'name': <String, Object?>{
        'translations': <String, Object?>{'en': 'Test Profile'},
      },
    };

    test(
      'Positive 1: PromptBlock CRUD, clone, draft, and simulate operations succeed with typed payloads',
      () async {
        when(
          () => mockDio.get<List<Object?>>('studio/prompt-blocks'),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: 'studio/prompt-blocks'),
            data: <Object?>[validBlockJson],
            statusCode: 200,
          ),
        );

        final blocks = await client.getPromptBlocks();
        expect(blocks.length, equals(1));
        expect(blocks.first.id, equals(testBlockId));
        expect(blocks.first, isA<SystemRulePromptBlock>());

        when(
          () => mockDio.get<Map<String, Object?>>(
            'studio/prompt-blocks/$testBlockId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/prompt-blocks/$testBlockId',
            ),
            data: validBlockJson,
            statusCode: 200,
          ),
        );

        final singleBlock = await client.getPromptBlock(testBlockId);
        expect(singleBlock.id, equals(testBlockId));

        const blockModel = PromptBlock.systemRule(
          id: testBlockId,
          slug: 'test_rule',
          label: I18nText(translations: {'en': 'Test Rule'}),
          description: I18nText(translations: {'en': 'Test Description'}),
        );

        when(
          () => mockDio.put<Map<String, Object?>>(
            'studio/prompt-blocks/$testBlockId',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/prompt-blocks/$testBlockId',
            ),
            data: validBlockJson,
            statusCode: 200,
          ),
        );

        final savedBlock = await client.savePromptBlock(
          testBlockId,
          blockModel,
        );
        expect(savedBlock.id, equals(testBlockId));

        when(
          () => mockDio.post<Map<String, Object?>>(
            'studio/prompt-blocks/simulate',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/prompt-blocks/simulate',
            ),
            data: <String, Object?>{
              'valid': true,
              'rendered_prompt': 'Rendered test prompt',
              'errors': <String>[],
              'prompt_context': null,
            },
            statusCode: 200,
          ),
        );

        final simResult = await client.simulatePromptBlock(
          const PromptBlockSimulationRequest(block: blockModel),
        );
        expect(simResult.valid, isTrue);

        when(
          () => mockDio.post<Map<String, Object?>>(
            'studio/prompt-blocks/$testBlockId/clone',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/prompt-blocks/$testBlockId/clone',
            ),
            data: validBlockJson,
            statusCode: 200,
          ),
        );

        final clonedBlock = await client.clonePromptBlock(testBlockId);
        expect(clonedBlock.id, equals(testBlockId));

        when(
          () => mockDio.post<Map<String, Object?>>(
            'studio/prompt-blocks/',
            queryParameters: any(named: 'queryParameters'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: 'studio/prompt-blocks/'),
            data: validBlockJson,
            statusCode: 201,
          ),
        );

        final draftBlock = await client.createPromptBlockDraft(
          categoryId: 'system_rule',
        );
        expect(draftBlock.id, equals(testBlockId));

        when(
          () => mockDio.delete<void>('studio/prompt-blocks/$testBlockId'),
        ).thenAnswer(
          (_) async => Response<void>(
            requestOptions: RequestOptions(
              path: 'studio/prompt-blocks/$testBlockId',
            ),
            statusCode: 204,
          ),
        );

        await client.deletePromptBlock(testBlockId);
        verify(
          () => mockDio.delete<void>('studio/prompt-blocks/$testBlockId'),
        ).called(1);
      },
    );

    test(
      'Positive 2: Workflow CRUD, simulate, clone, draft, and available-extensions strip output_profiles on save',
      () async {
        when(() => mockDio.get<List<Object?>>('studio/workflows')).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: 'studio/workflows'),
            data: <Object?>[validWorkflowJson],
            statusCode: 200,
          ),
        );

        final workflows = await client.getWorkflows();
        expect(workflows.single.id, equals(testWorkflowId));

        when(
          () => mockDio.get<Map<String, Object?>>(
            'studio/workflows/$testWorkflowId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$testWorkflowId',
            ),
            data: validWorkflowJson,
            statusCode: 200,
          ),
        );

        final wf = await client.getWorkflow(testWorkflowId);
        expect(wf.id, equals(testWorkflowId));

        when(
          () => mockDio.put<Map<String, Object?>>(
            'studio/workflows/$testWorkflowId',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$testWorkflowId',
            ),
            data: validWorkflowJson,
            statusCode: 200,
          ),
        );

        final savedWf = await client.saveWorkflow(testWorkflowId, wf);
        expect(savedWf.id, equals(testWorkflowId));
        final capturedPayload =
            verify(
                  () => mockDio.put<Map<String, Object?>>(
                    'studio/workflows/$testWorkflowId',
                    data: captureAny(named: 'data'),
                  ),
                ).captured.single
                as Map<String, Object?>;
        expect(capturedPayload.containsKey('output_profiles'), isFalse);

        when(
          () => mockDio.post<Map<String, Object?>>(
            'studio/workflows/simulate',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: 'studio/workflows/simulate'),
            data: <String, Object?>{
              'valid': true,
              'errors': <String>[],
              'step_status': <String, String>{},
              'execution_order': <String>[testStepId],
              'trace': <String, Object?>{},
            },
            statusCode: 200,
          ),
        );

        final wfSim = await client.simulateWorkflow(wf);
        expect(wfSim.valid, isTrue);
        expect(wfSim.executionOrder, equals(<String>[testStepId]));

        when(
          () => mockDio.get<Map<String, Object?>>(
            'studio/workflows/$testWorkflowId/available-extensions',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$testWorkflowId/available-extensions',
            ),
            data: <String, Object?>{
              'available_extensions': <Object?>['strengths', 'risks'],
            },
            statusCode: 200,
          ),
        );

        final exts = await client.getWorkflowAvailableExtensions(
          testWorkflowId,
        );
        expect(exts, equals(<String>['strengths', 'risks']));

        when(
          () => mockDio.post<Map<String, Object?>>(
            'studio/workflows/$testWorkflowId/clone',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$testWorkflowId/clone',
            ),
            data: validWorkflowJson,
            statusCode: 200,
          ),
        );

        expect((await client.cloneWorkflow(testWorkflowId)).id, testWorkflowId);

        when(
          () => mockDio.post<Map<String, Object?>>('studio/workflows/'),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: 'studio/workflows/'),
            data: validWorkflowJson,
            statusCode: 201,
          ),
        );

        expect((await client.createWorkflowDraft()).id, testWorkflowId);

        when(
          () => mockDio.delete<void>('studio/workflows/$testWorkflowId'),
        ).thenAnswer(
          (_) async => Response<void>(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$testWorkflowId',
            ),
            statusCode: 204,
          ),
        );

        await client.deleteWorkflow(testWorkflowId);
        verify(
          () => mockDio.delete<void>('studio/workflows/$testWorkflowId'),
        ).called(1);
      },
    );

    test(
      'Positive 3: Steps, Model Registry, MCP Gateways, and Output Profiles endpoints return strongly typed models',
      () async {
        // Steps
        when(
          () => mockDio.get<List<Object?>>(
            'studio/steps',
            queryParameters: any(named: 'queryParameters'),
          ),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: 'studio/steps'),
            data: <Object?>[validStepJson],
            statusCode: 200,
          ),
        );
        final steps = await client.getSteps(scope: StepFilterScope.all);
        expect(steps.single.id, equals(testStepId));

        when(
          () => mockDio.get<Map<String, Object?>>('studio/steps/$testStepId'),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: 'studio/steps/$testStepId'),
            data: validStepJson,
            statusCode: 200,
          ),
        );
        final step = await client.getStep(testStepId);
        expect(step.id, equals(testStepId));

        when(
          () => mockDio.put<Map<String, Object?>>(
            'studio/steps/$testStepId',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: 'studio/steps/$testStepId'),
            data: validStepJson,
            statusCode: 200,
          ),
        );
        expect((await client.saveStep(testStepId, step)).id, testStepId);

        when(
          () => mockDio.post<Map<String, Object?>>(
            'studio/steps/simulate',
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: 'studio/steps/simulate'),
            data: <String, Object?>{
              'valid': true,
              'errors': <String>[],
              'rendered_prompt': 'Step prompt',
            },
            statusCode: 200,
          ),
        );
        final stepSim = await client.simulateStep(
          StepSimulationRequest(step: step),
        );
        expect(stepSim.valid, isTrue);

        // Model Registry
        when(
          () => mockDio.get<List<Object?>>(
            'studio/model-registry/available-models',
            queryParameters: any(named: 'queryParameters'),
          ),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/model-registry/available-models',
            ),
            data: <Object?>['gemini-2.5-pro'],
            statusCode: 200,
          ),
        );
        expect(
          await client.getAvailableModels(
            platform: 'vertex_ai',
            location: 'europe-west1',
          ),
          equals(<String>['gemini-2.5-pro']),
        );

        when(
          () => mockDio.get<List<Object?>>('studio/model-registry/locations'),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/model-registry/locations',
            ),
            data: <Object?>[
              <String, Object?>{
                'id': 'europe-west1',
                'label': 'Belgium',
                'description': 'EU West 1',
              },
            ],
            statusCode: 200,
          ),
        );
        final locations = await client.getSupportedLocations();
        expect(locations.single.id, equals('europe-west1'));

        when(
          () => mockDio.get<List<Object?>>('studio/model-registry/platforms'),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/model-registry/platforms',
            ),
            data: <Object?>[
              <String, Object?>{
                'id': 'vertex_ai',
                'label': 'Google Vertex AI',
                'has_regions': true,
              },
            ],
            statusCode: 200,
          ),
        );
        final platforms = await client.getSupportedPlatforms();
        expect(platforms.single.id, equals('vertex_ai'));

        when(
          () => mockDio.get<Map<String, Object?>>(
            'studio/model-registry/$testRegistryId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/model-registry/$testRegistryId',
            ),
            data: validConfigJson,
            statusCode: 200,
          ),
        );
        final sysConfig = await client.getSystemConfig(testRegistryId);
        expect(sysConfig.id, equals(testRegistryId));

        // MCP Gateways
        when(
          () => mockDio.get<Map<String, Object?>>(
            'studio/mcp-gateways/$testGatewayId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/mcp-gateways/$testGatewayId',
            ),
            data: validGatewayJson,
            statusCode: 200,
          ),
        );
        final gateway = await client.getMcpGateway(testGatewayId);
        expect(gateway.id, equals(testGatewayId));

        when(
          () => mockDio.post<Map<String, Object?>>(
            'studio/mcp-gateways/$testGatewayId/discover',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/mcp-gateways/$testGatewayId/discover',
            ),
            data: validGatewayJson,
            statusCode: 200,
          ),
        );
        expect(
          (await client.discoverMcpGatewayTools(testGatewayId)).id,
          equals(testGatewayId),
        );

        // Output Profiles
        when(
          () => mockDio.get<Map<String, Object?>>(
            'output-profiles/$testProfileId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'output-profiles/$testProfileId',
            ),
            data: validProfileJson,
            statusCode: 200,
          ),
        );
        final profile = await client.getOutputProfile(testProfileId);
        expect(profile.id, equals(testProfileId));
      },
    );

    test(
      'Negative Test 1 (BVA): fails fast with AppException before HTTP call on invalid 32-hex Opaque Stripe IDs (empty, 16-hex, 31-hex min-1, 33-hex max+1)',
      () async {
        const invalidIds = <String>[
          '',
          'blk_1234567890abcdef', // legacy 16-hex
          'blk_0195f3a000007000800000000000000', // 31 hex chars (min-1)
          'blk_0195f3a00000700080000000000000012', // 33 hex chars (max+1)
          'b_0195f3a0000070008000000000000001', // 1-char prefix (min-1)
        ];

        for (final invalidId in invalidIds) {
          expect(
            () => client.getPromptBlock(invalidId),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                equals('VALIDATION_FAILED'),
              ),
            ),
          );
          expect(
            () => client.deletePromptBlock(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getWorkflow(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getWorkflowAvailableExtensions(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(() => client.getStep(invalidId), throwsA(isA<AppException>()));
          expect(
            () => client.getSystemConfig(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getMcpGateway(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.discoverMcpGatewayTools(invalidId),
            throwsA(isA<AppException>()),
          );
          expect(
            () => client.getOutputProfile(invalidId),
            throwsA(isA<AppException>()),
          );
        }

        // Also test simulatePromptBlock with empty/invalid block ID
        const emptyBlock = PromptBlock.systemRule(
          id: '',
          slug: 'empty_test',
          label: I18nText(translations: {'en': 'Empty'}),
          description: I18nText(translations: {'en': 'Empty'}),
        );
        expect(
          () => client.simulatePromptBlock(
            const PromptBlockSimulationRequest(block: emptyBlock),
          ),
          throwsA(isA<AppException>()),
        );

        verify(
          () => mockLogger.error('StudioClient', any(), any(), any()),
        ).called(invalidIds.length * 9 + 1);
        verifyNever(() => mockDio.get<Map<String, Object?>>(any()));
        verifyNever(
          () => mockDio.post<Map<String, Object?>>(
            any(),
            data: any(named: 'data'),
          ),
        );
        verifyNever(() => mockDio.delete<void>(any()));
      },
    );

    test(
      'Negative Test 2: fails fast with CheckedFromJsonException or AppException on unrecognized keys, null payload, or non-Map list elements',
      () async {
        // 1. Unrecognized key in PromptBlock list item
        final invalidBlockJson = <String, Object?>{
          ...validBlockJson,
          'legacy_field': 'forbidden_value',
        };
        when(
          () => mockDio.get<List<Object?>>('studio/prompt-blocks'),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: 'studio/prompt-blocks'),
            data: <Object?>[invalidBlockJson],
            statusCode: 200,
          ),
        );

        expect(
          () => client.getPromptBlocks(),
          throwsA(
            anyOf(isA<FormatException>(), isA<CheckedFromJsonException>()),
          ),
        );

        // 2. Null response payload in getWorkflow
        when(
          () => mockDio.get<Map<String, Object?>>(
            'studio/workflows/$testWorkflowId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$testWorkflowId',
            ),
            data: null,
            statusCode: 200,
          ),
        );

        expect(
          () => client.getWorkflow(testWorkflowId),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );

        // 3. Non-map element in getWorkflows list
        when(() => mockDio.get<List<Object?>>('studio/workflows')).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: 'studio/workflows'),
            data: <Object?>['not_a_map'],
            statusCode: 200,
          ),
        );

        expect(
          () => client.getWorkflows(),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );

        // 4. Malformed available_extensions payload
        when(
          () => mockDio.get<Map<String, Object?>>(
            'studio/workflows/$testWorkflowId/available-extensions',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: 'studio/workflows/$testWorkflowId/available-extensions',
            ),
            data: <String, Object?>{'available_extensions': 'invalid_string'},
            statusCode: 200,
          ),
        );

        expect(
          () => client.getWorkflowAvailableExtensions(testWorkflowId),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );
      },
    );

    test(
      'Negative Test 3: propagates DioException on network or server errors',
      () async {
        when(
          () => mockDio.get<List<Object?>>('studio/prompt-blocks'),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: 'studio/prompt-blocks'),
            type: DioExceptionType.connectionTimeout,
          ),
        );

        expect(() => client.getPromptBlocks(), throwsA(isA<DioException>()));
      },
    );
  });
}
