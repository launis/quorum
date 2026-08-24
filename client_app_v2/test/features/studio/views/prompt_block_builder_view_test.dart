import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/features/studio/views/prompt_block_builder_view.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/logging/logger_service.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

class TestPromptBlockForm extends PromptBlockForm {
  final PromptBlock initialBlock;
  final Future<void> Function(PromptBlock saved)? onSave;

  TestPromptBlockForm(this.initialBlock, {this.onSave});

  @override
  FutureOr<PromptBlock> build(String configId) {
    return initialBlock;
  }

  @override
  Future<void> submit(PromptBlock block) async {
    state = const AsyncLoading();
    if (onSave != null) {
      await onSave!(block);
    }
    state = AsyncData(block);
  }
}

class MockPromptBlocksController extends PromptBlocksController {
  final Future<Map<String, dynamic>> Function(
    PromptBlock payload,
    Map<String, dynamic> mockInputs,
  )?
  onSimulate;
  final Future<void> Function(String id)? onDelete;

  MockPromptBlocksController({this.onSimulate, this.onDelete});

  @override
  FutureOr<List<PromptBlock>> build() async => [];

  @override
  Future<Map<String, dynamic>> simulatePromptBlock(
    PromptBlock payload,
    Map<String, dynamic> mockInputs,
  ) async {
    if (onSimulate != null) {
      return onSimulate!(payload, mockInputs);
    }
    return {'rendered_prompt': '<system_rule>Test Simulation</system_rule>'};
  }

  @override
  Future<void> deletePromptBlock(String id) async {
    if (onDelete != null) {
      await onDelete!(id);
    }
  }
}

