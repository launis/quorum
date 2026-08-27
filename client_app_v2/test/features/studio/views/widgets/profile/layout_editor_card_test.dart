import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/views/widgets/profile/layout_editor_card.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('LayoutEditorCard Tests', () {
    testWidgets(
      'LayoutEditorCard renders MatrixSynthesisGroup without crashing',
      (WidgetTester tester) async {
        final group = const MatrixSynthesisGroup(
          id: 'grp_1111111111111111',
          title: I18nText(translations: {'en': 'Matrix Synthesis Group 1'}),
          targetBlocks: [],
        );

        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(
                body: SingleChildScrollView(
                  child: LayoutEditorCard(
                    groups: [group],
                    onChanged: (_) {},
                    allowedBlockIds: const {},
                    promptBlocksState: const AsyncValue.data([]),
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(LayoutEditorCard), findsOneWidget);
      },
    );

    testWidgets(
      'LayoutEditorCard adds and deletes matrix synthesis groups via callbacks',
      (WidgetTester tester) async {
        List<MatrixSynthesisGroup> currentGroups = [];

        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(
                body: SingleChildScrollView(
                  child: StatefulBuilder(
                    builder: (context, setState) {
                      return LayoutEditorCard(
                        groups: currentGroups,
                        onChanged: (newList) {
                          setState(() {
                            currentGroups = newList;
                          });
                        },
                        allowedBlockIds: const {},
                        promptBlocksState: const AsyncValue.data([]),
                      );
                    },
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Tap Add button
        final addButton = find.byIcon(Icons.add_box);
        expect(addButton, findsOneWidget);
        await tester.tap(addButton);
        await tester.pumpAndSettle();

        expect(currentGroups.length, equals(1));

        // Delete button
        final deleteButton = find.byIcon(Icons.delete_outline).first;
        expect(deleteButton, findsOneWidget);
        await tester.tap(deleteButton);
        await tester.pumpAndSettle();

        expect(currentGroups.isEmpty, isTrue);
      },
    );
  });
}
