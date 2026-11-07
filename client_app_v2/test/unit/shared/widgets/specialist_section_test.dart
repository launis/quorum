import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/shared/widgets/specialist_section.dart';
import 'package:client_app/shared/widgets/unified_metric_gauge.dart';
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
    required String title,
    required String type,
    required SpecialistSectionData data,
    SpecialistSectionMetrics? metrics,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double width = 900,
    LoggerService? logger,
  }) {
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
            child: SizedBox(
              width: width,
              child: SpecialistSection(
                title: title,
                type: type,
                data: data,
                metrics: metrics,
              ),
            ),
          ),
        ),
      ),
    );
  }

  group('SpecialistSection Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive 1: renders LOGIC_ANALYSIS section, expands tile, renders Logic Matrix, gauges, arguments, and toggles Raw JSON view',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            title: 'Logic Specialist Audit',
            type: 'LOGIC_ANALYSIS',
            metrics: const SpecialistSectionMetrics(
              wordCount: 420,
              sentenceCount: 18,
              lexicalDiversity: 0.68,
            ),
            data: const SpecialistSectionData(
              bloomScore: 4.5,
              strategicScore: 3.0,
              toulminScore: 4.0,
              methodologicalLog: 'Applied Toulmin dialectical model.',
              logicMatrixHelp: 'Matrix explanation text.',
              arguments: <SpecialistArgumentData>[
                SpecialistArgumentData(
                  claim: 'Primary strategic claim',
                  data: 'Empirical revenue figures',
                  warrant: 'Historical elasticity correlation',
                  backing: 'Industry benchmark study',
                  rebuttal: 'Unless macro recession occurs',
                  qualifier: 'With high probability',
                ),
              ],
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Logic Specialist Audit'), findsOneWidget);
        expect(find.text('Toulmin & Cognitive Level'), findsOneWidget);

        await tester.tap(find.text('Logic Specialist Audit'));
        await tester.pumpAndSettle();

        expect(find.text('Logic Matrix (Decision Profiling)'), findsOneWidget);
        expect(find.text('Grounded Synthesis'), findsOneWidget);
        expect(find.byType(UnifiedMetricGauge), findsNWidgets(3));
        expect(find.text('Primary strategic claim'), findsOneWidget);
        expect(find.text('Empirical revenue figures'), findsOneWidget);
        expect(find.text('420'), findsOneWidget);
        expect(find.text('0.68'), findsOneWidget);

        // Open help dialog
        await tester.tap(find.byIcon(Icons.help_outline).first);
        await tester.pumpAndSettle();
        expect(find.text('About Metric'), findsOneWidget);
        await tester.tap(find.text('OK'));
        await tester.pumpAndSettle();

        // Toggle raw JSON view
        await tester.tap(find.text('JSON'));
        await tester.pumpAndSettle();
        expect(find.text('Hide Raw Data'), findsOneWidget);
        expect(find.textContaining('"bloom_score": 4.5'), findsOneWidget);
      },
    );

    testWidgets(
      'Positive 2: renders STRESS_TEST, CAUSAL_ANALYSIS, PROFILER_ANALYSIS, FACT_CHECK, PERFORMATIVITY_CHECK, ARCHIVIST_CHECK, DRIVER_PROFILE, SECURITY_CHECK, and generic fallback map',
      (WidgetTester tester) async {
        final sections = <Widget>[
          const SpecialistSection(
            title: 'Stress Section',
            type: 'STRESS_TEST',
            data: SpecialistSectionData(
              fidelityAudit: SpecialistFidelityAuditData(
                fidelityScoreDisplay: '2.5',
                postHocRationalizationSuspected: true,
                reasoning: 'Detected post-hoc justification.',
              ),
              findings: <SpecialistStressFindingData>[
                SpecialistStressFindingData(
                  question: 'Does premise hold under stress?',
                  isHeld: false,
                  observation: 'Contradicted by section 2.',
                ),
              ],
            ),
          ),
          const SpecialistSection(
            title: 'Causal Section',
            type: 'CAUSAL_ANALYSIS',
            data: SpecialistSectionData(
              abductiveScore: 2.5,
              abductiveConclusion: 'Root cause is supply bottleneck.',
              observation: 'Direct causal chain verified.',
              counterfactualActual: 'Baseline delivery delay',
              counterfactualSimulated: 'Dual-vendor redundancy',
              plausibilityScore: 2.8,
            ),
          ),
          const SpecialistSection(
            title: 'Profiler Section',
            type: 'PROFILER_ANALYSIS',
            data: SpecialistSectionData(
              wordCount: 350,
              avgSentenceLength: 14.2,
              lexicalDiversity: 0.72,
              psychologicalProfile: 'Analytical and cautious.',
              intentAnalysis: 'Informative objective summary.',
              automationBiasLabel: 'BIAS_NONE',
              automationBiasColor: 'green',
              sayDoGapLabel: 'GAP_DETECTED',
              sayDoGapColor: 'red',
            ),
          ),
          const SpecialistSection(
            title: 'Fact Section',
            type: 'FACT_CHECK',
            data: SpecialistSectionData(
              factChecks: <SpecialistFactCheckItemData>[
                SpecialistFactCheckItemData(
                  verificationResult: 'VER_VERIFIED',
                  claim: 'Q3 growth was 12%.',
                  source: 'Audited Q3 ledger.',
                ),
              ],
              ethicalIssues: <SpecialistEthicalIssueData>[
                SpecialistEthicalIssueData(
                  isCritical: true,
                  label: 'PII Exposure',
                  description: 'Unmasked email address.',
                  severity: 'Critical',
                ),
              ],
            ),
          ),
          const SpecialistSection(
            title: 'Performativity Section',
            type: 'PERFORMATIVITY_CHECK',
            data: SpecialistSectionData(
              authenticityAssessment: 'AUTH_ORGANIC',
              authenticityScore: 2.7,
              heuristics: <SpecialistHeuristicItemData>[
                SpecialistHeuristicItemData(
                  name: 'Jargon Density',
                  flag: false,
                ),
              ],
            ),
          ),
          const SpecialistSection(
            title: 'Archivist Section',
            type: 'ARCHIVIST_CHECK',
            data: SpecialistSectionData(
              complianceScore: 4.2,
              consistencyAnalysis: 'Aligned with constitutional policy.',
              recommendations: <String>['Retain audit log.'],
            ),
          ),
          const SpecialistSection(
            title: 'Driver Section',
            type: 'DRIVER_PROFILE',
            data: SpecialistSectionData(
              roleClassification: 'ROLE_ARCHITECT',
              inputControlRatio: 0.85,
              imperativeCommandCount: 6,
              highDependency: true,
              strategy: 'Chain-of-Thought',
              complianceAnalysis: 'Consistent framing',
              alignmentDeviations: 'Minor deviation in step 2',
              judgeRecommendation: 'Approve with high confidence.',
            ),
          ),
          const SpecialistSection(
            title: 'Security Section',
            type: 'SECURITY_CHECK',
            data: SpecialistSectionData(
              threatDetected: true,
              riskColor: 'orange',
              anonymized: false,
              securityFindings: <String>['Prompt injection attempt blocked.'],
            ),
          ),
          const SpecialistSection(
            title: 'Generic Section',
            type: 'CUSTOM_UNKNOWN_TYPE',
            data: SpecialistSectionData(
              genericEntries: <String, String>{
                '**markdown_key**': 'Bold **markdown** content',
                'plain_key': 'Simple scalar value',
              },
            ),
          ),
        ];

        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              theme: AppTheme.light,
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(
                body: SingleChildScrollView(child: Column(children: sections)),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        for (final title in [
          'Stress Section',
          'Causal Section',
          'Profiler Section',
          'Fact Section',
          'Performativity Section',
          'Archivist Section',
          'Driver Section',
          'Security Section',
          'Generic Section',
        ]) {
          await tester.ensureVisible(find.text(title));
          await tester.tap(find.text(title));
          await tester.pumpAndSettle();
        }

        expect(find.text('Detected post-hoc justification.'), findsOneWidget);
        expect(find.text('Root cause is supply bottleneck.'), findsOneWidget);
        expect(find.text('Say-Do Gap: GAP DETECTED'), findsOneWidget);
        expect(find.text('Q3 growth was 12%.'), findsOneWidget);
        expect(
          find.text('Aligned with constitutional policy.'),
          findsOneWidget,
        );
        expect(find.text('85%'), findsOneWidget);
        expect(find.text('Approve with high confidence.'), findsOneWidget);
        expect(find.text('Prompt injection attempt blocked.'), findsOneWidget);
        expect(find.byType(OutputRenderer), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 1: empty data map renders localized dataUnavailable placeholder without crashing',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            title: 'Empty Specialist',
            type: 'LOGIC_ANALYSIS',
            data: const SpecialistSectionData(),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Empty Specialist'));
        await tester.pumpAndSettle();

        expect(find.text('Data unavailable'), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Boundary 2: narrow 280px mobile viewport in dark theme with Finnish locale renders stacked responsive layout without overflow',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            title: 'ErittäinPitkäAsiantuntijaOtsikkoKapeassaNäkymässä',
            type: 'DRIVER_PROFILE',
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 280,
            data: const SpecialistSectionData(
              roleClassification: 'Driver',
              inputControlRatio: 0.5,
              imperativeCommandCount: 3,
              highDependency: false,
              strategy: 'IteratiivinenOhjausStrategia',
            ),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(
          find.text('ErittäinPitkäAsiantuntijaOtsikkoKapeassaNäkymässä'),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('50%'), findsOneWidget);
        expect(find.text('Tunnistetut Strategiat:'), findsOneWidget);
        expect(find.text('Suoria käskyjä (Imperative): 3'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: empty title or type logs VALIDATION_FAILED via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: '   ',
            type: 'LOGIC_ANALYSIS',
            data: const SpecialistSectionData(),
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[SpecialistSection] VALIDATION_FAILED: SpecialistSection title cannot be empty',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: missing required keys in LOGIC_ANALYSIS logs VALIDATION_FAILED via LoggerService and renders compact ErrorView on expand',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: 'Broken Logic Section',
            type: 'LOGIC_ANALYSIS',
            data: const SpecialistSectionData(
              bloomScore: 4.0,
              // Missing 'strategicScore' and 'arguments'
            ),
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Broken Logic Section'));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[SpecialistSection] VALIDATION_FAILED: UI Graceful Degradation [LOGIC_ANALYSIS]',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 3: malformed non-list arguments or out-of-bounds gauge score logs VALIDATION_FAILED and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            title: 'Malformed Arguments Section',
            type: 'LOGIC_ANALYSIS',
            data: const SpecialistSectionData(
              bloomScore: 99.0, // Exceeds max 6.0
              strategicScore: 2.0,
              arguments: <SpecialistArgumentData>[],
            ),
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Malformed Arguments Section'));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[SpecialistSection] VALIDATION_FAILED: UI Graceful Degradation [LOGIC_ANALYSIS]',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
