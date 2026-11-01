import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/widgets/workflow_selector.dart';
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
    loggedErrors.add('[$context] $message: $error');
  }
}

void main() {
  Widget buildTestHarness({
    required List<Map<String, Object?>> workflows,
    String? selectedId,
    ValueChanged<String?>? onChanged,
    bool isLoading = false,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final selector = WorkflowSelector(
      workflows: workflows,
      selectedId: selectedId,
      onChanged: onChanged ?? (_) {},
      isLoading: isLoading,
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
          body: SingleChildScrollView(
            child: width != null
                ? SizedBox(width: width, child: selector)
                : selector,
          ),
        ),
      ),
    );
  }

  group('WorkflowSelector Dumb Painter & Fail-Fast Boundary Tests', () {
    testWidgets(
      'Positive: renders localized I18nText and String workflow names, highlights selectedId, and emits selection change',
      (WidgetTester tester) async {
        String? emittedId;
        final workflows = <Map<String, Object?>>[
          <String, Object?>{
            'id': 'wf_0195f000000070008000000000000001',
            'name': const I18nText(
              translations: <String, String>{
                'en': 'Executive Coaching Synthesis',
                'fi': 'Johdon valmennussynteesi',
              },
            ),
          },
          <String, Object?>{
            'id': 'wf_0195f000000070008000000000000002',
            'name': <String, Object?>{
              'translations': <String, String>{
                'en': 'Causal Discovery Audit',
                'fi': 'Kausaalinen auditointi',
              },
            },
          },
          <String, Object?>{
            'id': 'wf_0195f000000070008000000000000003',
            'name': 'Direct String Workflow',
          },
        ];

        await tester.pumpWidget(
          buildTestHarness(
            workflows: workflows,
            selectedId: 'wf_0195f000000070008000000000000001',
            locale: const Locale('fi'),
            onChanged: (value) => emittedId = value,
          ),
        );
        await tester.pumpAndSettle();

        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10nFi.chooseAnalysisType), findsOneWidget);
        expect(find.text('Johdon valmennussynteesi'), findsOneWidget);

        await tester.tap(find.byType(DropdownButton<String>));
        await tester.pumpAndSettle();

        expect(find.text('Kausaalinen auditointi'), findsWidgets);
        await tester.tap(find.text('Kausaalinen auditointi').last);
        await tester.pumpAndSettle();

        expect(emittedId, equals('wf_0195f000000070008000000000000002'));
      },
    );

    testWidgets(
      'Boundary 1: renders loading indicator, unmapped selectedId as null, and extreme long workflow name in narrow 240px dark viewport without overflow',
      (WidgetTester tester) async {
        final workflows = <Map<String, Object?>>[
          <String, Object?>{
            'id': 'wf_0195f000000070008000000000000010',
            'name':
                'ExtraordinarilyLongEnterpriseExecutiveCoachingWorkflowNameWithoutSpaces_v2026_Final',
          },
        ];

        await tester.pumpWidget(
          buildTestHarness(
            workflows: workflows,
            selectedId: 'wf_0195f000000070008000000000000010',
            isLoading: true,
            theme: AppTheme.dark,
            width: 240,
          ),
        );
        await tester.pump();

        expect(tester.takeException(), isNull);
        expect(find.byType(LinearProgressIndicator), findsOneWidget);
        expect(
          find.text(
            'ExtraordinarilyLongEnterpriseExecutiveCoachingWorkflowNameWithoutSpaces_v2026_Final',
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Negative 1: missing, blank, or duplicate workflow id or blank selectedId logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            workflows: const <Map<String, Object?>>[
              <String, Object?>{'id': '   ', 'name': 'Invalid ID Workflow'},
            ],
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render WorkflowSelector',
            ),
          ),
          isTrue,
        );

        logger.loggedErrors.clear();
        await tester.pumpWidget(
          buildTestHarness(
            workflows: const <Map<String, Object?>>[
              <String, Object?>{
                'id': 'wf_0195f000000070008000000000000001',
                'name': 'First',
              },
              <String, Object?>{
                'id': 'wf_0195f000000070008000000000000001',
                'name': 'Duplicate',
              },
            ],
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains('Duplicate workflow id'),
          ),
          isTrue,
        );

        logger.loggedErrors.clear();
        await tester.pumpWidget(
          buildTestHarness(
            workflows: const <Map<String, Object?>>[],
            selectedId: '   ',
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains('selectedId cannot be an empty string'),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: missing, blank, or malformed workflow name logs error via LoggerService and renders compact ErrorView without silent fallback',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            workflows: const <Map<String, Object?>>[
              <String, Object?>{
                'id': 'wf_0195f000000070008000000000000001',
                'name': '',
              },
            ],
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains('missing a valid localized "name"'),
          ),
          isTrue,
        );

        logger.loggedErrors.clear();
        await tester.pumpWidget(
          buildTestHarness(
            workflows: const <Map<String, Object?>>[
              <String, Object?>{
                'id': 'wf_0195f000000070008000000000000002',
                'name': <String, Object?>{'translations': <String, String>{}},
              },
            ],
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains('Missing required translation'),
          ),
          isTrue,
        );
      },
    );
  });
}
