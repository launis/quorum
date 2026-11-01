import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
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
              label: I18nText(translations: {'en': 'Claim 1'}),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_0195f3a0000070008000000000000001',
                  conceptDescription: 'Atom 1 Rule',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.exists,
                ),
                TDAAssertion(
                  tdaId: 'tda_0195f3a0000070008000000000000002',
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
          aiLabel:
              'CATASTROPHIC FAILURE - TRIGGER PASSIVITY AND HUBRIS PENALTY',
          name: I18nText(
            translations: {'fi': 'Sokea usko', 'en': 'Blind Faith'},
          ),
          claims: [
            MatrixClaim(
              label: I18nText(
                translations: {
                  'fi': 'Passiivinen delegointi ilman reunaehtoja',
                  'en': 'Passive Delegation Without Constraints',
                },
              ),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_0195f3a0000070008000000000000001',
                  conceptDescription:
                      'Author delegates execution or decision-making without specifying constraints.',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.exists,
                ),
              ],
            ),
            MatrixClaim(
              label: I18nText(
                translations: {
                  'fi': 'Kriittisen tarkistusvaiheen puuttuminen',
                  'en': 'Absence of Verification Step',
                },
              ),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_0195f3a0000070008000000000000002',
                  conceptDescription:
                      'Author incorporates or accepts generative output directly.',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.exists,
                ),
              ],
            ),
            MatrixClaim(
              label: I18nText(
                translations: {
                  'fi': 'Auktoriteettiharha ja oraakkeliasema',
                  'en': 'Authority Bias and Oracle Trap',
                },
              ),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_0195f3a0000070008000000000000003',
                  conceptDescription:
                      'Author treats probabilistic generation as infallible oracle.',
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
          name: I18nText(
            translations: {
              'fi': 'Reaktiivinen huomioija',
              'en': 'Reactive Observer',
            },
          ),
          claims: [
            MatrixClaim(
              label: I18nText(
                translations: {
                  'fi': 'Pinnalliset muotoseikat ja korjaukset',
                  'en': 'Superficial Formatting Corrections',
                },
              ),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_0195f3a0000070008000000000000004',
                  conceptDescription:
                      'Author restricts feedback exclusively to cosmetic adjustments.',
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
          name: I18nText(
            translations: {'fi': 'Pintapuolinen', 'en': 'Superficial'},
          ),
          claims: [
            MatrixClaim(
              label: I18nText(
                translations: {
                  'fi': 'Mekaaninen vaiheistettu eteneminen',
                  'en': 'Linear Step-by-Step Task Breakdown',
                },
              ),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_0195f3a0000070008000000000000005',
                  conceptDescription:
                      'Author structures workflow into sequential stages.',
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
          name: I18nText(
            translations: {'fi': 'Kriittinen ohjaaja', 'en': 'Critical Guide'},
          ),
          claims: [
            MatrixClaim(
              label: I18nText(
                translations: {
                  'fi':
                      'Goodhartin lain tunnistaminen ja mittarin kyseenalaistus',
                  'en': "Goodhart's Law Identification",
                },
              ),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_0195f3a0000070008000000000000006',
                  conceptDescription:
                      'Author actively identifies Goodhart law.',
                  inverseEvidence: false,
                  aggregationMode: AggregationMode.allMustComply,
                ),
              ],
            ),
          ],
        ),
        const MatrixScale(
          score: 5,
          aiLabel:
              'THEORETICAL PERFECTION - EXPLICIT COGNITIVE FRICTION AND ANCHORING REQUIRED',
          name: I18nText(
            translations: {
              'fi': 'Aktiivinen haastaja',
              'en': 'Active Challenger',
            },
          ),
          claims: [
            MatrixClaim(
              label: I18nText(
                translations: {
                  'fi': 'Sokraattinen ohjaus ja kognitiivinen kitka',
                  'en': 'Socratic Steering and Cognitive Friction',
                },
              ),
              tdaAssertions: [
                TDAAssertion(
                  tdaId: 'tda_0195f3a0000070008000000000000007',
                  conceptDescription:
                      'Author actively probes foundational reasoning.',
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
                  child: BarsMatrixBuilder(
                    scales: scales,
                    onChanged: (newScales) {},
                  ),
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      await tester.binding.setSurfaceSize(null);
    });

    testWidgets(
      'BVA & Overflow: truncates >3 TDA assertions with "+N more" badge and renders mobile (<800px) & desktop (>5 scales) boundaries',
      (WidgetTester tester) async {
        List<MatrixScale>? updatedScales;
        final scales = List.generate(
          6,
          (i) => MatrixScale(
            score: 6 - i, // Unsorted input to verify ascending sort
            aiLabel: 'SCALE_${6 - i}',
            name: I18nText(translations: {'en': 'Grade ${6 - i}'}),
            claims: [
              MatrixClaim(
                label: const I18nText(translations: {'en': 'Boundary Claim'}),
                tdaAssertions: List.generate(
                  5,
                  (j) => TDAAssertion(
                    tdaId: 'tda_0195f3a000007000800000000000001$j',
                    conceptDescription: 'Assertion Concept $j',
                    inverseEvidence: false,
                    aggregationMode: AggregationMode.exists,
                  ),
                ),
              ),
            ],
          ),
        );

        // 1. Desktop > 5 scales (horizontal scroll boundary)
        await tester.binding.setSurfaceSize(const Size(1250, 800));
        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Scaffold(
              body: BarsMatrixBuilder(
                scales: scales,
                onChanged: (val) => updatedScales = val,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Expect + 2 more badge (5 assertions - 3 shown = 2 more)
        expect(find.text('+ 2 more'), findsWidgets);

        // Delete first sorted scale (score 1)
        final deleteButtons = find.byIcon(Icons.delete);
        await tester.tap(deleteButtons.first);
        await tester.pump();
        expect(updatedScales, isNotNull);
        expect(updatedScales!.length, 5);
        expect(updatedScales!.any((s) => s.score == 1), isFalse);

        // 2. Small / Mobile (<800px) linear Column layout
        await tester.binding.setSurfaceSize(const Size(600, 900));
        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Scaffold(
              body: SingleChildScrollView(
                child: BarsMatrixBuilder(scales: scales, onChanged: (_) {}),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(find.textContaining('1 - Grade 1'), findsOneWidget);

        await tester.binding.setSurfaceSize(null);
      },
    );

    testWidgets(
      'Negative Fail-Fast: throws AppException when claim label translation is missing for both active locale and en fallback',
      (WidgetTester tester) async {
        final invalidScales = [
          const MatrixScale(
            score: 1,
            aiLabel: 'BROKEN',
            claims: [
              MatrixClaim(
                label: I18nText(translations: {}), // Missing 'fi' and 'en'
                tdaAssertions: [],
              ),
            ],
          ),
        ];

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('fi'),
            home: Scaffold(
              body: SingleChildScrollView(
                child: BarsMatrixBuilder(
                  scales: invalidScales,
                  onChanged: (_) {},
                ),
              ),
            ),
          ),
        );

        final exception = tester.takeException();
        expect(exception, isA<AppException>());
      },
    );
  });
}
