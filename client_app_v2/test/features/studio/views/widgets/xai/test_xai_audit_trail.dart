import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/views/widgets/xai_axis_telemetry_grid.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

void main() {
  testWidgets(
    'XAIAxisTelemetryGrid renders contextual override explanation instead of citation quote',
    (WidgetTester tester) async {
      // 1. Create a MatrixScorecardRowDto with contextualOverride = true
      const axis = MatrixScorecardRowDto(
        blockId: 'blk_test_matrix',
        name: 'Test Dimension',
        labelI18n: const I18nText(
          translations: {'fi': 'Testi Matriisi', 'en': 'Test Matrix'},
        ),
        rowExplanation: 'This is the explanation of the row.',
        contextualOverride: true,
        semanticReasoning:
            'This is the detailed semantic reasoning explaining page 12 of the document.',
        evidenceType: EvidenceType.explicitQuote,
      );

      // 2. Build the widget with Localizations support
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'),
          home: Scaffold(
            body: SingleChildScrollView(
              child: XAIAxisTelemetryGrid(
                axis: axis,
                textDeliveryMode: 'full',
                showQuote: true,
              ),
            ),
          ),
        ),
      );

      // 3. Verify that the row explanation is shown
      expect(find.text('This is the explanation of the row.'), findsOneWidget);

      // 4. Verify that the semantic explanation reasoning is rendered
      expect(
        find.textContaining(
          '💡 AI Semantic Explanation (Contextual Override):',
        ),
        findsOneWidget,
      );
      expect(
        find.textContaining(
          'This is the detailed semantic reasoning explaining page 12 of the document.',
        ),
        findsOneWidget,
      );

      // 5. Verify that the standard quote is NOT shown
      expect(
        find.textContaining('💬 Excerpt from original text:'),
        findsNothing,
      );
    },
  );
}
