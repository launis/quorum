import 'dart:async';
import 'dart:io';

import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/reports_client.dart';
import 'package:client_app/core/api/sse_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/models/generic_status_response_dto.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/human_override_request_dto.dart';
import 'package:client_app/features/execution/views/execution_view.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/execution_timeline.dart';
import 'package:client_app/shared/widgets/global_error_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

const String _validExecId = 'exe_0195f2c4e8a97d3b9a1c2e3f4a5b6c7d';
const String _validWfId = 'wfl_0195f2c4e8a97d3b9a1c2e3f4a5b6c7d';
const String _validProfileId = 'prf_0195f2c4e8a97d3b9a1c2e3f4a5b6c7d';
const String _validReportId = 'rep_0195f2c4e8a97d3b9a1c2e3f4a5b6c7d';

class _ControlledSseClient implements SseClient {
  StreamController<Map<String, Object?>> _controller =
      StreamController<Map<String, Object?>>(onCancel: () async {});
  int subscribeCount = 0;

  void emit(Map<String, Object?> event) {
    _controller.add(event);
  }

  @override
  Stream<Map<String, Object?>> subscribeToExecution(String executionId) {
    subscribeCount++;
    _controller = StreamController<Map<String, Object?>>(onCancel: () async {});
    return _controller.stream;
  }

  Future<void> dispose() async {
    if (!_controller.isClosed) {
      await _controller.close();
    }
  }
}

class _StubExecutionClient implements ExecutionClient {
  final bool shouldFailResume;

  _StubExecutionClient({this.shouldFailResume = false});

  @override
  Future<ExecutionRecord> startExecution({
    required ExecutionCreateRequestDto request,
  }) async {
    return ExecutionRecord(
      id: _validExecId,
      workflowId: request.workflowId,
      targetLocale: request.targetLocale,
      status: 'RUNNING',
    );
  }

  @override
  Future<ExecutionRecord> resumeExecution(String executionId) async {
    if (shouldFailResume) {
      throw AppException.server('Rehydration failed', statusCode: 500);
    }
    return ExecutionRecord(
      id: executionId,
      workflowId: _validWfId,
      targetLocale: 'fi',
      status: 'RUNNING',
    );
  }

  @override
  Future<ExecutionRecord> getExecutionStatus(String executionId) async {
    return ExecutionRecord(
      id: executionId,
      workflowId: _validWfId,
      targetLocale: 'fi',
      status: 'PASSED',
    );
  }

