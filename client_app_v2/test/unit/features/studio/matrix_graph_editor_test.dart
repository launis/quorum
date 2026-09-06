import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Widget buildTestableWidget({
    required MatrixSynthesisGroup group,
    required ValueChanged<MatrixSynthesisGroup> onUpdate,
    required List<PromptBlock> blocks,
    Locale locale = const Locale('fi'),
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
        body: SingleChildScrollView(
          child: MatrixGraphItemEditor(
            index: 0,
            group: group,
            onUpdate: onUpdate,
            onDelete: () {},
            allowedBlockIds: const {},
            promptBlocksState: AsyncValue.data(blocks),
          ),
        ),
      ),
    );
  }

  group('MatrixGraphItemEditor Slot & ViewType Constraints', () {
    final matrixBlock1 = MatrixPromptBlock(
      id: 'blk_mat_1',
      slug: 'matrix_1',
      label: const I18nText(translations: {'en': 'Matrix 1'}),
      description: const I18nText(translations: {'en': 'Matrix 1 desc'}),
      scales: const [],
    );
    final matrixBlock2 = MatrixPromptBlock(
      id: 'blk_mat_2',
      slug: 'matrix_2',
      label: const I18nText(translations: {'en': 'Matrix 2'}),
      description: const I18nText(translations: {'en': 'Matrix 2 desc'}),
      scales: const [],
    );
    final matrixBlock3 = MatrixPromptBlock(
      id: 'blk_mat_3',
      slug: 'matrix_3',
      label: const I18nText(translations: {'en': 'Matrix 3'}),
      description: const I18nText(translations: {'en': 'Matrix 3 desc'}),
      scales: const [],
    );
    final nonMatrixBlock = SystemRulePromptBlock(
      id: 'blk_rule_1',
      slug: 'rule_1',
      label: const I18nText(translations: {'en': 'Rule 1'}),
      description: const I18nText(translations: {'en': 'Rule 1 desc'}),
    );

    final allBlocks = [
      matrixBlock1,
      matrixBlock2,
      matrixBlock3,
      nonMatrixBlock,
    ];

    testWidgets(
      'Only matrix category prompt blocks are displayed for selection',
      (tester) async {
        final group = MatrixSynthesisGroup(
          id: 'grp_test',
          title: const I18nText(translations: {'en': 'Test Group'}),
          targetBlocks: const [],
          viewType: PresetView.metrics1d,
        );

        await tester.pumpWidget(
          buildTestableWidget(
            group: group,
            onUpdate: (_) {},
            blocks: allBlocks,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Matrix 1 (blk_mat_1)'), findsOneWidget);
        expect(find.text('Matrix 2 (blk_mat_2)'), findsOneWidget);
        expect(find.text('Matrix 3 (blk_mat_3)'), findsOneWidget);
        expect(find.text('Rule 1 (blk_rule_1)'), findsNothing);
      },
    );

    testWidgets('1D Metrics mode enforces single selection (max 1)', (
      tester,
    ) async {
      MatrixSynthesisGroup currentGroup = MatrixSynthesisGroup(
        id: 'grp_test',
        title: const I18nText(translations: {'en': 'Test Group'}),
        targetBlocks: ['blk_mat_1'],
        viewType: PresetView.metrics1d,
      );

      await tester.pumpWidget(
        buildTestableWidget(
          group: currentGroup,
          onUpdate: (updated) => currentGroup = updated,
          blocks: allBlocks,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('1 / 1 valittu'), findsOneWidget);

      // Selecting a different matrix in 1D replaces the choice
      await tester.tap(find.text('Matrix 2 (blk_mat_2)'));
      await tester.pumpAndSettle();

      expect(currentGroup.targetBlocks, ['blk_mat_2']);
    });

    testWidgets('2D Compare mode enforces max 2 selections', (tester) async {
      MatrixSynthesisGroup currentGroup = MatrixSynthesisGroup(
        id: 'grp_test',
        title: const I18nText(translations: {'en': 'Test Group'}),
        targetBlocks: ['blk_mat_1'],
        viewType: PresetView.compare2d,
      );

      await tester.pumpWidget(
        buildTestableWidget(
          group: currentGroup,
          onUpdate: (updated) => currentGroup = updated,
          blocks: allBlocks,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('1 / 2 valittu'), findsOneWidget);

      // Add 2nd block
      await tester.tap(find.text('Matrix 2 (blk_mat_2)'));
      await tester.pumpAndSettle();

      expect(currentGroup.targetBlocks, ['blk_mat_1', 'blk_mat_2']);
    });

    testWidgets(
      'Switching viewType trims targetBlocks exceeding the new limit',
      (tester) async {
        MatrixSynthesisGroup currentGroup = MatrixSynthesisGroup(
          id: 'grp_test',
          title: const I18nText(translations: {'en': 'Test Group'}),
          targetBlocks: ['blk_mat_1', 'blk_mat_2', 'blk_mat_3'],
          viewType: PresetView.matrix3d,
        );

        await tester.pumpWidget(
          buildTestableWidget(
            group: currentGroup,
            onUpdate: (updated) => currentGroup = updated,
            blocks: allBlocks,
          ),
        );
        await tester.pumpAndSettle();

        // Tap 1D segment
        await tester.tap(find.text('1D Mittari'));
        await tester.pumpAndSettle();

        expect(currentGroup.viewType, PresetView.metrics1d);
        expect(currentGroup.targetBlocks, ['blk_mat_1']);
      },
    );

    testWidgets('Unselected FilterChips are disabled when max quota is reached', (
      tester,
    ) async {
      MatrixSynthesisGroup currentGroup = MatrixSynthesisGroup(
        id: 'grp_test',
        title: const I18nText(translations: {'en': 'Test Group'}),
        targetBlocks: ['blk_mat_1', 'blk_mat_2'],
        viewType: PresetView.compare2d,
      );

      await tester.pumpWidget(
        buildTestableWidget(
          group: currentGroup,
          onUpdate: (updated) => currentGroup = updated,
          blocks: allBlocks,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('2 / 2 valittu'), findsOneWidget);

      // Verify Matrix 3 FilterChip is disabled (onSelected is null)
      final chipFinder = find.widgetWithText(FilterChip, 'Matrix 3 (blk_mat_3)');
      expect(chipFinder, findsOneWidget);
      final FilterChip chipWidget = tester.widget(chipFinder);
      expect(chipWidget.onSelected, isNull);
    });

    testWidgets('Move up and move down callbacks trigger properly', (tester) async {
      bool movedUp = false;
      bool movedDown = false;

      final group = MatrixSynthesisGroup(
        id: 'grp_test',
        title: const I18nText(translations: {'en': 'Test Group'}),
        targetBlocks: ['blk_mat_1'],
        viewType: PresetView.metrics1d,
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: const [Locale('en'), Locale('fi')],
          home: Scaffold(
            body: MatrixGraphItemEditor(
              index: 1,
              group: group,
              onUpdate: (_) {},
              onDelete: () {},
              allowedBlockIds: const {},
              promptBlocksState: AsyncValue.data(allBlocks),
              onMoveUp: () => movedUp = true,
              onMoveDown: () => movedDown = true,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Tap move up
      await tester.tap(find.byIcon(Icons.arrow_upward));
      await tester.pumpAndSettle();
      expect(movedUp, isTrue);

      // Tap move down
      await tester.tap(find.byIcon(Icons.arrow_downward));
      await tester.pumpAndSettle();
      expect(movedDown, isTrue);
    });
  });
}
