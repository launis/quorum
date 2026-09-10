import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/components/bars_matrix_builder.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/theme/app_theme.dart';

void main() {
  group('BarsMatrixBuilder Component Tests', () {
    testWidgets('renders Desktop Three-Pane format correctly', (
      WidgetTester tester,
    ) async {
      final scales = [
        const MatrixScale(
          score: 1,
          aiLabel: 'LOW',
          name: I18nText(translations: {'en': 'Terrible'}),
          claims: [
            MatrixClaim(
              label: const I18nText(translations: {'en': 'Claim 1'}),
              tdaAssertions: [
                const TDAAssertion(
                  tdaId: 'tda_1',
                  conceptDescription: 'Atom 1 Rule',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.exists,
                ),
                const TDAAssertion(
                  tdaId: 'tda_2',
                  conceptDescription: 'Atom 2 Rule',
                  inverseEvidence: true,
                  aggregationMode: AggregationMode.exists,
                ),
              ],
            ),
          ],
        ),
        const MatrixScale(
          score: 5,
          aiLabel: 'HIGH',
          name: I18nText(translations: {'en': 'Excellent'}),
          claims: [],
        ),
      ];

      await tester.binding.setSurfaceSize(const Size(1200, 800));

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
          ],
          supportedLocales: const [Locale('en')],
          home: Scaffold(
            body: BarsMatrixBuilder(scales: scales, onChanged: (newScales) {}),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.textContaining('1 - Terrible'), findsOneWidget);
      expect(find.textContaining('5 - Excellent'), findsOneWidget);
      expect(find.text('AI: LOW'), findsOneWidget);
      expect(find.text('Atom 1 Rule'), findsWidgets);
      expect(
        find.textContaining('Atom'),
        findsWidgets,
      ); // Due to tdaAssertions mapping

      // Cleanup
      await tester.binding.setSurfaceSize(null);
    });

    testWidgets('reproduces overflow on narrow desktop with 5 scales', (
      WidgetTester tester,
    ) async {
      final scales = [
        const MatrixScale(
          score: 1,
          aiLabel: 'CATASTROPHIC FAILURE - TRIGGER PASSIVITY AND HUBRIS PENALTY',
          name: I18nText(translations: {'fi': 'Sokea usko', 'en': 'Blind Faith'}),
          claims: [
            MatrixClaim(
              label: I18nText(translations: {
                'fi': 'Passiivinen delegointi ilman reunaehtoja',
                'en': 'Passive Delegation Without Constraints',
              }),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_1',
                  conceptDescription: 'Author delegates execution or decision-making without specifying constraints.',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.exists,
                ),
              ],
            ),
            MatrixClaim(
              label: I18nText(translations: {
                'fi': 'Kriittisen tarkistusvaiheen puuttuminen',
                'en': 'Absence of Verification Step',
              }),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_2',
                  conceptDescription: 'Author incorporates or accepts generative output directly.',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.exists,
                ),
              ],
            ),
            MatrixClaim(
              label: I18nText(translations: {
                'fi': 'Auktoriteettiharha ja oraakkeliasema',
                'en': 'Authority Bias and Oracle Trap',
              }),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_3',
                  conceptDescription: 'Author treats probabilistic generation as infallible oracle.',
                  inverseEvidence: true,
                  aggregationMode: AggregationMode.exists,
                ),
              ],
            ),
          ],
        ),
        const MatrixScale(
          score: 2,
          aiLabel: 'SIGNIFICANT DISTORTION - PASSIVE ACCEPTANCE OF METRICS',
          name: I18nText(translations: {'fi': 'Reaktiivinen huomioija', 'en': 'Reactive Observer'}),
          claims: [
            MatrixClaim(
              label: I18nText(translations: {
                'fi': 'Pinnalliset muotoseikat ja korjaukset',
                'en': 'Superficial Formatting Corrections',
              }),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_4',
                  conceptDescription: 'Author restricts feedback exclusively to cosmetic adjustments.',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.allMustComply,
                ),
              ],
            ),
          ],
        ),
        const MatrixScale(
          score: 3,
          aiLabel: 'MINOR DEVIATION - REQUIRES REBUTTALS FOR ADVANCEMENT',
          name: I18nText(translations: {'fi': 'Pintapuolinen', 'en': 'Superficial'}),
          claims: [
            MatrixClaim(
              label: I18nText(translations: {
                'fi': 'Mekaaninen vaiheistettu eteneminen',
                'en': 'Linear Step-by-Step Task Breakdown',
              }),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_5',
                  conceptDescription: 'Author structures workflow into sequential stages.',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.allMustComply,
                ),
              ],
            ),
          ],
        ),
        const MatrixScale(
          score: 4,
          aiLabel: 'ROBUST ALIGNMENT - REQUIRES EPISTEMOLOGICAL HUMILITY',
          name: I18nText(translations: {'fi': 'Kriittinen ohjaaja', 'en': 'Critical Guide'}),
          claims: [
            MatrixClaim(
              label: I18nText(translations: {
                'fi': 'Goodhartin lain tunnistaminen ja mittarin kyseenalaistus',
                'en': "Goodhart's Law Identification",
              }),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_6',
                  conceptDescription: 'Author actively identifies Goodhart law.',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.allMustComply,
                ),
              ],
            ),
          ],
        ),
        const MatrixScale(
          score: 5,
          aiLabel: 'THEORETICAL PERFECTION - EXPLICIT COGNITIVE FRICTION AND ANCHORING REQUIRED',
          name: I18nText(translations: {'fi': 'Aktiivinen haastaja', 'en': 'Active Challenger'}),
          claims: [
            MatrixClaim(
              label: I18nText(translations: {
                'fi': 'Sokraattinen ohjaus ja kognitiivinen kitka',
                'en': 'Socratic Steering and Cognitive Friction',
              }),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_7',
                  conceptDescription: 'Author actively probes foundational reasoning.',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.allMustComply,
                ),
              ],
            ),
          ],
        ),
      ];

      await tester.binding.setSurfaceSize(const Size(870, 800));

      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light,
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('fi'),
          home: Scaffold(
            body: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: BarsMatrixBuilder(scales: scales, onChanged: (newScales) {}),
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      await tester.binding.setSurfaceSize(null);
    });
  });
}
