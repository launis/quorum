import 'dart:async';
import 'dart:io';

import 'package:client_app/app.dart';
import 'package:client_app/core/environment/env.dart';
import 'package:client_app/core/logging/app_logger_observer.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/firebase_options.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Builds the global fallback diagnostic error widget when a framework build fails.
Widget buildGlobalErrorWidget(FlutterErrorDetails details) {
  bool isDebug = false;
  assert(() {
    isDebug = true;
    return true;
  }());

  return Builder(
    builder: (BuildContext context) {
      final theme = Theme.of(context);
      final colorScheme = theme.colorScheme;
      final l10n = AppLocalizations.of(context);

      return Material(
        color: colorScheme.errorContainer,
        child: Center(
          child: SingleChildScrollView(
            padding: AppSpacing.p16,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.warning_amber_rounded,
                  color: colorScheme.error,
                  size: AppSpacing.s24 * 2,
                ),
                AppSpacing.h16,
                if (l10n != null) ...[
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Flexible(
                        child: Text(
                          l10n.errorUnknown,
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: colorScheme.onErrorContainer,
                            fontWeight: FontWeight.bold,
                          ),
                          overflow: TextOverflow.ellipsis,
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ],
                  ),
                  AppSpacing.h8,
                ],
                if (isDebug)
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Flexible(
                        child: Text(
                          details.exceptionAsString(),
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: colorScheme.onErrorContainer,
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 6,
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        ),
      );
    },
  );
}

/// Configures global Flutter framework, error widget, and platform dispatcher error hooks.
void configureGlobalErrorHandling(LoggerService logger) {
  // A. Flutter Framework Errors (Widget Build)
  FlutterError.onError = (FlutterErrorDetails details) {
    logger.error(
      'FLUTTER',
      'Framework Error',
      details.exception,
      details.stack,
    );
    // Ensure the Red Screen / Error boundary is rendered
    FlutterError.presentError(details);
  };

  // Diagnostic Node: Replace Red Screen of Death with Local Error Box (No Graceful Degradation)
  ErrorWidget.builder = buildGlobalErrorWidget;

  // B. Async/Platform Errors (Futures, Zones)
  PlatformDispatcher.instance.onError = (error, stack) {
    logger.error('PLATFORM', 'Async Error', error, stack);
    return true; // prevent default handling (crashing app)
  };
}

/// Redirects global [debugPrint] messages to the structured [LoggerService] while filtering bootstrap noise.
DebugPrintCallback createFilteredDebugPrint(LoggerService logger) {
  return (String? message, {int? wrapWidth}) {
    if (message != null &&
        !message.contains('Error loading .env') &&
        !message.contains('Error initializing Firebase')) {
      logger.debug('FLUTTER_DEBUG', message);
    }
  };
}

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
  debugPrint = createFilteredDebugPrint(logger);

  // LOG: Detailed
  logger.info('SYSTEM', 'Startup Audit:');
  logger.info('SYSTEM', ' - API URL: ${Env.apiUrl}');
  logger.info(
    'SYSTEM',
    ' - Platform: ${kIsWeb ? "Web" : Platform.operatingSystem}',
  );
  logger.info('SYSTEM', ' - Build Mode: ${kReleaseMode ? "Release" : "Debug"}');

  // 5. Global Error Handling Setup
  configureGlobalErrorHandling(logger);

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
