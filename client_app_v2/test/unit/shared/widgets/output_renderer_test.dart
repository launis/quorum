import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
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
    required String markdownContent,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final renderer = OutputRenderer(markdownContent: markdownContent);
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
                ? SizedBox(width: width, child: renderer)
                : renderer,
          ),
        ),
      ),
    );
  }

  group('OutputRenderer Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders Markdown headings, paragraphs, code blocks, blockquotes, lists, and tables with Theme-sovereign tokens',
      (WidgetTester tester) async {
        const markdown = '''
# Executive Summary
## Key Findings
Line one<br>Line two<BR/>Line three.

> Strategic alignment requires strict schema adherence.

- First bullet item
- Second bullet item

Inline `code_token` and block:
```dart
final x = 42;
```

| Metric | Score |
| :--- | :--- |
| Cohesion | 95% |
''';

        final theme = AppTheme.light;
        await tester.pumpWidget(
          buildTestHarness(markdownContent: markdown, theme: theme),
        );
        await tester.pumpAndSettle();

        final mdBody = tester.widget<MarkdownBody>(find.byType(MarkdownBody));
        expect(mdBody.selectable, isTrue);
        expect(mdBody.data, contains('Line one Line two Line three.'));
        expect(mdBody.data, isNot(contains('<br>')));
        expect(mdBody.data, isNot(contains('<BR/>')));

        final sheet = mdBody.styleSheet!;
        expect(sheet.h1?.fontWeight, equals(FontWeight.bold));
        expect(sheet.h2?.fontWeight, equals(FontWeight.bold));
        expect(sheet.p?.height, equals(1.5));
        expect(
          sheet.code?.backgroundColor,
          equals(theme.colorScheme.surfaceContainerHighest),
        );
        expect(sheet.code?.fontFamily, equals('monospace'));
        expect(sheet.blockquote?.fontStyle, equals(FontStyle.italic));
        expect(
          sheet.blockquote?.color,
          equals(theme.colorScheme.onSurfaceVariant),
        );
        expect(
          sheet.blockquotePadding,
          equals(
            const EdgeInsets.symmetric(
              horizontal: AppSpacing.s16,
              vertical: AppSpacing.s8,
            ),
          ),
        );
        expect(sheet.listIndent, equals(AppSpacing.s24));
        expect(sheet.tableHead?.fontWeight, equals(FontWeight.bold));
      },
    );

    testWidgets(
      'Boundary 1: single-character markdown content renders cleanly without error',
      (WidgetTester tester) async {
        await tester.pumpWidget(buildTestHarness(markdownContent: 'A'));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byType(MarkdownBody), findsOneWidget);
        expect(find.byType(ErrorView), findsNothing);
      },
    );

    testWidgets(
      'Boundary 2: narrow 240px viewport in dark mode with long unbroken token and <br /> variants renders without overflow',
      (WidgetTester tester) async {
        final longToken = 'X' * 300;
        final content = 'Header<br />$longToken';

        await tester.pumpWidget(
          buildTestHarness(
            markdownContent: content,
            theme: AppTheme.dark,
            width: 240,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        final mdBody = tester.widget<MarkdownBody>(find.byType(MarkdownBody));
        expect(mdBody.data, equals('Header $longToken'));
        expect(
          mdBody.styleSheet?.code?.backgroundColor,
          equals(AppTheme.dark.colorScheme.surfaceContainerHighest),
        );
      },
    );

    testWidgets(
      'Negative 1: empty or whitespace-only markdownContent logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(markdownContent: '   \t\n  ', logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(MarkdownBody), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[OutputRenderer] VALIDATION_FAILED: Failed to render markdown output',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: markdownContent containing only HTML <br> tags collapses to empty after sanitization and triggers Fail-Fast ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            markdownContent: '<br><BR/><br />   <br>',
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(MarkdownBody), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              '[OutputRenderer] VALIDATION_FAILED: Failed to render markdown output',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
