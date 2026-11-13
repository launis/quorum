import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/views/workflows_master_view.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockLoggerService extends Mock implements LoggerService {}

class MockWorkflowsController extends WorkflowsController {
  final AsyncValue<List<Workflow>> initialState;
  final Future<Workflow> Function(String id)? onClone;
  final Future<Workflow> Function()? onCreateDraft;
  final Future<void> Function()? onRefresh;

  MockWorkflowsController([
    List<Workflow> workflows = const [],
    this.onClone,
    this.onCreateDraft,
    this.onRefresh,
  ]) : initialState = AsyncData(workflows);

  MockWorkflowsController.fromAsync(
    this.initialState, {
    this.onClone,
    this.onCreateDraft,
    this.onRefresh,
  });

  @override
  FutureOr<List<Workflow>> build() async {
    return switch (initialState) {
      AsyncData(:final value) => value,
      AsyncError(:final error, :final stackTrace) => Error.throwWithStackTrace(
        error,
        stackTrace,
      ),
      _ => Completer<List<Workflow>>().future,
    };
  }

  @override
  Future<Workflow> cloneWorkflow(String id) async {
    if (onClone != null) {
      return await onClone!(id);
    }
    return Workflow(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: '${id}_clone',
      slug: '$id-clone',
      name: const I18nText(translations: {'en': 'Cloned Workflow'}),
      description: const I18nText(translations: {'en': 'Desc'}),
      modelRegistryId: 'mr_test',
    );
  }

  @override
  Future<Workflow> createWorkflowDraft() async {
    if (onCreateDraft != null) {
      return await onCreateDraft!();
    }
    return const Workflow(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: 'wf_01950000000070008000000000000099',
      slug: 'draft-workflow',
      name: I18nText(translations: {'en': 'Draft Workflow'}),
      description: I18nText(translations: {'en': 'Desc'}),
      modelRegistryId: 'mr_test',
    );
  }

  @override
  Future<void> refresh() async {
    if (onRefresh != null) {
      await onRefresh!();
    }
  }
}