void main() {
  setUpAll(() {
    TestWidgetsFlutterBinding.ensureInitialized();
  });

  Widget createTestWidget({
    required PromptBlock block,
    PromptBlocksController? controller,
    Future<void> Function(PromptBlock)? onSave,
  }) {
    final mockStudioClient = MockStudioClient();
    final mockLogger = MockLoggerService();

    return ProviderScope(
      overrides: [
        studioClientProvider.overrideWithValue(mockStudioClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
        promptBlockFormProvider(
          block.id,
        ).overrideWith(() => TestPromptBlockForm(block, onSave: onSave)),
        promptBlocksControllerProvider.overrideWith(
          () => controller ?? MockPromptBlocksController(),
        ),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: PromptBlockBuilderView(id: block.id),
      ),
    );
  }

  group('PromptBlockBuilderView Zero-XML Form Tests', () {
    testWidgets(
      'SystemRulePromptBlock renders instructionText field and updates state',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const block = PromptBlock.systemRule(
          id: 'blk_test_sysrule',
          slug: 'test_rule',
          label: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'System Rule A'},
          ),
          description: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Description A'},
          ),
          instructionText: 'Strict instruction without XML',
        );

        await tester.pumpWidget(createTestWidget(block: block));
        await tester.pumpAndSettle();

        expect(find.text('System Instruction Text'), findsOneWidget);
        expect(find.text('Strict instruction without XML'), findsOneWidget);

        // Edit text
        await tester.enterText(
          find.widgetWithText(TextFormField, 'Strict instruction without XML'),
          'Updated rule content',
        );
        await tester.pumpAndSettle();

        expect(find.text('Updated rule content'), findsOneWidget);
      },
    );

    testWidgets(
      'ExecutionPersonaPromptBlock renders roleEnforcement and toneDirectives with add/remove',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const block = PromptBlock.executionPersona(
          id: 'blk_test_persona',
          slug: 'test_persona',
          label: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Persona Executive'},
          ),
          description: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Executive Persona Desc'},
          ),
          roleEnforcement: 'You are a Senior Strategic Advisor.',
          toneDirectives: ['Authoritative', 'Direct'],
        );

        await tester.pumpWidget(createTestWidget(block: block));
        await tester.pumpAndSettle();

        expect(find.text('Role Enforcement Directive'), findsOneWidget);
        expect(
          find.text('You are a Senior Strategic Advisor.'),
          findsOneWidget,
        );
        expect(find.text('Tone Directives'), findsOneWidget);
        expect(find.text('Authoritative'), findsOneWidget);
        expect(find.text('Direct'), findsOneWidget);

        // Add tone directive
        final addBtn = find.text('Add Tone Directive');
        await tester.ensureVisible(addBtn);
        await tester.pumpAndSettle();
        await tester.tap(addBtn);
        await tester.pumpAndSettle();

        expect(find.text('Tone Directive 3'), findsOneWidget);

        // Remove first tone directive
        final deleteButtons = find.byIcon(Icons.delete);
        await tester.ensureVisible(deleteButtons.first);
        await tester.pumpAndSettle();
        await tester.tap(deleteButtons.first);
        await tester.pumpAndSettle();

        expect(find.text('Authoritative'), findsNothing);
        expect(find.text('Direct'), findsOneWidget);
      },
    );

    testWidgets(
      'AgentRolePromptBlock renders roleEnforcement and toneDirectives',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const block = PromptBlock.agentRole(
          id: 'blk_test_agent_role',
          slug: 'agent_role',
          label: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Agent Role'},
          ),
          description: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Agent Role Desc'},
          ),
          roleEnforcement: 'You are an Audit Agent.',
          toneDirectives: ['Surgical'],
        );

        await tester.pumpWidget(createTestWidget(block: block));
        await tester.pumpAndSettle();

        expect(find.text('Role Enforcement Directive'), findsOneWidget);
        expect(find.text('You are an Audit Agent.'), findsOneWidget);
        expect(find.text('Surgical'), findsOneWidget);
      },
    );

    testWidgets('ProtocolPromptBlock renders protocolInstructions', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      const block = PromptBlock.protocol(
        id: 'blk_test_protocol',
        slug: 'protocol_test',
        label: I18nText(
          defaultLocale: 'en',
          translations: {'en': 'Protocol Block'},
        ),
        description: I18nText(
          defaultLocale: 'en',
          translations: {'en': 'Protocol Desc'},
        ),
        protocolInstructions: 'Step 1: Extract concepts. Step 2: Validate.',
      );

      await tester.pumpWidget(createTestWidget(block: block));
      await tester.pumpAndSettle();

      expect(find.text('Protocol Execution Instructions'), findsOneWidget);
      expect(
        find.text('Step 1: Extract concepts. Step 2: Validate.'),
        findsOneWidget,
      );
    });

    testWidgets(
      'RuntimeVariablesPromptBlock and TaskDefinitionPromptBlock render instructionText',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const block = PromptBlock.runtimeVariables(
          id: 'blk_test_vars',
          slug: 'runtime_vars',
          label: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Runtime Variables'},
          ),
          description: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Vars Desc'},
          ),
          instructionText: 'Variables instruction text',
        );

        await tester.pumpWidget(createTestWidget(block: block));
        await tester.pumpAndSettle();

        expect(find.text('System Instruction Text'), findsOneWidget);
        expect(find.text('Variables instruction text'), findsOneWidget);
      },
    );

    testWidgets('MatrixPromptBlock renders notice card and BARS scales card', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      const block = PromptBlock.matrix(
        id: 'blk_test_matrix',
        slug: 'matrix_test',
        label: I18nText(
          defaultLocale: 'en',
          translations: {'en': 'Matrix Block'},
        ),
        description: I18nText(
          defaultLocale: 'en',
          translations: {'en': 'Matrix Desc'},
        ),
        scales: [
          MatrixScale(
            score: 1,
            aiLabel: '1',
            name: I18nText(
              defaultLocale: 'en',
              translations: {'en': 'Grade 1'},
            ),
            claims: [],
          ),
        ],
      );

      await tester.pumpWidget(createTestWidget(block: block));
      await tester.pumpAndSettle();

      expect(
        find.text(
          'Evaluation matrix guidelines and criteria are configured in the BARS Matrix scales below.',
        ),
        findsOneWidget,
      );
      expect(find.text('BARS Scales / Score Grades'), findsOneWidget);
    });

    testWidgets(
      'Compiled prompt preview dialog opens and copy-to-clipboard works',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        String? clipboardText;
        tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
          SystemChannels.platform,
          (MethodCall methodCall) async {
            if (methodCall.method == 'Clipboard.setData') {
              clipboardText =
                  (methodCall.arguments as Map<dynamic, dynamic>)['text']
                      as String?;
              return null;
            }
            return null;
          },
        );

        const block = PromptBlock.systemRule(
          id: 'blk_test_preview',
          slug: 'test_preview',
          label: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'System Rule Preview'},
          ),
          description: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Description Preview'},
          ),
          instructionText: 'Compiled prompt instructions',
        );

        final controller = MockPromptBlocksController(
          onSimulate: (payload, mockInputs) async {
            return {
              'rendered_prompt':
                  '<system_rule>\nCompiled prompt instructions\n</system_rule>',
            };
          },
        );

        await tester.pumpWidget(
          createTestWidget(block: block, controller: controller),
        );
        await tester.pumpAndSettle();

        // Tap the simulate bug report icon
        await tester.tap(find.byIcon(Icons.bug_report));
        await tester.pumpAndSettle();

        // Modal should be open
        expect(find.text('Live Compiled Prompt Preview'), findsOneWidget);
        expect(
          find.text(
            '<system_rule>\nCompiled prompt instructions\n</system_rule>',
          ),
          findsOneWidget,
        );
        expect(find.text('Copy to Clipboard'), findsOneWidget);

        // Tap copy button
        await tester.tap(find.text('Copy to Clipboard'));
        await tester.pumpAndSettle();

        expect(
          clipboardText,
          '<system_rule>\nCompiled prompt instructions\n</system_rule>',
        );
        expect(
          find.text('Compiled prompt copied to clipboard!'),
          findsOneWidget,
        );
      },
    );

    testWidgets('Validation gate prevents save when English label is empty', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      const block = PromptBlock.systemRule(
        id: 'blk_test_empty_en',
        slug: 'test_empty',
        label: I18nText(defaultLocale: 'en', translations: {'en': ''}),
        description: I18nText(
          defaultLocale: 'en',
          translations: {'en': 'Desc'},
        ),
        instructionText: 'Test Instruction',
      );

      bool saveCalled = false;
      await tester.pumpWidget(
        createTestWidget(
          block: block,
          onSave: (saved) async {
            saveCalled = true;
          },
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Save'));
      await tester.pumpAndSettle();

      expect(saveCalled, isFalse);
      expect(
        find.text('English Label is required (English-Only Mandate).'),
        findsOneWidget,
      );
    });
  });
}
