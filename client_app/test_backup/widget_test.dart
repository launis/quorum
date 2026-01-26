import 'package:client_app/app.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('ClientApp renders correctly', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ProviderScope(child: App()));
    // await tester.pumpAndSettle(); // This might timeout if there are infinite animations or network calls

    // Verify that the app builds (smoke test)
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