  @override
  Future<GenericStatusResponseDto> overrideAtom({
    required String executionId,
    required String atomId,
    required HumanOverrideRequestDto payload,
  }) async {
    return const GenericStatusResponseDto(message: 'ok');
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _StubReportsClient implements Fake, ReportsClient {
  bool shouldFailCreate;
  int createReportCallCount = 0;
  String? lastProfileId;

  _StubReportsClient({this.shouldFailCreate = false});

  @override
  Future<ReportArtifactSummary> createReport({
    required String executionId,
    required CreateReportRequest request,
  }) async {
    createReportCallCount++;
    lastProfileId = request.profileId;
    if (shouldFailCreate) {
      throw AppException.server('Report compilation failed', statusCode: 500);
    }
    return ReportArtifactSummary(
      id: _validReportId,
      executionId: executionId,
      profileId: request.profileId,
      locale: request.locale,
      title: 'Executive Report',
      status: ReportStatus.generating,
      createdAt: DateTime.utc(2026, 1, 1),
      updatedAt: DateTime.utc(2026, 1, 1),
    );
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _StubLoggerService implements LoggerService {
  final List<String> errors = [];

  @override
  Future<void> init({File? logFile}) async {}
  @override
  void debug(String context, String message) {}
  @override
  void info(String context, String message) {}
  @override
  void warning(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {}
  @override
  void error(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    errors.add('$context: $message');
  }
}

GoRouter _buildTestRouter({bool autoGenerateReport = false}) {
  return GoRouter(
    initialLocation: '/execution/$_validExecId',
    routes: [
      GoRoute(
        path: '/execution/:executionId',
        builder: (context, state) => ExecutionView(
          executionId: state.pathParameters['executionId']!,
          autoGenerateReport: autoGenerateReport,
        ),
        routes: [
          GoRoute(
            path: 'report',
            builder: (context, state) =>
                const Scaffold(body: Center(child: Icon(Icons.summarize))),
          ),
        ],
      ),
    ],
  );
}

Widget _buildTestApp({
  required GoRouter router,
  required SseClient sseClient,
  required ExecutionClient executionClient,
  required ReportsClient reportsClient,
  required LoggerService loggerService,
}) {
  return ProviderScope(
    overrides: [
      sseClientProvider.overrideWithValue(sseClient),
      executionClientProvider.overrideWithValue(executionClient),
      reportsClientProvider.overrideWithValue(reportsClient),
      loggerServiceProvider.overrideWithValue(loggerService),
    ],
    child: MaterialApp.router(
      routerConfig: router,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en'), Locale('fi')],
      locale: const Locale('en'),
    ),
  );
}

void main() {
  group('ExecutionView Hardening Widget Tests', () {
    testWidgets(
      'Positive 1: renders running execution with progress, status message, version drift warning, and timeline steps, then transitions to PASSED',
      (WidgetTester tester) async {
        final sseClient = _ControlledSseClient();
        addTearDown(sseClient.dispose);
        final execClient = _StubExecutionClient();
        final reportsClient = _StubReportsClient();
        final logger = _StubLoggerService();
        final router = _buildTestRouter();
        addTearDown(router.dispose);

        await tester.pumpWidget(
          _buildTestApp(
            router: router,
            sseClient: sseClient,
            executionClient: execClient,
            reportsClient: reportsClient,
            loggerService: logger,
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        sseClient.emit({
          'id': _validExecId,
          'workflow_id': _validWfId,
          'target_locale': 'en',
          'status': 'RUNNING',
          'progress': 45,
          'status_message': 'Evaluating TDA assertions...',
          'frozen_context': {'version_id': 'v1.9.0'},
          'steps': [
            {
              'id': 'stp_0195f2c4e8a97d3b9a1c2e3f4a5b6c7d',
              'label': 'Step 1 Ingestion',
              'status': 'PASSED',
            },
          ],
        });
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(find.byType(LinearProgressIndicator), findsOneWidget);
        expect(find.text('Evaluating TDA assertions...'), findsOneWidget);
        expect(find.text('45%'), findsOneWidget);
        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
        expect(find.byType(ExecutionTimeline), findsOneWidget);

        sseClient.emit({
          'id': _validExecId,
          'workflow_id': _validWfId,
          'target_locale': 'en',
          'status': 'PASSED',
          'output_profile_id': _validProfileId,
        });
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(find.byIcon(Icons.check_circle), findsOneWidget);
        expect(find.byIcon(Icons.article_outlined), findsOneWidget);
      },
    );

    testWidgets(
      'Positive 2: auto-generates report when autoGenerateReport is true and execution completes with valid outputProfileId',
      (WidgetTester tester) async {
        final sseClient = _ControlledSseClient();
        addTearDown(sseClient.dispose);
        final execClient = _StubExecutionClient();
        final reportsClient = _StubReportsClient();
        final logger = _StubLoggerService();
        final router = _buildTestRouter(autoGenerateReport: true);
        addTearDown(router.dispose);

        await tester.pumpWidget(
          _buildTestApp(
            router: router,
            sseClient: sseClient,
            executionClient: execClient,
            reportsClient: reportsClient,
            loggerService: logger,
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        sseClient.emit({
          'id': _validExecId,
          'workflow_id': _validWfId,
          'target_locale': 'en',
          'status': 'PASSED',
          'output_profile_id': _validProfileId,
        });
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(reportsClient.createReportCallCount, 1);
        expect(reportsClient.lastProfileId, _validProfileId);
        expect(logger.errors, isEmpty);
      },
    );

    testWidgets(
      'Negative 1: renders ErrorView on stream error payload and reconnects when retry is tapped',
      (WidgetTester tester) async {
        final sseClient = _ControlledSseClient();
        addTearDown(sseClient.dispose);
        final execClient = _StubExecutionClient();
        final reportsClient = _StubReportsClient();
        final logger = _StubLoggerService();
        final router = _buildTestRouter();
        addTearDown(router.dispose);

        await tester.pumpWidget(
          _buildTestApp(
            router: router,
            sseClient: sseClient,
            executionClient: execClient,
            reportsClient: reportsClient,
            loggerService: logger,
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));
        expect(sseClient.subscribeCount, 1);

        sseClient.emit({
          'error_code': 'QUOTA_EXCEEDED',
          'message': 'Upstream LLM quota exceeded',
        });
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(find.byType(ErrorView), findsOneWidget);

        final retryButton = find.byIcon(Icons.refresh);
        await tester.ensureVisible(retryButton);
        await tester.tap(retryButton);
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(sseClient.subscribeCount, 2);
      },
    );

    testWidgets(
      'Negative 2: renders GlobalErrorView and recoverable MutationButton on FAILED execution, showing SnackBar when rehydration fails',
      (WidgetTester tester) async {
        final sseClient = _ControlledSseClient();
        addTearDown(sseClient.dispose);
        final execClient = _StubExecutionClient(shouldFailResume: true);
        final reportsClient = _StubReportsClient();
        final logger = _StubLoggerService();
        final router = _buildTestRouter();
        addTearDown(router.dispose);

        await tester.pumpWidget(
          _buildTestApp(
            router: router,
            sseClient: sseClient,
            executionClient: execClient,
            reportsClient: reportsClient,
            loggerService: logger,
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        sseClient.emit({
          'id': _validExecId,
          'workflow_id': _validWfId,
          'target_locale': 'en',
          'status': 'FAILED',
          'error': 'Step synthesis failed with timeout',
          'is_resumable': true,
        });
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(find.byType(GlobalErrorView), findsOneWidget);
        expect(find.byIcon(Icons.error), findsOneWidget);

        await tester.tap(find.byIcon(Icons.refresh).first);
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(find.byType(SnackBar), findsOneWidget);
        expect(logger.errors, isNotEmpty);
      },
    );

    testWidgets(
      'Negative/Boundary 3: renders inline report failure alert when createReport throws, then succeeds on retry tap',
      (WidgetTester tester) async {
        final sseClient = _ControlledSseClient();
        addTearDown(sseClient.dispose);
        final execClient = _StubExecutionClient();
        final reportsClient = _StubReportsClient(shouldFailCreate: true);
        final logger = _StubLoggerService();
        final router = _buildTestRouter(autoGenerateReport: true);
        addTearDown(router.dispose);

        await tester.pumpWidget(
          _buildTestApp(
            router: router,
            sseClient: sseClient,
            executionClient: execClient,
            reportsClient: reportsClient,
            loggerService: logger,
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        sseClient.emit({
          'id': _validExecId,
          'workflow_id': _validWfId,
          'target_locale': 'en',
          'status': 'PASSED',
          'active_profile_id': _validProfileId,
        });
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(reportsClient.createReportCallCount, 1);
        expect(find.byIcon(Icons.error_outline), findsOneWidget);
        expect(logger.errors, isNotEmpty);

        reportsClient.shouldFailCreate = false;
        await tester.tap(find.byIcon(Icons.refresh));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(reportsClient.createReportCallCount, 2);
        expect(reportsClient.lastProfileId, _validProfileId);
      },
    );

    testWidgets(
      'Negative/Boundary 4: fails fast with validation error when autoGenerateReport is true but outputProfileId and activeProfileId are both missing',
      (WidgetTester tester) async {
        final sseClient = _ControlledSseClient();
        addTearDown(sseClient.dispose);
        final execClient = _StubExecutionClient();
        final reportsClient = _StubReportsClient();
        final logger = _StubLoggerService();
        final router = _buildTestRouter(autoGenerateReport: true);
        addTearDown(router.dispose);

        await tester.pumpWidget(
          _buildTestApp(
            router: router,
            sseClient: sseClient,
            executionClient: execClient,
            reportsClient: reportsClient,
            loggerService: logger,
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        sseClient.emit({
          'id': _validExecId,
          'workflow_id': _validWfId,
          'target_locale': 'en',
          'status': 'PASSED',
        });
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 50));

        expect(reportsClient.createReportCallCount, 0);
        expect(find.byIcon(Icons.error_outline), findsOneWidget);
        expect(logger.errors, isNotEmpty);
      },
    );
  });
}
