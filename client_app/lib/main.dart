import 'dart:async';
import 'dart:ui';
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
import 'package:client_app/core/logging/app_logger_observer.dart';

Future<void> main() async {
  // 1. Initialize Bindings First
  WidgetsFlutterBinding.ensureInitialized();

  // 2. Load Environment Variables
  try {
    await dotenv.load(fileName: '.env');
  } catch (e) {
    debugPrint('Error loading .env: $e');
  }

  // 3. Initialize Firebase
  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
  } catch (e) {
    debugPrint('Error initializing Firebase: $e');
  }

  // 4. Initialize Logger & Startup Audit
  final logger = LoggerService(); 
  await logger.init(); 
  
  // CONSOLE: Minimal
  if (!kIsWeb) {
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

  // 5. Global Error Handling Setup
  
  // A. Flutter Framework Errors (Widget Build)
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details); // Dump to console too
    logger.error('FLUTTER', 'Framework Error', details.exception, details.stack);
  };

  // B. Async/Platform Errors (Futures, Zones)
  PlatformDispatcher.instance.onError = (error, stack) {
    logger.error('PLATFORM', 'Async Error', error, stack);
    return true; // prevent default handling (crashing app)
  };

  // 6. Launch App
  runApp(
    ProviderScope(
      observers: [
        AppLoggerObserver(logger), // Add Riverpod Observer
      ],
      overrides: [
        loggerServiceProvider.overrideWithValue(logger),
      ],
      child: const App(),
    ),
  );
}
