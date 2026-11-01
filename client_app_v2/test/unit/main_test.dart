import 'dart:io';

import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/main.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class RecordingLoggerService implements LoggerService {
  final List<({String context, String message})> debugLogs = [];
  final List<({String context, String message})> infoLogs = [];
  final List<
    ({String context, String message, Object? error, StackTrace? stack})
  >
  warningLogs = [];
  final List<
    ({String context, String message, Object? error, StackTrace? stack})
  >
  errorLogs = [];

  @override
  Future<void> init({File? logFile}) async {}

  @override
  void debug(String context, String message) {
    debugLogs.add((context: context, message: message));
  }

  @override
  void info(String context, String message) {
    infoLogs.add((context: context, message: message));
  }

  @override
  void warning(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    warningLogs.add((
      context: context,
      message: message,
      error: error,
      stack: stack,
    ));
  }

  @override
  void error(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    errorLogs.add((
      context: context,
      message: message,
      error: error,
      stack: stack,
    ));
  }
}

void main() {
  group('main.dart Global Error Boundary & Logging Hardening Tests', () {
    testWidgets(
      'Positive: buildGlobalErrorWidget renders Theme-sovereign tokens and localized title',
      (WidgetTester tester) async {
        final details = FlutterErrorDetails(
          exception: StateError('Fail-Fast render crash'),
          library: 'widgets library',
        );

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.light,
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Scaffold(body: buildGlobalErrorWidget(details)),
          ),
        );

        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
        expect(find.text('Unknown error'), findsOneWidget);
        expect(find.textContaining('Fail-Fast render crash'), findsOneWidget);

        final icon = tester.widget<Icon>(
          find.byIcon(Icons.warning_amber_rounded),
        );
        expect(icon.color, equals(AppTheme.light.colorScheme.error));
      },
    );

    testWidgets(
      'Negative/Boundary 1: buildGlobalErrorWidget handles extreme narrow width (50px) and 2000-char exception without overflow',
      (WidgetTester tester) async {
        final longException = 'X' * 2000;
        final details = FlutterErrorDetails(
          exception: FormatException(longException),
        );

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.dark,
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('fi'),
            home: Center(
              child: SizedBox(
                width: 50,
                height: 200,
                child: buildGlobalErrorWidget(details),
              ),
            ),
          ),
        );

        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
        expect(find.textContaining('FormatException'), findsOneWidget);
      },
    );

    test(
      'Negative/Boundary 2: createFilteredDebugPrint filters null and bootstrap error noise while forwarding valid messages',
      () {
        final fakeLogger = RecordingLoggerService();
        final callback = createFilteredDebugPrint(fakeLogger);

        // Boundary: null message
        callback(null);
        // Boundary: bootstrap noise strings
        callback('Error loading .env: FileSystemException');
        callback('Error initializing Firebase: PlatformException');

        expect(fakeLogger.debugLogs, isEmpty);

        // Valid debug message
        callback('Valid diagnostic trace');
        expect(fakeLogger.debugLogs, hasLength(1));
        expect(fakeLogger.debugLogs.first.context, equals('FLUTTER_DEBUG'));
        expect(
          fakeLogger.debugLogs.first.message,
          equals('Valid diagnostic trace'),
        );
      },
    );

    test(
      'Negative/Boundary 3: configureGlobalErrorHandling routes FlutterError and PlatformDispatcher errors to LoggerService',
      () {
        final fakeLogger = RecordingLoggerService();
        final originalOnError = FlutterError.onError;
        final originalErrorBuilder = ErrorWidget.builder;
        final originalPlatformOnError = PlatformDispatcher.instance.onError;

        try {
          configureGlobalErrorHandling(fakeLogger);

          expect(ErrorWidget.builder, equals(buildGlobalErrorWidget));

          final stack = StackTrace.current;
          final handled = PlatformDispatcher.instance.onError!(
            ArgumentError('Invalid async state'),
            stack,
          );

          expect(handled, isTrue);
          expect(fakeLogger.errorLogs, hasLength(1));
          expect(fakeLogger.errorLogs.first.context, equals('PLATFORM'));
          expect(fakeLogger.errorLogs.first.message, equals('Async Error'));
          expect(fakeLogger.errorLogs.first.error, isA<ArgumentError>());
        } finally {
          FlutterError.onError = originalOnError;
          ErrorWidget.builder = originalErrorBuilder;
          PlatformDispatcher.instance.onError = originalPlatformOnError;
        }
      },
    );
  });
}
