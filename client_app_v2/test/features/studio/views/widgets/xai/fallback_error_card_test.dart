import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/views/widgets/xai/fallback_error_card.dart';

void main() {
  testWidgets('FallbackErrorCard renders title and message', (
    WidgetTester tester,
  ) async {
    const title = 'Error Title';
    const message = 'Error message details.';

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: FallbackErrorCard(title: title, message: message),
        ),
      ),
    );

    expect(find.text(title), findsOneWidget);
    expect(find.text(message), findsOneWidget);
    expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
  });
}
