import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/mcp_tool_params_panel.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

void main() {
  group('McpToolParamsPanel Studio Schema-Driven Widget Tests', () {
    late List<McpGateway> mockGateways;

    setUp(() {
      mockGateways = <McpGateway>[
        const McpGateway(
          id: 'sys_1111222233334444',
          slug: 'exa_gateway',
          endpointUrl: 'https://mcp.exa.ai/mcp',
          transportType: McpTransportType.streamableHttp,
          authType: McpAuthType.none,
          tools: <AllowedMcpTool>[
            AllowedMcpTool(
              toolId: 'web_search_exa',
              capability: ToolCapability.search,
              name: I18nText(
                translations: <String, String>{
                  'en': 'Exa Web Search',
                  'fi': 'Exa-verkkohaku',
                },
              ),
              description: 'Search the web with Exa AI.',
              inputSchema: McpToolInputSchemaDto(
                properties: <String, McpToolSchemaPropertyDto>{
                  'query': McpToolSchemaPropertyDto(
                    type: JsonSchemaPropertyType.string,
                    description: 'Runtime search query.',
                  ),
                  'numResults': McpToolSchemaPropertyDto(
                    type: JsonSchemaPropertyType.integer,
                    description: 'Maximum results to return.',
                    defaultValue: 10,
                    minimum: 1,
                    maximum: 100,
                  ),
                },
                requiredFields: <String>['query'],
              ),
            ),
          ],
        ),
        const McpGateway(
          id: 'sys_5555666677778888',
          slug: 'tavily_gateway',
          endpointUrl: 'https://mcp.tavily.com/mcp',
          transportType: McpTransportType.streamableHttp,
          authType: McpAuthType.none,
          tools: <AllowedMcpTool>[
            AllowedMcpTool(
              toolId: 'mcp_tavily_search',
              capability: ToolCapability.search,
              name: I18nText(
                translations: <String, String>{
                  'en': 'Tavily Search',
                  'fi': 'Tavily-haku',
                },
              ),
              description: 'Factual web search via Tavily.',
              inputSchema: McpToolInputSchemaDto(
                properties: <String, McpToolSchemaPropertyDto>{
                  'query': McpToolSchemaPropertyDto(
                    type: JsonSchemaPropertyType.string,
                  ),
                  'search_depth': McpToolSchemaPropertyDto(
                    type: JsonSchemaPropertyType.string,
                    enumValues: <String>['basic', 'advanced'],
                    defaultValue: 'basic',
                    description: 'Depth of search.',
                  ),
                  'include_images': McpToolSchemaPropertyDto(
                    type: JsonSchemaPropertyType.boolean,
                    defaultValue: true,
                    description: 'Include images in response.',
                  ),
                },
                requiredFields: <String>['query'],
              ),
            ),
          ],
        ),
      ];
    });

    testWidgets(
      'mcp_tool_params_panel_renders_and_mutates_schema_controls (TC-STUDIO-UI-01)',
      (WidgetTester tester) async {
        Map<String, Map<String, Object?>> currentParams =
            <String, Map<String, Object?>>{};

        await tester.pumpWidget(
          MaterialApp(
            locale: const Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: StatefulBuilder(
              builder: (BuildContext context, StateSetter setState) {
                return Scaffold(
                  body: SingleChildScrollView(
                    child: McpToolParamsPanel(
                      allowedMcpTools: const <String>[
                        'exa_gateway__web_search_exa',
                        'tavily_gateway__mcp_tavily_search',
                      ],
                      mcpToolParams: currentParams,
                      mcpGateways: mockGateways,
                      onChanged: (Map<String, Map<String, Object?>> updated) {
                        setState(() {
                          currentParams = updated;
                        });
                      },
                    ),
                  ),
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('MCP Tool Parameter Overrides'), findsOneWidget);
        expect(find.text('Exa Web Search'), findsOneWidget);
        expect(find.text('Tavily Search'), findsOneWidget);
        // Primary runtime 'query' parameter must be filtered out
        expect(find.text('query'), findsNothing);

        // 1. Mutate integer parameter: numResults = 5
        final numFieldFinder = find.byKey(
          const ValueKey<String>(
            'mcp_param_num_exa_gateway__web_search_exa_numResults',
          ),
        );
        expect(numFieldFinder, findsOneWidget);
        await tester.enterText(numFieldFinder, '5');
        await tester.pumpAndSettle();

        expect(
          currentParams['exa_gateway__web_search_exa']?['numResults'],
          equals(5),
        );

        // 2. Mutate enum dropdown: search_depth = 'advanced'
        final enumDropdownFinder = find.byKey(
          const ValueKey<String>(
            'mcp_param_enum_tavily_gateway__mcp_tavily_search_search_depth_null',
          ),
        );
        expect(enumDropdownFinder, findsOneWidget);
        await tester.tap(enumDropdownFinder);
        await tester.pumpAndSettle();
        await tester.tap(find.text('advanced').last);
        await tester.pumpAndSettle();

        expect(
          currentParams['tavily_gateway__mcp_tavily_search']?['search_depth'],
          equals('advanced'),
        );

        // 3. Mutate boolean switch: include_images = false (default was true)
        final boolSwitchFinder = find.byKey(
          const ValueKey<String>(
            'mcp_param_bool_tavily_gateway__mcp_tavily_search_include_images',
          ),
        );
        expect(boolSwitchFinder, findsOneWidget);
        await tester.tap(boolSwitchFinder);
        await tester.pumpAndSettle();

        expect(
          currentParams['tavily_gateway__mcp_tavily_search']?['include_images'],
          isFalse,
        );

        // 4. Reset Exa tool parameters
        final resetBtnFinder = find.byKey(
          const ValueKey<String>('mcp_param_reset_exa_gateway__web_search_exa'),
        );
        expect(resetBtnFinder, findsOneWidget);
        await tester.tap(resetBtnFinder);
        await tester.pumpAndSettle();

        expect(
          currentParams.containsKey('exa_gateway__web_search_exa'),
          isFalse,
        );
        expect(
          currentParams['tavily_gateway__mcp_tavily_search']?['search_depth'],
          equals('advanced'),
        );
      },
    );

    testWidgets(
      'mcp_tool_params_panel_rejects_out_of_bounds_and_non_numeric (TC-STUDIO-UI-02)',
      (WidgetTester tester) async {
        Map<String, Map<String, Object?>> currentParams =
            <String, Map<String, Object?>>{};

        await tester.pumpWidget(
          MaterialApp(
            locale: const Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: StatefulBuilder(
              builder: (BuildContext context, StateSetter setState) {
                return Scaffold(
                  body: SingleChildScrollView(
                    child: McpToolParamsPanel(
                      allowedMcpTools: const <String>[
                        'exa_gateway__web_search_exa',
                      ],
                      mcpToolParams: currentParams,
                      mcpGateways: mockGateways,
                      onChanged: (Map<String, Map<String, Object?>> updated) {
                        setState(() {
                          currentParams = updated;
                        });
                      },
                    ),
                  ),
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        final numFieldFinder = find.byKey(
          const ValueKey<String>(
            'mcp_param_num_exa_gateway__web_search_exa_numResults',
          ),
        );

        // Non-numeric text is ignored without mutating currentParams
        await tester.enterText(numFieldFinder, 'abc');
        await tester.pumpAndSettle();
        expect(currentParams.isEmpty, isTrue);

        // Below minimum (minimum: 1) is rejected
        await tester.enterText(numFieldFinder, '-5');
        await tester.pumpAndSettle();
        expect(currentParams.isEmpty, isTrue);

        // Above maximum (maximum: 100) is rejected
        await tester.enterText(numFieldFinder, '250');
        await tester.pumpAndSettle();
        expect(currentParams.isEmpty, isTrue);

        // Valid value within bounds is accepted
        await tester.enterText(numFieldFinder, '15');
        await tester.pumpAndSettle();
        expect(
          currentParams['exa_gateway__web_search_exa']?['numResults'],
          equals(15),
        );

        // Clearing field removes the override key
        await tester.enterText(numFieldFinder, '');
        await tester.pumpAndSettle();
        expect(
          currentParams.containsKey('exa_gateway__web_search_exa'),
          isFalse,
        );
      },
    );

    testWidgets('mcp_tool_params_pruned_when_tool_deselected (TC-STUDIO-UI-03)', (
      WidgetTester tester,
    ) async {
      NodeStrategy stepPayload = const NodeStrategy.llm(
        id: 'stp_1111222233334444',
        slug: 'verify_step',
        name: I18nText(translations: <String, String>{'en': 'Verify Step'}),
        allowedMcpTools: <String>[
          'exa_gateway__web_search_exa',
          'tavily_gateway__mcp_tavily_search',
        ],
        mcpToolParams: <String, Map<String, Object?>>{
          'exa_gateway__web_search_exa': <String, Object?>{'numResults': 5},
          'tavily_gateway__mcp_tavily_search': <String, Object?>{
            'search_depth': 'advanced',
          },
        },
      );

      // Verify 1:1 snake_case JSON serialization parity with Python Step.mcp_tool_params
      final jsonMap = stepPayload.toJson();
      expect(
        jsonMap['mcp_tool_params'],
        equals(<String, Object?>{
          'exa_gateway__web_search_exa': <String, Object?>{'numResults': 5},
          'tavily_gateway__mcp_tavily_search': <String, Object?>{
            'search_depth': 'advanced',
          },
        }),
      );
      final roundtripped = NodeStrategy.fromJson(jsonMap);
      expect(roundtripped.mcpToolParams, equals(stepPayload.mcpToolParams));

      // Simulate deselecting exa_gateway__web_search_exa as performed in StepBuilderView
      const deselectedAlias = 'exa_gateway__web_search_exa';
      final nextAllowed = List<String>.from(stepPayload.allowedMcpTools)
        ..remove(deselectedAlias);
      final nextParams = <String, Map<String, Object?>>{
        for (final entry in stepPayload.mcpToolParams.entries)
          if (entry.key != deselectedAlias)
            entry.key: Map<String, Object?>.from(entry.value),
      };
      stepPayload = stepPayload.copyWith(
        allowedMcpTools: nextAllowed,
        mcpToolParams: nextParams,
      );

      expect(
        stepPayload.mcpToolParams.containsKey('exa_gateway__web_search_exa'),
        isFalse,
      );
      expect(
        stepPayload.mcpToolParams['tavily_gateway__mcp_tavily_search'],
        equals(<String, Object?>{'search_depth': 'advanced'}),
      );

      await tester.pumpWidget(
        MaterialApp(
          locale: const Locale('en'),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: SingleChildScrollView(
              child: McpToolParamsPanel(
                allowedMcpTools: stepPayload.allowedMcpTools,
                mcpToolParams: stepPayload.mcpToolParams,
                mcpGateways: mockGateways,
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Exa Web Search'), findsNothing);
      expect(find.text('Tavily Search'), findsOneWidget);
    });
  });
}
