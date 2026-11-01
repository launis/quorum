import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/global_error_view.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('GlobalErrorView Widget Hardening Tests', () {
    testWidgets(
      'Positive 1: renders structured AppException with localized title, hint, raw detail box, and triggers action button',
      (WidgetTester tester) async {
        bool actionTriggered = false;
        const appError = AppException(
          type: 'https://api.quorum.fi/errors/server-error',
          title: 'Server Error',
          status: 500,
          detail: 'Database connection pool exhausted on node-01.',
          extensions: <String, Object?>{'error_code': 'SERVER_ERROR'},
        );

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.light,
            locale: const Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: GlobalErrorView(
                error: appError,
                onAction: () {
                  actionTriggered = true;
                },
                actionLabel: 'Retry Now',
                actionIcon: Icons.replay,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
        expect(find.textContaining('SERVER_ERROR'), findsOneWidget);
        expect(
          find.text('Database connection pool exhausted on node-01.'),
          findsOneWidget,
        );
        expect(find.byType(SelectableText), findsOneWidget);

        final buttonFinder = find.widgetWithText(FilledButton, 'Retry Now');
        expect(buttonFinder, findsOneWidget);
        expect(find.byIcon(Icons.replay), findsOneWidget);

        await tester.tap(buttonFinder);
        await tester.pumpAndSettle();
        expect(actionTriggered, isTrue);
      },
    );

    testWidgets(
      'Positive 2: renders specialized localized title for TOOL_EXECUTION_FAILED and defaults action icon to Icons.refresh',
      (WidgetTester tester) async {
        const toolError = AppException(
          type: 'https://api.quorum.fi/errors/tool-execution-failed',
          title: 'Tool Error',
          status: 502,
          detail: 'MCP gateway timeout after 30s.',
          extensions: <String, Object?>{'error_code': 'TOOL_EXECUTION_FAILED'},
        );

        late AppLocalizations l10n;
        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Builder(
              builder: (BuildContext context) {
                l10n = AppLocalizations.of(context)!;
                return Scaffold(
                  body: GlobalErrorView(
                    error: toolError,
                    onAction: () {},
                    actionLabel: l10n.retry,
                  ),
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text(l10n.toolExecutionFailed), findsOneWidget);
        expect(find.text('MCP gateway timeout after 30s.'), findsOneWidget);
        expect(find.byIcon(Icons.refresh), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 1: omits rawDetail container when detail is empty or identical to hintText, and omits action button when actionLabel is null',
      (WidgetTester tester) async {
        const emptyDetailError = AppException(
          type: 'https://api.quorum.fi/errors/network-fatal',
          title: 'Network Error',
          status: 0,
          detail: '',
          extensions: <String, Object?>{'error_code': 'NETWORK_FATAL'},
        );

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.light,
            locale: const Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: GlobalErrorView(
                error: emptyDetailError,
                onAction: () {},
                actionLabel: null,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(SelectableText), findsNothing);
        expect(find.byType(FilledButton), findsNothing);
      },
    );

    testWidgets(
      'Negative/Boundary 2: handles non-AppException String error and arbitrary Object error under narrow 160px width without layout overflow',
      (WidgetTester tester) async {
        final longErrorCode = 'ERR_${'X' * 500}';
        final boundaryError = AppException(
          type: 'https://api.quorum.fi/errors/custom',
          title: 'Custom Error',
          status: 500,
          detail: 'D' * 1000,
          extensions: <String, Object?>{'error_code': longErrorCode},
        );

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.light,
            locale: const Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: SingleChildScrollView(
                child: SizedBox(
                  width: 160,
                  child: Column(
                    children: [
                      GlobalErrorView(error: boundaryError),
                      const GlobalErrorView(error: 'Direct raw string error'),
                      GlobalErrorView(error: StateError('Unexpected state')),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text('Direct raw string error'), findsOneWidget);
        expect(find.byType(GlobalErrorView), findsNWidgets(3));
      },
    );
  });
}
