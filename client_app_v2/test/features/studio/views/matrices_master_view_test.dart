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
import 'package:client_app/features/studio/views/matrices_master_view.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockLoggerService extends Mock implements LoggerService {}

class MockPromptBlocksController extends PromptBlocksController {
  final AsyncValue<List<PromptBlock>> initialState;
  final Future<PromptBlock> Function(String id)? onClone;
  final Future<PromptBlock> Function({String? categoryId})? onCreateDraft;
  final Future<void> Function()? onRefresh;

  MockPromptBlocksController(
    List<PromptBlock> blocks, {
    this.onClone,
    this.onCreateDraft,
    this.onRefresh,
  }) : initialState = AsyncData(blocks);

  MockPromptBlocksController.fromAsync(
    this.initialState, {
    this.onClone,
    this.onCreateDraft,
    this.onRefresh,
  });

  @override
  FutureOr<List<PromptBlock>> build() async {
    return switch (initialState) {
      AsyncData(:final value) => value,
      AsyncError(:final error, :final stackTrace) => Error.throwWithStackTrace(
        error,
        stackTrace,
      ),
      _ => Completer<List<PromptBlock>>().future,
    };
  }

  @override
  Future<PromptBlock> clonePromptBlock(String id) async {
    if (onClone != null) {
      return await onClone!(id);
    }
    return PromptBlock.matrix(
      id: '${id}_clone',
      slug: '$id-clone',
      label: const I18nText(translations: {'en': 'Cloned Matrix'}),
      description: const I18nText(translations: {'en': 'Desc'}),
      scales: const [],
    );
  }

  @override
  Future<PromptBlock> createPromptBlockDraft({String? categoryId}) async {
    if (onCreateDraft != null) {
      return await onCreateDraft!(categoryId: categoryId);
    }
    return PromptBlock.matrix(
      id: 'blk_draft',
      slug: 'draft-matrix',
      label: const I18nText(translations: {'en': 'Draft Matrix'}),
      description: const I18nText(translations: {'en': 'Desc'}),
      scales: const [],
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
    List<PromptBlock> blocks, {
    Size screenSize = const Size(1920, 1080),
    Future<PromptBlock> Function(String id)? onClone,
    Future<PromptBlock> Function({String? categoryId})? onCreateDraft,
    Future<void> Function()? onRefresh,
  }) {
    return ProviderScope(
      key: UniqueKey(),
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(
            blocks,
            onClone: onClone,
            onCreateDraft: onCreateDraft,
            onRefresh: onRefresh,
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
          child: const Scaffold(body: MatricesMasterView()),
        ),
      ),
    );
  }

  Widget createAsyncTestWidget(
    AsyncValue<List<PromptBlock>> asyncState, {
    Future<void> Function()? onRefresh,
  }) {
    return ProviderScope(
      key: UniqueKey(),
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController.fromAsync(
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
        home: Scaffold(body: MatricesMasterView()),
      ),
    );
  }

  PromptBlock createMatrixBlock(String id, String name, String slug) {
    return PromptBlock.matrix(
      id: id,
      slug: slug,
      label: I18nText(translations: {'en': name, 'fi': name}),
      description: const I18nText(translations: {'en': 'Desc'}),
      scales: const [],
    );
  }

