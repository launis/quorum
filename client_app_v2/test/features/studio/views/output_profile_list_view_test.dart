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
import 'package:client_app/features/studio/views/output_profile_list_view.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockLoggerService extends Mock implements LoggerService {}

class MockOutputProfilesController extends OutputProfilesController {
  final AsyncValue<List<OutputProfile>> initialValue;
  final Future<OutputProfile> Function(String id)? onClone;
  final Future<OutputProfile> Function()? onCreateDraft;
  final Future<void> Function()? onRefresh;

  MockOutputProfilesController(
    this.initialValue, {
    this.onClone,
    this.onCreateDraft,
    this.onRefresh,
  });

  @override
  FutureOr<List<OutputProfile>> build() async {
    return switch (initialValue) {
      AsyncData(:final value) => value,
      AsyncError(:final error, :final stackTrace) => Error.throwWithStackTrace(
        error,
        stackTrace,
      ),
      _ => Completer<List<OutputProfile>>().future,
    };
  }

  @override
  Future<OutputProfile> cloneProfile(String id) async {
    if (onClone != null) {
      return await onClone!(id);
    }
    return OutputProfile(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: '${id}_clone',
      slug: '$id-clone',
      workflowId: 'wf_test',
      name: const I18nText(translations: {'en': 'Cloned Profile'}),
    );
  }