void main() {
  late MockLoggerService mockLogger;

  setUp(() {
    mockLogger = MockLoggerService();
    when(() => mockLogger.error(any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
    when(() => mockLogger.info(any(), any())).thenReturn(null);
  });

  Widget createTestWidget(
    List<Workflow> workflows, {
    Size screenSize = const Size(1920, 1080),
    Future<Workflow> Function(String id)? onClone,
    Future<Workflow> Function()? onCreateDraft,
    Future<void> Function()? onRefresh,
  }) {
    return ProviderScope(
      key: UniqueKey(),
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(
            workflows,
            onClone,
            onCreateDraft,
            onRefresh,
          ),
        ),
      ],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en'), Locale('fi')],
        home: MediaQuery(
          data: MediaQueryData(size: screenSize),
          child: const Scaffold(body: WorkflowsMasterView()),
        ),
      ),
    );
  }

  Widget createAsyncTestWidget(
    AsyncValue<List<Workflow>> asyncState, {
    Future<void> Function()? onRefresh,
  }) {
    return ProviderScope(
      key: UniqueKey(),
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController.fromAsync(
            asyncState,
            onRefresh: onRefresh,
          ),
        ),
      ],
      child: const MaterialApp(
        localizationsDelegates: [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: [Locale('en'), Locale('fi')],
        home: Scaffold(body: WorkflowsMasterView()),
      ),
    );
  }

  List<Workflow> generateMockWorkflows(int count) {
    return List.generate(
      count,
      (i) => Workflow(
        organizationId: 'org_0195f3a0000070008000000000000001',
        id: 'wf_${i.toString().padLeft(3, '0')}',
        slug: 'workflow-slug-$i',
        name: I18nText(
          translations: {'en': 'Workflow $i', 'fi': 'Työnkulku $i'},
        ),
        description: I18nText(
          translations: {'en': 'Description $i', 'fi': 'Kuvaus $i'},
        ),
        modelRegistryId: 'mr_test',
      ),
    );
  }

  group('WorkflowsMasterView Widget Tests', () {
    testWidgets('test_workflows_master_view_virtualized_rendering', (
      tester,
    ) async {
      final mockList = generateMockWorkflows(50);
      await tester.pumpWidget(createTestWidget(mockList));
      await tester.pumpAndSettle();

      expect(find.byType(AppErrorBoundary), findsOneWidget);

      // Verify ListView.builder exists and uses virtualization
      final listViewFinder = find.byType(ListView);
      expect(listViewFinder, findsOneWidget);

      final listView = tester.widget<ListView>(listViewFinder);
      expect(listView.prototypeItem, isNotNull);

      // Virtualized ListView should NOT inflate all 50 items simultaneously in an 1080p viewport
      final visibleTiles = find.byType(ListTile);
      expect(visibleTiles.evaluate().length, lessThan(50));
      expect(visibleTiles.evaluate().length, greaterThan(0));

      // Header shows count pill 'Showing 50 of 50 items'
      expect(find.text('Showing 50 of 50 items'), findsOneWidget);
    });

    testWidgets('test_master_views_4k_display_containment', (tester) async {
      tester.view.physicalSize = const Size(3840, 2160);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final mockList = generateMockWorkflows(5);
      await tester.pumpWidget(
        createTestWidget(mockList, screenSize: const Size(3840, 2160)),
      );
      await tester.pumpAndSettle();

      // Verify ConstrainedBox clamps maxWidth to 1200
      final constrainedBoxFinder = find.byWidgetPredicate(
        (widget) =>
            widget is ConstrainedBox && widget.constraints.maxWidth == 1200.0,
      );
      expect(constrainedBoxFinder, findsOneWidget);

      final box = tester.renderObject(constrainedBoxFinder) as RenderBox;
      expect(box.size.width, lessThanOrEqualTo(1200.0));
    });

    testWidgets('instant search filters workflows in-memory', (tester) async {
      final mockList = [
        Workflow(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'wf_alpha',
          slug: 'alpha-analysis',
          name: const I18nText(translations: {'en': 'Alpha Diagnostic'}),
          description: const I18nText(translations: {'en': 'Alpha Desc'}),
          modelRegistryId: 'mr_1',
        ),
        Workflow(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'wf_beta',
          slug: 'beta-synthesis',
          name: const I18nText(translations: {'en': 'Beta Reporting'}),
          description: const I18nText(translations: {'en': 'Beta Desc'}),
          modelRegistryId: 'mr_1',
        ),
      ];

      await tester.pumpWidget(createTestWidget(mockList));
      await tester.pumpAndSettle();

      expect(find.text('Alpha Diagnostic'), findsOneWidget);
      expect(find.text('Beta Reporting'), findsOneWidget);
      expect(find.text('Showing 2 of 2 items'), findsOneWidget);

      // Type search query
      await tester.enterText(find.byType(TextField), 'Alpha');
      await tester.pumpAndSettle();

      expect(find.text('Alpha Diagnostic'), findsOneWidget);
      expect(find.text('Beta Reporting'), findsNothing);
      expect(find.text('Showing 1 of 2 items'), findsOneWidget);

      // Clear search
      await tester.tap(find.byIcon(Icons.clear));
      await tester.pumpAndSettle();

      expect(find.text('Alpha Diagnostic'), findsOneWidget);
      expect(find.text('Beta Reporting'), findsOneWidget);
      expect(find.text('Showing 2 of 2 items'), findsOneWidget);
    });

    testWidgets('shows empty search miss message when query matches 0 items', (
      tester,
    ) async {
      final mockList = [
        Workflow(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: 'wf_alpha',
          slug: 'alpha-analysis',
          name: const I18nText(translations: {'en': 'Alpha Diagnostic'}),
          description: const I18nText(translations: {'en': 'Alpha Desc'}),
          modelRegistryId: 'mr_1',
        ),
      ];

      await tester.pumpWidget(createTestWidget(mockList));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'NonexistentQuery');
      await tester.pumpAndSettle();

      expect(find.text('No matching items found.'), findsOneWidget);
      expect(find.text('Showing 0 of 1 items'), findsOneWidget);
    });

    testWidgets(
      'shows initial zero-state message when 0 workflows configured',
      (tester) async {
        await tester.pumpWidget(createTestWidget([]));
        await tester.pumpAndSettle();

        expect(find.text('No workflows configured.'), findsOneWidget);
        expect(find.text('Showing 0 of 0 items'), findsOneWidget);
      },
    );

    testWidgets(
      'renders ErrorView on AsyncError and triggers refresh on retry',
      (tester) async {
        bool refreshCalled = false;
        final error = AppException.validation('Backend fetch failure');

        await tester.pumpWidget(
          createAsyncTestWidget(
            AsyncError(error, StackTrace.current),
            onRefresh: () async {
              refreshCalled = true;
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(AppErrorBoundary), findsOneWidget);
        expect(find.byType(ErrorView), findsOneWidget);

        final retryButton = find.byIcon(Icons.refresh);
        expect(retryButton, findsOneWidget);
        await tester.tap(retryButton);
        await tester.pumpAndSettle();

        expect(refreshCalled, isTrue);
      },
    );

    testWidgets(
      'displays MaterialBanner and logs error when draft creation fails, and dismisses on cancel',
      (tester) async {
        await tester.pumpWidget(
          createTestWidget(
            [],
            onCreateDraft: () async {
              throw AppException.validation('Minting failed');
            },
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.account_tree));
        await tester.pumpAndSettle();

        expect(find.byType(MaterialBanner), findsOneWidget);
        verify(
          () => mockLogger.error(
            'Studio',
            any(that: contains('Failed to mint workflow draft')),
            any(),
            any(),
          ),
        ).called(1);

        await tester.tap(find.text('Cancel'));
        await tester.pumpAndSettle();

        expect(find.byType(MaterialBanner), findsNothing);
      },
    );

    testWidgets(
      'crashes Fail-Fast into AppErrorBoundary when workflow slug is empty',
      (tester) async {
        final originalOnError = FlutterError.onError;
        FlutterError.onError = (FlutterErrorDetails details) {};
        try {
          final mockList = [
            const Workflow(
              organizationId: 'org_0195f3a0000070008000000000000001',
              id: 'wf_empty_slug',
              slug: '',
              name: I18nText(translations: {'en': 'Empty Slug Workflow'}),
              description: I18nText(translations: {'en': 'Desc'}),
              modelRegistryId: 'mr_1',
            ),
          ];

          await tester.pumpWidget(createTestWidget(mockList));
          await tester.pumpAndSettle();

          expect(find.byIcon(Icons.report_problem), findsOneWidget);
          expect(
            find.textContaining('Fail-Fast: Workflow slug is missing.'),
            findsOneWidget,
          );
        } finally {
          FlutterError.onError = originalOnError;
        }
      },
    );
  });
}
