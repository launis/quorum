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
        // We know it didn't throw a fatal rendering exception during build.
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

        // Retry button should be visible
        final retryButton = find.byType(TextButton);
        expect(retryButton, findsOneWidget);

        await tester.tap(retryButton);
        await tester.pumpAndSettle();

        expect(retryClicked, isTrue);
      },
    );
  });
}
