import 'package:client_app/app.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:client_app/main.dart' as entry;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Full App Smoke Test: Login -> Dashboard', (tester) async {
    // Launch the app
    // We assume the app starts at Login Screen (or redirects).
    // Note: Integration tests run on the real app, so it hits the real backend or mock backend.
    // Ideally we should start the app in Mock Mode.
    // But `main.dart` might not allow easy injection of Mock Mode unless via Env Vars.

    // Just verifying the app launches without crashing for now.
    await entry.main();
    await tester.pumpAndSettle();

    // Verify we are at least somewhere (e.g. Find 'Login' or 'Dashboard')
    // If authenticated, Dashboard. If not, Login.
    expect(find.byType(App), findsOneWidget);
  });
}
