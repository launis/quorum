import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/bibliography_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets('BibliographyBlockCard renders title and header toggle switch', (
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
    // There are 2 switches: 1 in BaseBlockCard header, 1 in body for summary box
    expect(find.byType(Switch), findsNWidgets(2));

    // Tap header toggle switch to remove block
    await tester.tap(find.byType(Switch).first);
    await tester.pumpAndSettle();

    expect(
      payload.targetBlockOrder.contains(TargetBlockType.printableSourcesBlock),
      isFalse,
    );
  });

  testWidgets('BibliographyBlockCard toggles display mode and summary box switch', (
    WidgetTester tester,
  ) async {
    OutputProfile payload = const OutputProfile(
      id: 'profile_1',
      workflowId: 'wf_1',
      name: I18nText(translations: {'en': 'Test Profile'}),
      targetBlockOrder: [TargetBlockType.printableSourcesBlock],
      showSourcesSummaryBox: true,
      sourcesDisplayMode: SourcesDisplayMode.verifiedEvidence,
    );

    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            child: StatefulBuilder(
              builder: (context, setState) {
                return BibliographyBlockCard(
                  payload: payload,
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

    // Verify SegmentedButton exists
    expect(
      find.byType(SegmentedButton<SourcesDisplayMode>),
      findsOneWidget,
    );

    // Tap second segment (Simple Bibliography)
    final simpleBibSegment = find.byIcon(Icons.format_list_bulleted_outlined);
    expect(simpleBibSegment, findsOneWidget);
    await tester.tap(simpleBibSegment);
    await tester.pumpAndSettle();

    expect(payload.sourcesDisplayMode, SourcesDisplayMode.simpleBibliography);

    // Tap summary box switch (the second Switch on screen)
    final summarySwitch = find.byType(Switch).last;
    await tester.tap(summarySwitch);
    await tester.pumpAndSettle();

    expect(payload.showSourcesSummaryBox, isFalse);
  });
}

