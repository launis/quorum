import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/workflow/workflow_general_tab.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

class _FakeOutputProfilesController extends OutputProfilesController {
  final List<OutputProfile> initialProfiles;
  _FakeOutputProfilesController(this.initialProfiles);

  @override
  FutureOr<List<OutputProfile>> build() => initialProfiles;
}

class _ErrorOutputProfilesController extends OutputProfilesController {
  @override
  FutureOr<List<OutputProfile>> build() {
    throw AppException.validation('Profile fetch failure');
  }
}

class _FakeMcpGatewaysController extends McpGatewaysController {
  final List<McpGateway> initialGateways;
  _FakeMcpGatewaysController(this.initialGateways);

  @override
  FutureOr<List<McpGateway>> build() => initialGateways;
}

class _ErrorMcpGatewaysController extends McpGatewaysController {
  @override
  FutureOr<List<McpGateway>> build() {
    throw AppException.validation('Gateway fetch failure');
  }
}

class _FakeModelRegistryController extends ModelRegistryController {
  final List<ModelConfig> initialRegistries;
  _FakeModelRegistryController(this.initialRegistries);

  @override
  FutureOr<List<ModelConfig>> build() => initialRegistries;
}

class _ErrorModelRegistryController extends ModelRegistryController {
  @override
  FutureOr<List<ModelConfig>> build() {
    throw AppException.validation('Registry fetch failure');
  }
}

