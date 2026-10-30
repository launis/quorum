import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  const String validPrfId = 'prf_01964528b7707d5081986327cf9a6e82';
  const String validWfId = 'wf_01964528b7707d5081986327cf9a6e82';
  const String validBlkId1 = 'blk_01964528b7707d5081986327cf9a6e81';
  const String validBlkId2 = 'blk_01964528b7707d5081986327cf9a6e82';
  const String validGrpId1 = 'grp_01964528b7707d5081986327cf9a6e81';
  const String validGrpId2 = 'grp_01964528b7707d5081986327cf9a6e82';

  OutputProfile createTestProfile({
    List<TargetBlockType> targetBlockOrder = const [
      TargetBlockType.matrixGraphsBlock,
    ],
    List<MatrixSynthesisGroup> matrixSynthesisGroups = const [],
    int? matrixGraphLengthConstraint,
  }) {
    return OutputProfile(
      id: validPrfId,
      workflowId: validWfId,
      name: const I18nText(translations: {'en': 'Test Profile'}),
      targetBlockOrder: targetBlockOrder,
      matrixSynthesisGroups: matrixSynthesisGroups,
      matrixGraphLengthConstraint: matrixGraphLengthConstraint,
    );
  }

  final mockPromptBlock1 = const PromptBlock.matrix(
    id: validBlkId1,
    slug: 'matrix_block_1',
    label: I18nText(translations: {'en': 'Matrix Block 1'}),
    description: I18nText(translations: {'en': 'Matrix block 1 description'}),
    scales: [],
  );

  final mockPromptBlock2 = const PromptBlock.matrix(
    id: validBlkId2,
    slug: 'matrix_block_2',
    label: I18nText(translations: {'en': 'Matrix Block 2'}),
    description: I18nText(translations: {'en': 'Matrix block 2 description'}),
    scales: [],
  );

  Widget buildTestHarness({
    required OutputProfile initialPayload,
    required void Function(OutputProfile) onUpdate,
    Set<String> allowedBlockIds = const {validBlkId1, validBlkId2},
    AsyncValue<List<PromptBlock>>? promptBlocksState,
    Locale locale = const Locale('en'),
  }) {
    return MaterialApp(
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: Scaffold(
        body: SingleChildScrollView(
          child: StatefulBuilder(
            builder: (context, setState) {
              OutputProfile currentPayload = initialPayload;
              return MatrixGraphsBlockCard(
                payload: currentPayload,
                updatePayload: (newPayload) {
                  setState(() {
                    currentPayload = newPayload;
                  });
                  onUpdate(newPayload);
                },
                allowedBlockIds: allowedBlockIds,
                promptBlocksState:
                    promptBlocksState ??
                    AsyncValue.data([mockPromptBlock1, mockPromptBlock2]),
              );
            },
          ),
        ),
      ),
    );
  }

  group('MatrixGraphsBlockCard Positive & Functional Tests', () {
    testWidgets(
      'renders empty state and generates 32-hex RFC 9562 UUIDv7 grp_ ID on add',
      (WidgetTester tester) async {
        OutputProfile payload = createTestProfile();

        await tester.pumpWidget(
          buildTestHarness(
            initialPayload: payload,
            onUpdate: (newPayload) => payload = newPayload,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(MatrixGraphsBlockCard), findsOneWidget);
        expect(find.byType(FilledButton), findsOneWidget);

        await tester.tap(find.byType(FilledButton));
        await tester.pumpAndSettle();

        expect(payload.matrixSynthesisGroups.length, equals(1));
        final generatedGroup = payload.matrixSynthesisGroups.first;
        expect(
          RegExp(
            r'^grp_[0-9a-f]{12}7[0-9a-f]{19}$',
          ).hasMatch(generatedGroup.id),
          isTrue,
        );
        expect(generatedGroup.title.translations['en'], equals('Group 1'));
        expect(generatedGroup.title.translations['fi'], equals('Ryhmä 1'));
      },
    );

    testWidgets(
      'toggles TargetBlockType.matrixGraphsBlock in targetBlockOrder on switch tap',
      (WidgetTester tester) async {
        OutputProfile payload = createTestProfile(
          targetBlockOrder: [TargetBlockType.matrixGraphsBlock],
        );

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: StatefulBuilder(
                  builder: (context, setState) {
                    return MatrixGraphsBlockCard(
                      payload: payload,
                      updatePayload: (newPayload) {
                        setState(() {
                          payload = newPayload;
                        });
                      },
                      allowedBlockIds: const {validBlkId1},
                      promptBlocksState: AsyncValue.data([mockPromptBlock1]),
                    );
                  },
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          payload.targetBlockOrder.contains(TargetBlockType.matrixGraphsBlock),
          isFalse,
        );

        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          payload.targetBlockOrder.contains(TargetBlockType.matrixGraphsBlock),
          isTrue,
        );
      },
    );

    testWidgets(
      'handles moveUp, moveDown, onUpdate, and onDelete on synthesis groups',
      (WidgetTester tester) async {
        const group1 = MatrixSynthesisGroup(
          id: validGrpId1,
          title: I18nText(translations: {'en': 'Alpha Group'}),
          targetBlocks: [validBlkId1],
          viewType: PresetView.metrics1d,
        );
        const group2 = MatrixSynthesisGroup(
          id: validGrpId2,
          title: I18nText(translations: {'en': 'Beta Group'}),
          targetBlocks: [validBlkId2],
          viewType: PresetView.compare2d,
        );

        OutputProfile payload = createTestProfile(
          matrixSynthesisGroups: [group1, group2],
        );

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: StatefulBuilder(
                  builder: (context, setState) {
                    return MatrixGraphsBlockCard(
                      payload: payload,
                      updatePayload: (newPayload) {
                        setState(() {
                          payload = newPayload;
                        });
                      },
                      allowedBlockIds: const {validBlkId1, validBlkId2},
                      promptBlocksState: AsyncValue.data([
                        mockPromptBlock1,
                        mockPromptBlock2,
                      ]),
                    );
                  },
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Move group 1 down (index 0 -> index 1)
        final moveDownBtn = find.byIcon(Icons.arrow_downward);
        expect(moveDownBtn, findsOneWidget);
        await tester.tap(moveDownBtn);
        await tester.pumpAndSettle();

        expect(payload.matrixSynthesisGroups[0].id, equals(validGrpId2));
        expect(payload.matrixSynthesisGroups[1].id, equals(validGrpId1));

        // Move group 1 back up (index 1 -> index 0)
        final moveUpBtn = find.byIcon(Icons.arrow_upward);
        expect(moveUpBtn, findsOneWidget);
        await tester.tap(moveUpBtn);
        await tester.pumpAndSettle();

        expect(payload.matrixSynthesisGroups[0].id, equals(validGrpId1));
        expect(payload.matrixSynthesisGroups[1].id, equals(validGrpId2));

        // Delete first group
        final deleteBtns = find.byIcon(Icons.delete_outline);
        expect(deleteBtns, findsNWidgets(2));
        await tester.tap(deleteBtns.first);
        await tester.pumpAndSettle();

        expect(payload.matrixSynthesisGroups.length, equals(1));
        expect(payload.matrixSynthesisGroups.first.id, equals(validGrpId2));
      },
    );

    testWidgets(
      'renders matrixGraphLengthConstraint field and updates payload on valid numeric input',
      (WidgetTester tester) async {
        OutputProfile payload = createTestProfile(
          matrixGraphLengthConstraint: 400,
        );

        await tester.pumpWidget(
          buildTestHarness(
            initialPayload: payload,
            onUpdate: (newPayload) => payload = newPayload,
          ),
        );
        await tester.pumpAndSettle();

        final lengthFieldFinder = find.byKey(
          const Key('profile_matrix_graph_length_constraint_field'),
        );
        expect(lengthFieldFinder, findsOneWidget);

        final textFormField = tester.widget<TextFormField>(lengthFieldFinder);
        expect(textFormField.initialValue, '400');

        await tester.enterText(lengthFieldFinder, '550');
        await tester.pumpAndSettle();
        expect(payload.matrixGraphLengthConstraint, 550);

        await tester.enterText(lengthFieldFinder, '');
        await tester.pumpAndSettle();
        expect(payload.matrixGraphLengthConstraint, isNull);
      },
    );
  });

  group('MatrixGraphsBlockCard ISTQB Negative & Boundary Tests', () {
    testWidgets(
      'Negative ISTQB: filters out non-digits in matrixGraphLengthConstraint field via inputFormatters',
      (WidgetTester tester) async {
        OutputProfile payload = createTestProfile(
          matrixGraphLengthConstraint: null,
        );

        await tester.pumpWidget(
          buildTestHarness(
            initialPayload: payload,
            onUpdate: (newPayload) => payload = newPayload,
          ),
        );
        await tester.pumpAndSettle();

        final lengthFieldFinder = find.byKey(
          const Key('profile_matrix_graph_length_constraint_field'),
        );
        await tester.enterText(lengthFieldFinder, 'abc-!@#');
        await tester.pumpAndSettle();

        expect(payload.matrixGraphLengthConstraint, isNull);
      },
    );

    testWidgets(
      'Boundary ISTQB: hides card body when matrixGraphsBlock is excluded from targetBlockOrder',
      (WidgetTester tester) async {
        final payload = createTestProfile(
          targetBlockOrder: const [],
          matrixSynthesisGroups: const [
            MatrixSynthesisGroup(
              id: validGrpId1,
              title: I18nText(translations: {'en': 'Hidden Group'}),
              targetBlocks: [],
            ),
          ],
        );

        await tester.pumpWidget(
          buildTestHarness(initialPayload: payload, onUpdate: (_) {}),
        );
        await tester.pumpAndSettle();

        expect(find.byType(MatrixGraphsBlockCard), findsOneWidget);
        expect(find.byType(FilledButton), findsNothing);
        expect(
          find.byKey(const Key('profile_matrix_graph_length_constraint_field')),
          findsNothing,
        );
      },
    );

    testWidgets(
      'Boundary ISTQB: renders cleanly on narrow viewport (360x640) with AsyncError promptBlocksState without overflow',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 640);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final payload = createTestProfile(matrixSynthesisGroups: const []);

        await tester.pumpWidget(
          buildTestHarness(
            initialPayload: payload,
            onUpdate: (_) {},
            promptBlocksState: AsyncValue.error(
              Exception('Simulated network failure'),
              StackTrace.empty,
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(MatrixGraphsBlockCard), findsOneWidget);
        expect(tester.takeException(), isNull);
      },
    );

    testWidgets(
      'Boundary ISTQB: updates item inside matrixSynthesisGroups when MatrixGraphItemEditor triggers onUpdate',
      (WidgetTester tester) async {
        const group1 = MatrixSynthesisGroup(
          id: validGrpId1,
          title: I18nText(translations: {'en': 'Initial Title'}),
          targetBlocks: [],
          viewType: PresetView.metrics1d,
        );

        OutputProfile payload = createTestProfile(
          matrixSynthesisGroups: [group1],
        );

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: StatefulBuilder(
                  builder: (context, setState) {
                    return MatrixGraphsBlockCard(
                      payload: payload,
                      updatePayload: (newPayload) {
                        setState(() {
                          payload = newPayload;
                        });
                      },
                      allowedBlockIds: const {validBlkId1},
                      promptBlocksState: AsyncValue.data([mockPromptBlock1]),
                    );
                  },
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        final chipFinder = find.widgetWithText(FilterChip, 'Matrix Block 1');
        expect(chipFinder, findsOneWidget);
        await tester.tap(chipFinder);
        await tester.pumpAndSettle();

        expect(
          payload.matrixSynthesisGroups.first.targetBlocks,
          contains(validBlkId1),
        );
      },
    );
  });
}
