import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

// Stub widget that fails during build to simulate rendering or synchronous state death
class FaultyWidget extends StatelessWidget {
  const FaultyWidget({super.key});

  @override
  Widget build(BuildContext context) {
    // We simulate a Riverpod/Controller parsing boundary fail by throwing during render.
    throw CheckedFromJsonException(
      const {'malicious_dart_key': 'injection'},
      'malicious_dart_key',
      'TestClass',
      'Unrecognized keys: [malicious_dart_key]',
    );
  }
}

void main() {
  testWidgets('AppExceptionBoundary catches render crashes and draws Diagnostic Node', (WidgetTester tester) async {
    // We must temporarily intercept FlutterError to prevent test runner from failing instantly
    final originalOnError = FlutterError.onError;
    FlutterError.onError = (FlutterErrorDetails details) {
      // Allow AppExceptionBoundary to process it through ErrorWidget.builder 
    };

    try {
      await tester.pumpWidget(
        const MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: Locale('en'),
          home: Scaffold(
            body: AppExceptionBoundary(
              child: FaultyWidget(),
            ),
          ),
        ),
      );

      // The first pump triggers the failing build. 
      // The ErrorWidget.builder inside AppExceptionBoundary handles it and schedules a setState for the next frame.
      // We must pumpAndSettle to draw the fallback UI.
      await tester.pumpAndSettle();

      // Ensure that the original faulty child is removed
      expect(find.byType(FaultyWidget), findsNothing);
      
      // Verify the Diagnostic Node render details are present
      expect(find.byIcon(Icons.report_problem), findsOneWidget);
      expect(find.byIcon(Icons.refresh), findsOneWidget);

      // We expect the JSON exception key to be displayed verbatim inside the Diagnostic Node
      expect(find.textContaining('malicious_dart_key'), findsOneWidget);
    } finally {
      // Restore global error handler
      FlutterError.onError = originalOnError;
    }
  });
}
