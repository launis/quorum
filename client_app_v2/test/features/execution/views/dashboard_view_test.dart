import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/execution/views/dashboard_view.dart';
import 'package:client_app/features/execution/controllers/execution_controller.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/views/new_execution_view.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_theme.dart';

void main() {
  Widget createTestWidget({
    List overrides = const [],
    Size screenSize = const Size(1920, 1080),
  }) {
    return ProviderScope(
      overrides: overrides.cast(),
      child: MaterialApp(
        theme: AppTheme.light,
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en'), Locale('fi')],
        home: MediaQuery(
          data: MediaQueryData(size: screenSize),
          child: const DashboardView(),
        ),
      ),
    );
  }

  Workflow createWorkflow({
    required String id,
    required String name,
  }) {
    return Workflow(
      id: id,
      slug: 'slug_$id',
      name: I18nText(translations: {'en': name, 'fi': 'FI $name'}),
      description: const I18nText(translations: {'en': 'Desc', 'fi': 'Kuvaus'}),
      modelRegistryId: 'reg_default',
      outputProfiles: const {},
    );
  }

  ExecutionRecord createExecution({
    required String id,
    required String workflowId,
    required String status,
    String? createdAt,
    double? costEstimate,
    int promptTokens = 100,
    int completionTokens = 50,
  }) {
    return ExecutionRecord(
      id: id,
      workflowId: workflowId,
      targetLocale: 'en',
      status: status,
      createdAt: createdAt ?? '2026-10-12T10:00:00.000Z',
      costEstimate: costEstimate ?? 0.05,
      promptTokens: promptTokens,
      completionTokens: completionTokens,
    );
  }

  group('DashboardView Widget Tests', () {
    testWidgets('renders empty state when no executions are present', (tester) async {
      await tester.pumpWidget(
        createTestWidget(
          overrides: [
            executionListProvider.overrideWith((ref) => Future.value([])),
            availableWorkflowsProvider.overrideWith((ref) => Future.value([])),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Executions Dashboard'), findsOneWidget);
      expect(find.text('No executions found.'), findsOneWidget);
      expect(find.byType(FloatingActionButton), findsOneWidget);
    });

    testWidgets('renders execution list with workflow title, status chip, and metrics', (tester) async {
      final wf = createWorkflow(id: 'wor_causal_01', name: 'Causal Discovery Workflow');
      final exec = createExecution(
        id: 'exe_test_01',
        workflowId: 'wor_causal_01',
        status: 'completed',
        createdAt: '2026-10-12T12:00:00.000Z',
        costEstimate: 0.123456,
      );

      await tester.pumpWidget(
        createTestWidget(
          overrides: [
            executionListProvider.overrideWith((ref) => Future.value([exec])),
            availableWorkflowsProvider.overrideWith((ref) => Future.value([wf])),
          ],
        ),
      );
      await tester.pumpAndSettle();

      // Check workflow title display
      expect(find.textContaining('Causal Discovery Workflow'), findsOneWidget);

      // Check execution ID and status chip
      expect(find.textContaining('exe_test_01'), findsOneWidget);
      expect(find.text('COMPLETED'), findsOneWidget);

      // Check actions: Print, Replay, Delete
      expect(find.byIcon(Icons.print), findsOneWidget);
      expect(find.byIcon(Icons.replay), findsOneWidget);
      expect(find.byIcon(Icons.delete), findsOneWidget);
    });

    testWidgets('negative boundary: renders ErrorView when execution list provider throws', (tester) async {
      await tester.pumpWidget(
        createTestWidget(
          overrides: [
            executionListProvider.overrideWith(
              (ref) => Future.error(Exception('Failed to load executions')),
            ),
            availableWorkflowsProvider.overrideWith((ref) => Future.value([])),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(ErrorView), findsOneWidget);
      expect(find.byIcon(Icons.error_outline), findsOneWidget);
      expect(find.byIcon(Icons.refresh), findsWidgets);
    });

    testWidgets('boundary test: renders different status chips appropriately', (tester) async {
      final execs = [
        createExecution(id: 'exe_pass', workflowId: 'wor_1', status: 'passed'),
        createExecution(id: 'exe_fail', workflowId: 'wor_1', status: 'failed'),
        createExecution(id: 'exe_run', workflowId: 'wor_1', status: 'running'),
      ];

      await tester.pumpWidget(
        createTestWidget(
          overrides: [
            executionListProvider.overrideWith((ref) => Future.value(execs)),
            availableWorkflowsProvider.overrideWith((ref) => Future.value([])),
          ],
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('PASSED'), findsOneWidget);
      expect(find.text('FAILED'), findsOneWidget);
      expect(find.text('RUNNING'), findsOneWidget);
    });
  });
}
