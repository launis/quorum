import 'package:client_app/app.dart';
import 'package:client_app/firebase_options.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

Future<void> main() async {
  try {
    WidgetsFlutterBinding.ensureInitialized();

    // 1. Load Environment Variables
    try {
      await dotenv.load(fileName: '.env');
      debugPrint('Env loaded');
    } catch (e) {
      debugPrint('Error loading .env: $e');
      // Continue without env if essential, or rethrow?
      // Proceeding might be dangerous if API_URL needed.
    }

    // 2. Initialize Firebase
    try {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );

    } catch (e) {
      debugPrint('Error initializing Firebase: $e');
    }

    // 3. Launch App
    runApp(
      // 4. ProviderScope for Riverpod
      const ProviderScope(child: App()),
    );
  } catch (e, stack) {
    debugPrint('Fatal Error in main: $e\n$stack');
  }
}
