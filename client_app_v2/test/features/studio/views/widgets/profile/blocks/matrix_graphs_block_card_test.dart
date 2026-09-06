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
  testWidgets(
    'MatrixGraphsBlockCard renders group collection and handles add button',
    (WidgetTester tester) async {
      OutputProfile payload = const OutputProfile(
        id: 'profile_1',
        workflowId: 'wf_1',
        name: I18nText(translations: {'en': 'Test Profile'}),
        targetBlockOrder: [TargetBlockType.matrixGraphsBlock],
        matrixSynthesisGroups: [],
      );

      final mockPromptBlock = const PromptBlock.matrix(
        id: 'block_1',
        slug: 'matrix_block_1',
        label: I18nText(translations: {'en': 'Matrix Block 1'}),
        description: I18nText(translations: {'en': 'Matrix block description'}),
        scales: [],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: SingleChildScrollView(
              child: MatrixGraphsBlockCard(
                payload: payload,
                updatePayload: (newPayload) {
                  payload = newPayload;
                },
                allowedBlockIds: {'block_1'},
                promptBlocksState: AsyncValue.data([mockPromptBlock]),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(MatrixGraphsBlockCard), findsOneWidget);
      expect(find.byType(FilledButton), findsOneWidget);

      await tester.tap(find.byType(FilledButton));
      await tester.pumpAndSettle();

      expect(payload.matrixSynthesisGroups.length, equals(1));
    },
  );

  testWidgets(
    'MatrixGraphsBlockCard renders matrixGraphLengthConstraint field and updates payload on input',
    (WidgetTester tester) async {
      OutputProfile payload = const OutputProfile(
        id: 'profile_1',
        workflowId: 'wf_1',
        name: I18nText(translations: {'en': 'Test Profile'}),
        targetBlockOrder: [TargetBlockType.matrixGraphsBlock],
        matrixSynthesisGroups: [],
        matrixGraphLengthConstraint: 400,
      );

      final mockPromptBlock = const PromptBlock.matrix(
        id: 'block_1',
        slug: 'matrix_block_1',
        label: I18nText(translations: {'en': 'Matrix Block 1'}),
        description: I18nText(translations: {'en': 'Matrix block description'}),
        scales: [],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: SingleChildScrollView(
              child: MatrixGraphsBlockCard(
                payload: payload,
                updatePayload: (newPayload) {
                  payload = newPayload;
                },
                allowedBlockIds: {'block_1'},
                promptBlocksState: AsyncValue.data([mockPromptBlock]),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final lengthFieldFinder = find.byKey(
        const Key('profile_matrix_graph_length_constraint_field'),
      );
      expect(lengthFieldFinder, findsOneWidget);

      final textFormField = tester.widget<TextFormField>(lengthFieldFinder);
      expect(textFormField.initialValue, '400');

      // Update to 550
      await tester.enterText(lengthFieldFinder, '550');
      await tester.pumpAndSettle();
      expect(payload.matrixGraphLengthConstraint, 550);

      // Clear field sets to null
      await tester.enterText(lengthFieldFinder, '');
      await tester.pumpAndSettle();
      expect(payload.matrixGraphLengthConstraint, isNull);
    },
  );
}

