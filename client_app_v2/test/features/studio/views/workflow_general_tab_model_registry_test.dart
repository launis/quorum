import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_general_tab.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_step_card.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Workflow createTestWorkflow({
    String modelRegistryId = 'mrg_0195f3a0000070008000bf23c2670ad5',
  }) {
    return Workflow(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: 'wf_0195f3a0000070008000000000000001',
      slug: 'test-workflow',
      name: const I18nText(translations: {'en': 'Test Workflow'}),
      description: const I18nText(translations: {'en': 'Test Description'}),
      modelRegistryId: modelRegistryId,
    );
  }

  Widget buildTestApp(
    Workflow workflow, {
    required void Function(Workflow) onChanged,
    Locale locale = const Locale('en'),
  }) {
    return ProviderScope(
      overrides: [
        modelRegistryControllerProvider.overrideWith(
          () => MockModelRegistryController(),
        ),
        outputProfilesControllerProvider.overrideWith(
          () => MockOutputProfilesController(),
        ),
        mcpGatewaysControllerProvider.overrideWith(
          () => MockMcpGatewaysController(),
        ),
      ],
      child: MaterialApp(
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: WorkflowGeneralTab(
            workflow: workflow,
            idController: TextEditingController(text: workflow.id),
            slugController: TextEditingController(text: workflow.slug),
            onChanged: onChanged,
          ),
        ),
      ),
    );
  }

  group('WorkflowGeneralTab Model Registry Selector Tests', () {
    testWidgets('renders Model Registry selector with stack name and provider', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1200, 2400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final workflow = createTestWorkflow(
        modelRegistryId: 'mrg_0195f3a0000070008000bf23c2670ad5',
      );

      await tester.pumpWidget(buildTestApp(workflow, onChanged: (_) {}));
      await tester.pumpAndSettle();

      // 1. Verify Label and Helper text
      expect(find.text('Model Registry'), findsOneWidget);
      expect(
        find.text(
          'Sovereign model stack binding physical LLM profiles to cognitive tiers',
        ),
        findsOneWidget,
      );

      // 2. Verify selected item text is rendered
      expect(
        find.text('Google Gemini Sovereign Stack (GOOGLE)'),
        findsOneWidget,
      );
    });

    testWidgets(
      'invokes onChanged with new modelRegistryId when another stack is selected',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 2400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() => tester.view.resetPhysicalSize());

        Workflow currentWorkflow = createTestWorkflow(
          modelRegistryId: 'mrg_0195f3a0000070008000bf23c2670ad5',
        );
        Workflow? updatedWorkflow;

        await tester.pumpWidget(
          buildTestApp(
            currentWorkflow,
            onChanged: (updated) {
              updatedWorkflow = updated;
            },
          ),
        );
        await tester.pumpAndSettle();

        // Open dropdown
        final dropdownFinder = find.byWidgetPredicate(
          (w) =>
              w is DropdownButtonFormField<String> &&
              w.decoration.labelText == 'Model Registry',
        );
        expect(dropdownFinder, findsOneWidget);
        await tester.ensureVisible(dropdownFinder);
        await tester.tap(dropdownFinder);
        await tester.pumpAndSettle();

        // Select OpenAI stack
        final openAiOption = find.text('OpenAI O-Series Stack (OPENAI)').last;
        await tester.tap(openAiOption);
        await tester.pumpAndSettle();

        expect(updatedWorkflow, isNotNull);
        expect(
          updatedWorkflow!.modelRegistryId,
          'mrg_0195f3a0000070008000bf23c2670ad6',
        );
      },
    );

    testWidgets(
      'handles unmapped modelRegistryId boundary condition by safely rendering unmapped ID as dropdown item',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 2400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() => tester.view.resetPhysicalSize());

        // Boundary: unmapped / foreign registry ID not present in registered stacks
        const unmappedId = 'mrg_0195f3a0000070008000999999999999';
        final workflow = createTestWorkflow(modelRegistryId: unmappedId);

        await tester.pumpWidget(buildTestApp(workflow, onChanged: (_) {}));
        await tester.pumpAndSettle();

        // Must display the unmapped ID safely without throwing
        expect(find.text(unmappedId), findsOneWidget);
      },
    );

    testWidgets(
      'handles empty model registry list boundary condition gracefully without throwing exceptions',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 2400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() => tester.view.resetPhysicalSize());

        const testId = 'mrg_0195f3a0000070008000bf23c2670ad5';
        final workflow = createTestWorkflow(modelRegistryId: testId);

        // Build with empty registry controller override
        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              modelRegistryControllerProvider.overrideWith(
                () => MockEmptyModelRegistryController(),
              ),
              outputProfilesControllerProvider.overrideWith(
                () => MockOutputProfilesController(),
              ),
              mcpGatewaysControllerProvider.overrideWith(
                () => MockMcpGatewaysController(),
              ),
            ],
            child: MaterialApp(
              locale: const Locale('en'),
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(
                body: WorkflowGeneralTab(
                  workflow: workflow,
                  idController: TextEditingController(text: workflow.id),
                  slugController: TextEditingController(text: workflow.slug),
                  onChanged: (_) {},
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Must render testId without crashing
        expect(find.text(testId), findsOneWidget);
      },
    );

    testWidgets(
      'enforces Opaque Stripe ID immutability by keeping ID field strictly read-only',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 2400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() => tester.view.resetPhysicalSize());

        final workflow = createTestWorkflow();

        await tester.pumpWidget(buildTestApp(workflow, onChanged: (_) {}));
        await tester.pumpAndSettle();

        final idFieldFinder = find.byWidgetPredicate(
          (w) =>
              w is TextField &&
              w.decoration?.labelText ==
                  'Opaque Workflow ID (System Generated)',
        );
        expect(idFieldFinder, findsOneWidget);

        final idTextField = tester.widget<TextField>(idFieldFinder);
        expect(idTextField.readOnly, isTrue);
      },
    );

    testWidgets(
      'verifies isExpanded is true on all DropdownButtonFormField widgets to prevent horizontal layout overflow',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 2400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() => tester.view.resetPhysicalSize());

        final workflow = createTestWorkflow();

        await tester.pumpWidget(buildTestApp(workflow, onChanged: (_) {}));
        await tester.pumpAndSettle();

        final dropdowns = tester.widgetList<Widget>(
          find.byWidgetPredicate(
            (w) => w.runtimeType.toString().startsWith('DropdownButton<'),
          ),
        );
        expect(dropdowns.length, greaterThanOrEqualTo(3));

        for (final dropdown in dropdowns) {
          expect(
            (dropdown as dynamic).isExpanded,
            isTrue,
            reason:
                'Dropdown must have isExpanded: true to prevent horizontal overflow',
          );
        }
      },
    );

    testWidgets(
      'WorkflowStepCard renders read-only summary badges for bound namespaced MCP tools',
      (WidgetTester tester) async {
        const stepRule = StepRule(
          id: 'sr_1234567890abcdef',
          taskBlueprint: 'sp_1234567890abcdef',
        );
        const blueprint = NodeStrategy.llm(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'sp_1234567890abcdef',
          slug: 'web_research_specialist',
          name: I18nText(translations: {'en': 'Web Research Specialist'}),
          allowedMcpTools: ['default_mcp_gateway__mcp_tavily_search'],
        );
        const gateway = McpGateway(
          id: 'mcp_0195f3a00000700080008172bda70c86',
          organizationId: 'org_0195f3a0000070008000000000000001',
          name: 'Default MCP Gateway',
          slug: 'default_mcp_gateway',
          tools: [
            AllowedMcpTool(
              toolId: 'mcp_tavily_search',
              name: I18nText(translations: {'en': 'Tavily Search'}),
              description: 'Search web',
            ),
          ],
        );

        await tester.pumpWidget(
          MaterialApp(
            locale: const Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: Builder(
                builder: (context) => WorkflowStepCard(
                  index: 0,
                  stepDef: stepRule,
                  blueprints: const [blueprint],
                  allSteps: const [stepRule],
                  mcpGateways: const [gateway],
                  globalWorkflowInputs: const [],
                  l10n: AppLocalizations.of(context)!,
                  onChanged: (_) {},
                  onDelete: () {},
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Bound MCP Tools:'), findsOneWidget);
        expect(
          find.text('default_mcp_gateway__mcp_tavily_search'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'negative ISTQB partition: WorkflowStepCard omits MCP tool badges when blueprint has empty allowedMcpTools',
      (WidgetTester tester) async {
        const stepRule = StepRule(
          id: 'sr_1234567890abcdef',
          taskBlueprint: 'sp_1234567890abcdef',
        );
        const blueprint = NodeStrategy.llm(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'sp_1234567890abcdef',
          slug: 'no_tools_specialist',
          name: I18nText(translations: {'en': 'No Tools Specialist'}),
          allowedMcpTools: [],
        );

        await tester.pumpWidget(
          MaterialApp(
            locale: const Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: Builder(
                builder: (context) => WorkflowStepCard(
                  index: 0,
                  stepDef: stepRule,
                  blueprints: const [blueprint],
                  allSteps: const [stepRule],
                  mcpGateways: const [],
                  globalWorkflowInputs: const [],
                  l10n: AppLocalizations.of(context)!,
                  onChanged: (_) {},
                  onDelete: () {},
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Bound MCP Tools:'), findsNothing);
      },
    );
  });
}

class MockEmptyModelRegistryController extends AsyncNotifier<List<ModelConfig>>
    implements ModelRegistryController {
  @override
  Future<List<ModelConfig>> build() async => const [];
  @override
  Future<void> refresh() async {}
  @override
  Future<ModelConfig> saveConfig(String id, ModelConfig config) async => config;
  @override
  Future<void> deleteConfig(String id) async {}
  @override
  Future<ModelConfig> createSystemConfigDraft() async => const ModelConfig(
    id: 'mrg_0195f3a0000070008000000000000091',
    slug: 'draft',
  );
  @override
  Future<ModelConfig> cloneConfig(String id) async => const ModelConfig(
    id: 'mrg_0195f3a0000070008000000000000092',
    slug: 'cloned',
  );
}

class MockModelRegistryController extends AsyncNotifier<List<ModelConfig>>
    implements ModelRegistryController {
  @override
  Future<List<ModelConfig>> build() async {
    return const [
      ModelConfig(
        id: 'mrg_0195f3a0000070008000bf23c2670ad5',
        slug: 'google-stack',
        name: 'Google Gemini Sovereign Stack',
        defaultProvider: 'google',
        tierDefinitions: {},
      ),
      ModelConfig(
        id: 'mrg_0195f3a0000070008000bf23c2670ad6',
        slug: 'openai-stack',
        name: 'OpenAI O-Series Stack',
        defaultProvider: 'openai',
        tierDefinitions: {},
      ),
    ];
  }

  @override
  Future<void> refresh() async {}
  @override
  Future<ModelConfig> saveConfig(String id, ModelConfig config) async => config;
  @override
  Future<void> deleteConfig(String id) async {}
  @override
  Future<ModelConfig> createSystemConfigDraft() async => const ModelConfig(
    id: 'mrg_0195f3a0000070008000000000000091',
    slug: 'draft',
  );
  @override
  Future<ModelConfig> cloneConfig(String id) async => const ModelConfig(
    id: 'mrg_0195f3a0000070008000000000000092',
    slug: 'cloned',
  );
}

class MockOutputProfilesController extends AsyncNotifier<List<OutputProfile>>
    implements OutputProfilesController {
  @override
  Future<List<OutputProfile>> build() async => const [];
  @override
  Future<void> refresh() async {}
  @override
  Future<OutputProfile> saveProfile(String id, OutputProfile payload) async =>
      payload;
  @override
  Future<void> deleteProfile(String id) async {}
  @override
  Future<OutputProfile> cloneProfile(String id) async => const OutputProfile(
    organizationId: 'org_0195f3a0000070008000000000000001',
    id: 'cloned',
    workflowId: 'wor_123',
    slug: 'cloned',
    name: I18nText(translations: {'en': 'Cloned'}),
  );
  @override
  Future<OutputProfile> createOutputProfileDraft() async => const OutputProfile(
    organizationId: 'org_0195f3a0000070008000000000000001',
    id: 'draft',
    workflowId: 'wor_123',
    slug: 'draft',
    name: I18nText(translations: {'en': 'Draft'}),
  );
}

class MockMcpGatewaysController extends AsyncNotifier<List<McpGateway>>
    implements McpGatewaysController {
  @override
  Future<List<McpGateway>> build() async => const [];
  @override
  Future<void> refresh() async {}
  @override
  Future<McpGateway> saveGateway(String id, McpGateway data) async => data;
  @override
  Future<void> deleteGateway(String id) async {}
  @override
  Future<McpGateway> cloneGateway(String id) async => const McpGateway(
    id: 'mcp_0195f3a0000070008000000000000093',
    organizationId: 'org_0195f3a0000070008000000000000001',
    name: 'Cloned Gateway',
    slug: 'cloned',
  );
  @override
  Future<McpGateway> createMcpGatewayDraft() async => const McpGateway(
    id: 'mcp_0195f3a0000070008000000000000094',
    organizationId: 'org_0195f3a0000070008000000000000001',
    name: 'Draft Gateway',
    slug: 'draft',
  );
  @override
  Future<McpGateway> discoverTools(String id) async => McpGateway(
    id: id,
    organizationId: 'org_0195f3a0000070008000000000000001',
    name: 'Discovered Gateway',
    slug: 'discovered',
  );
}
