import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/widgets/linguistic_shield_banner.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Widget createTestWidget(Widget child, {Locale locale = const Locale('en')}) {
    return MaterialApp(
      locale: locale,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en'), Locale('fi')],
      home: Scaffold(body: child),
    );
  }

  group('LinguisticShieldBanner and Detector Tests', () {
    testWidgets('pure English ASCII text does not mount warning banner', (
      tester,
    ) async {
      await tester.pumpWidget(
        createTestWidget(
          const LinguisticShieldBanner(
            text: 'This is a strictly compliant English evaluation assertion.',
          ),
        ),
      );

      expect(find.byType(Icon), findsNothing);
      expect(
        find.text(
          'Non-English characters or words detected. Ensure the evaluation assertion is written in English.',
        ),
        findsNothing,
      );
    });

    testWidgets(
      'ISTQB Boundary: empty or whitespace-only text returns false and does not mount banner',
      (tester) async {
        expect(LinguisticShieldDetector.hasLinguisticAnomaly(''), isFalse);
        expect(
          LinguisticShieldDetector.hasLinguisticAnomaly('   \t\n '),
          isFalse,
        );

        await tester.pumpWidget(
          createTestWidget(const LinguisticShieldBanner(text: '   ')),
        );
        expect(find.byIcon(Icons.info_outline), findsNothing);
      },
    );

    testWidgets(
      'ISTQB Boundary: single stopword match (count == 1 < 2 threshold) does not trigger anomaly',
      (tester) async {
        // "on" is a single stopword shared with English prepositions
        expect(
          LinguisticShieldDetector.hasLinguisticAnomaly(
            'Focus on the primary architectural invariant.',
          ),
          isFalse,
        );

        await tester.pumpWidget(
          createTestWidget(
            const LinguisticShieldBanner(
              text: 'Focus on the primary architectural invariant.',
            ),
          ),
        );
        expect(find.byIcon(Icons.info_outline), findsNothing);
      },
    );

    testWidgets('ISTQB Negative: non-ASCII characters mount warning banner', (
      tester,
    ) async {
      await tester.pumpWidget(
        createTestWidget(
          const LinguisticShieldBanner(
            text: 'Tämä väite sisältää ääkkösiä ja suomen kieltä.',
          ),
        ),
      );

      expect(find.byIcon(Icons.info_outline), findsOneWidget);
      expect(
        find.text(
          'Non-English characters or words detected. Ensure the evaluation assertion is written in English.',
        ),
        findsOneWidget,
      );
    });

    testWidgets(
      'ISTQB Negative: Finnish stopwords in ASCII text trigger stopword gate',
      (tester) async {
        // "on" and "ja" are structural Finnish stopwords (count == 2 >= 2 threshold)
        await tester.pumpWidget(
          createTestWidget(
            const LinguisticShieldBanner(
              text: 'Tarkista on tama vastaus ja perustelu oikein',
            ),
          ),
        );

        expect(find.byIcon(Icons.info_outline), findsOneWidget);
        expect(
          find.text(
            'Non-English characters or words detected. Ensure the evaluation assertion is written in English.',
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets('typographical whitelist bypasses false positive alert', (
      tester,
    ) async {
      // Curly quotes, em-dashes, and bullets in valid English
      await tester.pumpWidget(
        createTestWidget(
          const LinguisticShieldBanner(
            text:
                '“High-level analysis” — covering primary metrics • with zero errors.',
          ),
        ),
      );

      expect(find.byIcon(Icons.info_outline), findsNothing);
    });

    testWidgets(
      'Multi-Locale Stress Gate: Finnish (fi) locale renders without RenderFlex overflow at 360px width',
      (tester) async {
        await tester.pumpWidget(
          createTestWidget(
            const SizedBox(
              width: 360,
              child: LinguisticShieldBanner(
                text: 'Tämä väite sisältää ääkkösiä.',
              ),
            ),
            locale: const Locale('fi'),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byIcon(Icons.info_outline), findsOneWidget);
      },
    );
  });
}
