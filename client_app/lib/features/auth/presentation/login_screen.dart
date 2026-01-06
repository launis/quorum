import 'package:firebase_ui_auth/firebase_ui_auth.dart';
import 'package:flutter/material.dart';

/// **Login Screen**
///
/// Uses `firebase_ui_auth` to provide a production-grade Sign-In UI.
///
/// **Features**:
/// - Email/Password Authentication (configured in providers).
/// - Automatic handling of auth state (user is redirected by Router upon success).
/// - Responsive design (courtesy of Firebase UI).
/// - Localization support.
class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SignInScreen(
      providers: [EmailAuthProvider()],
      actions: [
        AuthStateChangeAction<SignedIn>((context, state) {
          // Router listens to auth state changes and will redirect automatically.
          // We don't need manual navigation here, but this callback is available
          // if we needed to clear specific local state.
        }),
      ],
      // Optional: Add a header with the App Logo
      headerBuilder: (context, constraints, shrinkOffset) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Center(
            child: Text(
              'Cognitive Quorum',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: Theme.of(context).colorScheme.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        );
      },
    );
  }
}
