import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/output_profile_list_view.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockOutputProfilesController extends OutputProfilesController {
  final AsyncValue<List<OutputProfile>> initialValue;
  MockOutputProfilesController(this.initialValue);

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
}

void main() {
  Widget createTestWidget(
    AsyncValue<List<OutputProfile>> profilesState, {
    Size screenSize = const Size(1920, 1080),
    Key? key,
  }) {
    return ProviderScope(
      key: key ?? UniqueKey(),
      overrides: [
        outputProfilesControllerProvider.overrideWith(
          () => MockOutputProfilesController(profilesState),
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
      id: id,
      slug: slug,
      workflowId: 'wf_test',
      name: I18nText(translations: {'en': name, 'fi': name}),
    );
  }

  group('OutputProfileListView Widget Tests', () {
    testWidgets(
      'test_output_profile_list_view_empty_and_error_states',
      (tester) async {
        // 1. Empty state: 0 profiles
        await tester.pumpWidget(createTestWidget(const AsyncData([])));
        await tester.pumpAndSettle();

        expect(find.text('No Output Profiles defined.'), findsOneWidget);
        expect(find.text('Showing 0 of 0 items'), findsOneWidget);

        // 2. Search miss: matching 0 items
        final profiles = [createProfile('prf_1', 'Executive Summary', 'exec-sum')];
        await tester.pumpWidget(createTestWidget(AsyncData(profiles)));
        await tester.pumpAndSettle();

        await tester.enterText(find.byType(TextField), 'NonexistentQuery');
        await tester.pumpAndSettle();

        expect(find.text('No matching items found.'), findsOneWidget);
        expect(find.text('Showing 0 of 1 items'), findsOneWidget);

        // 3. Error state: AsyncError emitted
        final testError = AppException.validation('Network failure');
        await tester.pumpWidget(
          createTestWidget(AsyncError(testError, StackTrace.current)),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
      },
    );

    testWidgets(
      'test_master_views_4k_display_containment',
      (tester) async {
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
              widget is ConstrainedBox &&
              widget.constraints.maxWidth == 1200.0,
        );
        expect(constrainedBoxFinder, findsOneWidget);

        final box = tester.renderObject(constrainedBoxFinder) as RenderBox;
        expect(box.size.width, lessThanOrEqualTo(1200.0));
      },
    );

    testWidgets(
      'test_output_profile_list_view_virtualized_rendering',
      (tester) async {
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
      },
    );

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
  });
}
