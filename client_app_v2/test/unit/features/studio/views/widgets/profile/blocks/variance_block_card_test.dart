import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/variance_block_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

void main() {
  const String matrixBlockId1 = 'blk_0195f3a00000700a8000000000000010';
  const String matrixBlockId2 = 'blk_0195f3a00000700a8000000000000020';
  const String systemRuleId = 'blk_0195f3a00000700a8000000000000030';
  const String orphanTargetId = 'blk_0195f3a00000700a8000000000000099';

  PromptBlock createMatrixBlock({
    required String id,
    required String enLabel,
    String? fiLabel,
  }) {
    return PromptBlock.matrix(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: id,
      slug: 'matrix_$id',
      label: I18nText(translations: {'en': enLabel, 'fi': ?fiLabel}),
      description: const I18nText(translations: {'en': 'Matrix description'}),
      scales: const [
        MatrixScale(score: 1, aiLabel: 'Low', claims: []),
        MatrixScale(score: 5, aiLabel: 'High', claims: []),
      ],
    );
  }

  PromptBlock createSystemRuleBlock({required String id}) {
    return PromptBlock.systemRule(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: id,
      slug: 'sys_$id',
      label: const I18nText(translations: {'en': 'System Rule'}),
      description: const I18nText(translations: {'en': 'Rule description'}),
    );
  }

  OutputProfile createTestProfile({
    List<TargetBlockType>? targetBlockOrder,
    List<XaiExtensionType>? visibleWorkflowExtensions,
    String? varianceSynthesisDirective = 'Evaluate multi-evaluator consensus.',
    int? varianceLengthConstraint = 350,
    String? varianceTargetBlock = matrixBlockId1,
  }) {
    return OutputProfile(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: 'prf_0195f3a00000700a8000000000000001',
      workflowId: 'wf_0195f3a00000700a8000000000000002',
      name: const I18nText(translations: {'en': 'Test Profile'}),
      varianceSynthesisDirective: varianceSynthesisDirective,
      varianceLengthConstraint: varianceLengthConstraint,
      varianceTargetBlock: varianceTargetBlock,
      visibleWorkflowExtensions:
          visibleWorkflowExtensions ??
          const [XaiExtensionType.varianceValidation],
      targetBlockOrder:
          targetBlockOrder ?? const [TargetBlockType.varianceValidationBlock],
    );
  }

  Widget createTestWidget({
    required Widget child,
    Locale locale = const Locale('en'),
  }) {
    return MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: locale,
      home: Scaffold(body: SingleChildScrollView(child: child)),
    );
  }

  group('VarianceBlockCard Unit & Widget Tests', () {
    testWidgets(
      'renders localized title, subtitle, directive, length constraint, and filtered matrix target dropdown',
      (tester) async {
        final profile = createTestProfile();
        final blocks = [
          createMatrixBlock(
            id: matrixBlockId1,
            enLabel: 'Strategic Matrix',
            fiLabel: 'Strateginen matriisi',
          ),
          createMatrixBlock(id: matrixBlockId2, enLabel: 'Excluded Matrix'),
          createSystemRuleBlock(id: systemRuleId),
        ];

        await tester.pumpWidget(
          createTestWidget(
            child: VarianceBlockCard(
              payload: profile,
              updatePayload: (_) {},
              allowedBlockIds: {matrixBlockId1, systemRuleId},
              promptBlocksState: AsyncValue.data(blocks),
              dragHandle: const Icon(Icons.drag_handle),
            ),
          ),
        );
        await tester.pumpAndSettle();

        final l10nEn = await AppLocalizations.delegate.load(const Locale('en'));
        expect(find.byType(VarianceBlockCard), findsOneWidget);
        expect(find.text(l10nEn.blockVarianceTitle), findsOneWidget);
        expect(find.text(l10nEn.blockVarianceSubtitle), findsOneWidget);
        expect(
          find.byKey(const Key('profile_variance_directive_field')),
          findsOneWidget,
        );
        expect(
          find.byKey(const Key('profile_variance_length_constraint_field')),
          findsOneWidget,
        );
        expect(
          find.byKey(const Key('profile_variance_target_block_field')),
          findsOneWidget,
        );
        expect(
          find.text('Evaluate multi-evaluator consensus.'),
          findsOneWidget,
        );
        expect(find.text('350'), findsOneWidget);
        expect(find.text('Strategic Matrix ($matrixBlockId1)'), findsOneWidget);
        expect(find.text('Excluded Matrix ($matrixBlockId2)'), findsNothing);
        expect(find.byIcon(Icons.drag_handle), findsOneWidget);
      },
    );

    testWidgets(
      'renders Finnish localizations cleanly when fi locale is active',
      (tester) async {
        final profile = createTestProfile();
        final blocks = [
          createMatrixBlock(
            id: matrixBlockId1,
            enLabel: 'Strategic Matrix',
            fiLabel: 'Strateginen matriisi',
          ),
        ];

        await tester.pumpWidget(
          createTestWidget(
            locale: const Locale('fi'),
            child: VarianceBlockCard(
              payload: profile,
              updatePayload: (_) {},
              allowedBlockIds: const {},
              promptBlocksState: AsyncValue.data(blocks),
            ),
          ),
        );
        await tester.pumpAndSettle();

        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10nFi.blockVarianceTitle), findsOneWidget);
        expect(find.text(l10nFi.blockVarianceSubtitle), findsOneWidget);
        expect(
          find.text('Strateginen matriisi ($matrixBlockId1)'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'toggling switch synchronizes both targetBlockOrder and visibleWorkflowExtensions cleanly',
      (tester) async {
        OutputProfile currentProfile = createTestProfile();

        await tester.pumpWidget(
          createTestWidget(
            child: StatefulBuilder(
              builder: (context, setState) {
                return VarianceBlockCard(
                  payload: currentProfile,
                  updatePayload: (updated) {
                    setState(() {
                      currentProfile = updated;
                    });
                  },
                  allowedBlockIds: const {},
                  promptBlocksState: const AsyncValue.data([]),
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Toggle off -> removes both TargetBlockType.varianceValidationBlock and XaiExtensionType.varianceValidation
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          currentProfile.targetBlockOrder,
          isNot(contains(TargetBlockType.varianceValidationBlock)),
        );
        expect(
          currentProfile.visibleWorkflowExtensions,
          isNot(contains(XaiExtensionType.varianceValidation)),
        );
        expect(
          find.byKey(const Key('profile_variance_directive_field')),
          findsNothing,
        );

        // Toggle back on -> adds both back without duplicates
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          currentProfile.targetBlockOrder,
          contains(TargetBlockType.varianceValidationBlock),
        );
        expect(
          currentProfile.visibleWorkflowExtensions,
          contains(XaiExtensionType.varianceValidation),
        );
        expect(
          find.byKey(const Key('profile_variance_directive_field')),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'updating directive, length constraint, and target block dropdown mutates payload cleanly',
      (tester) async {
        OutputProfile currentProfile = createTestProfile();
        final blocks = [
          createMatrixBlock(id: matrixBlockId1, enLabel: 'Matrix One'),
          createMatrixBlock(id: matrixBlockId2, enLabel: 'Matrix Two'),
        ];

        await tester.pumpWidget(
          createTestWidget(
            child: StatefulBuilder(
              builder: (context, setState) {
                return VarianceBlockCard(
                  payload: currentProfile,
                  updatePayload: (updated) {
                    setState(() {
                      currentProfile = updated;
                    });
                  },
                  allowedBlockIds: const {},
                  promptBlocksState: AsyncValue.data(blocks),
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('profile_variance_directive_field')),
          '  Analyze divergence across models.  ',
        );
        await tester.pump();
        expect(
          currentProfile.varianceSynthesisDirective,
          equals('Analyze divergence across models.'),
        );

        await tester.enterText(
          find.byKey(const Key('profile_variance_length_constraint_field')),
          '600',
        );
        await tester.pump();
        expect(currentProfile.varianceLengthConstraint, equals(600));

        // Select second matrix block from dropdown
        await tester.tap(
          find.byKey(const Key('profile_variance_target_block_field')),
        );
        await tester.pumpAndSettle();
        await tester.tap(find.text('Matrix Two ($matrixBlockId2)').last);
        await tester.pumpAndSettle();
        expect(currentProfile.varianceTargetBlock, equals(matrixBlockId2));
      },
    );

    testWidgets(
      'Negative/Boundary ISTQB: whitespace-only directive and non-numeric length constraint resolve to null',
      (tester) async {
        OutputProfile currentProfile = createTestProfile(
          varianceSynthesisDirective: 'Initial directive',
          varianceLengthConstraint: 500,
        );

        await tester.pumpWidget(
          createTestWidget(
            child: StatefulBuilder(
              builder: (context, setState) {
                return VarianceBlockCard(
                  payload: currentProfile,
                  updatePayload: (updated) {
                    setState(() {
                      currentProfile = updated;
                    });
                  },
                  allowedBlockIds: const {},
                  promptBlocksState: const AsyncValue.data([]),
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('profile_variance_directive_field')),
          '    ',
        );
        await tester.pump();
        expect(currentProfile.varianceSynthesisDirective, isNull);

        await tester.enterText(
          find.byKey(const Key('profile_variance_length_constraint_field')),
          'abc',
        );
        await tester.pump();
        expect(currentProfile.varianceLengthConstraint, isNull);
      },
    );

    testWidgets(
      'Negative/Boundary ISTQB: preserves orphan target block ID when promptBlocksState is loading/error and renders without overflow on narrow viewport (260px)',
      (tester) async {
        final profile = createTestProfile(
          varianceTargetBlock: orphanTargetId,
          varianceSynthesisDirective: null,
          varianceLengthConstraint: null,
        );

        await tester.pumpWidget(
          createTestWidget(
            child: SizedBox(
              width: 260,
              child: VarianceBlockCard(
                payload: profile,
                updatePayload: (_) {},
                allowedBlockIds: {matrixBlockId1},
                promptBlocksState: const AsyncValue.loading(),
                dragHandle: const Icon(Icons.drag_indicator),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text(orphanTargetId), findsOneWidget);
      },
    );
  });
}
