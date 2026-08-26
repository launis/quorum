import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/views/widgets/profile/layout_editor_card.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('LayoutEditorCard Tests', () {
    testWidgets(
      'LayoutEditorCard renders matrixSummary PresetView without crashing',
      (WidgetTester tester) async {
        final layout = const OutputLayoutBlock(
          presetView: PresetView.matrixSummary,
          title: I18nText(translations: {'en': 'Matrix Summary'}),
          textDeliveryMode: TextDeliveryMode.full,
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
                    layouts: [layout],
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
      'LayoutEditorCard adds and deletes layout blocks via callbacks',
      (WidgetTester tester) async {
        List<OutputLayoutBlock> currentLayouts = [];

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
                        layouts: currentLayouts,
                        onChanged: (newList) {
                          setState(() {
                            currentLayouts = newList;
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

        expect(currentLayouts.length, equals(1));

        // Delete button
        final deleteButton = find.byIcon(Icons.delete_outline);
        expect(deleteButton, findsOneWidget);
        await tester.tap(deleteButton);
        await tester.pumpAndSettle();

        expect(currentLayouts.isEmpty, isTrue);
      },
    );
  });
}
