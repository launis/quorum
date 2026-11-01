import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/xai_evidence_box.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _RecordingLoggerService extends LoggerService {
  final List<String> loggedErrors = [];

  _RecordingLoggerService()
    : super(
        telemetryDio: Dio(BaseOptions(baseUrl: 'https://test.invalid'))
          ..interceptors.add(
            InterceptorsWrapper(
              onRequest: (options, handler) => handler.resolve(
                Response(requestOptions: options, statusCode: 200),
              ),
            ),
          ),
      );

  @override
  void error(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    loggedErrors.add('[$context] $message');
  }
}

class _ThrowingMcpAuditTraceDto implements McpAuditTraceDto {
  const _ThrowingMcpAuditTraceDto();

  @override
  String? get claimText => throw StateError('Corrupted trace payload');

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  const urlLauncherChannel = MethodChannel('plugins.flutter.io/url_launcher');
  const urlLauncherWindowsChannel = MethodChannel(
    'plugins.flutter.io/url_launcher_windows',
  );

  tearDown(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(urlLauncherChannel, null);
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(urlLauncherWindowsChannel, null);
  });

  Widget buildTestHarness(
    List<McpAuditTraceDto> traces, {
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final child = XAIEvidenceBox(traces: traces);
    return ProviderScope(
      overrides: [
        if (logger != null) loggerServiceProvider.overrideWithValue(logger),
      ],
      child: MaterialApp(
        theme: theme ?? AppTheme.light,
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            child: width != null ? SizedBox(width: width, child: child) : child,
          ),
        ),
      ),
    );
  }

  group('XAIEvidenceBox Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders localized audit entry fields, semantic badges, truncated source URLs, and dividers across multiple traces',
      (WidgetTester tester) async {
        const traces = [
          McpAuditTraceDto(
            id: 'trc_01960000000070008000000000000001',
            toolId: 'mcp_web_search',
            stepName: 'Fact Verification',
            claimText: 'AI investment grew by 40% year-over-year.',
            query: 'global AI investment growth 2026',
            reasoning: 'Verified via quarterly industry reports.',
            responseSummary: 'Found 3 matching analyst publications.',
            impactedAxisNames: ['Strategic Vision', 'Capital Allocation'],
            sourceUrls: [
              'https://research.example.com/reports/2026/ai-growth',
              'https://root.example.org',
            ],
            durationMs: 340,
          ),
          McpAuditTraceDto(
            id: 'trc_01960000000070008000000000000002',
            toolId: 'mcp_sec_filings',
            stepName: 'Secondary Check',
            query: '10-K R&D expenditure',
            durationMs: 120,
          ),
        ];

        await tester.pumpWidget(buildTestHarness(traces));
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.text(l10n.xaiEvidenceTitle), findsOneWidget);
        expect(find.text('mcp_web_search'), findsOneWidget);
        expect(find.text('mcp_sec_filings'), findsOneWidget);
        expect(
          find.textContaining('AI investment grew by 40% year-over-year.'),
          findsOneWidget,
        );
        expect(
          find.text(
            '${l10n.xaiEvidenceQuery}: "global AI investment growth 2026"',
          ),
          findsOneWidget,
        );
        expect(find.text('${l10n.xaiEvidenceDuration}: 340ms'), findsOneWidget);
        expect(
          find.textContaining('Verified via quarterly industry reports.'),
          findsOneWidget,
        );
        expect(
          find.text('Found 3 matching analyst publications.'),
          findsOneWidget,
        );
        expect(
          find.textContaining('Strategic Vision, Capital Allocation'),
          findsOneWidget,
        );
        expect(find.text(l10n.xaiEvidenceSources), findsOneWidget);
        expect(find.text('research.example.com/reports'), findsOneWidget);
        expect(find.text('root.example.org'), findsOneWidget);

        final autoAwesomeIcon = tester.widget<Icon>(
          find.byIcon(Icons.auto_awesome),
        );
        expect(autoAwesomeIcon.color, equals(AppSemanticColors.light.success));
      },
    );

    testWidgets(
      'Boundary 1: empty traces list renders zero-clutter empty SizedBox without Card or ExpansionTile',
      (WidgetTester tester) async {
        await tester.pumpWidget(buildTestHarness(const []));
        await tester.pumpAndSettle();

        expect(find.byType(Card), findsNothing);
        expect(find.byType(ExpansionTile), findsNothing);
        expect(find.byType(SizedBox), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 2: narrow 280px viewport in dark mode contains long queries, axes, and malformed URLs without RenderFlex overflow',
      (WidgetTester tester) async {
        const trace = McpAuditTraceDto(
          toolId: 'mcp_deep_corpus_indexer',
          stepName: 'Deep Search',
          claimText:
              'Long architectural claim text spanning multiple lines in narrow desktop inspector pane.',
          query:
              'extremely long search query with multiple technical keywords for boundary overflow verification',
          reasoning: 'Detailed reasoning block.',
          responseSummary: 'Detailed response summary block.',
          impactedAxisNames: [
            'Enterprise Architecture Governance',
            'Cross-Domain Resilience',
          ],
          sourceUrls: [':::invalid_uri_scheme:::', 'relative/path/only'],
          durationMs: 9999,
        );

        await tester.pumpWidget(
          buildTestHarness([trace], theme: AppTheme.dark, width: 280),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text(':::invalid_uri_scheme:::'), findsOneWidget);
        expect(find.text('/relative'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: corrupted trace entry catches exception, logs via LoggerService, and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        const corruptedTrace = _ThrowingMcpAuditTraceDto();

        await tester.pumpWidget(
          buildTestHarness([corruptedTrace], logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) =>
                msg.contains('VALIDATION_FAILED: Failed to render audit entry'),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: tapping ActionChip with unparseable URI logs error and throws AppException',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        const trace = McpAuditTraceDto(
          toolId: 'mcp_web_search',
          stepName: 'URL Test',
          query: 'bad url test',
          sourceUrls: ['http://[::1'],
        );

        await tester.pumpWidget(buildTestHarness([trace], logger: logger));
        await tester.pumpAndSettle();

        final chip = tester.widget<ActionChip>(find.byType(ActionChip));
        expect(() => chip.onPressed!(), throwsA(isA<AppException>()));
        expect(
          logger.loggedErrors.any((msg) => msg.contains('URL launch error:')),
          isTrue,
        );
      },
    );
  });
}
