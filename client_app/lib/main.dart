import 'package:client_app/app.dart';
import 'package:client_app/firebase_options.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'dart:io';
import 'package:client_app/core/environment/env.dart';
import 'package:flutter/foundation.dart';

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

    // 3. Initialize Logger & Startup Audit
    final logger = LoggerService(); // Singleton-ish usage here for startup
    await logger.init(); // Wait for file handle
    
    // CONSOLE: Minimal
    if (!kIsWeb) {
      // Use print directly to ensure it hits stdout, though Logger does too
      print("===================================================");
      print("  CQ CLIENT STARTED");
      print("  -> Log: client_debug.log (CHECK FOR DETAILS)");
      print("===================================================");
    }

    // LOG: Detailed
    logger.info('SYSTEM', 'Startup Audit:');
    logger.info('SYSTEM', ' - API URL: ${Env.apiUrl}');
    logger.info('SYSTEM', ' - Platform: ${kIsWeb ? "Web" : Platform.operatingSystem}');
    logger.info('SYSTEM', ' - Build Mode: ${kReleaseMode ? "Release" : "Debug"}');

    // 4. Launch App
    runApp(
      // 5. ProviderScope for Riverpod (Observer disabled to fix build)
      ProviderScope(
        overrides: [
          loggerServiceProvider.overrideWithValue(logger),
        ],
        child: const App(),
      ),
    );
  } catch (e, stack) {
    debugPrint('Fatal Error in main: $e\n$stack');
  }
}
