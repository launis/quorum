import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/audit_trail_viewer.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';
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
  Widget buildTestHarness(
    Map<String, Object?> data, {
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final child = AuditTrailViewer(data: data);
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

  group('AuditTrailViewer Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: sorts steps by numeric step index and renders localized headers, reasoning trace, and methodological log when expanded',
      (WidgetTester tester) async {
        final data = <String, Object?>{
          'Raw_Steps': <String, Object?>{
            'step_two': <String, Object?>{
              'metadata': <String, Object?>{
                'step': 2,
                'agent': 'FalsifierAgent',
                'version': 'v2.1',
                'timestamp': '2026-11-01T02:00:00Z',
              },
              'reasoning_trace': 'Checked counterfactual hypothesis B.',
              'methodological_log': 'Walton Stress Test',
            },
            'step_one': <String, Object?>{
              'metadata': <String, Object?>{
                'step': 1,
                'agent': 'LogicianAgent',
                'version': 'v2.0',
                'timestamp': '2026-11-01T01:59:00Z',
              },
              'reasoning_trace': 'Extracted Toulmin claims.',
              'methodological_log': 'Toulmin Decomposition',
            },
          },
        };

        await tester.pumpWidget(buildTestHarness(data));
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.byType(DeepDiveExpander), findsOneWidget);
        expect(find.text(l10n.systemAuditTrailLabel), findsOneWidget);

        // Expand tile to inspect rendered steps
        await tester.tap(find.text(l10n.systemAuditTrailLabel));
        await tester.pumpAndSettle();

        final stepOneFinder = find.text('LogicianAgent (v2.0)');
        final stepTwoFinder = find.text('FalsifierAgent (v2.1)');
        expect(stepOneFinder, findsOneWidget);
        expect(stepTwoFinder, findsOneWidget);

        // Verify chronological sort order (step 1 rendered above step 2)
        final stepOneDy = tester.getTopLeft(stepOneFinder).dy;
        final stepTwoDy = tester.getTopLeft(stepTwoFinder).dy;
        expect(stepOneDy, lessThan(stepTwoDy));

        expect(find.text('Extracted Toulmin claims.'), findsOneWidget);
        expect(
          find.text('${l10n.lblMethodologicalLog}: Toulmin Decomposition'),
          findsOneWidget,
        );
        expect(
          find.text('${l10n.lblMethodologicalLog}: Walton Stress Test'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Boundary 1: empty data map or empty Raw_Steps map renders empty SizedBox without DeepDiveExpander',
      (WidgetTester tester) async {
        await tester.pumpWidget(buildTestHarness(const {}));
        await tester.pumpAndSettle();

        expect(find.byType(DeepDiveExpander), findsNothing);
        expect(find.byType(SizedBox), findsOneWidget);

        await tester.pumpWidget(
          buildTestHarness(const {'Raw_Steps': <String, Object?>{}}),
        );
        await tester.pumpAndSettle();

        expect(find.byType(DeepDiveExpander), findsNothing);
      },
    );

    testWidgets(
      'Boundary 2: narrow 280px viewport in dark mode contains long agent names and timestamps without RenderFlex overflow',
      (WidgetTester tester) async {
        final data = <String, Object?>{
          'Raw_Steps': <String, Object?>{
            'step_narrow': <String, Object?>{
              'metadata': <String, Object?>{
                'step': 1,
                'agent':
                    'ExtraordinarilyLongEnterpriseCognitiveSynthesisAgentIdentifier',
                'version': 'v2.99.100-enterprise-build',
                'timestamp': '2026-11-01T02:45:59.999999999+02:00',
              },
              'reasoning_trace':
                  'Long monospace reasoning trace inside narrow 280px container.',
              'methodological_log':
                  'Extended methodological verification protocol log.',
            },
          },
        };

        await tester.pumpWidget(
          buildTestHarness(data, theme: AppTheme.dark, width: 280),
        );
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));
        await tester.tap(find.text(l10n.systemAuditTrailLabel));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(
          find.textContaining(
            'ExtraordinarilyLongEnterpriseCognitiveSynthesisAgentIdentifier',
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Negative 1: malformed Raw_Steps type logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final corruptedData = <String, Object?>{
          'Raw_Steps': 'invalid_non_map_payload',
        };

        await tester.pumpWidget(
          buildTestHarness(corruptedData, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) =>
                msg.contains('VALIDATION_FAILED: Failed to render audit trail'),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: step entry with missing required metadata fields logs error and renders ErrorView without silent fallback',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final incompleteData = <String, Object?>{
          'Raw_Steps': <String, Object?>{
            'broken_step': <String, Object?>{
              'metadata': <String, Object?>{
                'step': 1,
                // Missing required 'agent', 'version', and 'timestamp'
              },
            },
          },
        };

        await tester.pumpWidget(
          buildTestHarness(incompleteData, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) =>
                msg.contains('VALIDATION_FAILED: Failed to render audit trail'),
          ),
          isTrue,
        );
      },
    );
  });
}
