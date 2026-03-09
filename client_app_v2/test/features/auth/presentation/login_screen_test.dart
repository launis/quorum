import 'package:client_app/features/auth/presentation/login_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('LoginScreen shows mock login buttons in debug mode', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );

    // Verify UI Elements exist
    expect(find.text('Cognitive Quorum'), findsOneWidget);
    expect(find.text('Sign in to continue'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(2));
    
    // Verify Mock Login Buttons exist with correct labels matching IDs
    expect(find.text('Mock Login (Root Master)'), findsOneWidget);
    expect(find.text('Mock Login (Admin)'), findsOneWidget);
    expect(find.text('Mock Login (Manager)'), findsOneWidget);
    
    // Test that the ROOT button is tappable
    final rootButton = find.text('Mock Login (Root Master)');
    await tester.ensureVisible(rootButton);
    expect(rootButton, findsOneWidget);
  });
}
