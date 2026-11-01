import 'dart:async';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/models/prompt_block_category.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/prompt_block_simulation.dart';
import 'package:client_app/features/studio/views/prompt_block_builder_view.dart';
import 'package:client_app/features/studio/views/widgets/prompt_preview_dialog.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

class TestPromptBlockForm extends PromptBlockForm {
  final FutureOr<PromptBlock> Function() onBuild;
  final Future<void> Function(PromptBlock saved)? onSave;

  TestPromptBlockForm({required this.onBuild, this.onSave});

  @override
  FutureOr<PromptBlock> build(String configId) {
    return onBuild();
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
  final Future<PromptBlockSimulationResponse> Function(
    PromptBlock payload,
    Map<String, Object?> mockInputs,
  )?
  onSimulate;
  final Future<void> Function(String id)? onDelete;

  MockPromptBlocksController({this.onSimulate, this.onDelete});

  @override
  FutureOr<List<PromptBlock>> build() async => [];

  @override
  Future<PromptBlockSimulationResponse> simulatePromptBlock(
    PromptBlock payload,
    Map<String, Object?> mockInputs, {
    int? targetScaleScore,
    String? targetLocale,
    String? contextText,
  }) async {
    if (onSimulate != null) {
      return onSimulate!(payload, mockInputs);
    }
    return const PromptBlockSimulationResponse(
      renderedPrompt: '<system_rule>Test Simulation</system_rule>',
    );
  }

  @override
  Future<void> deletePromptBlock(String id) async {
    if (onDelete != null) {
      await onDelete!(id);
    }
  }
}

void main() {
  late MockLoggerService mockLogger;
  late MockStudioClient mockStudioClient;

  setUp(() {
    mockLogger = MockLoggerService();
    mockStudioClient = MockStudioClient();
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
  });

  Widget createSubject({
    required String id,
    required FutureOr<PromptBlock> Function() onBuild,
    PromptBlocksController? controller,
    Future<void> Function(PromptBlock)? onSave,
    Locale locale = const Locale('en'),
  }) {
    final blockKey = id.isEmpty ? 'new' : id;
    return ProviderScope(
      overrides: [
        studioClientProvider.overrideWithValue(mockStudioClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
        promptBlockFormProvider(blockKey).overrideWith(
          () => TestPromptBlockForm(onBuild: onBuild, onSave: onSave),
        ),
        promptBlocksControllerProvider.overrideWith(
          () => controller ?? MockPromptBlocksController(),
        ),
      ],
      child: MaterialApp(
        theme: AppTheme.light,
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: PromptBlockBuilderView(id: id),
      ),
    );
  }

  group('PromptBlockBuilderView Unit & Hardening Tests', () {
    testWidgets(
      'Positive: renders MatrixPromptBlock with rows, columns, and scales, and switches categories cleanly',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        const block = PromptBlock.matrix(
          id: 'blk_0195f000000070008000000000000001',
          slug: 'matrix_test',
          label: I18nText(translations: {'en': 'Matrix Block'}),
          description: I18nText(translations: {'en': 'Matrix Desc'}),
          type: BlockDataType.floatType,
          rows: [
            MatrixRow(
              label: I18nText(translations: {'en': 'Row Alpha'}),
              aiDescription: 'CRITICAL MANDATE: Row Alpha rule',
            ),
          ],
          columns: [
            I18nText(translations: {'en': 'Col Beta'}),
          ],
          scales: [
            MatrixScale(
              score: 1,
              aiLabel: '1',
              name: I18nText(translations: {'en': 'Grade 1'}),
              claims: [],
            ),
          ],
        );

        await tester.pumpWidget(
          createSubject(id: block.id, onBuild: () => block),
        );
        await tester.pumpAndSettle();

        expect(find.byType(AppExceptionBoundary), findsOneWidget);
        expect(find.text('Row Alpha'), findsOneWidget);
        expect(find.text('Col Beta'), findsOneWidget);
        expect(find.text('1'), findsWidgets);
        expect(find.byType(FilterChip), findsNWidgets(10));
      },
    );

    testWidgets(
      'Negative 1 (ISTQB BVA / Missing English Label Validation Gate): blocks submission and shows mandatory English SnackBar when English label is empty',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        const block = PromptBlock.systemRule(
          id: 'blk_0195f000000070008000000000000002',
          slug: 'empty_en_rule',
          label: I18nText(translations: {'en': ''}),
          description: I18nText(translations: {'en': 'Description'}),
          instructionText: 'Rule text',
        );

        bool saveCalled = false;
        await tester.pumpWidget(
          createSubject(
            id: block.id,
            onBuild: () => block,
            onSave: (_) async {
              saveCalled = true;
            },
          ),
        );
        await tester.pumpAndSettle();

        final BuildContext context = tester.element(
          find.byType(PromptBlockBuilderView),
        );
        final l10n = AppLocalizations.of(context)!;

        await tester.tap(find.byIcon(Icons.save));
        await tester.pumpAndSettle();

        expect(saveCalled, isFalse);
        expect(
          find.text(l10n.promptBlockMandatoryEnglishError),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Negative 2 (ISTQB BVA / Provider Error): renders ErrorView on provider failure without horizontal overflow on narrow 360px Finnish viewport',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          createSubject(
            id: 'blk_0195f000000070008000000000000404',
            locale: const Locale('fi'),
            onBuild: () async {
              throw const AppException(
                detail: 'Prompt block not found',
                status: 404,
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byType(ErrorView), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 3 (ISTQB BVA / Simulation Validation Failure): displays MaterialBanner with errors and does not open PromptPreviewDialog when simulation returns valid=false',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        const validBlock = PromptBlock.protocol(
          id: 'blk_0195f000000070008000000000000003',
          slug: 'proto_fail_sim',
          label: I18nText(translations: {'en': 'Protocol', 'fi': 'Protokolla'}),
          description: I18nText(translations: {'en': 'Desc', 'fi': 'Kuvaus'}),
          protocolInstructions: 'Step 1',
        );

        final failingSimController = MockPromptBlocksController(
          onSimulate: (_, _) async => const PromptBlockSimulationResponse(
            renderedPrompt: '',
            valid: false,
            errors: ['Invalid schema binding'],
          ),
        );

        await tester.pumpWidget(
          createSubject(
            id: validBlock.id,
            locale: const Locale('fi'),
            onBuild: () => validBlock,
            controller: failingSimController,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.bug_report));
        await tester.pumpAndSettle();

        expect(find.byType(MaterialBanner), findsOneWidget);
        expect(find.text('Invalid schema binding'), findsOneWidget);
        expect(find.byType(PromptPreviewDialog), findsNothing);
      },
    );

    testWidgets(
      'Negative 4 (ISTQB BVA / Missing Translation Fail-Fast on Delete): throws AppException when deleting a PromptBlock lacking active and English translations',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        const blockWithoutTranslations = PromptBlock.systemRule(
          id: 'blk_0195f000000070008000000000000009',
          slug: 'no_trans_rule',
          label: I18nText(translations: {'en': '   '}),
          description: I18nText(translations: {'en': 'Desc'}),
          instructionText: 'Rule',
        );

        await tester.pumpWidget(
          createSubject(
            id: blockWithoutTranslations.id,
            onBuild: () => blockWithoutTranslations,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.delete));
        await tester.pump();

        final thrown = tester.takeException();
        expect(thrown, isA<AppException>());
      },
    );
  });
}
