import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/features/reports/views/dialogs/create_report_dialog.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockReportsClient extends Mock implements ReportsClient {}

void main() {
  late MockStudioClient mockStudioClient;
  late MockReportsClient mockReportsClient;

  const testExecutionId = 'exe_01b1d71000000001';
  const testWorkflowId = 'wor_01b1d71000000001';
  const testProfileId = 'prf_01b1d71000000001';

  const testProfile = OutputProfile(
    id: testProfileId,
    workflowId: testWorkflowId,
    name: I18nText(translations: {'fi': 'Testiprofiili', 'en': 'Test Profile'}),
  );

  setUp(() {
    mockStudioClient = MockStudioClient();
    mockReportsClient = MockReportsClient();
  });

  Widget buildTestDialog({
    String? workflowId = testWorkflowId,
    String? initialProfileId,
  }) {
    return ProviderScope(
      overrides: [
        studioClientProvider.overrideWithValue(mockStudioClient),
        reportsClientProvider.overrideWithValue(mockReportsClient),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('fi'),
        home: Scaffold(
          body: CreateReportDialog(
            executionId: testExecutionId,
            workflowId: workflowId,
            initialProfileId: initialProfileId,
          ),
        ),
      ),
    );
  }

  testWidgets(
    'CreateReportDialog renders profiles and auto-selects first profile',
    (WidgetTester tester) async {
      when(
        () => mockStudioClient.getOutputProfiles(),
      ).thenAnswer((_) async => [testProfile]);

      await tester.pumpWidget(buildTestDialog());
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      expect(find.text('Luo uusi tuloste'), findsOneWidget);
      expect(find.text('Testiprofiili'), findsOneWidget);
      expect(find.text('Suomi (FI)'), findsOneWidget);
    },
  );

  testWidgets(
    'CreateReportDialog displays inline error when studio client fails to load profiles',
    (WidgetTester tester) async {
      when(
        () => mockStudioClient.getOutputProfiles(),
      ).thenThrow(Exception('Backend network timeout'));

      await tester.pumpWidget(buildTestDialog());
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      expect(find.text('Exception: Backend network timeout'), findsOneWidget);
      expect(find.byType(SnackBar), findsNothing);
    },
  );

  testWidgets(
    'CreateReportDialog shows discard confirmation on Escape when dirty with preface text',
    (WidgetTester tester) async {
      when(
        () => mockStudioClient.getOutputProfiles(),
      ).thenAnswer((_) async => [testProfile]);

      await tester.pumpWidget(buildTestDialog());
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Enter preface text to make dirty
      await tester.enterText(
        find.byType(TextFormField),
        'Custom executive preface notes',
      );
      await tester.pump();

      // Trigger Escape shortcut
      await tester.sendKeyEvent(LogicalKeyboardKey.escape);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Confirmation dialog should be shown
      expect(find.text('Hylätäänkö muutokset?'), findsOneWidget);
      expect(find.text('Jatka muokkausta'), findsOneWidget);
      expect(find.text('Hylkää muutokset'), findsOneWidget);

      // Tap keep editing
      await tester.tap(find.text('Jatka muokkausta'));
      await tester.pump();

      expect(find.text('Hylätäänkö muutokset?'), findsNothing);
      expect(find.text('Custom executive preface notes'), findsOneWidget);
    },
  );

  testWidgets(
    'CreateReportDialog successfully submits and pops result summary',
    (WidgetTester tester) async {
      when(
        () => mockStudioClient.getOutputProfiles(),
      ).thenAnswer((_) async => [testProfile]);

      final reportSummary = ReportArtifactSummary(
        id: 'rep_01b1d71000000001',
        executionId: testExecutionId,
        profileId: testProfileId,
        locale: 'fi',
        title: 'Uusi Raportti',
        status: ReportStatus.generating,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      when(
        () => mockReportsClient.createReport(
          executionId: testExecutionId,
          profileId: testProfileId,
          locale: 'fi',
          customPrefaceMd: any(named: 'customPrefaceMd'),
        ),
      ).thenAnswer((_) async => reportSummary);

      await tester.pumpWidget(buildTestDialog());
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Tap generate report button
      await tester.tap(find.text('Generoi tuloste'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      verify(
        () => mockReportsClient.createReport(
          executionId: testExecutionId,
          profileId: testProfileId,
          locale: 'fi',
          customPrefaceMd: null,
        ),
      ).called(1);
    },
  );
}
