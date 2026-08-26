import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets(
    'MatrixSummaryTableCard renders visible column chips and handles selection',
    (WidgetTester tester) async {
      OutputProfile payload = const OutputProfile(
        id: 'profile_1',
        workflowId: 'wf_1',
        name: I18nText(translations: {'en': 'Test Profile'}),
        targetBlockOrder: [TargetBlockType.matrixSummaryTableBlock],
        layouts: [
          OutputLayoutBlock(
            presetView: PresetView.matrixSummary,
            matrixVisibleColumns: ['label', 'score'],
          ),
        ],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: SingleChildScrollView(
              child: MatrixSummaryTableCard(
                payload: payload,
                updatePayload: (newPayload) {
                  payload = newPayload;
                },
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(MatrixSummaryTableCard), findsOneWidget);
      expect(find.byType(FilterChip), findsNWidgets(6));

      // Tap on quotes filter chip
      await tester.tap(find.widgetWithText(FilterChip, 'quotes'));
      await tester.pumpAndSettle();

      final summaryBlock = payload.layouts.firstWhere(
        (l) => l.presetView == PresetView.matrixSummary,
      );
      expect(summaryBlock.matrixVisibleColumns.contains('quotes'), isTrue);
    },
  );
}
