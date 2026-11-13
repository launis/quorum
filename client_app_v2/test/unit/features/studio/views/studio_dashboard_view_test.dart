import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/studio_dashboard_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  setUpAll(() {
    registerFallbackValue(StepFilterScope.specialists);
  });

  group('StudioDashboardView Widget & Hardening Tests', () {
    late MockStudioClient mockClient;
    late MockLoggerService mockLogger;

    final validRegularBlock = PromptBlock.systemRule(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: 'blk_01965b80000070008000000000000001',
      slug: 'standard_rule_block',
      label: const I18nText(
        translations: {'en': 'Standard Rule Block', 'fi': 'Perussääntölohko'},
      ),
      description: const I18nText(
        translations: {'en': 'Standard Desc', 'fi': 'Kuvaus'},
      ),
    );

    final validMatrixBlock = PromptBlock.matrix(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: 'blk_01965b80000070008000000000000002',
      slug: 'matrix_eval_block',
      label: const I18nText(
        translations: {'en': 'Matrix Eval Block', 'fi': 'Matriisilohko'},
      ),
      description: const I18nText(
        translations: {'en': 'Matrix Desc', 'fi': 'Matriisin kuvaus'},
      ),
      scales: const [],
    );

    final validSpecialistStep = NodeStrategyLogic(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: 'sp_01965b80000070008000000000000001',
      slug: 'specialist_step',
      name: const I18nText(
        translations: {'en': 'Specialist Step', 'fi': 'Asiantuntija-askel'},
      ),
      description: const I18nText(
        translations: {'en': 'Specialist Desc', 'fi': 'Kuvaus'},
      ),
      isSystemCore: false,
      hook: 'test_hook',
    );

    const validModelConfig = ModelConfig(
      id: 'cfg_01965b80000070008000000000000001',
      name: 'Enterprise Vertex Stack',
      slug: 'enterprise-vertex',
      defaultProvider: 'vertex_ai',
    );

    setUp(() {
      mockClient = MockStudioClient();
      mockLogger = MockLoggerService();

      when(() => mockLogger.error(any(), any())).thenReturn(null);
      when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
      when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
      when(() => mockLogger.info(any(), any())).thenReturn(null);

      when(
        () => mockClient.getPromptBlocks(),
      ).thenAnswer((_) async => [validRegularBlock, validMatrixBlock]);
      when(
        () => mockClient.getSteps(scope: any(named: 'scope')),
      ).thenAnswer((_) async => [validSpecialistStep]);
      when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
      when(
        () => mockClient.getSystemConfigs(),
      ).thenAnswer((_) async => [validModelConfig]);
      when(() => mockClient.getWorkflows()).thenAnswer((_) async => []);
      when(() => mockClient.getOutputProfiles()).thenAnswer((_) async => []);
    });

    Widget createSubject({Locale locale = const Locale('en')}) {
      return ProviderScope(
        overrides: [
          studioClientProvider.overrideWithValue(mockClient),
          loggerServiceProvider.overrideWithValue(mockLogger),
        ],
        child: MaterialApp(
          theme: AppTheme.light,
          locale: locale,
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: const StudioDashboardView(),
        ),
      );
    }

    testWidgets(
      'Positive: renders 7 Studio tabs inside AppErrorBoundary, switches across Prompt Blocks, Matrices, Steps, and Model Registry, and triggers Clone & Refresh actions',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        when(
          () => mockClient.clonePromptBlock(any()),
        ).thenAnswer((_) async => validRegularBlock);

        await tester.pumpWidget(createSubject());
        await tester.pumpAndSettle();

        expect(find.byType(AppErrorBoundary), findsWidgets);
        expect(find.byType(Tab), findsNWidgets(7));

        // Trigger top-bar refresh button
        await tester.tap(find.byIcon(Icons.refresh).first);
        await tester.pumpAndSettle();
        verify(
          () => mockClient.getPromptBlocks(),
        ).called(greaterThanOrEqualTo(2));

        // Tab 2: Regular Prompt Blocks
        await tester.tap(find.byIcon(Icons.chat));
        await tester.pumpAndSettle();
        expect(find.text('Standard Rule Block'), findsOneWidget);
        expect(find.text('Matrix Eval Block'), findsNothing);

        // Clone regular prompt block
        await tester.tap(find.byIcon(Icons.copy).first);
        await tester.pumpAndSettle();
        verify(
          () => mockClient.clonePromptBlock(
            'blk_01965b80000070008000000000000001',
          ),
        ).called(1);

        // Tab 3: Matrices
        await tester.tap(find.byIcon(Icons.dataset));
        await tester.pumpAndSettle();
        expect(find.text('Matrix Eval Block'), findsOneWidget);

        // Tab 4: Steps
        await tester.tap(find.byIcon(Icons.extension));
        await tester.pumpAndSettle();
        expect(find.text('Specialist Step'), findsOneWidget);

        // Tab 6: Model Registry
        await tester.tap(find.byIcon(Icons.settings));
        await tester.pumpAndSettle();
        expect(find.text('Enterprise Vertex Stack'), findsOneWidget);
        expect(find.text('1 / 1'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1 (ISTQB BVA / Corrupted Domain Entities): empty ID, empty slug, or missing translation across Regular Blocks, Matrices, Steps, and Model Registry logs error and renders compact ErrorView',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        final corruptedRegularBlock = PromptBlock.systemRule(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: '',
          slug: 'missing_id_rule',
          label: const I18nText(translations: {'en': 'Broken Rule'}),
          description: const I18nText(translations: {'en': 'Desc'}),
        );

        final corruptedMatrixBlock = PromptBlock.matrix(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'blk_01965b80000070008000000000000099',
          slug: '',
          label: const I18nText(translations: {'en': 'Broken Matrix'}),
          description: const I18nText(translations: {'en': 'Desc'}),
          scales: const [],
        );

        final corruptedStep = NodeStrategyLogic(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: '',
          slug: 'broken_step',
          name: const I18nText(translations: {'en': 'Broken Step'}),
          isSystemCore: false,
          hook: 'hook',
        );

        const corruptedConfig = ModelConfig(
          id: '',
          name: 'Broken Config',
          defaultProvider: 'vertex_ai',
        );

        when(() => mockClient.getPromptBlocks()).thenAnswer(
          (_) async => [corruptedRegularBlock, corruptedMatrixBlock],
        );
        when(
          () => mockClient.getSteps(scope: any(named: 'scope')),
        ).thenAnswer((_) async => [corruptedStep]);
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [corruptedConfig]);

        await tester.pumpWidget(createSubject());
        await tester.pumpAndSettle();

        // Regular Prompt Blocks Tab
        await tester.tap(find.byIcon(Icons.chat));
        await tester.pumpAndSettle();
        expect(find.byType(ErrorView), findsOneWidget);

        // Matrices Tab
        await tester.tap(find.byIcon(Icons.dataset));
        await tester.pumpAndSettle();
        expect(find.byType(ErrorView), findsOneWidget);

        // Steps Tab
        await tester.tap(find.byIcon(Icons.extension));
        await tester.pumpAndSettle();
        expect(find.byType(ErrorView), findsOneWidget);

        // Model Registry Tab
        await tester.tap(find.byIcon(Icons.settings));
        await tester.pumpAndSettle();
        expect(find.byType(ErrorView), findsOneWidget);

        verify(
          () => mockLogger.error('Studio', any(), any(), any()),
        ).called(greaterThanOrEqualTo(4));
      },
    );

    testWidgets(
      'Negative 2 (Network / Mint Draft Failure & Retry Recovery): failed fetch renders ErrorView with Retry recovery, and failed draft creation logs error and displays localized SnackBar',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        var failPromptBlocks = true;
        when(() => mockClient.getPromptBlocks()).thenAnswer((_) async {
          if (failPromptBlocks) {
            throw AppException.server('PromptBlocks service offline');
          }
          return [validRegularBlock];
        });
        when(
          () => mockClient.createPromptBlockDraft(
            categoryId: any(named: 'categoryId'),
          ),
        ).thenThrow(AppException.server('Mint draft rejected'));

        await tester.pumpWidget(createSubject());
        await tester.pumpAndSettle();

        // Switch to Prompt Blocks tab -> shows ErrorView
        await tester.tap(find.byIcon(Icons.chat));
        await tester.pumpAndSettle();
        expect(find.byType(ErrorView), findsOneWidget);

        // Recover via Retry button
        failPromptBlocks = false;
        await tester.tap(find.text('Retry'));
        await tester.pumpAndSettle();
        expect(find.byType(ErrorView), findsNothing);
        expect(find.text('Standard Rule Block'), findsOneWidget);

        // Trigger "+ New" button when createPromptBlockDraft fails
        await tester.tap(find.byIcon(Icons.add));
        await tester.pumpAndSettle();

        verify(
          () => mockLogger.error(
            'Studio',
            any(that: contains('Failed to mint standard prompt block draft')),
            any(),
            any(),
          ),
        ).called(1);
        expect(find.byType(SnackBar), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 3 (Finnish 360px Compact Viewport Stress Gate): renders without RenderFlex horizontal overflow under Finnish locale',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(createSubject(locale: const Locale('fi')));
        await tester.pumpAndSettle();

        // Switch through tabs at 360px width in Finnish
        await tester.tap(find.byIcon(Icons.chat));
        await tester.pumpAndSettle();
        expect(tester.takeException(), isNull);

        await tester.ensureVisible(find.byIcon(Icons.dataset));
        await tester.pumpAndSettle();
        await tester.tap(find.byIcon(Icons.dataset));
        await tester.pumpAndSettle();
        expect(tester.takeException(), isNull);
      },
    );
  });
}
