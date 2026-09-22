import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/workflows_master_view.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockWorkflowsController extends WorkflowsController {
  final List<Workflow> workflows;
  MockWorkflowsController([this.workflows = const []]);

  @override
  FutureOr<List<Workflow>> build() async {
    return workflows;
  }
}

void main() {
  Widget createTestWidget(
    List<Workflow> workflows, {
    Size screenSize = const Size(1920, 1080),
  }) {
    return ProviderScope(
      overrides: [
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(workflows),
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

  List<Workflow> generateMockWorkflows(int count) {
    return List.generate(
      count,
      (i) => Workflow(
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
          id: 'wf_alpha',
          slug: 'alpha-analysis',
          name: const I18nText(translations: {'en': 'Alpha Diagnostic'}),
          description: const I18nText(translations: {'en': 'Alpha Desc'}),
          modelRegistryId: 'mr_1',
        ),
        Workflow(
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
  });
}
