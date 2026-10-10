import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/metadata_block_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

void main() {
  OutputProfile createTestProfile({
    List<TargetBlockType>? targetBlockOrder,
    List<String> visibleMetadata = const ['date', 'organization'],
  }) {
    return OutputProfile(
      id: 'prf_test',
      workflowId: 'wf_test',
      name: const I18nText(translations: {'en': 'Test Profile'}),
      visibleMetadata: visibleMetadata,
      targetBlockOrder: targetBlockOrder ?? [TargetBlockType.metadataBlock],
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

  group('MetadataBlockCard Unit & Widget Tests', () {
    testWidgets(
      'renders all 7 metadata field chips with English localizations',
      (tester) async {
        final profile = createTestProfile();
        await tester.pumpWidget(
          createTestWidget(
            child: MetadataBlockCard(payload: profile, updatePayload: (_) {}),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(MetadataBlockCard), findsOneWidget);
        expect(find.text('Date'), findsOneWidget);
        expect(find.text('Organization'), findsOneWidget);
        expect(find.text('User'), findsOneWidget);
        expect(find.text('Scoring Engine'), findsOneWidget);
        expect(find.text('Strictness'), findsOneWidget);
        expect(find.text('Cost'), findsOneWidget);
        expect(find.text('Tokens'), findsOneWidget);
      },
    );

    testWidgets(
      'renders Finnish localizations cleanly when fi locale is active',
      (tester) async {
        final profile = createTestProfile();
        await tester.pumpWidget(
          createTestWidget(
            locale: const Locale('fi'),
            child: MetadataBlockCard(payload: profile, updatePayload: (_) {}),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Päivämäärä'), findsOneWidget);
        expect(find.text('Organisaatio'), findsOneWidget);
        expect(find.text('Käyttäjä'), findsOneWidget);
        expect(find.text('Arviointimoottori'), findsOneWidget);
        expect(find.text('Tiukkuusaste'), findsOneWidget);
        expect(find.text('Kustannukset'), findsOneWidget);
        expect(find.text('Tokenit'), findsOneWidget);
      },
    );

    testWidgets('toggling chip adds and removes metadata fields', (
      tester,
    ) async {
      OutputProfile currentProfile = createTestProfile(
        visibleMetadata: ['date'],
      );

      await tester.pumpWidget(
        createTestWidget(
          child: StatefulBuilder(
            builder: (context, setState) {
              return MetadataBlockCard(
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

      // Tap 'Cost' chip to add it
      await tester.tap(find.text('Cost'));
      await tester.pumpAndSettle();
      expect(currentProfile.visibleMetadata, contains('cost'));
      expect(currentProfile.visibleMetadata, contains('date'));

      // Tap 'Date' chip to remove it
      await tester.tap(find.text('Date'));
      await tester.pumpAndSettle();
      expect(currentProfile.visibleMetadata, isNot(contains('date')));
      expect(currentProfile.visibleMetadata, contains('cost'));
    });

    testWidgets(
      'toggling block switch adds and removes metadataBlock from targetBlockOrder',
      (tester) async {
        OutputProfile currentProfile = createTestProfile(
          targetBlockOrder: [TargetBlockType.metadataBlock],
        );

        await tester.pumpWidget(
          createTestWidget(
            child: StatefulBuilder(
              builder: (context, setState) {
                return MetadataBlockCard(
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

        // Toggle switch to off
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          currentProfile.targetBlockOrder,
          isNot(contains(TargetBlockType.metadataBlock)),
        );

        // Toggle switch back on
        await tester.tap(find.byType(Switch));
        await tester.pumpAndSettle();
        expect(
          currentProfile.targetBlockOrder,
          contains(TargetBlockType.metadataBlock),
        );
      },
    );

    testWidgets('Negative ISTQB: unknown field fallback in getFieldLabel', (
      tester,
    ) async {
      late String resolvedLabel;
      await tester.pumpWidget(
        createTestWidget(
          child: Builder(
            builder: (context) {
              resolvedLabel = MetadataBlockCard.getFieldLabel(
                context,
                'unknown_custom_slug',
              );
              return Text(resolvedLabel);
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(resolvedLabel, equals('unknown_custom_slug'));
      expect(find.text('unknown_custom_slug'), findsOneWidget);
    });

    testWidgets(
      'Negative ISTQB: empty visibleMetadata renders without crashing',
      (tester) async {
        final profile = createTestProfile(visibleMetadata: []);
        await tester.pumpWidget(
          createTestWidget(
            child: MetadataBlockCard(payload: profile, updatePayload: (_) {}),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(FilterChip), findsNWidgets(7));
        for (final chipFinder in tester.widgetList<FilterChip>(
          find.byType(FilterChip),
        )) {
          expect(chipFinder.selected, isFalse);
        }
      },
    );
  });
}
