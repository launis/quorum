import 'dart:async';
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
    debugPrint('CRITICAL: Failed to load .env: $e');
    rethrow;
  }

  // 3. Initialize Firebase
  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
  } catch (e) {
    debugPrint('CRITICAL: Failed to load Firebase: $e');
    rethrow;
  }

  // 4. Initialize Logger & Startup Audit
  final logger = LoggerService();
  await logger.init();

  // Redirect all debugPrints so the console remains clean
  debugPrint = (String? message, {int? wrapWidth}) {
    if (message != null &&
        !message.contains('Error loading .env') &&
        !message.contains('Error initializing Firebase')) {
      logger.debug('FLUTTER_DEBUG', message);
    }
  };

  // LOG: Detailed
  logger.info('SYSTEM', 'Startup Audit:');
  logger.info('SYSTEM', ' - API URL: ${Env.apiUrl}');
  logger.info(
    'SYSTEM',
    ' - Platform: ${kIsWeb ? "Web" : Platform.operatingSystem}',
  );
  logger.info('SYSTEM', ' - Build Mode: ${kReleaseMode ? "Release" : "Debug"}');

  // 5. Global Error Handling Setup

  // A. Flutter Framework Errors (Widget Build)
  FlutterError.onError = (FlutterErrorDetails details) {
    logger.error(
      'FLUTTER',
      'Framework Error',
      details.exception,
      details.stack,
    );
  };

  // Prevent Red Screen of Death (Graceful UI Degradation)
  ErrorWidget.builder = (FlutterErrorDetails details) {
    bool isDebug = false;
    assert(() {
      isDebug = true;
      return true;
    }());

    if (!isDebug) {
      return const SizedBox.shrink();
    }

    return Material(
      color: Colors.red.shade50,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.warning_amber_rounded,
                color: Colors.red.shade900,
                size: 48,
              ),
              const SizedBox(height: 16),
              if (isDebug)
                Text(
                  details.exceptionAsString(),
                  style: TextStyle(color: Colors.red.shade700, fontSize: 14),
                  textAlign: TextAlign.center,
                ),
            ],
          ),
        ),
      ),
    );
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
      overrides: [loggerServiceProvider.overrideWithValue(logger)],
      child: const App(),
    ),
  );
}
