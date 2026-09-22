import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/widgets/studio_master_header.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Widget createTestWidget(Widget child, {Locale locale = const Locale('en')}) {
    return MaterialApp(
      locale: locale,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en'), Locale('fi')],
      home: Scaffold(body: child),
    );
  }

  group('StudioMasterHeader Widget Tests', () {
    testWidgets('test_studio_master_header_rendering_and_search_trigger', (
      tester,
    ) async {
      String query = 'diag';
      bool actionTriggered = false;

      await tester.pumpWidget(
        createTestWidget(
          StudioMasterHeader(
            title: 'Workflows',
            subtitle: 'Manage master DAG blueprints',
            searchQuery: query,
            onSearchChanged: (val) => query = val,
            itemCount: 3,
            totalCount: 10,
            actionLabel: 'New Workflow',
            actionIcon: Icons.add,
            onAction: () => actionTriggered = true,
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify title & subtitle
      expect(find.text('Workflows'), findsOneWidget);
      expect(find.text('Manage master DAG blueprints'), findsOneWidget);

      // Verify count pill badge in English
      expect(find.text('Showing 3 of 10 items'), findsOneWidget);

      // Verify search input has initial text 'diag' and clear button
      expect(find.widgetWithText(TextField, 'diag'), findsOneWidget);
      expect(find.byIcon(Icons.clear), findsOneWidget);

      // Clear query trigger
      await tester.tap(find.byIcon(Icons.clear));
      await tester.pumpAndSettle();
      expect(query, '');

      // Action button trigger
      expect(find.text('New Workflow'), findsOneWidget);
      await tester.tap(find.text('New Workflow'));
      await tester.pumpAndSettle();
      expect(actionTriggered, isTrue);
    });

    testWidgets('renders localized count pill in Finnish locale', (
      tester,
    ) async {
      await tester.pumpWidget(
        createTestWidget(
          StudioMasterHeader(
            title: 'Työnkulut',
            searchQuery: '',
            onSearchChanged: (_) {},
            itemCount: 3,
            totalCount: 10,
          ),
          locale: const Locale('fi'),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('3 / 10 kohteesta'), findsOneWidget);
    });

    testWidgets('typing into search field fires onSearchChanged', (
      tester,
    ) async {
      String changedQuery = '';
      await tester.pumpWidget(
        createTestWidget(
          StudioMasterHeader(
            title: 'Test Title',
            searchQuery: '',
            onSearchChanged: (val) => changedQuery = val,
            itemCount: 0,
            totalCount: 0,
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'matrix');
      await tester.pumpAndSettle();
      expect(changedQuery, 'matrix');
    });

    testWidgets('renders leading and bottom widgets when provided', (
      tester,
    ) async {
      await tester.pumpWidget(
        createTestWidget(
          StudioMasterHeader(
            title: 'Title',
            searchQuery: '',
            onSearchChanged: (_) {},
            itemCount: 1,
            totalCount: 1,
            leading: const Icon(Icons.star, key: Key('header-leading')),
            bottom: const Text('Bottom Content', key: Key('header-bottom')),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('header-leading')), findsOneWidget);
      expect(find.byKey(const Key('header-bottom')), findsOneWidget);
    });
  });
}
