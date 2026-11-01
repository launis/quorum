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
    required Map<String, Object?> data,
    Map<String, Object?>? metrics,
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
            metrics: const <String, Object?>{
              'word_count': 420,
              'sentence_count': 18,
              'lexical_diversity': 0.68,
            },
            data: <String, Object?>{
              'bloom_score': 4.5,
              'strategic_score': 3.0,
              'toulmin_score': 4.0,
              'methodological_log': 'Applied Toulmin dialectical model.',
              'logicMatrix_help': 'Matrix explanation text.',
              'arguments': <Object?>[
                <String, Object?>{
                  'claim': 'Primary strategic claim',
                  'data': 'Empirical revenue figures',
                  'warrant': 'Historical elasticity correlation',
                  'backing': 'Industry benchmark study',
                  'rebuttal': 'Unless macro recession occurs',
                  'qualifier': 'With high probability',
                },
              ],
            },
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
            data: <String, Object?>{
              'fidelity_audit': <String, Object?>{
                'fidelity_score_display': '2.5',
                'post_hoc_rationalization_suspected': true,
                'reasoning': 'Detected post-hoc justification.',
              },
              'findings': <Object?>[
                <String, Object?>{
                  'question': 'Does premise hold under stress?',
                  'is_held': false,
                  'observation': 'Contradicted by section 2.',
                },
              ],
            },
          ),
          const SpecialistSection(
            title: 'Causal Section',
            type: 'CAUSAL_ANALYSIS',
            data: <String, Object?>{
              'abductive_score': 2.5,
              'abductive_conclusion': 'Root cause is supply bottleneck.',
              'observation': 'Direct causal chain verified.',
              'counterfactual_actual': 'Baseline delivery delay',
              'counterfactual_simulated': 'Dual-vendor redundancy',
              'plausibility_score': 2.8,
            },
          ),
          const SpecialistSection(
            title: 'Profiler Section',
            type: 'PROFILER_ANALYSIS',
            data: <String, Object?>{
              'word_count': 350,
              'avg_sentence_length': 14.2,
              'lexical_diversity': 0.72,
              'psychological_profile': 'Analytical and cautious.',
              'intent_analysis': 'Informative objective summary.',
              'automation_bias_label': 'BIAS_NONE',
              'automation_bias_color': 'green',
              'say_do_gap_label': 'GAP_DETECTED',
              'say_do_gap_color': 'red',
            },
          ),
          const SpecialistSection(
            title: 'Fact Section',
            type: 'FACT_CHECK',
            data: <String, Object?>{
              'fact_checks': <Object?>[
                <String, Object?>{
                  'verification_result': 'VER_VERIFIED',
                  'claim': 'Q3 growth was 12%.',
                  'source': 'Audited Q3 ledger.',
                },
              ],
              'ethical_issues': <Object?>[
                <String, Object?>{
                  'is_critical': true,
                  'label': 'PII Exposure',
                  'description': 'Unmasked email address.',
                  'severity': 'Critical',
                },
              ],
            },
          ),
          const SpecialistSection(
            title: 'Performativity Section',
            type: 'PERFORMATIVITY_CHECK',
            data: <String, Object?>{
              'authenticity_assessment': 'AUTH_ORGANIC',
              'authenticity_score': 2.7,
              'heuristics': <Object?>[
                <String, Object?>{'name': 'Jargon Density', 'flag': false},
              ],
            },
          ),
          const SpecialistSection(
            title: 'Archivist Section',
            type: 'ARCHIVIST_CHECK',
            data: <String, Object?>{
              'compliance_score': 4.2,
              'consistency_analysis': 'Aligned with constitutional policy.',
              'recommendations': <Object?>['Retain audit log.'],
            },
          ),
          const SpecialistSection(
            title: 'Driver Section',
            type: 'DRIVER_PROFILE',
            data: <String, Object?>{
              'role_classification': 'ROLE_ARCHITECT',
              'input_control_ratio': 0.85,
              'imperative_command_count': 6,
              'high_dependency': true,
              'strategy': 'Chain-of-Thought',
              'compliance_analysis': 'Consistent framing',
              'poikkeamat_linjasta': 'Minor deviation in step 2',
              'suositus_tuomarille': 'Approve with high confidence.',
            },
          ),
          const SpecialistSection(
            title: 'Security Section',
            type: 'SECURITY_CHECK',
            data: <String, Object?>{
              'threat_detected': true,
              'risk_color': 'orange',
              'anonymized': false,
              'findings': <Object?>['Prompt injection attempt blocked.'],
            },
          ),
          const SpecialistSection(
            title: 'Generic Section',
            type: 'CUSTOM_UNKNOWN_TYPE',
            data: <String, Object?>{
              '**markdown_key**': 'Bold **markdown** content',
              'plain_key': 'Simple scalar value',
            },
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
            data: const <String, Object?>{},
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
            data: const <String, Object?>{
              'role_classification': 'Driver',
              'input_control_ratio': 0.5,
              'imperative_command_count': 3,
              'high_dependency': false,
              'strategy': 'IteratiivinenOhjausStrategia',
            },
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
            data: const <String, Object?>{},
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
            data: const <String, Object?>{
              'bloom_score': 4.0,
              // Missing 'strategic_score' and 'arguments'
            },
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
            data: const <String, Object?>{
              'bloom_score': 99.0, // Exceeds max 6.0
              'strategic_score': 2.0,
              'arguments': <Object?>[],
            },
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
