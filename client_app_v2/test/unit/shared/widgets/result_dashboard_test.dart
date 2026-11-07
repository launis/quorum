import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/generic_grid.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/shared/widgets/result_dashboard.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
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

void main() {
  Widget buildTestHarness({
    required ResultDashboardRawData rawResult,
    ResultDashboardViewData? reportView,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double width = 900,
    double height = 800,
    LoggerService? logger,
  }) {
    final dashboard = ResultDashboard(
      rawResult: rawResult,
      reportView: reportView,
    );
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
          body: SizedBox(width: width, height: height, child: dashboard),
        ),
      ),
    );
  }

  group('ResultDashboard Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive 1: renders localized tabs, header with semantic success intent, HITL warning, system notification, blocks, and reference groups',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            rawResult: const ResultDashboardRawData(
              entries: <String, ResultDashboardNodeValue>{
                'final_score': ResultDashboardNodeValue.number(92),
              },
            ),
            reportView: const ResultDashboardViewData(
              title: 'Executive Audit Summary',
              intent: 'success',
              metrics: ResultDashboardMetricsData(
                hitlRequired: true,
                hasWarning: false,
                coachFeedback: 'Verify section 3 citations manually.',
              ),
              systemNotification: ResultDashboardNotificationData(
                level: 'danger',
                title: 'Policy Alert',
                message: 'Strict compliance mode active.',
              ),
              blocks: <ResultDashboardBlockData>[
                ResultDashboardBlockData(
                  type: 'paragraph',
                  id: 'coach-markdown',
                  label: 'Senior Coach Synthesis',
                  paragraphContent: 'Strong analytical structure verified.',
                ),
                ResultDashboardBlockData(
                  type: 'metric',
                  id: 'grid-1',
                  label: 'Key Telemetry',
                  metricGridData: GenericGridData(
                    items: <GenericGridItem>[
                      GenericGridItem(
                        label: 'Accuracy',
                        value: '98%',
                        highlight: true,
                      ),
                    ],
                  ),
                ),
              ],
              references: <ResultDashboardReferenceData>[
                ResultDashboardReferenceData(
                  id: 'REF-1',
                  intent: 'search',
                  title: 'Market Benchmark Study',
                  snippet: 'Empirical baseline data.',
                  url: 'https://example.org/benchmark',
                ),
                ResultDashboardReferenceData(
                  id: 'REF-2',
                  intent: 'grounding',
                  title: 'Regulatory Standard',
                ),
                ResultDashboardReferenceData(
                  id: 'REF-3',
                  intent: 'internal_kb',
                  title: 'Internal Architecture Guideline',
                ),
              ],
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Report'), findsOneWidget);
        expect(find.text('Condensed Data (Flat)'), findsOneWidget);
        expect(find.text('Full Raw Data'), findsOneWidget);

        final headerTitle = tester.widget<Text>(
          find.text('EXECUTIVE AUDIT SUMMARY'),
        );
        expect(
          headerTitle.style?.color,
          equals(AppSemanticColors.light.success),
        );

        expect(find.text('Human Review Required (HITL)'), findsOneWidget);
        expect(
          find.text('Verify section 3 citations manually.'),
          findsOneWidget,
        );
        expect(find.text('Policy Alert'), findsOneWidget);
        expect(find.text('Strict compliance mode active.'), findsOneWidget);

        expect(find.text('Senior Coach Synthesis'), findsOneWidget);
        expect(find.byType(OutputRenderer), findsOneWidget);
        expect(find.byType(GenericGrid), findsOneWidget);

        expect(find.text('Bibliography & References'), findsOneWidget);
        expect(find.text('Analytics Searches'), findsOneWidget);
        expect(
          find.text('Fact-Checking (Vertex AI Grounding)'),
          findsOneWidget,
        );
        expect(
          find.text('Organizational Guidelines & Knowledge Base'),
          findsOneWidget,
        );
        expect(find.text('REF-1 - Market Benchmark Study'), findsOneWidget);
      },
    );

    testWidgets(
      'Positive 2: flattens snake_case keys to PascalCase, strips UUID prefixes, skips trace/token keys in Flat tab, and renders full JSON in Raw tab',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            rawResult: const ResultDashboardRawData(
              contextVariables: <String, ResultDashboardNodeValue>{
                'step_judge': ResultDashboardNodeValue.nested(<
                  String,
                  ResultDashboardNodeValue
                >{
                  'judge_score': ResultDashboardNodeValue.number(88),
                  'key_tags': ResultDashboardNodeValue.stringList(<String>[
                    'alpha',
                    'beta',
                  ]),
                  'empty_list': ResultDashboardNodeValue.stringList(<String>[]),
                  'thought_process': ResultDashboardNodeValue.text(
                    'should be omitted',
                  ),
                  'step_id': ResultDashboardNodeValue.text('should be omitted'),
                }),
                '12345678-1234-1234-1234-123456789abc_audit_label':
                    ResultDashboardNodeValue.text('Approved'),
              },
              entries: <String, ResultDashboardNodeValue>{
                'trace_log': ResultDashboardNodeValue.text('raw-only-field'),
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Condensed Data (Flat)'));
        await tester.pumpAndSettle();

        final flatSelectable = tester.widget<SelectableText>(
          find.byType(SelectableText),
        );
        final flatText = flatSelectable.data ?? '';
        expect(flatText, contains('"StepJudgeJudgeScore": 88'));
        expect(flatText, contains('"StepJudgeKeyTags": "alpha, beta"'));
        expect(flatText, contains('"StepJudgeEmptyList": "[]"'));
        expect(flatText, contains('"AuditLabel": "Approved"'));
        expect(flatText, isNot(contains('thought_process')));

        await tester.tap(find.text('Full Raw Data'));
        await tester.pumpAndSettle();

        final rawSelectable = tester.widget<SelectableText>(
          find.byType(SelectableText),
        );
        expect(rawSelectable.data, contains('"trace_log": "raw-only-field"'));
      },
    );

    testWidgets(
      'Boundary 1: renders localized empty placeholders when reportView is null and rawResult has no flattenable keys',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            rawResult: const ResultDashboardRawData(
              entries: <String, ResultDashboardNodeValue>{
                'id': ResultDashboardNodeValue.text('exec_1'),
                'token_usage': ResultDashboardNodeValue.number(500),
              },
            ),
            reportView: null,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('No report data available.'), findsOneWidget);

        await tester.tap(find.text('Condensed Data (Flat)'));
        await tester.pumpAndSettle();

        final flatSelectable = tester.widget<SelectableText>(
          find.byType(SelectableText),
        );
        expect(
          flatSelectable.data,
          contains('No Flat Report data found for this execution.'),
        );
      },
    );

    testWidgets(
      'Boundary 2: narrow 280px viewport in dark mode with Finnish locale renders without RenderFlex overflow',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 280,
            rawResult: const ResultDashboardRawData(),
            reportView: const ResultDashboardViewData(
              title: 'ErittäinPitkäRaportinOtsikkoIlmanVälilyöntejä',
              intent: 'warning',
              metrics: ResultDashboardMetricsData(hasWarning: true),
              systemNotification: ResultDashboardNotificationData(
                level: 'warning',
                title: 'ErittäinPitkäJärjestelmäIlmoitusOtsikkoKapeassaTilassa',
                message: 'Tarkista poikkeamat.',
              ),
              blocks: <ResultDashboardBlockData>[
                ResultDashboardBlockData(
                  type: 'list',
                  id: 'sources-list',
                  label: 'ErittäinPitkäLähdelistanOtsikkoKapeassaNäkymässä',
                  listItems: <ResultDashboardSourceListItemData>[
                    ResultDashboardSourceListItemData(
                      source: 'Lähde A',
                      content: 'Sisältö A',
                    ),
                  ],
                ),
              ],
              references: <ResultDashboardReferenceData>[
                ResultDashboardReferenceData(
                  id: 'REF-FI-1',
                  intent: 'grounding',
                  title: 'PitkäViiteOtsikko',
                ),
              ],
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('Raportti'), findsOneWidget);
        expect(find.text('Järjestelmän varoitus'), findsOneWidget);
        expect(find.text('Lähdeluettelo & Viitteet'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: non-list blocks in reportView logs VALIDATION_FAILED via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            logger: logger,
            rawResult: const ResultDashboardRawData(),
            reportView: const ResultDashboardViewData(
              title: 'Broken Report',
              hasInvalidBlocksPayload: true,
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render dynamic dashboard',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: unsupported block type logs VALIDATION_FAILED via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            logger: logger,
            rawResult: const ResultDashboardRawData(),
            reportView: const ResultDashboardViewData(
              title: 'Unknown Block Report',
              blocks: <ResultDashboardBlockData>[
                ResultDashboardBlockData(
                  type: 'unsupported_custom_widget',
                  id: 'blk_bad',
                  label: 'Bad Block',
                ),
              ],
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render report block',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 3: non-map context_variables in rawResult logs VALIDATION_FAILED via LoggerService and renders compact ErrorView on Flat tab',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            logger: logger,
            rawResult: const ResultDashboardRawData(
              hasInvalidContextVariables: true,
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Condensed Data (Flat)'));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) =>
                msg.contains('VALIDATION_FAILED: Flat Report parsing failed'),
          ),
          isTrue,
        );
      },
    );
  });
}
