import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/workflow_client.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/views/dynamic_start_screen.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/workflow_ui_schema.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:mocktail/mocktail.dart';

class MockWorkflowClient extends Mock implements WorkflowClient {}

class MockExecutionClient extends Mock implements ExecutionClient {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late MockWorkflowClient mockWorkflowClient;
  late MockExecutionClient mockExecutionClient;
  late MockLoggerService mockLogger;

  const testWorkflowId = 'wf_0123456789abcdef';

  final standardInput = const ExpectedInput(
    inputKey: 'transcription',
    label: I18nText(translations: {'en': 'Transcription', 'fi': 'Transkriptio'}),
    required: true,
    description: I18nText(translations: {'en': 'Interview transcription'}),
  );

  final questionnaireInput = const ExpectedInput(
    inputKey: 'survey',
    label: I18nText(translations: {'en': 'Survey', 'fi': 'Kysely'}),
    required: false,
    inputModes: ['questionnaire'],
    description: I18nText(translations: {'en': 'Survey questionnaire'}),
    questionnaireDefinition: [
      QuestionnaireItem(
        questionId: 'q1',
        question: I18nText(translations: {'en': 'Company name', 'fi': 'Yrityksen nimi'}),
        type: 'text',
      ),
    ],
  );

  setUpAll(() {
    registerFallbackValue(const ExecutionCreateRequestDto(
      workflowId: testWorkflowId,
      targetLocale: 'en',
    ));
  });

  setUp(() {
    mockWorkflowClient = MockWorkflowClient();
    mockExecutionClient = MockExecutionClient();
    mockLogger = MockLoggerService();
  });

  Widget createTestWidget({
    Locale locale = const Locale('en'),
  }) {
    return ProviderScope(
      overrides: [
        workflowClientProvider.overrideWithValue(mockWorkflowClient),
        executionClientProvider.overrideWithValue(mockExecutionClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
      ],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en'), Locale('fi')],
        locale: locale,
        home: const Scaffold(
          body: DynamicStartScreen(workflowId: testWorkflowId),
        ),
      ),
    );
  }

  group('DynamicStartScreen Widget Tests', () {
    testWidgets('renders loading indicator while schema is resolving',
        (tester) async {
      when(() => mockWorkflowClient.getWorkflowUiSchema(testWorkflowId))
          .thenAnswer((_) => Completer<WorkflowUiSchema>().future);

      await tester.pumpWidget(createTestWidget());
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('renders ErrorView when schema loading fails (Negative Test)',
        (tester) async {
      when(() => mockWorkflowClient.getWorkflowUiSchema(testWorkflowId))
          .thenThrow(Exception('Failed to fetch schema'));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      expect(find.byType(ErrorView), findsOneWidget);
    });

    testWidgets('renders input fields, questionnaire, and executes start on click',
        (tester) async {
      final schema = WorkflowUiSchema(
        expectedInputs: [standardInput, questionnaireInput],
      );

      when(() => mockWorkflowClient.getWorkflowUiSchema(testWorkflowId))
          .thenAnswer((_) async => schema);

      when(() => mockExecutionClient.startExecution(
            request: any(named: 'request'),
          )).thenAnswer((_) async => const ExecutionRecord(
            id: 'exec_123',
            workflowId: testWorkflowId,
            targetLocale: 'en',
            status: 'PENDING',
          ));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Verify header and fields
      expect(find.textContaining(testWorkflowId), findsOneWidget);
      expect(find.textContaining('Transcription *'), findsOneWidget);
      expect(find.textContaining('Survey'), findsOneWidget);
      expect(find.text('Company name'), findsOneWidget);

      // Fill in questionnaire
      await tester.enterText(find.byType(TextFormField).first, 'Acme Corp');
      await tester.pumpAndSettle();

      // Tap start button
      final startButton = find.byType(FilledButton);
      expect(startButton, findsOneWidget);
      await tester.tap(startButton);
      await tester.pumpAndSettle();

      verify(() => mockExecutionClient.startExecution(
            request: any(named: 'request'),
          )).called(1);
    });
  });
}
