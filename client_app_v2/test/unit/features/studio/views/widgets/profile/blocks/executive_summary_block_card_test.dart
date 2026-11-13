import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/executive_summary_block_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

void main() {
  OutputProfile createTestProfile({
    List<TargetBlockType>? targetBlockOrder,
    String? executiveSummaryDirective = 'Focus on key strategic takeaways.',
    int? synthesisLengthConstraint = 400,
  }) {
    return OutputProfile(
      organizationId: 'org_0195f3a0000070008000000000000001',
      id: 'prf_0195f3a00000700a8000000000000001',
      workflowId: 'wf_0195f3a00000700a8000000000000002',
      name: const I18nText(translations: {'en': 'Test Profile'}),
      executiveSummaryDirective: executiveSummaryDirective,
      synthesisLengthConstraint: synthesisLengthConstraint,
      targetBlockOrder:
          targetBlockOrder ?? [TargetBlockType.executiveSummaryBlock],
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

  group('ExecutiveSummaryBlockCard Unit & Widget Tests', () {
    testWidgets(
      'renders localized title, subtitle, directive field, and synthesis length field when included',
      (tester) async {
        final profile = createTestProfile();

        await tester.pumpWidget(
          createTestWidget(
            child: ExecutiveSummaryBlockCard(
              payload: profile,
              updatePayload: (_) {},
              dragHandle: const Icon(Icons.drag_handle),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ExecutiveSummaryBlockCard), findsOneWidget);
        expect(find.text('Executive Summary'), findsOneWidget);
        expect(
          find.byKey(const Key('profile_executive_summary_directive_field')),
          findsOneWidget,
        );
        expect(
          find.byKey(const Key('profile_synthesis_length_constraint_field')),
          findsOneWidget,
        );
        expect(find.text('Focus on key strategic takeaways.'), findsOneWidget);
        expect(find.text('400'), findsOneWidget);
        expect(find.byIcon(Icons.drag_handle), findsOneWidget);
      },
    );

    testWidgets(
      'renders Finnish localizations cleanly when fi locale is active',
      (tester) async {
        final profile = createTestProfile();

        await tester.pumpWidget(
          createTestWidget(
            locale: const Locale('fi'),
            child: ExecutiveSummaryBlockCard(
              payload: profile,
              updatePayload: (_) {},
            ),
          ),
        );
        await tester.pumpAndSettle();

        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10nFi.blockExecutiveSummaryTitle), findsOneWidget);
        expect(find.text(l10nFi.blockExecutiveSummarySubtitle), findsOneWidget);
      },
    );

    testWidgets(
      'toggling switch removes and re-adds executiveSummaryBlock in targetBlockOrder without duplication',
      (tester) async {
        OutputProfile currentProfile = createTestProfile(
          targetBlockOrder: [TargetBlockType.executiveSummaryBlock],
        );

        await tester.pumpWidget(
          createTestWidget(
            child: StatefulBuilder(
              builder: (context, setState) {
                return ExecutiveSummaryBlockCard(
                  payload: currentProfile,
                  updatePayload: (updated) {
                    setState(() {
                      currentProfile = updated;
                    });
                  },
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Toggle off
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          currentProfile.targetBlockOrder,
          isNot(contains(TargetBlockType.executiveSummaryBlock)),
        );
        expect(
          find.byKey(const Key('profile_executive_summary_directive_field')),
          findsNothing,
        );

        // Toggle back on
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          currentProfile.targetBlockOrder,
          contains(TargetBlockType.executiveSummaryBlock),
        );
        expect(
          find.byKey(const Key('profile_executive_summary_directive_field')),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'updating directive and length constraint fields mutates payload cleanly',
      (tester) async {
        OutputProfile currentProfile = createTestProfile();

        await tester.pumpWidget(
          createTestWidget(
            child: StatefulBuilder(
              builder: (context, setState) {
                return ExecutiveSummaryBlockCard(
                  payload: currentProfile,
                  updatePayload: (updated) {
                    setState(() {
                      currentProfile = updated;
                    });
                  },
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('profile_executive_summary_directive_field')),
          '  Summarize key risks and opportunities.  ',
        );
        await tester.pump();
        expect(
          currentProfile.executiveSummaryDirective,
          equals('Summarize key risks and opportunities.'),
        );

        await tester.enterText(
          find.byKey(const Key('profile_synthesis_length_constraint_field')),
          '750',
        );
        await tester.pump();
        expect(currentProfile.synthesisLengthConstraint, equals(750));
      },
    );

    testWidgets(
      'Negative/Boundary ISTQB: whitespace-only directive and empty or non-numeric length constraint resolve to null',
      (tester) async {
        OutputProfile currentProfile = createTestProfile(
          executiveSummaryDirective: 'Initial directive',
          synthesisLengthConstraint: 500,
        );

        await tester.pumpWidget(
          createTestWidget(
            child: StatefulBuilder(
              builder: (context, setState) {
                return ExecutiveSummaryBlockCard(
                  payload: currentProfile,
                  updatePayload: (updated) {
                    setState(() {
                      currentProfile = updated;
                    });
                  },
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Enter whitespace-only directive -> must trim to empty and resolve to null
        await tester.enterText(
          find.byKey(const Key('profile_executive_summary_directive_field')),
          '    ',
        );
        await tester.pump();
        expect(currentProfile.executiveSummaryDirective, isNull);

        // Enter non-digits into digitsOnly length field -> filtered out to empty -> resolves to null
        await tester.enterText(
          find.byKey(const Key('profile_synthesis_length_constraint_field')),
          'abc',
        );
        await tester.pump();
        expect(currentProfile.synthesisLengthConstraint, isNull);
      },
    );

    testWidgets(
      'Negative/Boundary ISTQB: excluded block suppresses body fields and renders without overflow on narrow viewport (260px)',
      (tester) async {
        final profile = createTestProfile(
          targetBlockOrder: const [],
          executiveSummaryDirective: null,
          synthesisLengthConstraint: null,
        );

        await tester.pumpWidget(
          createTestWidget(
            child: SizedBox(
              width: 260,
              child: ExecutiveSummaryBlockCard(
                payload: profile,
                updatePayload: (_) {},
                dragHandle: const Icon(Icons.drag_indicator),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(
          find.byKey(const Key('profile_executive_summary_directive_field')),
          findsNothing,
        );
        expect(
          find.byKey(const Key('profile_synthesis_length_constraint_field')),
          findsNothing,
        );
      },
    );
  });
}
