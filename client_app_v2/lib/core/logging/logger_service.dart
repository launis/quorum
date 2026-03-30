import 'dart:io';
import 'dart:convert';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:intl/intl.dart';
import 'package:logger/logger.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:dio/dio.dart';
import 'package:client_app/core/environment/env.dart';

part 'logger_service.g.dart';

/// Global Logger Provider (Singleton)
@riverpod
LoggerService loggerService(Ref ref) {
  return LoggerService();
}

class LoggerService {
  late Logger _logger;
  late final Dio _telemetryDio;

  LoggerService() {
    // Initialize with buffer and console output
    const useJson = bool.fromEnvironment(
      'USE_JSON_LOGGING',
      defaultValue: false,
    );

    _logger = Logger(
      printer: useJson ? JsonPrinter() : CustomPrinter(),
      output: DevNullOutput(),
      filter: ProductionFilter(),
    );

    // Setup isolated Dio for telemetry to avoid circular dependencies
    _telemetryDio = Dio(
      BaseOptions(
        baseUrl: Env.apiUrl,
        connectTimeout: const Duration(seconds: 5),
        sendTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 5),
      ),
    );
  }

  Future<void> init() async {
    if (kIsWeb) return;

    try {
      // Use CWD (root) -> Parent for shared visibility
      // Verify absolute path
      var file = File('../client_debug.log');
      // If we are in Debug mode, sometimes we are deep in build folders?
      // But typically flutter run keeps CWD.

      // debugPrint("LoggerService: Attempting to write to ${file.absolute.path}");

      // Re-initialize
      const useJson = bool.fromEnvironment(
        'USE_JSON_LOGGING',
        defaultValue: false,
      );

      _logger = Logger(
        filter: ProductionFilter(),
        printer: useJson ? JsonPrinter() : CustomPrinter(),
        output: FileOutput(file), // ONLY file output, no console
      );

      info('SYSTEM', 'Logging initialized. Writing to: ${file.absolute.path}');
    } catch (e) {
      debugPrint("Failed to initialize file logging: $e");
    }
  }

  void debug(String context, String message) =>
      _logger.d('[$context] | client | $message');
  void info(String context, String message) =>
      _logger.i('[$context] | client | $message');
  void warning(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) => _logger.w(
    '[$context] | client | $message',
    error: error,
    stackTrace: stack,
  );
  void error(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    _logger.e(
      '[$context] | client | $message',
      error: error,
      stackTrace: stack,
    );

    // Dual-Reporting Telemetry Sync
    _sendTelemetry(context, message, error, stack);
  }

  Future<void> _sendTelemetry(
    String context,
    String message,
    Object? error,
    StackTrace? stack,
  ) async {
    // Prevent spamming in debug mode unless strictly needed, but RFC wants it on
    // In dev, maybe skip to avoid noise if API is down, but we wrap in try-catch.
    try {
      final payload = {
        'platform': kIsWeb ? 'web' : Platform.operatingSystem,
        'app_version': '1.0.0', // Could be fetched via package_info_plus later
        'session_id': 'flutter_client',
        'error_message':
            '[$context] $message ${error != null ? "- $error" : ""}',
        'stack_trace': stack?.toString(),
        'severity': 'error',
      };
      // Added leading slash since Env.apiUrl doesn't guarantee a trailing slash.
      await _telemetryDio.post(
        '/api/v2/system/telemetry/client-error',
        data: payload,
      );
    } catch (e) {
      // Silently fail telemetry to prevent infinite error loops
      debugPrint('Telemetry sync failed: $e');
    }
  }
}

// --- Custom Components ---

class CustomPrinter extends LogPrinter {
  final DateFormat _formatter = DateFormat('yyyy-MM-dd HH:mm:ss');

  @override
  List<String> log(LogEvent event) {
    final time = _formatter.format(event.time);
    final levelStr = event.level.name.toUpperCase();

    // Message already contains [CONTEXT] from helper
    final message = event.message;

    // Check if error/stacktrace
    if (event.error != null) {
      // Intentionally left blank as result list handles it
    }

    final output = '$time | $levelStr | $message';

    final result = <String>[output];
    if (event.error != null) result.add("ERROR: ${event.error}");
    if (event.stackTrace != null) result.add(event.stackTrace.toString());

    return result;
  }
}

class JsonPrinter extends LogPrinter {
  @override
  List<String> log(LogEvent event) {
    final timestamp = DateTime.now().toIso8601String();
    final level = event.level.name.toUpperCase();
    var message = event.message.toString();
    String context = "UNKNOWN";

    // Try to parse context from standard format "[$context] | client | $msg"
    // Format defined in LoggerService methods: '[$context] | client | $message'
    if (message.startsWith("[")) {
      final endIndex = message.indexOf("]");
      if (endIndex != -1) {
        context = message.substring(1, endIndex);
        // Strip the prefix "[$context] | client | "
        final prefixEnd = message.indexOf("| client | ");
        if (prefixEnd != -1) {
          message = message.substring(prefixEnd + 11);
        }
      }
    }

    final logRecord = <String, dynamic>{
      "timestamp": timestamp,
      "level": level,
      "logger": "client",
      "context_id": context,
      "execution_id": context, // Map context to execution_id for parity
      "message": message,
    };

    if (event.error != null) {
      logRecord["error"] = event.error.toString();
    }
    if (event.stackTrace != null) {
      logRecord["stack_trace"] = event.stackTrace.toString();
    }

    final jsonStr = jsonEncode(logRecord);
    return [jsonStr];
  }
}

class FileOutput extends LogOutput {
  final File file;

  FileOutput(this.file);

  @override
  void output(OutputEvent event) {
    if (event.lines.isEmpty) return;

    try {
      for (var line in event.lines) {
        file.writeAsStringSync('$line\n', mode: FileMode.append);
      }
    } catch (e) {
      Zone.root.print('FileOutput failed: $e');
    }
  }
}

class DevNullOutput extends LogOutput {
  @override
  void output(OutputEvent event) {}
}
