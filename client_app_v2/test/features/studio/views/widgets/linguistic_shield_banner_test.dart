import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/widgets/linguistic_shield_banner.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Widget createTestWidget(Widget child) {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en')],
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
        // "on" and "ja" are structural Finnish stopwords
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
  });
}
