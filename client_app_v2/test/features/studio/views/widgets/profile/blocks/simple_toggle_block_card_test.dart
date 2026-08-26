import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/block_card_registry.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('SimpleToggleBlockCard Tests', () {
    testWidgets(
      'test_toggle_variance_block_adds_and_removes_variance_validation_extension',
      (WidgetTester tester) async {
        OutputProfile payload = const OutputProfile(
          id: 'profile_1',
          workflowId: 'wf_1',
          name: I18nText(translations: {'en': 'Test Profile'}),
          targetBlockOrder: [],
          visibleWorkflowExtensions: [],
        );

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: StatefulBuilder(
                  builder: (context, setState) {
                    return SimpleToggleBlockCard(
                      blockType: TargetBlockType.varianceValidationBlock,
                      title: 'Variance Validation',
                      subtitle: 'Variance metrics',
                      icon: Icons.rule_outlined,
                      payload: payload,
                      syncWorkflowExtensions:
                          BlockCardRegistry
                              .syncWorkflowExtensionsMap[TargetBlockType
                              .varianceValidationBlock],
                      updatePayload: (newPayload) {
                        setState(() {
                          payload = newPayload;
                        });
                      },
                    );
                  },
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Toggle ON
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();

        expect(
          payload.targetBlockOrder,
          contains(TargetBlockType.varianceValidationBlock),
        );
        expect(
          payload.visibleWorkflowExtensions,
          contains(XaiExtensionType.varianceValidation),
        );

        // Toggle OFF
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();

        expect(
          payload.targetBlockOrder,
          isNot(contains(TargetBlockType.varianceValidationBlock)),
        );
        expect(
          payload.visibleWorkflowExtensions,
          isNot(contains(XaiExtensionType.varianceValidation)),
        );
      },
    );

    testWidgets(
      'test_toggle_authenticity_block_adds_and_removes_authenticity_evaluation_extension',
      (WidgetTester tester) async {
        OutputProfile payload = const OutputProfile(
          id: 'profile_1',
          workflowId: 'wf_1',
          name: I18nText(translations: {'en': 'Test Profile'}),
          targetBlockOrder: [],
          visibleWorkflowExtensions: [],
        );

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: StatefulBuilder(
                  builder: (context, setState) {
                    return SimpleToggleBlockCard(
                      blockType: TargetBlockType.authenticityEvaluationBlock,
                      title: 'Authenticity Evaluation',
                      subtitle: 'Authenticity metrics',
                      icon: Icons.verified_user_outlined,
                      payload: payload,
                      syncWorkflowExtensions:
                          BlockCardRegistry
                              .syncWorkflowExtensionsMap[TargetBlockType
                              .authenticityEvaluationBlock],
                      updatePayload: (newPayload) {
                        setState(() {
                          payload = newPayload;
                        });
                      },
                    );
                  },
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Toggle ON
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();

        expect(
          payload.targetBlockOrder,
          contains(TargetBlockType.authenticityEvaluationBlock),
        );
        expect(
          payload.visibleWorkflowExtensions,
          contains(XaiExtensionType.authenticityEvaluation),
        );

        // Toggle OFF
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();

        expect(
          payload.targetBlockOrder,
          isNot(contains(TargetBlockType.authenticityEvaluationBlock)),
        );
        expect(
          payload.visibleWorkflowExtensions,
          isNot(contains(XaiExtensionType.authenticityEvaluation)),
        );
      },
    );

    testWidgets(
      'test_toggle_penalties_block_leaves_workflow_extensions_unchanged',
      (WidgetTester tester) async {
        OutputProfile payload = const OutputProfile(
          id: 'profile_1',
          workflowId: 'wf_1',
          name: I18nText(translations: {'en': 'Test Profile'}),
          targetBlockOrder: [],
          visibleWorkflowExtensions: [XaiExtensionType.citation],
        );

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: StatefulBuilder(
                  builder: (context, setState) {
                    return SimpleToggleBlockCard(
                      blockType: TargetBlockType.penaltiesBlock,
                      title: 'Penalties',
                      subtitle: 'Penalties deduction',
                      icon: Icons.gavel_outlined,
                      payload: payload,
                      syncWorkflowExtensions:
                          BlockCardRegistry
                              .syncWorkflowExtensionsMap[TargetBlockType
                              .penaltiesBlock],
                      updatePayload: (newPayload) {
                        setState(() {
                          payload = newPayload;
                        });
                      },
                    );
                  },
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Toggle ON
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();

        expect(
          payload.targetBlockOrder,
          contains(TargetBlockType.penaltiesBlock),
        );
        expect(
          payload.visibleWorkflowExtensions,
          equals([XaiExtensionType.citation]),
        );
      },
    );
  });
}
