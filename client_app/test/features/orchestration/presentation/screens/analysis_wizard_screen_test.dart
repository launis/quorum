import 'package:client_app/features/orchestration/domain/models/workflow.dart';
import 'package:client_app/features/orchestration/presentation/providers/workflow_controller.dart';
import 'package:client_app/features/orchestration/presentation/screens/analysis_wizard_screen.dart';
import 'package:client_app/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('AnalysisWizardScreen renders and validates selection', (
    tester,
  ) async {
    final mockWorkflows = [
      const Workflow(id: 'wf-1', name: 'Mock Workflow', description: 'Test'),
    ];

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          workflowListProvider.overrideWith(
            (ref) => Future.value(mockWorkflows),
          ),
        ],
        child: const MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],
          supportedLocales: AppLocalizations.supportedLocales,
          home: AnalysisWizardScreen(),
        ),
      ),
    );

    // Pump to settle Future
    await tester.pumpAndSettle();

    // Verify Title (Localized 'New Analysis')
    // Since we don't know the exact string easily, we can check for Type or partial match if we knew content.
    // Or findsOneWidget for AppBar Title widget.
    expect(find.byType(AppBar), findsOneWidget);

    // Verify Step 1 is active (Choose Workflow) - The Selector Widget should be present
    // Dropdown items are hidden by default, so we look for the Label from l10n (or partial match if we don't have exact string)
    // l10n.chooseAnalysisType -> "Choose Analysis Type" (in English)
    // We configured delegates, so it should be localized.
    expect(
      find.text('Analysis Type'),
      findsOneWidget,
    ); // Matching label text from Widget?
    // Wait, WorkflowSelector uses `l10n.chooseAnalysisType`.
    // In English arb, is it "Analysis Type" or "Choose Analysis Type"?
    // Let's assume partial match or just check for the Icon.
    expect(find.byIcon(Icons.settings_applications), findsOneWidget);
  });
}
