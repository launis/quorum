import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/dynamic_form.dart';
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
    required DynamicFormSchema schema,
    DynamicFormValues initialData = const DynamicFormValues(),
    ValueChanged<DynamicFormValues>? onChanged,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final form = DynamicFormWidget(
      schema: schema,
      initialData: initialData,
      onChanged: onChanged ?? (_) {},
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
            child: width != null ? SizedBox(width: width, child: form) : form,
          ),
        ),
      ),
    );
  }

  group('DynamicFormWidget Dumb Painter & Fail-Fast Boundary Tests', () {
    testWidgets(
      'Positive: renders string, integer, and boolean schema properties, populates initialData, and emits updated map via onChanged',
      (WidgetTester tester) async {
        DynamicFormValues? latestEmitted;
        const schema = DynamicFormSchema(
          properties: <String, SchemaFieldDefinition>{
            'agent_name': SchemaFieldDefinition(
              type: 'string',
              title: 'Agent Name',
              description: 'Primary identifier',
            ),
            'max_retries': SchemaFieldDefinition(
              type: 'integer',
              title: 'Max Retries',
            ),
            'strict_mode': SchemaFieldDefinition(
              type: 'boolean',
              title: 'Strict Mode',
            ),
          },
          requiredFields: <String>['agent_name'],
        );

        await tester.pumpWidget(
          buildTestHarness(
            schema: schema,
            initialData: const DynamicFormValues(
              entries: <String, DynamicFormFieldValue?>{
                'agent_name': DynamicFormFieldValue.string('Logician'),
                'max_retries': DynamicFormFieldValue.integer(3),
                'strict_mode': DynamicFormFieldValue.boolean(true),
              },
            ),
            onChanged: (updated) => latestEmitted = updated,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Agent Name *'), findsOneWidget);
        expect(find.text('Max Retries'), findsOneWidget);
        expect(find.text('Strict Mode'), findsOneWidget);
        expect(find.byType(SwitchListTile), findsOneWidget);

        await tester.enterText(
          find.widgetWithText(TextFormField, 'Logician'),
          'Falsifier',
        );
        await tester.pumpAndSettle();

        expect(latestEmitted, isNotNull);
        expect(latestEmitted!['agent_name'], equals('Falsifier'));
        expect(latestEmitted!['max_retries'], equals(3));
        expect(latestEmitted!['strict_mode'], isTrue);

        await tester.tap(find.byType(SwitchListTile));
        await tester.pumpAndSettle();

        expect(latestEmitted!['strict_mode'], isFalse);
      },
    );

    testWidgets(
      'Boundary 1: didUpdateWidget synchronizes internal state when initialData map changes and narrow 280px dark viewport renders without overflow',
      (WidgetTester tester) async {
        const schema = DynamicFormSchema(
          properties: <String, SchemaFieldDefinition>{
            'mode': SchemaFieldDefinition(
              type: 'string',
              title: 'Execution Mode',
              enumOptions: <String>['deterministic', 'exploratory'],
            ),
          },
        );

        await tester.pumpWidget(
          buildTestHarness(
            schema: schema,
            initialData: const DynamicFormValues(
              entries: <String, DynamicFormFieldValue?>{
                'mode': DynamicFormFieldValue.string('deterministic'),
              },
            ),
            theme: AppTheme.dark,
            width: 280,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('deterministic'), findsOneWidget);

        await tester.pumpWidget(
          buildTestHarness(
            schema: schema,
            initialData: const DynamicFormValues(
              entries: <String, DynamicFormFieldValue?>{
                'mode': DynamicFormFieldValue.string('exploratory'),
              },
            ),
            theme: AppTheme.dark,
            width: 280,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('exploratory'), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: empty schema or missing properties map logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(schema: const DynamicFormSchema(), logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render dynamic form',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: malformed property definition or invalid required list logs error via LoggerService and renders compact ErrorView without silent fallback',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        const corruptedSchema = DynamicFormSchema(
          properties: <String, SchemaFieldDefinition>{
            'broken_field': SchemaFieldDefinition(type: 'unsupported_type'),
          },
          requiredFields: <String>['   '],
        );

        await tester.pumpWidget(
          buildTestHarness(schema: corruptedSchema, logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render dynamic form',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
