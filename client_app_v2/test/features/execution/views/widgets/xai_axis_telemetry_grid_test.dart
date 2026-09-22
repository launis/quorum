import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/xai_axis_telemetry_grid.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

void main() {
  Widget buildTestableWidget({
    required MatrixScorecardRowDto axis,
    TextDeliveryMode deliveryMode = TextDeliveryMode.full,
    bool showQuote = true,
  }) {
    return MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: const Locale('en'),
      home: Scaffold(
        body: SingleChildScrollView(
          child: XAIAxisTelemetryGrid(
            axis: axis,
            textDeliveryMode: deliveryMode,
            showQuote: showQuote,
          ),
        ),
      ),
    );
  }

  testWidgets(
    'XAIAxisTelemetryGrid renders main content and telemetry grid in full delivery mode',
    (WidgetTester tester) async {
      const axis = MatrixScorecardRowDto(
        blockId: 'blk_1',
        name: 'Strategic Vision',
        labelI18n: I18nText(translations: {'en': 'Strategic Vision'}),
        rowExplanation: 'Consistent strategic orientation demonstrated.',
        evidenceType: EvidenceType.explicitQuote,
        citedTextQuote: 'Our multi-year strategy prioritizes AI.',
        citedSourceId: 'src_doc_1',
        citedWebCitation: 'https://example.com/strategy',
        confidence: 0.92,
        coaching: 'Maintain cross-functional communication cadence.',
        falsification: 'Falsified if Q3 targets are abandoned.',
        remediationSteps: 'Align roadmaps quarterly.',
        isEvaluative: true,
        allowContextualOverride: false,
      );

      await tester.pumpWidget(buildTestableWidget(axis: axis));
      await tester.pumpAndSettle();

      expect(
        find.text('Consistent strategic orientation demonstrated.'),
        findsOneWidget,
      );
      expect(find.byIcon(Icons.check_circle), findsOneWidget);
      expect(find.byIcon(Icons.format_quote), findsOneWidget);
      expect(
        find.byIcon(Icons.gavel),
        findsNWidgets(2),
      ); // framework + falsification
      expect(find.byIcon(Icons.verified), findsOneWidget);
      expect(find.textContaining('92%'), findsOneWidget);
      expect(
        find.text('Maintain cross-functional communication cadence.'),
        findsOneWidget,
      );
      expect(
        find.text('Falsified if Q3 targets are abandoned.'),
        findsOneWidget,
      );
      expect(find.text('Align roadmaps quarterly.'), findsOneWidget);
    },
  );

  testWidgets(
    'XAIAxisTelemetryGrid returns empty SizedBox when textDeliveryMode is none',
    (WidgetTester tester) async {
      const axis = MatrixScorecardRowDto(
        blockId: 'blk_none',
        name: 'Hidden Axis',
        labelI18n: I18nText(translations: {'en': 'Hidden Axis'}),
        rowExplanation: 'Should not render in mode none.',
        isEvaluative: false,
        allowContextualOverride: false,
      );

      await tester.pumpWidget(
        buildTestableWidget(axis: axis, deliveryMode: TextDeliveryMode.none),
      );
      await tester.pumpAndSettle();

      expect(find.text('Should not render in mode none.'), findsNothing);
    },
  );

  testWidgets(
    'XAIAxisTelemetryGrid suppresses telemetry grid when textDeliveryMode is titlesOnly',
    (WidgetTester tester) async {
      const axis = MatrixScorecardRowDto(
        blockId: 'blk_titles_only',
        name: 'Titles Only Axis',
        labelI18n: I18nText(translations: {'en': 'Titles Only Axis'}),
        rowExplanation: 'Titles only explanation shown.',
        confidence: 0.88,
        coaching: 'Coaching text should be hidden in titlesOnly mode.',
        isEvaluative: false,
        allowContextualOverride: false,
      );

      await tester.pumpWidget(
        buildTestableWidget(
          axis: axis,
          deliveryMode: TextDeliveryMode.titlesOnly,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Titles only explanation shown.'), findsOneWidget);
      expect(
        find.text('Coaching text should be hidden in titlesOnly mode.'),
        findsNothing,
      );
      expect(find.text('88%'), findsNothing);
    },
  );

  testWidgets(
    'XAIAxisTelemetryGrid renders semantic reasoning when contextualOverride is true',
    (WidgetTester tester) async {
      const axis = MatrixScorecardRowDto(
        blockId: 'blk_override',
        name: 'Override Axis',
        labelI18n: I18nText(translations: {'en': 'Override Axis'}),
        rowExplanation: 'Override row explanation.',
        contextualOverride: true,
        semanticReasoning: 'Cognitive reasoning justifies positive evaluation.',
        citedTextQuote: 'Ignored quote when override is true.',
        isEvaluative: true,
        allowContextualOverride: true,
      );

      await tester.pumpWidget(buildTestableWidget(axis: axis));
      await tester.pumpAndSettle();

      expect(find.text('Override row explanation.'), findsOneWidget);
      expect(find.byIcon(Icons.lightbulb_outline), findsOneWidget);
      // Quote icon should be suppressed when contextualOverride is true
      expect(find.byIcon(Icons.format_quote), findsNothing);
    },
  );

  testWidgets(
    'XAIAxisTelemetryGrid renders distinct evidence icons for all EvidenceType values',
    (WidgetTester tester) async {
      const explicitAxis = MatrixScorecardRowDto(
        blockId: 'blk_exp',
        name: 'Explicit',
        labelI18n: I18nText(translations: {'en': 'Explicit'}),
        rowExplanation: 'Explicit quote evidence.',
        evidenceType: EvidenceType.explicitQuote,
        isEvaluative: true,
        allowContextualOverride: false,
      );

      const impliedAxis = MatrixScorecardRowDto(
        blockId: 'blk_imp',
        name: 'Implied',
        labelI18n: I18nText(translations: {'en': 'Implied'}),
        rowExplanation: 'Implied intent evidence.',
        evidenceType: EvidenceType.impliedIntent,
        isEvaluative: true,
        allowContextualOverride: false,
      );

      const noEvidenceAxis = MatrixScorecardRowDto(
        blockId: 'blk_nonev',
        name: 'No Evidence',
        labelI18n: I18nText(translations: {'en': 'No Evidence'}),
        rowExplanation: 'No evidence found.',
        evidenceType: EvidenceType.noEvidence,
        isEvaluative: true,
        allowContextualOverride: false,
      );

      await tester.pumpWidget(buildTestableWidget(axis: explicitAxis));
      await tester.pumpAndSettle();
      expect(find.byIcon(Icons.check_circle), findsOneWidget);

      await tester.pumpWidget(buildTestableWidget(axis: impliedAxis));
      await tester.pumpAndSettle();
      expect(find.byIcon(Icons.warning), findsOneWidget);

      await tester.pumpWidget(buildTestableWidget(axis: noEvidenceAxis));
      await tester.pumpAndSettle();
      expect(find.byIcon(Icons.cancel), findsOneWidget);
    },
  );

  testWidgets(
    'XAIAxisTelemetryGrid returns empty SizedBox when all main content fields are blank',
    (WidgetTester tester) async {
      const blankAxis = MatrixScorecardRowDto(
        blockId: 'blk_blank',
        name: 'Blank Axis',
        labelI18n: I18nText(translations: {'en': 'Blank Axis'}),
        rowExplanation: '',
        isEvaluative: false,
        allowContextualOverride: false,
      );

      await tester.pumpWidget(buildTestableWidget(axis: blankAxis));
      await tester.pumpAndSettle();

      expect(find.byType(Text), findsNothing);
    },
  );
}
