import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('SimpleToggleBlockCard Tests', () {
    testWidgets('SimpleToggleBlockCard enables block when toggled on', (
      WidgetTester tester,
    ) async {
      OutputProfile payload = const OutputProfile(
        id: 'profile_1',
        workflowId: 'wf_1',
        name: I18nText(
          defaultLocale: 'en',
          translations: {'en': 'Test Profile'},
        ),
        targetBlockOrder: [],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: SingleChildScrollView(
              child: SimpleToggleBlockCard(
                blockType: TargetBlockType.authenticityEvaluationBlock,
                title: 'Authenticity Evaluation',
                subtitle: 'Evaluates document authenticity metrics',
                icon: Icons.verified_user,
                payload: payload,
                updatePayload: (newPayload) {
                  payload = newPayload;
                },
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Authenticity Evaluation'), findsOneWidget);
      expect(
        find.text('Evaluates document authenticity metrics'),
        findsOneWidget,
      );
      expect(find.byType(Switch), findsOneWidget);

      await tester.tap(find.byType(Switch));
      await tester.pumpAndSettle();

      expect(
        payload.targetBlockOrder.contains(
          TargetBlockType.authenticityEvaluationBlock,
        ),
        isTrue,
      );
    });

    testWidgets('SimpleToggleBlockCard disables block when toggled off', (
      WidgetTester tester,
    ) async {
      OutputProfile payload = const OutputProfile(
        id: 'profile_1',
        workflowId: 'wf_1',
        name: I18nText(
          defaultLocale: 'en',
          translations: {'en': 'Test Profile'},
        ),
        targetBlockOrder: [TargetBlockType.authenticityEvaluationBlock],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: SingleChildScrollView(
              child: SimpleToggleBlockCard(
                blockType: TargetBlockType.authenticityEvaluationBlock,
                title: 'Authenticity Evaluation',
                subtitle: 'Evaluates document authenticity metrics',
                icon: Icons.verified_user,
                payload: payload,
                updatePayload: (newPayload) {
                  payload = newPayload;
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
        payload.targetBlockOrder.contains(
          TargetBlockType.authenticityEvaluationBlock,
        ),
        isFalse,
      );
    });
  });
}
