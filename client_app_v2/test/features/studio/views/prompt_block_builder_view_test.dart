import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/features/studio/views/prompt_block_builder_view.dart';
import 'package:client_app/features/studio/views/widgets/prompt_preview_dialog.dart';
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
    Map<String, dynamic> mockInputs, {
    int? targetScaleScore,
    String? targetLocale,
    String? contextText,
  }) async {
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
    Locale? locale,
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
        locale: locale,
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
          label: I18nText(translations: {'en': 'System Rule A'}),
          description: I18nText(translations: {'en': 'Description A'}),
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
          label: I18nText(translations: {'en': 'Persona Executive'}),
          description: I18nText(translations: {'en': 'Executive Persona Desc'}),
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
          label: I18nText(translations: {'en': 'Agent Role'}),
          description: I18nText(translations: {'en': 'Agent Role Desc'}),
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
        label: I18nText(translations: {'en': 'Protocol Block'}),
        description: I18nText(translations: {'en': 'Protocol Desc'}),
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
          label: I18nText(translations: {'en': 'Runtime Variables'}),
          description: I18nText(translations: {'en': 'Vars Desc'}),
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
        label: I18nText(translations: {'en': 'Matrix Block'}),
        description: I18nText(translations: {'en': 'Matrix Desc'}),
        scales: [
          MatrixScale(
            score: 1,
            aiLabel: '1',
            name: I18nText(translations: {'en': 'Grade 1'}),
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
      'Compiled prompt preview opens shared PromptPreviewDialog',
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
          label: I18nText(translations: {'en': 'System Rule Preview'}),
          description: I18nText(translations: {'en': 'Description Preview'}),
          instructionText: 'Compiled prompt instructions',
        );

        final controller = MockPromptBlocksController(
          onSimulate: (payload, mockInputs) async {
            return {
              'rendered_prompt':
                  '<system_rule>\nCompiled prompt instructions\n</system_rule>',
              'prompt_context': {
                'static_messages': [
                  {
                    'role': 'system',
                    'content': 'Compiled prompt instructions',
                  },
                ],
                'dynamic_messages': <dynamic>[],
              },
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

        // Modal should be open with shared PromptPreviewDialog
        expect(find.byType(PromptPreviewDialog), findsOneWidget);
        expect(find.text('Compiled Prompt Preview'), findsOneWidget);
        expect(
          find.descendant(
            of: find.byType(PromptPreviewDialog),
            matching: find.textContaining('Compiled prompt instructions'),
          ),
          findsOneWidget,
        );

        // Tap Copy to Clipboard button
        final copyBtn = find.descendant(
          of: find.byType(PromptPreviewDialog),
          matching: find.text('Copy to Clipboard'),
        );
        expect(copyBtn, findsOneWidget);
        await tester.tap(copyBtn);
        await tester.pumpAndSettle();

        expect(clipboardText, contains('Compiled prompt instructions'));
        expect(find.text('Copied to Clipboard!'), findsOneWidget);

        // Advance timer
        await tester.pump(const Duration(seconds: 2));

        // Tap close button on dialog
        await tester.tap(
          find.descendant(
            of: find.byType(PromptPreviewDialog),
            matching: find.byIcon(Icons.close),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(PromptPreviewDialog), findsNothing);
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
        label: I18nText(translations: {'en': ''}),
        description: I18nText(translations: {'en': 'Desc'}),
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

    testWidgets(
      'MatrixPromptBlock renders without RenderFlex overflow on narrow viewport with Finnish locale',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(440, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const block = PromptBlock.matrix(
          id: 'blk_test_matrix_overflow',
          slug: 'matrix_overflow',
          label: I18nText(
            translations: {'en': 'Test Matrix', 'fi': 'Testimatriisi'},
          ),
          description: I18nText(translations: {'en': 'Test Description'}),
          type: BlockDataType.floatType,
          scales: [],
          theoryGrounding: null,
          isEvaluative: true,
          allowDecimals: true,
          allowContextualOverride: true,
          isLightweightProtocol: false,
          targetInputKey: 'product_text',
          aiDescription: 'Test AI Description',
          rows: null,
          columns: null,
        );

        await tester.pumpWidget(
          createTestWidget(block: block, locale: const Locale('fi')),
        );
        await tester.pumpAndSettle();

        expect(find.text('Ruudukon sarakkeet (Valinnainen)'), findsOneWidget);
        expect(find.text('Ruudukon rivit (Valinnainen)'), findsOneWidget);
      },
    );

    testWidgets(
      'MatrixPromptBlock with active rows and columns renders without RenderFlex overflow on 360px viewport with Finnish locale',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const block = PromptBlock.matrix(
          id: 'blk_test_matrix_active_controls',
          slug: 'matrix_active_controls',
          label: I18nText(
            translations: {'en': 'Active Matrix', 'fi': 'Aktiivinen matriisi'},
          ),
          description: I18nText(translations: {'en': 'Test Description'}),
          type: BlockDataType.floatType,
          scales: [],
          theoryGrounding: null,
          isEvaluative: true,
          allowDecimals: true,
          allowContextualOverride: true,
          isLightweightProtocol: false,
          targetInputKey: 'product_text',
          aiDescription: 'Test AI Description',
          rows: [],
          columns: [],
        );

        await tester.pumpWidget(
          createTestWidget(block: block, locale: const Locale('fi')),
        );
        await tester.pumpAndSettle();

        expect(find.byType(Switch), findsWidgets);
        expect(find.byType(OutlinedButton), findsWidgets);
        expect(tester.takeException(), isNull);
      },
    );

    testWidgets(
      'ExecutionPersonaPromptBlock tone directives header renders cleanly on 360px viewport with Finnish locale',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const block = PromptBlock.executionPersona(
          id: 'blk_test_persona_narrow',
          slug: 'test_persona_narrow',
          label: I18nText(translations: {'en': 'Persona', 'fi': 'Persoona'}),
          description: I18nText(translations: {'en': 'Test Description'}),
          roleEnforcement: 'You are an advisor.',
          toneDirectives: ['Authoritative', 'Direct'],
        );

        await tester.pumpWidget(
          createTestWidget(block: block, locale: const Locale('fi')),
        );
        await tester.pumpAndSettle();

        expect(find.byType(OutlinedButton), findsOneWidget);
        expect(tester.takeException(), isNull);
      },
    );

    testWidgets(
      'MatrixPromptBlock with long titles on 520px viewport ellipsizes cleanly via Expanded without overflow',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(520, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const block = PromptBlock.matrix(
          id: 'blk_test_long_title',
          slug: 'long_title',
          label: I18nText(
            translations: {
              'en':
                  'Very Long English Matrix Title Requiring Ellipsis Containment',
              'fi':
                  'Erittäin pitkä suomenkielinen matriisin otsikko, joka vaatii tekstin katkaisua',
            },
          ),
          description: I18nText(translations: {'en': 'Test Description'}),
          type: BlockDataType.floatType,
          scales: [],
          theoryGrounding: null,
          isEvaluative: true,
          allowDecimals: true,
          allowContextualOverride: true,
          isLightweightProtocol: false,
          targetInputKey: 'product_text',
          aiDescription: 'Test AI Description',
          rows: [],
          columns: [],
        );

        await tester.pumpWidget(
          createTestWidget(block: block, locale: const Locale('fi')),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
      },
    );

    testWidgets(
      'PromptBlockBuilderView body enforces 1200px maxWidth constraint on ultrawide viewport (3440x1440)',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(3440, 1440);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const block = PromptBlock.matrix(
          id: 'blk_test_ultrawide',
          slug: 'ultrawide',
          label: I18nText(translations: {'en': 'Matrix', 'fi': 'Matriisi'}),
          description: I18nText(translations: {'en': 'Test Description'}),
          type: BlockDataType.floatType,
          scales: [],
          theoryGrounding: null,
          isEvaluative: true,
          allowDecimals: true,
          allowContextualOverride: true,
          isLightweightProtocol: false,
          targetInputKey: 'product_text',
          aiDescription: 'Test AI Description',
          rows: null,
          columns: null,
        );

        await tester.pumpWidget(
          createTestWidget(block: block, locale: const Locale('en')),
        );
        await tester.pumpAndSettle();

        final constrainedBoxFinder = find.byWidgetPredicate(
          (widget) =>
              widget is ConstrainedBox && widget.constraints.maxWidth == 1200.0,
        );
        expect(constrainedBoxFinder, findsOneWidget);

        final constrainedBox = tester.widget<ConstrainedBox>(
          constrainedBoxFinder,
        );
        expect(constrainedBox.constraints.maxWidth, equals(1200.0));
      },
    );
  });
}
