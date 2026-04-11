import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/components/bars_matrix_builder.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

void main() {
  group('BarsMatrixBuilder Component Tests', () {
    testWidgets('renders Desktop Three-Pane format correctly', (
      WidgetTester tester,
    ) async {
      final scales = [
        const MatrixScale(
          score: 1,
          aiLabel: 'LOW',
          name: I18nText(defaultLocale: 'en', translations: {'en': 'Terrible'}),
          claims: [
            MatrixClaim(
              label: I18nText(
                defaultLocale: 'en',
                translations: {'en': 'Claim 1'},
              ),
              aiDescription: 'AI Rule 1',
              microAtoms: ['Atom 1', 'Atom 2'],
            ),
          ],
        ),
        const MatrixScale(
          score: 5,
          aiLabel: 'HIGH',
          name: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Excellent'},
          ),
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
      expect(find.text('Atom'), findsWidgets); // Due to microAtoms mapping

      // Cleanup
      await tester.binding.setSurfaceSize(null);
    });
  });
}
