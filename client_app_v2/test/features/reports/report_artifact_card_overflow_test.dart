import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/features/reports/views/widgets/report_artifact_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets(
    'ReportArtifactCard in master sidebar width with Finnish failed status renders without overflow',
    (WidgetTester tester) async {
      final report = ReportArtifactSummary(
        id: 'rep_c27224f120164da4',
        executionId: 'exe_4f1d346783054b56',
        profileId: 'prf_01b1d71000000001',
        locale: 'fi',
        title: 'Tekoälyajokortti: Vuorovaikutus ja yhteistyö',
        status: ReportStatus.failed,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('fi'),
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 256,
                child: ReportArtifactCard(
                  report: report,
                  isSelected: false,
                  onSelect: () {},
                  onRegenerate: () {},
                  onDelete: () {},
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'ReportArtifactCard under extreme narrow constraint (180px) renders without overflow',
    (WidgetTester tester) async {
      final report = ReportArtifactSummary(
        id: 'rep_c27224f120164da4',
        executionId: 'exe_4f1d346783054b56',
        profileId: 'prf_01b1d71000000001',
        locale: 'fi',
        title: 'Tekoälyajokortti: Vuorovaikutus ja yhteistyö',
        status: ReportStatus.generating,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('fi'),
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 180,
                child: ReportArtifactCard(
                  report: report,
                  isSelected: false,
                  onSelect: () {},
                  onRegenerate: () {},
                  onDelete: () {},
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'ReportArtifactCard with ready status and 4 action buttons renders without overflow in sidebar width',
    (WidgetTester tester) async {
      final report = ReportArtifactSummary(
        id: 'rep_c27224f120164da4',
        executionId: 'exe_4f1d346783054b56',
        profileId: 'prf_01b1d71000000001',
        locale: 'fi',
        title: 'Tekoälyajokortti: Vuorovaikutus ja yhteistyö',
        status: ReportStatus.ready,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('fi'),
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 256,
                child: ReportArtifactCard(
                  report: report,
                  isSelected: false,
                  onSelect: () {},
                  onDownloadPdf: () {},
                  onDownloadExcel: () {},
                  onDownloadCsv: () {},
                  onRegenerate: () {},
                  onDelete: () {},
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    },
  );
}
