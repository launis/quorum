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
        final citationChip = find.widgetWithText(FilterChip, 'Source Citation');
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
  });
}