  group('MatricesMasterView Widget Tests', () {
    testWidgets('test_matrices_master_view_instant_search_filtering', (
      tester,
    ) async {
      final mockBlocks = [
        createMatrixBlock('blk_empathy', 'Empathy Matrix', 'empathy-matrix'),
        createMatrixBlock('blk_clarity', 'Clarity Matrix', 'clarity-matrix'),
      ];

      await tester.pumpWidget(createTestWidget(mockBlocks));
      await tester.pumpAndSettle();

      expect(find.text('Empathy Matrix'), findsOneWidget);
      expect(find.text('Clarity Matrix'), findsOneWidget);
      expect(find.text('Showing 2 of 2 items'), findsOneWidget);

      // Search for 'clarity'
      await tester.enterText(find.byType(TextField), 'clarity');
      await tester.pumpAndSettle();

      expect(find.text('Empathy Matrix'), findsNothing);
      expect(find.text('Clarity Matrix'), findsOneWidget);
      expect(find.text('Showing 1 of 2 items'), findsOneWidget);

      // Clear search
      await tester.tap(find.byIcon(Icons.clear));
      await tester.pumpAndSettle();

      expect(find.text('Empathy Matrix'), findsOneWidget);
      expect(find.text('Clarity Matrix'), findsOneWidget);
      expect(find.text('Showing 2 of 2 items'), findsOneWidget);
    });

    testWidgets('test_master_views_4k_display_containment', (tester) async {
      tester.view.physicalSize = const Size(3840, 2160);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final mockBlocks = [createMatrixBlock('blk_1', 'Matrix 1', 'matrix-1')];

      await tester.pumpWidget(
        createTestWidget(mockBlocks, screenSize: const Size(3840, 2160)),
      );
      await tester.pumpAndSettle();

      final constrainedBoxFinder = find.byWidgetPredicate(
        (widget) =>
            widget is ConstrainedBox && widget.constraints.maxWidth == 1200.0,
      );
      expect(constrainedBoxFinder, findsOneWidget);

      final box = tester.renderObject(constrainedBoxFinder) as RenderBox;
      expect(box.size.width, lessThanOrEqualTo(1200.0));
    });

    testWidgets('test_matrices_master_view_virtualized_rendering', (
      tester,
    ) async {
      final mockBlocks = List.generate(
        40,
        (i) => createMatrixBlock('blk_$i', 'Matrix $i', 'matrix-slug-$i'),
      );

      await tester.pumpWidget(createTestWidget(mockBlocks));
      await tester.pumpAndSettle();

      final listViewFinder = find.byType(ListView);
      expect(listViewFinder, findsOneWidget);

      final listView = tester.widget<ListView>(listViewFinder);
      expect(listView.prototypeItem, isNotNull);

      final visibleTiles = find.byType(ListTile);
      expect(visibleTiles.evaluate().length, lessThan(40));
      expect(visibleTiles.evaluate().length, greaterThan(0));

      expect(find.text('Showing 40 of 40 items'), findsOneWidget);
    });

    testWidgets('excludes non-matrix category blocks', (tester) async {
      final mockBlocks = [
        createMatrixBlock('blk_matrix', 'Active Matrix', 'matrix-slug'),
        const PromptBlock.executionPersona(
          id: 'blk_persona',
          slug: 'persona-slug',
          label: I18nText(translations: {'en': 'Executive Coach Persona'}),
          description: I18nText(translations: {'en': 'Persona Desc'}),
        ),
      ];

      await tester.pumpWidget(createTestWidget(mockBlocks));
      await tester.pumpAndSettle();

      expect(find.text('Active Matrix'), findsOneWidget);
      expect(find.text('Executive Coach Persona'), findsNothing);
      expect(find.text('Showing 1 of 1 items'), findsOneWidget);
    });

    testWidgets('renders zero-state when no matrices available', (
      tester,
    ) async {
      await tester.pumpWidget(createTestWidget([]));
      await tester.pumpAndSettle();

      expect(find.text('No Matrices Available.'), findsOneWidget);
      expect(find.text('Showing 0 of 0 items'), findsOneWidget);
    });

    testWidgets('renders search miss when query yields 0 results', (
      tester,
    ) async {
      final mockBlocks = [
        createMatrixBlock('blk_1', 'Cognitive Bias', 'cognitive-bias'),
      ];

      await tester.pumpWidget(createTestWidget(mockBlocks));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'UnknownQuery');
      await tester.pumpAndSettle();

      expect(find.text('No matching items found.'), findsOneWidget);
      expect(find.text('Showing 0 of 1 items'), findsOneWidget);
    });

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
            onCreateDraft: ({categoryId = 'matrix'}) async {
              throw AppException.validation('Minting failed');
            },
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.grid_on));
        await tester.pumpAndSettle();

        expect(find.byType(MaterialBanner), findsOneWidget);
        verify(
          () => mockLogger.error(
            'MatricesMasterView',
            'Failed to mint',
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
      'clones matrix via CloneEntityButton and displays error SnackBar when clone fails',
      (tester) async {
        String? clonedId;
        final mockBlocks = [
          createMatrixBlock('blk_empathy', 'Empathy Matrix', 'empathy-matrix'),
        ];

        await tester.pumpWidget(
          createTestWidget(
            mockBlocks,
            onClone: (id) async {
              clonedId = id;
              return createMatrixBlock(
                '${id}_clone',
                'Empathy Clone',
                'empathy-clone',
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.copy));
        await tester.pumpAndSettle();

        expect(clonedId, 'blk_empathy');

        // Verify failure path on clone
        await tester.pumpWidget(
          createTestWidget(
            mockBlocks,
            onClone: (id) async {
              throw AppException.validation('Duplicate failure');
            },
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.copy));
        await tester.pumpAndSettle();

        verify(
          () => mockLogger.error(
            'CloneEntityButton',
            'Clone operation failed',
            any(),
          ),
        ).called(1);
        expect(find.byType(SnackBar), findsOneWidget);
      },
    );
  });
}
