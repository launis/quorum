import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  const String validGrpId = 'grp_01964528b7707d5081986327cf9a6e81';
  const String validBlkId1 = 'blk_01964528b7707d5081986327cf9a6e81';
  const String validBlkId2 = 'blk_01964528b7707d5081986327cf9a6e82';
  const String validBlkId3 = 'blk_01964528b7707d5081986327cf9a6e83';
  const String validRuleBlkId = 'blk_01964528b7707d5081986327cf9a6e84';

  const matrixBlock1 = PromptBlock.matrix(
    id: validBlkId1,
    slug: 'matrix_1',
    label: I18nText(translations: {'en': 'Matrix 1'}),
    description: I18nText(translations: {'en': 'Matrix 1 desc'}),
    scales: [],
  );
  const matrixBlock2 = PromptBlock.matrix(
    id: validBlkId2,
    slug: 'matrix_2',
    label: I18nText(translations: {'en': 'Matrix 2'}),
    description: I18nText(translations: {'en': 'Matrix 2 desc'}),
    scales: [],
  );
  const matrixBlock3 = PromptBlock.matrix(
    id: validBlkId3,
    slug: 'matrix_3',
    label: I18nText(translations: {'en': 'Matrix 3'}),
    description: I18nText(translations: {'en': 'Matrix 3 desc'}),
    scales: [],
  );
  const nonMatrixBlock = PromptBlock.systemRule(
    id: validRuleBlkId,
    slug: 'rule_1',
    label: I18nText(translations: {'en': 'Rule 1'}),
    description: I18nText(translations: {'en': 'Rule 1 desc'}),
  );

  final allBlocks = <PromptBlock>[
    matrixBlock1,
    matrixBlock2,
    matrixBlock3,
    nonMatrixBlock,
  ];

  Widget buildTestableWidget({
    required MatrixSynthesisGroup group,
    required ValueChanged<MatrixSynthesisGroup> onUpdate,
    VoidCallback? onDelete,
    int index = 0,
    Set<String> allowedBlockIds = const {},
    AsyncValue<List<PromptBlock>>? promptBlocksState,
    Locale locale = const Locale('en'),
    VoidCallback? onMoveUp,
    VoidCallback? onMoveDown,
  }) {
    return MaterialApp(
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: Scaffold(
        body: SingleChildScrollView(
          child: MatrixGraphItemEditor(
            index: index,
            group: group,
            onUpdate: onUpdate,
            onDelete: onDelete ?? () {},
            allowedBlockIds: allowedBlockIds,
            promptBlocksState: promptBlocksState ?? AsyncValue.data(allBlocks),
            onMoveUp: onMoveUp,
            onMoveDown: onMoveDown,
          ),
        ),
      ),
    );
  }

  group('MatrixGraphItemEditor Positive & Functional Tests', () {
    testWidgets(
      'displays only matrix category prompt blocks filtered by allowedBlockIds',
      (WidgetTester tester) async {
        const group = MatrixSynthesisGroup(
          id: validGrpId,
          title: I18nText(translations: {'en': 'Test Group'}),
          targetBlocks: [],
          viewType: PresetView.metrics1d,
        );

        await tester.pumpWidget(
          buildTestableWidget(
            group: group,
            onUpdate: (_) {},
            allowedBlockIds: const {validBlkId1, validBlkId2, validRuleBlkId},
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Matrix 1'), findsOneWidget);
        expect(find.text('Matrix 2'), findsOneWidget);
        expect(find.text('Matrix 3'), findsNothing);
        expect(find.text('Rule 1'), findsNothing);
      },
    );

    testWidgets(
      'enforces single selection (max 1) in PresetView.metrics1d and replaces selection on tap',
      (WidgetTester tester) async {
        MatrixSynthesisGroup currentGroup = const MatrixSynthesisGroup(
          id: validGrpId,
          title: I18nText(translations: {'en': 'Test Group'}),
          targetBlocks: [validBlkId1],
          viewType: PresetView.metrics1d,
        );

        await tester.pumpWidget(
          buildTestableWidget(
            group: currentGroup,
            onUpdate: (updated) => currentGroup = updated,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Matrix 2'));
        await tester.pumpAndSettle();

        expect(currentGroup.targetBlocks, equals([validBlkId2]));
      },
    );

    testWidgets(
      'enforces max 2 selections in PresetView.compare2d and disables unselected chips at quota',
      (WidgetTester tester) async {
        MatrixSynthesisGroup currentGroup = const MatrixSynthesisGroup(
          id: validGrpId,
          title: I18nText(translations: {'en': 'Test Group'}),
          targetBlocks: [validBlkId1, validBlkId2],
          viewType: PresetView.compare2d,
        );

        await tester.pumpWidget(
          buildTestableWidget(
            group: currentGroup,
            onUpdate: (updated) => currentGroup = updated,
          ),
        );
        await tester.pumpAndSettle();

        final chip3Finder = find.widgetWithText(FilterChip, 'Matrix 3');
        expect(chip3Finder, findsOneWidget);
        final FilterChip chip3 = tester.widget(chip3Finder);
        expect(chip3.onSelected, isNull);

        // Deselecting Matrix 1 removes it from targetBlocks
        await tester.tap(find.text('Matrix 1'));
        await tester.pumpAndSettle();
        expect(currentGroup.targetBlocks, equals([validBlkId2]));
      },
    );

    testWidgets(
      'triggers onMoveUp, onMoveDown, and onDelete callbacks when buttons are tapped',
      (WidgetTester tester) async {
        bool movedUp = false;
        bool movedDown = false;
        bool deleted = false;

        const group = MatrixSynthesisGroup(
          id: validGrpId,
          title: I18nText(translations: {'en': 'Test Group'}),
          targetBlocks: [validBlkId1],
          viewType: PresetView.metrics1d,
        );

        await tester.pumpWidget(
          buildTestableWidget(
            index: 1,
            group: group,
            onUpdate: (_) {},
            onDelete: () => deleted = true,
            onMoveUp: () => movedUp = true,
            onMoveDown: () => movedDown = true,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.arrow_upward));
        await tester.pumpAndSettle();
        expect(movedUp, isTrue);

        await tester.tap(find.byIcon(Icons.arrow_downward));
        await tester.pumpAndSettle();
        expect(movedDown, isTrue);

        await tester.tap(find.byIcon(Icons.delete_outline));
        await tester.pumpAndSettle();
        expect(deleted, isTrue);
      },
    );
  });

  group('MatrixGraphItemEditor ISTQB Negative & Boundary Tests', () {
    testWidgets(
      'Negative ISTQB: throws AppException when group title has empty translations',
      (WidgetTester tester) async {
        const invalidGroup = MatrixSynthesisGroup(
          id: validGrpId,
          title: I18nText(translations: {}),
          targetBlocks: [],
          viewType: PresetView.metrics1d,
        );

        await tester.pumpWidget(
          buildTestableWidget(group: invalidGroup, onUpdate: (_) {}),
        );

        final exception = tester.takeException();
        expect(exception, isA<AppException>());
      },
    );

    testWidgets(
      'Boundary ISTQB: trims targetBlocks from 3 (max) to 1 (min) when switching from matrix3d to textOnly',
      (WidgetTester tester) async {
        MatrixSynthesisGroup currentGroup = const MatrixSynthesisGroup(
          id: validGrpId,
          title: I18nText(translations: {'en': 'Test Group'}),
          targetBlocks: [validBlkId1, validBlkId2, validBlkId3],
          viewType: PresetView.matrix3d,
        );

        await tester.pumpWidget(
          buildTestableWidget(
            group: currentGroup,
            onUpdate: (updated) => currentGroup = updated,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.article_outlined));
        await tester.pumpAndSettle();

        expect(currentGroup.viewType, equals(PresetView.textOnly));
        expect(currentGroup.targetBlocks, equals([validBlkId1]));
      },
    );

    testWidgets(
      'Boundary ISTQB: renders empty-matrix warning state cleanly on AsyncError and narrow viewport (360x640)',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 640);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const group = MatrixSynthesisGroup(
          id: validGrpId,
          title: I18nText(
            translations: {
              'en': 'Very Long Synthesis Group Title For Overflow Verification',
            },
          ),
          targetBlocks: [],
          viewType: PresetView.metrics1d,
        );

        await tester.pumpWidget(
          buildTestableWidget(
            group: group,
            onUpdate: (_) {},
            promptBlocksState: AsyncValue.error(
              Exception('Network error'),
              StackTrace.empty,
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(MatrixGraphItemEditor), findsOneWidget);
        expect(find.byType(FilterChip), findsNothing);
        expect(tester.takeException(), isNull);
      },
    );
  });
}
