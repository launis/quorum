import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/features/reports/views/widgets/report_artifact_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const validReportId = 'rep_01960000000070008000000000000001';
  const validExecutionId = 'exec_01960000000070008000000000000001';
  const validProfileId = 'prf_01960000000070008000000000000001';
  final fixedTime = DateTime.utc(2026, 11, 1);

  ReportArtifactSummary buildSummary({
    ReportStatus status = ReportStatus.ready,
    String locale = 'fi',
    String title = 'Executive Synthesis Report',
  }) {
    return ReportArtifactSummary(
      id: validReportId,
      executionId: validExecutionId,
      profileId: validProfileId,
      locale: locale,
      title: title,
      status: status,
      createdAt: fixedTime,
      updatedAt: fixedTime,
    );
  }

  Widget buildHarness({
    required Widget child,
    Locale locale = const Locale('fi'),
    ThemeData? theme,
  }) {
    return MaterialApp(
      theme: theme ?? AppTheme.light,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: locale,
      home: Scaffold(body: Center(child: child)),
    );
  }

  group('ReportArtifactCard Hardening & ISTQB Widget Tests', () {
    testWidgets(
      'Positive: renders ready report card with AppErrorBoundary, localized badge, action buttons, and delete confirmation dialog',
      (WidgetTester tester) async {
        var selected = false;
        var pdfDownloaded = false;
        var excelDownloaded = false;
        var csvDownloaded = false;
        var regenerated = false;
        var deleted = false;

        final summary = buildSummary(status: ReportStatus.ready, locale: 'en');

        await tester.pumpWidget(
          buildHarness(
            locale: const Locale('en'),
            child: SizedBox(
              width: 320,
              child: ReportArtifactCard(
                report: summary,
                isSelected: true,
                onSelect: () => selected = true,
                onDownloadPdf: () => pdfDownloaded = true,
                onDownloadExcel: () => excelDownloaded = true,
                onDownloadCsv: () => csvDownloaded = true,
                onRegenerate: () => regenerated = true,
                onDelete: () => deleted = true,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        final l10nEn = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.byType(AppErrorBoundary), findsOneWidget);
        expect(find.text(l10nEn.reportStatusReady), findsOneWidget);
        expect(find.text('EN'), findsOneWidget);
        expect(find.text(validReportId), findsOneWidget);
        expect(find.text('Executive Synthesis Report'), findsOneWidget);

        await tester.tap(find.text('Executive Synthesis Report'));
        await tester.pumpAndSettle();
        expect(selected, isTrue);

        await tester.tap(find.byIcon(Icons.picture_as_pdf_outlined));
        await tester.pumpAndSettle();
        expect(pdfDownloaded, isTrue);

        await tester.tap(find.byIcon(Icons.table_chart_outlined));
        await tester.pumpAndSettle();
        expect(excelDownloaded, isTrue);

        await tester.tap(find.byIcon(Icons.description_outlined));
        await tester.pumpAndSettle();
        expect(csvDownloaded, isTrue);

        await tester.tap(find.byIcon(Icons.refresh));
        await tester.pumpAndSettle();
        expect(regenerated, isTrue);

        await tester.tap(find.byIcon(Icons.delete_outline));
        await tester.pumpAndSettle();

        expect(find.text(l10nEn.deleteReportConfirmTitle), findsOneWidget);
        expect(find.text(l10nEn.deleteReportConfirmMessage), findsOneWidget);

        // Confirm deletion in dialog
        await tester.tap(
          find.widgetWithText(FilledButton, l10nEn.deleteReportTooltip),
        );
        await tester.pumpAndSettle();
        expect(deleted, isTrue);
      },
    );

    testWidgets(
      'Negative/Boundary 1: hides download and regenerate buttons when status is generating and cancels delete on discard',
      (WidgetTester tester) async {
        var deleted = false;
        final generatingSummary = buildSummary(
          status: ReportStatus.generating,
          locale: 'fi',
        );

        await tester.pumpWidget(
          buildHarness(
            locale: const Locale('fi'),
            theme: AppTheme.dark,
            child: SizedBox(
              width: 256,
              child: ReportArtifactCard(
                report: generatingSummary,
                isSelected: false,
                onDownloadPdf: () {},
                onDownloadExcel: () {},
                onDownloadCsv: () {},
                onRegenerate: () {},
                onDelete: () => deleted = true,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10nFi.reportStatusGenerating), findsOneWidget);

        expect(find.byIcon(Icons.picture_as_pdf_outlined), findsNothing);
        expect(find.byIcon(Icons.table_chart_outlined), findsNothing);
        expect(find.byIcon(Icons.description_outlined), findsNothing);
        expect(find.byIcon(Icons.refresh), findsNothing);
        expect(find.byIcon(Icons.delete_outline), findsOneWidget);

        // Open delete dialog and cancel via discard button
        await tester.tap(find.byIcon(Icons.delete_outline));
        await tester.pumpAndSettle();

        await tester.tap(
          find.widgetWithText(TextButton, l10nFi.discardButtonLabel),
        );
        await tester.pumpAndSettle();
        expect(deleted, isFalse);
      },
    );

    testWidgets(
      'Negative/Boundary 2: renders pending and failed statuses under narrow constraint (180px) with long title without overflow',
      (WidgetTester tester) async {
        final failedSummary = buildSummary(
          status: ReportStatus.failed,
          locale: 'fi',
          title:
              'Erittäin pitkä raportin otsikko joka testaa tekstin katkaisua kapeassa näkymässä ilman ylivuotoa',
        );

        await tester.pumpWidget(
          buildHarness(
            locale: const Locale('fi'),
            child: SizedBox(
              width: 180,
              child: ReportArtifactCard(
                report: failedSummary,
                isSelected: false,
                onDownloadPdf: () {},
                onRegenerate: () {},
                onDelete: () {},
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10nFi.reportStatusFailed), findsOneWidget);
        expect(find.byIcon(Icons.picture_as_pdf_outlined), findsNothing);
        expect(find.byIcon(Icons.refresh), findsOneWidget);

        final pendingSummary = buildSummary(
          status: ReportStatus.pending,
          locale: 'fi',
        );

        await tester.pumpWidget(
          buildHarness(
            locale: const Locale('fi'),
            child: SizedBox(
              width: 180,
              child: ReportArtifactCard(
                report: pendingSummary,
                isSelected: false,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text(l10nFi.reportStatusPending), findsOneWidget);
      },
    );
  });
}