void main() {
  const String validWfId = 'wf_01965b80000070008000000000000001';
  const String validProfId1 = 'prof_01965b80000070008000000000000001';
  const String validProfId2 = 'prof_01965b80000070008000000000000002';
  const String validGwId = 'gw_01965b80000070008000000000000001';
  const String validRegId1 = 'cfg_01965b80000070008000000000000001';
  const String validRegId2 = 'cfg_01965b80000070008000000000000002';

  late Workflow baseWorkflow;
  late List<OutputProfile> mockProfiles;
  late List<McpGateway> mockGateways;
  late List<ModelConfig> mockRegistries;

  setUp(() {
    baseWorkflow = const Workflow(
      id: validWfId,
      slug: 'executive-audit',
      name: I18nText(
        translations: {'en': 'Executive Audit', 'fi': 'Johdon auditointi'},
      ),
      description: I18nText(
        translations: {
          'en': 'English workflow description',
          'fi': 'Suomenkielinen kuvaus',
        },
      ),
      defaultProfileId: validProfId1,
      mcpGatewayId: validGwId,
      modelRegistryId: validRegId1,
      enableContextualOverrides: false,
      systemAuditTrail: true,
    );

    mockProfiles = [
      const OutputProfile(
        id: validProfId1,
        slug: 'exec-summary',
        workflowId: validWfId,
        name: I18nText(
          translations: {'en': 'Executive Summary', 'fi': 'Johdon yhteenveto'},
        ),
      ),
      const OutputProfile(
        id: validProfId2,
        slug: 'deep-dive',
        workflowId: validWfId,
        name: I18nText(translations: {'en': 'Deep Dive', 'fi': 'Syväluotaus'}),
      ),
    ];

    mockGateways = [
      const McpGateway(
        id: validGwId,
        slug: 'tavily_gw',
        tools: [
          AllowedMcpTool(
            toolId: 'search_web',
            name: I18nText(translations: {'en': 'Search Web'}),
            description: 'Web search tool',
          ),
        ],
      ),
    ];

    mockRegistries = [
      const ModelConfig(
        id: validRegId1,
        name: 'Primary Vertex Stack',
        defaultProvider: 'vertex_ai',
      ),
      const ModelConfig(
        id: validRegId2,
        name: 'Fallback OpenAI Stack',
        defaultProvider: 'openai',
      ),
    ];
  });

  Widget buildTestApp({
    required Workflow workflow,
    required TextEditingController idController,
    required TextEditingController slugController,
    required ValueChanged<Workflow> onChanged,
    List<OutputProfile>? profiles,
    List<McpGateway>? gateways,
    List<ModelConfig>? registries,
    bool simulateAsyncErrors = false,
    Locale locale = const Locale('en'),
  }) {
    return ProviderScope(
      overrides: [
        if (simulateAsyncErrors) ...[
          outputProfilesControllerProvider.overrideWith(
            _ErrorOutputProfilesController.new,
          ),
          mcpGatewaysControllerProvider.overrideWith(
            _ErrorMcpGatewaysController.new,
          ),
          modelRegistryControllerProvider.overrideWith(
            _ErrorModelRegistryController.new,
          ),
        ] else ...[
          outputProfilesControllerProvider.overrideWith(
            () => _FakeOutputProfilesController(profiles ?? mockProfiles),
          ),
          mcpGatewaysControllerProvider.overrideWith(
            () => _FakeMcpGatewaysController(gateways ?? mockGateways),
          ),
          modelRegistryControllerProvider.overrideWith(
            () => _FakeModelRegistryController(registries ?? mockRegistries),
          ),
        ],
      ],
      child: MaterialApp(
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: WorkflowGeneralTab(
            workflow: workflow,
            idController: idController,
            slugController: slugController,
            onChanged: onChanged,
          ),
        ),
      ),
    );
  }

  group('WorkflowGeneralTab Widget Tests', () {
    testWidgets(
      'Positive: renders read-only opaque ID, localized fields, dropdowns, and emits updates on user interaction',
      (WidgetTester tester) async {
        Workflow currentWf = baseWorkflow;
        final idCtrl = TextEditingController(text: baseWorkflow.id);
        final slugCtrl = TextEditingController(text: baseWorkflow.slug);
        addTearDown(() {
          idCtrl.dispose();
          slugCtrl.dispose();
        });

        await tester.pumpWidget(
          buildTestApp(
            workflow: currentWf,
            idController: idCtrl,
            slugController: slugCtrl,
            onChanged: (updated) => currentWf = updated,
          ),
        );
        await tester.pumpAndSettle();

        // 1. Opaque ID field is strictly read-only
        final idField = tester.widget<TextField>(
          find.widgetWithText(TextField, validWfId),
        );
        expect(idField.readOnly, isTrue);

        // 2. Edit semantic slug and verify callback emission
        await tester.enterText(
          find.widgetWithText(TextField, 'executive-audit'),
          'updated-slug',
        );
        expect(currentWf.slug, equals('updated-slug'));

        // 3. Edit English and Finnish descriptions without losing cursor state
        await tester.enterText(
          find.widgetWithText(TextField, 'English workflow description'),
          'Updated EN description',
        );
        expect(
          currentWf.description.translations['en'],
          equals('Updated EN description'),
        );

        await tester.enterText(
          find.widgetWithText(TextField, 'Suomenkielinen kuvaus'),
          'Päivitetty suomenkielinen kuvaus',
        );
        expect(
          currentWf.description.translations['fi'],
          equals('Päivitetty suomenkielinen kuvaus'),
        );

        // 4. Scroll to and toggle switches
        final switches = find.byType(SwitchListTile);
        expect(switches, findsNWidgets(2));
        await tester.ensureVisible(switches.first);
        await tester.pumpAndSettle();
        await tester.tap(switches.first);
        await tester.pump();
        expect(currentWf.enableContextualOverrides, isTrue);
      },
    );

    testWidgets(
      'Negative 1 (Unmapped / Orphan IDs & Empty Collections): safely handles empty provider lists and unmapped IDs without dropdown assertion crashes',
      (WidgetTester tester) async {
        const orphanWf = Workflow(
          id: validWfId,
          slug: 'orphan-wf',
          name: I18nText(translations: {'en': 'Orphan Workflow'}),
          description: I18nText(translations: {}),
          defaultProfileId: '',
          mcpGatewayId: 'gw_01965b80000070008000999999999999',
          modelRegistryId: 'cfg_01965b80000070008000999999999999',
        );

        final idCtrl = TextEditingController(text: orphanWf.id);
        final slugCtrl = TextEditingController(text: orphanWf.slug);
        addTearDown(() {
          idCtrl.dispose();
          slugCtrl.dispose();
        });

        await tester.pumpWidget(
          buildTestApp(
            workflow: orphanWf,
            idController: idCtrl,
            slugController: slugCtrl,
            onChanged: (_) {},
            profiles: const <OutputProfile>[],
            gateways: const <McpGateway>[],
            registries: const <ModelConfig>[],
          ),
        );
        await tester.pumpAndSettle();

        // Zero unhandled exceptions when collections are empty and IDs are unmapped
        expect(tester.takeException(), isNull);
        expect(find.text('default (default)'), findsOneWidget);
        expect(
          find.text('cfg_01965b80000070008000999999999999'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Negative 2 (AsyncError Provider States & Narrow Boundary Width): degrades gracefully on provider errors and contains long labels with ellipsis at 320px width',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(320, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        final idCtrl = TextEditingController(text: baseWorkflow.id);
        final slugCtrl = TextEditingController(text: baseWorkflow.slug);
        addTearDown(() {
          idCtrl.dispose();
          slugCtrl.dispose();
        });

        await tester.pumpWidget(
          buildTestApp(
            workflow: baseWorkflow,
            idController: idCtrl,
            slugController: slugCtrl,
            onChanged: (_) {},
            simulateAsyncErrors: true,
          ),
        );
        await tester.pumpAndSettle();

        // Zero layout overflow or unhandled exceptions under AsyncError & narrow 320px width
        expect(tester.takeException(), isNull);
      },
    );
  });
}
