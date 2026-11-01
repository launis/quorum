import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  OutputProfile createSampleProfile({
    List<XaiExtensionType> visibleExtensions = const [
      XaiExtensionType.citation,
    ],
  }) {
    return OutputProfile(
      id: 'profile_1',
      workflowId: 'wf_1',
      name: const I18nText(translations: {'en': 'Test Profile'}),
      targetBlockOrder: const [TargetBlockType.groupedExtensionsBlock],
      visibleBlockExtensions: visibleExtensions,
      maxExtensionItems: 3,
    );
  }

  Widget createTestWidget({
    required OutputProfile payload,
    required void Function(OutputProfile) updatePayload,
    List<String> availableExtensions = const [
      'citation',
      'justification',
      'falsification',
      'risk_flag',
    ],
  }) {
    return ProviderScope(
      overrides: [
        workflowAvailableExtensionsProvider(
          'wf_1',
        ).overrideWithValue(AsyncValue.data(availableExtensions)),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            child: XaiExtensionsBlockCard(
              payload: payload,
              updatePayload: updatePayload,
            ),
          ),
        ),
      ),
    );
  }

  group('XaiExtensionsBlockCard Tests', () {
    testWidgets(
      'renders Macro Synthesis and Micro Atom section titles, subtitles, and chips',
      (WidgetTester tester) async {
        final payload = createSampleProfile();

        await tester.pumpWidget(
          createTestWidget(payload: payload, updatePayload: (_) {}),
        );
        await tester.pumpAndSettle();

        expect(find.byType(XaiExtensionsBlockCard), findsOneWidget);
        expect(find.text('XAI Highlights & Extensions'), findsNWidgets(2));
        expect(
          find.text('Overall Evaluation & Synthesis (Macro-level)'),
          findsOneWidget,
        );
        expect(
          find.text(
            'Generated as a synthesis of the entire text upon execution completion.',
          ),
          findsOneWidget,
        );
        expect(
          find.text('Observation-specific Enrichments (Micro-level)'),
          findsOneWidget,
        );
        expect(
          find.text('Extracted directly from individual matrix observations.'),
          findsOneWidget,
        );

        // Filter chips present
        expect(find.byType(FilterChip), findsWidgets);
      },
    );

    testWidgets(
      'mutates visibleBlockExtensions when chips are tapped across macro and micro sections',
      (WidgetTester tester) async {
        OutputProfile payload = createSampleProfile(
          visibleExtensions: [XaiExtensionType.citation],
        );

        await tester.pumpWidget(
          StatefulBuilder(
            builder: (context, setState) {
              return createTestWidget(
                payload: payload,
                updatePayload: (newPayload) {
                  setState(() {
                    payload = newPayload;
                  });
                },
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        // Tap Macro chip 'justification' (not currently selected)
        final justificationChip = find.widgetWithText(
          FilterChip,
          'Justification',
        );
        expect(justificationChip, findsOneWidget);
        await tester.tap(justificationChip);
        await tester.pumpAndSettle();

        expect(
          payload.visibleBlockExtensions.contains(
            XaiExtensionType.justification,
          ),
          isTrue,
        );

        // Tap Micro chip 'citation' (currently selected) to deselect
        final citationChip = find.widgetWithText(FilterChip, 'Citation');
        expect(citationChip, findsOneWidget);
        await tester.tap(citationChip);
        await tester.pumpAndSettle();

        expect(
          payload.visibleBlockExtensions.contains(XaiExtensionType.citation),
          isFalse,
        );
      },
    );

    testWidgets(
      'renders without RenderFlex overflow on narrow viewport (360x640)',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 640);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final payload = createSampleProfile();

        await tester.pumpWidget(
          createTestWidget(payload: payload, updatePayload: (_) {}),
        );
        await tester.pumpAndSettle();

        expect(find.byType(XaiExtensionsBlockCard), findsOneWidget);
        expect(tester.takeException(), isNull);
      },
    );

    testWidgets(
      'rejects out-of-bounds (min-1, max+1) and non-integer maxExtensionItems inputs (BVA negative)',
      (WidgetTester tester) async {
        final formKey = GlobalKey<FormState>();
        OutputProfile payload = createSampleProfile();
        int mutationCount = 0;

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              workflowAvailableExtensionsProvider(
                'wf_1',
              ).overrideWithValue(const AsyncValue.data(['citation'])),
            ],
            child: MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(
                body: Form(
                  key: formKey,
                  child: SingleChildScrollView(
                    child: XaiExtensionsBlockCard(
                      payload: payload,
                      updatePayload: (updated) {
                        payload = updated;
                        mutationCount++;
                      },
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        final maxField = find.byKey(const ValueKey('max_ext_3'));
        expect(maxField, findsOneWidget);

        final minAllowed = SystemUiConstraints.maxExtensionItemsSliderMin.value;
        final maxAllowed =
            SystemUiConstraints.maxExtensionItemsAbsoluteMax.value;

        // Boundary min - 1 (0 < 1)
        await tester.enterText(maxField, '${minAllowed - 1}');
        await tester.pump();
        expect(mutationCount, 0);
        expect(formKey.currentState!.validate(), isFalse);

        // Boundary max + 1 (101 > 100)
        await tester.enterText(maxField, '${maxAllowed + 1}');
        await tester.pump();
        expect(mutationCount, 0);
        expect(formKey.currentState!.validate(), isFalse);

        // Non-integer input
        await tester.enterText(maxField, 'abc');
        await tester.pump();
        expect(mutationCount, 0);
        expect(formKey.currentState!.validate(), isFalse);

        // Valid upper boundary (100)
        await tester.enterText(maxField, '$maxAllowed');
        await tester.pump();
        expect(mutationCount, 1);
        expect(payload.maxExtensionItems, maxAllowed);
        expect(formKey.currentState!.validate(), isTrue);
      },
    );

    testWidgets(
      'handles AsyncError state and normalizes whitespace/empty optional directives to null (negative)',
      (WidgetTester tester) async {
        OutputProfile payload = createSampleProfile().copyWith(
          xaiSynthesisDirective: 'Initial directive',
          xaiLengthConstraint: 50,
        );

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              workflowAvailableExtensionsProvider('wf_1').overrideWithValue(
                AsyncValue.error(
                  Exception('Extension lookup failed'),
                  StackTrace.empty,
                ),
              ),
            ],
            child: MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(
                body: SingleChildScrollView(
                  child: XaiExtensionsBlockCard(
                    payload: payload,
                    updatePayload: (updated) {
                      payload = updated;
                    },
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Error message rendered, no FilterChips shown
        expect(find.textContaining('Unknown error'), findsOneWidget);
        expect(find.byType(FilterChip), findsNothing);

        // Whitespace-only directive normalizes to null
        final directiveField = find.byKey(
          const Key('profile_xai_synthesis_directive_field'),
        );
        await tester.enterText(directiveField, '   ');
        await tester.pump();
        expect(payload.xaiSynthesisDirective, isNull);

        // Empty length constraint normalizes to null
        final lengthField = find.byKey(
          const Key('profile_xai_length_constraint_field'),
        );
        await tester.enterText(lengthField, '');
        await tester.pump();
        expect(payload.xaiLengthConstraint, isNull);
      },
    );
  });
}
