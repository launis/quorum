import 'package:client_app/features/studio/views/widgets/xai/fallback_error_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

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

  testWidgets(
    'FallbackErrorCard contains extreme title length without horizontal overflow in narrow viewport',
    (WidgetTester tester) async {
      final longTitle = 'A' * 500;
      final longMessage = 'B' * 200;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: SizedBox(
                width: 120.0,
                child: FallbackErrorCard(
                  title: longTitle,
                  message: longMessage,
                ),
              ),
            ),
          ),
        ),
      );

      expect(tester.takeException(), isNull);
      final titleText = tester.widget<Text>(find.text(longTitle));
      expect(titleText.maxLines, 2);
      expect(titleText.overflow, TextOverflow.ellipsis);
    },
  );

  testWidgets(
    'FallbackErrorCard handles boundary empty strings without throwing layout exceptions',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: FallbackErrorCard(title: '', message: ''),
          ),
        ),
      );

      expect(tester.takeException(), isNull);
      expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
      expect(find.text(''), findsNWidgets(2));
    },
  );
}
