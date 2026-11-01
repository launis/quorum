import 'package:client_app/features/shell/presentation/widgets/admin_sidebar.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _buildTestWidget({
  required int selectedIndex,
  required ValueChanged<int> onDestinationSelected,
  Locale locale = const Locale('en'),
}) {
  return MaterialApp(
    locale: locale,
    localizationsDelegates: const [
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ],
    supportedLocales: const [Locale('en'), Locale('fi')],
    home: Scaffold(
      body: AdminSidebar(
        selectedIndex: selectedIndex,
        onDestinationSelected: onDestinationSelected,
      ),
    ),
  );
}

void main() {
  group('AdminSidebar Hardening Tests', () {
    testWidgets(
      'Positive: renders 5 localized NavigationRail destinations and dispatches selected index on tap',
      (WidgetTester tester) async {
        int? tappedIndex;

        await tester.pumpWidget(
          _buildTestWidget(
            selectedIndex: 1,
            onDestinationSelected: (index) => tappedIndex = index,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(NavigationRail), findsOneWidget);
        expect(find.byIcon(Icons.schema), findsOneWidget);
        expect(find.byIcon(Icons.auto_graph_outlined), findsOneWidget);

        await tester.tap(find.byIcon(Icons.analytics_outlined));
        await tester.pumpAndSettle();

        expect(tappedIndex, equals(2));
      },
    );

    testWidgets(
      'Boundary 1 (Min=0, Max=4): accurately highlights active icons at lower and upper valid index bounds',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          _buildTestWidget(selectedIndex: 0, onDestinationSelected: (_) {}),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.auto_graph), findsOneWidget);
        expect(find.byIcon(Icons.api_outlined), findsOneWidget);

        await tester.pumpWidget(
          _buildTestWidget(
            selectedIndex: 4,
            onDestinationSelected: (_) {},
            locale: const Locale('fi'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.api), findsOneWidget);
        expect(find.byIcon(Icons.auto_graph_outlined), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 2 (Below min=-1): throws AssertionError when selectedIndex is negative',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          _buildTestWidget(selectedIndex: -1, onDestinationSelected: (_) {}),
        );
        expect(tester.takeException(), isA<AssertionError>());
      },
    );

    testWidgets(
      'Negative/Boundary 3 (Above max=5): throws AssertionError when selectedIndex exceeds destination count',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          _buildTestWidget(selectedIndex: 5, onDestinationSelected: (_) {}),
        );
        expect(tester.takeException(), isA<AssertionError>());
      },
    );
  });
}
