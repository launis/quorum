import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets('BibliographyBlockCard renders title and toggle switch', (
    WidgetTester tester,
  ) async {
    OutputProfile payload = const OutputProfile(
      id: 'profile_1',
      workflowId: 'wf_1',
      name: I18nText(translations: {'en': 'Test Profile'}),
      targetBlockOrder: [TargetBlockType.printableSourcesBlock],
    );

    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            child: BibliographyBlockCard(
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

    expect(find.byType(BibliographyBlockCard), findsOneWidget);
    expect(find.byType(Switch), findsOneWidget);

    await tester.tap(find.byType(Switch));
    await tester.pumpAndSettle();

    expect(
      payload.targetBlockOrder.contains(TargetBlockType.printableSourcesBlock),
      isFalse,
    );
  });
}
