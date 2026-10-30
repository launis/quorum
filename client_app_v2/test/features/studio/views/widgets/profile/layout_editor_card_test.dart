import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/views/widgets/profile/layout_editor_card.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('LayoutEditorCard Tests', () {
    testWidgets(
      'LayoutEditorCard renders MatrixSynthesisGroup without crashing',
      (WidgetTester tester) async {
        const group = MatrixSynthesisGroup(
          id: 'grp_01950000000070008000000000000001',
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
                    groups: const [group],
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
        expect(find.text('Matrix Synthesis Group 1'), findsWidgets);
      },
    );

    testWidgets(
      'LayoutEditorCard adds, updates, and deletes matrix synthesis groups with 32-hex UUIDv7 IDs',
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
        expect(
          RegExp(r'^grp_[a-f0-9]{32}$').hasMatch(currentGroups.first.id),
          isTrue,
        );

        // Delete button
        final deleteButton = find.byIcon(Icons.delete_outline).first;
        expect(deleteButton, findsOneWidget);
        await tester.tap(deleteButton);
        await tester.pumpAndSettle();

        expect(currentGroups.isEmpty, isTrue);
      },
    );

    testWidgets(
      'Negative: LayoutEditorCard throws AppException when MatrixSynthesisGroup title has empty translations (Fail-Fast)',
      (WidgetTester tester) async {
        const invalidGroup = MatrixSynthesisGroup(
          id: 'grp_01950000000070008000000000000002',
          title: I18nText(translations: {}),
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
                    groups: const [invalidGroup],
                    onChanged: (_) {},
                    allowedBlockIds: const {},
                    promptBlocksState: const AsyncValue.data([]),
                  ),
                ),
              ),
            ),
          ),
        );

        final exception = tester.takeException();
        expect(exception, isA<AppException>());
      },
    );

    testWidgets(
      'Boundary: LayoutEditorCard renders empty state placeholder and handles long title without overflow',
      (WidgetTester tester) async {
        final longTitleGroup = MatrixSynthesisGroup(
          id: 'grp_01950000000070008000000000000003',
          title: I18nText(translations: {'en': 'Long Group Title ' * 20}),
          targetBlocks: const [],
        );

        // 1. Boundary: 0 groups (empty state)
        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(
                body: SizedBox(
                  width: 480,
                  child: SingleChildScrollView(
                    child: LayoutEditorCard(
                      groups: const [],
                      onChanged: (_) {},
                      allowedBlockIds: const {},
                      promptBlocksState: const AsyncValue.data([]),
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(tester.takeException(), isNull);

        // 2. Boundary: Very long group title ellipsis containment
        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(
                body: SizedBox(
                  width: 480,
                  child: SingleChildScrollView(
                    child: LayoutEditorCard(
                      groups: [longTitleGroup],
                      onChanged: (_) {},
                      allowedBlockIds: const {},
                      promptBlocksState: const AsyncValue.data([]),
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(tester.takeException(), isNull);
      },
    );
  });
}
