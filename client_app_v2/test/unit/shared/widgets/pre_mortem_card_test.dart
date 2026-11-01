import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/deep_dive_expander.dart';
import 'package:client_app/shared/widgets/pre_mortem_card.dart';
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
    required Map<String, Object?> report,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final card = PreMortemCard(report: report);
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
            child: width != null ? SizedBox(width: width, child: card) : card,
          ),
        ),
      ),
    );
  }

  group('PreMortemCard Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive 1: renders DeepDiveExpander, check icon with semantic success color, and weak signals when expanded',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            report: {
              'pre_mortem_analyysi': <String, Object?>{
                'suoritettu': true,
                'hiljaiset_signaalit': <Object?>[
                  'Vendor lock-in risk on proprietary schema',
                  'Single point of failure in ingress queue',
                ],
              },
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(DeepDiveExpander), findsOneWidget);
        expect(find.text('Authenticity & Pre-Mortem'), findsOneWidget);

        await tester.tap(find.text('Authenticity & Pre-Mortem'));
        await tester.pumpAndSettle();

        expect(find.text('Analysis Performed: '), findsOneWidget);
        final checkIcon = tester.widget<Icon>(find.byIcon(Icons.check));
        expect(checkIcon.color, equals(AppSemanticColors.light.success));

        expect(find.text('Findings:'), findsOneWidget);
        expect(
          find.text('Vendor lock-in risk on proprietary schema'),
          findsOneWidget,
        );
        expect(
          find.text('Single point of failure in ingress queue'),
          findsOneWidget,
        );

        final sensorIcons = tester
            .widgetList<Icon>(find.byIcon(Icons.sensors))
            .toList();
        expect(sensorIcons.length, equals(2));
        expect(
          sensorIcons.first.color,
          equals(AppSemanticColors.light.warning),
        );
      },
    );

    testWidgets(
      'Positive 2: renders close icon with onSurfaceVariant color when suoritettu is false and omits findings list when empty',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(
            report: {
              'pre_mortem_analyysi': <String, Object?>{
                'suoritettu': false,
                'hiljaiset_signaalit': <Object?>[],
              },
            },
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Authenticity & Pre-Mortem'));
        await tester.pumpAndSettle();

        final closeIcon = tester.widget<Icon>(find.byIcon(Icons.close));
        expect(
          closeIcon.color,
          equals(AppTheme.light.colorScheme.onSurfaceVariant),
        );
        expect(find.text('Findings:'), findsNothing);
      },
    );

    testWidgets(
      'Boundary 1: returns empty SizedBox when report is empty or pre_mortem_analyysi is null',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestHarness(report: const <String, Object?>{}),
        );
        await tester.pumpAndSettle();

        expect(find.byType(DeepDiveExpander), findsNothing);
        expect(find.byType(ErrorView), findsNothing);

        await tester.pumpWidget(
          buildTestHarness(
            report: const <String, Object?>{'pre_mortem_analyysi': null},
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(DeepDiveExpander), findsNothing);
        expect(find.byType(ErrorView), findsNothing);
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
            report: {
              'pre_mortem_analyysi': <String, Object?>{
                'suoritettu': true,
                'hiljaiset_signaalit': <Object?>[
                  'ErittäinPitkäHiljainenSignaaliIlmanVälilyöntejäTaiRivinvaihtojaTestaamaanKapeaaNäkymää',
                ],
              },
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Aitous & Pre-Mortem'), findsOneWidget);
        await tester.tap(find.text('Aitous & Pre-Mortem'));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('Analyysi suoritettu: '), findsOneWidget);
        expect(find.text('Löydökset:'), findsOneWidget);
        final checkIcon = tester.widget<Icon>(find.byIcon(Icons.check));
        expect(checkIcon.color, equals(AppSemanticColors.dark.success));
      },
    );

    testWidgets(
      'Negative 1: non-map pre_mortem_analyysi logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            logger: logger,
            report: const <String, Object?>{
              'pre_mortem_analyysi': 'invalid_scalar_payload',
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render pre-mortem card',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: missing or non-boolean suoritettu logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            logger: logger,
            report: {
              'pre_mortem_analyysi': <String, Object?>{'suoritettu': 'yes'},
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render pre-mortem card',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 3: whitespace-only weak signal item logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            logger: logger,
            report: {
              'pre_mortem_analyysi': <String, Object?>{
                'suoritettu': true,
                'hiljaiset_signaalit': <Object?>['   '],
              },
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render pre-mortem card',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
