import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_general_tab.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Workflow createTestWorkflow({
    String modelRegistryId = 'sys_e26807f3bfa3454d',
  }) {
    return Workflow(
      id: 'wor_1234567890abcdef',
      slug: 'test-workflow',
      name: const I18nText(translations: {'en': 'Test Workflow'}),
      description: const I18nText(translations: {'en': 'Test Description'}),
      modelRegistryId: modelRegistryId,
    );
  }

  Widget buildTestApp(
    Workflow workflow, {
    required Function(Workflow) onChanged,
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
        modelRegistryId: 'sys_e26807f3bfa3454d',
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
          modelRegistryId: 'sys_e26807f3bfa3454d',
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
        expect(updatedWorkflow!.modelRegistryId, 'sys_6f8b1c4a2e0d49f1');
      },
    );

    testWidgets(
      'handles unmapped modelRegistryId boundary condition by safely rendering unmapped ID as dropdown item',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 2400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() => tester.view.resetPhysicalSize());

        // Boundary: unmapped / foreign registry ID not present in registered stacks
        const unmappedId = 'sys_custom_foreign_99999999';
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

        const testId = 'sys_e26807f3bfa3454d';
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
  Future<ModelConfig> createSystemConfigDraft() async =>
      const ModelConfig(id: 'draft', slug: 'draft', type: 'model_registry');
  @override
  Future<ModelConfig> cloneConfig(String id) async =>
      const ModelConfig(id: 'cloned', slug: 'cloned', type: 'model_registry');
}

class MockModelRegistryController extends AsyncNotifier<List<ModelConfig>>
    implements ModelRegistryController {
  @override
  Future<List<ModelConfig>> build() async {
    return const [
      ModelConfig(
        id: 'sys_e26807f3bfa3454d',
        slug: 'google-stack',
        type: 'model_registry',
        name: 'Google Gemini Sovereign Stack',
        defaultProvider: 'google',
        tierDefinitions: {},
      ),
      ModelConfig(
        id: 'sys_6f8b1c4a2e0d49f1',
        slug: 'openai-stack',
        type: 'model_registry',
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
  Future<ModelConfig> createSystemConfigDraft() async =>
      const ModelConfig(id: 'draft', slug: 'draft', type: 'model_registry');
  @override
  Future<ModelConfig> cloneConfig(String id) async =>
      const ModelConfig(id: 'cloned', slug: 'cloned', type: 'model_registry');
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
    id: 'cloned',
    workflowId: 'wor_123',
    slug: 'cloned',
    name: I18nText(translations: {'en': 'Cloned'}),
  );
  @override
  Future<OutputProfile> createOutputProfileDraft() async => const OutputProfile(
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
  Future<McpGateway> saveGateway(
    String id,
    McpGateway data,
  ) async => data;
  @override
  Future<void> deleteGateway(String id) async {}
  @override
  Future<McpGateway> cloneGateway(String id) async => const McpGateway(
    id: 'gw_cloned',
    slug: 'cloned',
  );
  @override
  Future<McpGateway> createMcpGatewayDraft() async => const McpGateway(
    id: 'gw_draft',
    slug: 'draft',
  );
}
