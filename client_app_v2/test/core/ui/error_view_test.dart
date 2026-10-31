import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('Error Boundary Tests', () {
    testWidgets(
      'ErrorView renders gracefully for JSON Schema violations (Fail-Fast)',
      (WidgetTester tester) async {
        final validationException = AppException.validation(
          'Fail-Fast: ReportDataDto validation failed',
        );

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Scaffold(body: ErrorView(error: validationException)),
          ),
        );

        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byIcon(Icons.error_outline), findsOneWidget);
        expect(find.byType(ExpansionTile), findsOneWidget);

        await tester.tap(find.byType(ExpansionTile));
        await tester.pumpAndSettle();

        expect(find.byType(SelectableText), findsOneWidget);
      },
    );

    testWidgets(
      'ErrorView renders Graceful Network Degradation state with Retry',
      (WidgetTester tester) async {
        final networkException = Exception(
          'SocketException: Failed to connect',
        );

        bool retryClicked = false;

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Scaffold(
              body: ErrorView(
                error: networkException,
                onRetry: () {
                  retryClicked = true;
                },
              ),
            ),
          ),
        );

        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);

        final retryButton = find.byType(TextButton);
        expect(retryButton, findsOneWidget);

        await tester.tap(retryButton);
        await tester.pumpAndSettle();

        expect(retryClicked, isTrue);
      },
    );

    testWidgets(
      'Negative: raw FormatException and wrapped DioException do not leak raw exception strings and unwrap technical details',
      (WidgetTester tester) async {
        const secretPayload = 'INTERNAL_STACK_SECRET_999';
        const rawFormatException = FormatException(secretPayload);

        await tester.pumpWidget(
          const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: Locale('en'),
            home: Scaffold(body: ErrorView(error: rawFormatException)),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.textContaining(secretPayload), findsNothing);
        expect(find.byType(ExpansionTile), findsNothing);

        final wrappedDioException = DioException(
          requestOptions: RequestOptions(path: '/api/v2/workflows'),
          error: AppException.server('Backend node failure', statusCode: 503),
        );

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Scaffold(body: ErrorView(error: wrappedDioException)),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ExpansionTile), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary: compact mode omits outer header and omits action button when actionLabel is null',
      (WidgetTester tester) async {
        bool actionClicked = false;

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Scaffold(
              body: ErrorView(
                error: AppException.unauthorized(),
                compact: true,
                title: 'Custom Header Should Be Omitted In Compact Mode',
                onAction: () {
                  actionClicked = true;
                },
                actionLabel: null,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(
          find.text('Custom Header Should Be Omitted In Compact Mode'),
          findsNothing,
        );
        expect(find.byType(FilledButton), findsNothing);

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Scaffold(
              body: ErrorView(
                error: AppException.unauthorized(),
                compact: true,
                onAction: () {
                  actionClicked = true;
                },
                actionLabel: 'Re-authenticate',
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        final actionButton = find.byType(FilledButton);
        expect(actionButton, findsOneWidget);
        await tester.tap(actionButton);
        await tester.pumpAndSettle();
        expect(actionClicked, isTrue);
      },
    );
  });
}
