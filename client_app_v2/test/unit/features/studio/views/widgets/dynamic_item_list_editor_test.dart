import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/views/widgets/dynamic_item_list_editor.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Widget buildTestHarness({
    required List<String> initialItems,
    required ValueChanged<List<String>> onChanged,
    String addButtonLabel = 'Add Criterion',
    String? placeholder = 'Enter criterion...',
    bool enabled = true,
  }) {
    var currentItems = List<String>.from(initialItems);
    return MaterialApp(
      locale: const Locale('en'),
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: StatefulBuilder(
        builder: (context, setState) {
          return Scaffold(
            body: DynamicItemListEditor(
              items: currentItems,
              addButtonLabel: addButtonLabel,
              placeholder: placeholder,
              enabled: enabled,
              onChanged: (updated) {
                setState(() {
                  currentItems = updated;
                });
                onChanged(updated);
              },
            ),
          );
        },
      ),
    );
  }

  group('DynamicItemListEditor Widget Tests', () {
    testWidgets(
      'Positive: renders numbered badges, adds item, edits text, and deletes first item cleanly',
      (WidgetTester tester) async {
        List<String> captured = <String>['First rule', 'Second rule'];

        await tester.pumpWidget(
          buildTestHarness(
            initialItems: captured,
            onChanged: (updated) => captured = updated,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('1'), findsOneWidget);
        expect(find.text('2'), findsOneWidget);
        expect(
          find.widgetWithText(TextFormField, 'First rule'),
          findsOneWidget,
        );
        expect(
          find.widgetWithText(TextFormField, 'Second rule'),
          findsOneWidget,
        );
        expect(find.byTooltip('Delete'), findsNWidgets(2));

        // Add new item
        await tester.tap(find.text('Add Criterion'));
        await tester.pumpAndSettle();
        expect(captured.length, 3);
        expect(find.text('3'), findsOneWidget);

        // Edit the third item
        final fields = find.byType(TextFormField);
        await tester.enterText(fields.at(2), 'Third rule');
        await tester.pumpAndSettle();
        expect(captured[2], 'Third rule');

        // Delete the FIRST item and verify remaining controllers sync without stale state
        final deleteButtons = find.byIcon(Icons.delete_outline);
        await tester.tap(deleteButtons.first);
        await tester.pumpAndSettle();

        expect(captured, equals(<String>['Second rule', 'Third rule']));
        expect(find.widgetWithText(TextFormField, 'First rule'), findsNothing);
        expect(
          find.widgetWithText(TextFormField, 'Second rule'),
          findsOneWidget,
        );
        expect(
          find.widgetWithText(TextFormField, 'Third rule'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Negative/Boundary 1: empty initial items list renders zero rows and only add button',
      (WidgetTester tester) async {
        List<String> captured = <String>[];

        await tester.pumpWidget(
          buildTestHarness(
            initialItems: captured,
            onChanged: (updated) => captured = updated,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(TextFormField), findsNothing);
        expect(find.byIcon(Icons.delete_outline), findsNothing);
        expect(find.text('Add Criterion'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 2: disabled state blocks adding, editing, and deleting items',
      (WidgetTester tester) async {
        int callbackCount = 0;

        await tester.pumpWidget(
          buildTestHarness(
            initialItems: const <String>['Locked item'],
            enabled: false,
            onChanged: (_) => callbackCount++,
          ),
        );
        await tester.pumpAndSettle();

        final textField = tester.widget<TextFormField>(
          find.byType(TextFormField),
        );
        expect(textField.enabled, isFalse);

        final deleteBtn = tester.widget<IconButton>(find.byType(IconButton));
        expect(deleteBtn.onPressed, isNull);

        final addBtn = tester.widget<OutlinedButton>(
          find.byType(OutlinedButton),
        );
        expect(addBtn.onPressed, isNull);

        await tester.tap(find.text('Add Criterion'), warnIfMissed: false);
        await tester.tap(
          find.byIcon(Icons.delete_outline),
          warnIfMissed: false,
        );
        await tester.pumpAndSettle();

        expect(callbackCount, 0);
      },
    );
  });
}
