import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/src/app.dart';

void main() {
  testWidgets('ClientApp renders correctly', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ProviderScope(child: ClientApp()));
    await tester.pumpAndSettle();

    // Verify that our app initialized text is present.
    expect(
      find.text('Client App Initialized'),
      findsOneWidget,
    ); // Fail intended: text is 'Client App Initialized'
    // Actually, app.dart says 'Client App Initialized' (with spaces)
  });
}