  @override
  Future<OutputProfile> createOutputProfileDraft() async {
    if (onCreateDraft != null) {
      return await onCreateDraft!();
    }
    return const OutputProfile(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: 'prf_draft',
      slug: 'draft-profile',
      workflowId: 'wf_test',
      name: I18nText(translations: {'en': 'Draft Profile'}),
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
    AsyncValue<List<OutputProfile>> profilesState, {
    Size screenSize = const Size(1920, 1080),
    Key? key,
    Future<OutputProfile> Function(String id)? onClone,
    Future<OutputProfile> Function()? onCreateDraft,
    Future<void> Function()? onRefresh,
  }) {
    return ProviderScope(
      key: key ?? UniqueKey(),
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        outputProfilesControllerProvider.overrideWith(
          () => MockOutputProfilesController(
            profilesState,
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
          child: const Scaffold(body: OutputProfileListView()),
        ),
      ),
    );
  }

  OutputProfile createProfile(String id, String name, String slug) {
    return OutputProfile(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: id,
      slug: slug,
      workflowId: 'wf_test',
      name: I18nText(translations: {'en': name, 'fi': name}),
    );
  }

  group('OutputProfileListView Widget Tests', () {
    testWidgets('test_output_profile_list_view_empty_and_error_states', (
      tester,
    ) async {
      // 1. Empty state: 0 profiles
      await tester.pumpWidget(createTestWidget(const AsyncData([])));
      await tester.pumpAndSettle();

      expect(find.text('No Output Profiles defined.'), findsOneWidget);
      expect(find.text('Showing 0 of 0 items'), findsOneWidget);

      // 2. Search miss: matching 0 items
      final profiles = [
        createProfile('prf_1', 'Executive Summary', 'exec-sum'),
      ];
      await tester.pumpWidget(createTestWidget(AsyncData(profiles)));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'NonexistentQuery');
      await tester.pumpAndSettle();

      expect(find.text('No matching items found.'), findsOneWidget);
      expect(find.text('Showing 0 of 1 items'), findsOneWidget);

      // 3. Error state: AsyncError emitted and retry triggers refresh
      bool refreshCalled = false;
      final testError = AppException.validation('Network failure');
      await tester.pumpWidget(
        createTestWidget(
          AsyncError(testError, StackTrace.current),
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
    });

    testWidgets('test_master_views_4k_display_containment', (tester) async {
      tester.view.physicalSize = const Size(3840, 2160);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final profiles = [createProfile('prf_1', 'Profile 1', 'prf-1')];
      await tester.pumpWidget(
        createTestWidget(
          AsyncData(profiles),
          screenSize: const Size(3840, 2160),
        ),
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

    testWidgets('test_output_profile_list_view_virtualized_rendering', (
      tester,
    ) async {
      final mockList = List.generate(
        35,
        (i) => createProfile('prf_$i', 'Profile $i', 'profile-slug-$i'),
      );

      await tester.pumpWidget(createTestWidget(AsyncData(mockList)));
      await tester.pumpAndSettle();

      final listViewFinder = find.byType(ListView);
      expect(listViewFinder, findsOneWidget);

      final listView = tester.widget<ListView>(listViewFinder);
      expect(listView.prototypeItem, isNotNull);

      final visibleTiles = find.byType(ListTile);
      expect(visibleTiles.evaluate().length, lessThan(35));
      expect(visibleTiles.evaluate().length, greaterThan(0));

      expect(find.text('Showing 35 of 35 items'), findsOneWidget);
    });

    testWidgets('instant search filters profiles in-memory', (tester) async {
      final profiles = [
        createProfile('prf_alpha', 'Alpha Report', 'alpha-report'),
        createProfile('prf_beta', 'Beta Dashboard', 'beta-dashboard'),
      ];

      await tester.pumpWidget(createTestWidget(AsyncData(profiles)));
      await tester.pumpAndSettle();

      expect(find.text('Alpha Report'), findsOneWidget);
      expect(find.text('Beta Dashboard'), findsOneWidget);
      expect(find.text('Showing 2 of 2 items'), findsOneWidget);

      await tester.enterText(find.byType(TextField), 'beta');
      await tester.pumpAndSettle();

      expect(find.text('Alpha Report'), findsNothing);
      expect(find.text('Beta Dashboard'), findsOneWidget);
      expect(find.text('Showing 1 of 2 items'), findsOneWidget);

      await tester.tap(find.byIcon(Icons.clear));
      await tester.pumpAndSettle();

      expect(find.text('Alpha Report'), findsOneWidget);
      expect(find.text('Beta Dashboard'), findsOneWidget);
      expect(find.text('Showing 2 of 2 items'), findsOneWidget);
    });

    testWidgets(
      'displays MaterialBanner and logs error when draft creation fails, and dismisses on cancel',
      (tester) async {
        await tester.pumpWidget(
          createTestWidget(
            const AsyncData([]),
            onCreateDraft: () async {
              throw AppException.validation('Profile minting failed');
            },
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.add));
        await tester.pumpAndSettle();

        expect(find.byType(MaterialBanner), findsOneWidget);
        verify(
          () => mockLogger.error(
            'OutputProfileListView',
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
      'clones output profile via CloneEntityButton and displays error SnackBar when clone fails',
      (tester) async {
        String? clonedId;
        final profiles = [
          createProfile('prf_exec', 'Executive Report', 'executive-report'),
        ];

        await tester.pumpWidget(
          createTestWidget(
            AsyncData(profiles),
            onClone: (id) async {
              clonedId = id;
              return createProfile(
                '${id}_clone',
                'Executive Clone',
                'executive-clone',
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.copy));
        await tester.pumpAndSettle();

        expect(clonedId, 'prf_exec');

        // Verify failure path on clone
        await tester.pumpWidget(
          createTestWidget(
            AsyncData(profiles),
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

    testWidgets(
      'throws Fail-Fast AppException.validation when profile ID or slug is empty',
      (tester) async {
        final emptyIdProfile = [
          createProfile('', 'Invalid ID Profile', 'valid-slug'),
        ];

        await tester.pumpWidget(createTestWidget(AsyncData(emptyIdProfile)));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isA<AppException>());

        final emptySlugProfile = [
          createProfile('prf_valid', 'Invalid Slug Profile', ''),
        ];

        await tester.pumpWidget(createTestWidget(AsyncData(emptySlugProfile)));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isA<AppException>());
      },
    );
  });
}
