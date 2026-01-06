import 'package:flutter/material.dart';

/// **Splash Screen**
///
/// Displayed during the initial authentication and profile hydration phase.
///
/// **Usage**:
/// - Shown by [GoRouter] redirect logic when the user is logged in
///   but their role (Admin/Member) is not yet fetched from the backend.
class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: CircularProgressIndicator.adaptive()),
    );
  }
}
