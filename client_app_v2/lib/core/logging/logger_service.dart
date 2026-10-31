import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:client_app/core/environment/env.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:intl/intl.dart';
import 'package:logger/logger.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'logger_service.g.dart';

/// Global Logger Provider (Singleton).
@Riverpod(keepAlive: true)
LoggerService loggerService(Ref ref) {
  return LoggerService();
}

class LoggerService {
  late Logger _logger;
  late final Dio _telemetryDio;

  LoggerService({Dio? telemetryDio, Logger? logger}) {
    const useJson = bool.fromEnvironment(
      'USE_JSON_LOGGING',
      defaultValue: false,
    );

    _logger =
        logger ??
        Logger(
          printer: useJson ? JsonPrinter() : CustomPrinter(),
          output: DevNullOutput(),
          filter: ProductionFilter(),
        );

    _telemetryDio =
        telemetryDio ??
        Dio(
          BaseOptions(
            connectTimeout: const Duration(seconds: 5),
            sendTimeout: const Duration(seconds: 5),
            receiveTimeout: const Duration(seconds: 5),
          ),
        );
  }

  Future<void> init({File? logFile}) async {
    if (kIsWeb) return;

    try {
      final file = logFile ?? File('../client_debug.log');

      const useJson = bool.fromEnvironment(
        'USE_JSON_LOGGING',
        defaultValue: false,
      );

      _logger = Logger(
        filter: ProductionFilter(),
        printer: useJson ? JsonPrinter() : CustomPrinter(),
        output: FileOutput(file),
      );

      info('SYSTEM', 'Logging initialized. Writing to: ${file.absolute.path}');
    } catch (e) {
      debugPrint('Failed to initialize file logging: $e');
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

    _sendTelemetry(context, message, error, stack);
  }

  Future<void> _sendTelemetry(
    String context,
    String message,
    Object? error,
    StackTrace? stack,
  ) async {
    try {
      final payload = <String, Object?>{
        'platform': kIsWeb ? 'web' : Platform.operatingSystem,
        'app_version': '1.0.0',
        'session_id': 'flutter_client',
        'error_message':
            '[$context] $message ${error != null ? "- $error" : ""}',
        'stack_trace': stack?.toString(),
        'severity': 'error',
      };
      final baseUrl = _telemetryDio.options.baseUrl.isNotEmpty
          ? _telemetryDio.options.baseUrl
          : Env.apiUrl;
      await _telemetryDio.post<Object?>(
        '$baseUrl/api/v2/system/telemetry/client-error',
        data: payload,
      );
    } catch (e) {
      debugPrint('Telemetry sync failed: $e');
    }
  }
}

class CustomPrinter extends LogPrinter {
  final DateFormat _formatter = DateFormat('yyyy-MM-dd HH:mm:ss');

  @override
  List<String> log(LogEvent event) {
    final time = _formatter.format(event.time);
    final levelStr = event.level.name.toUpperCase();
    final message = event.message;
    final output = '$time | $levelStr | $message';

    final result = <String>[output];
    if (event.error != null) result.add('ERROR: ${event.error}');
    if (event.stackTrace != null) result.add(event.stackTrace.toString());

    return result;
  }
}

class JsonPrinter extends LogPrinter {
  static final RegExp _contextPattern = RegExp(
    r'^\[([^\]]+)\]\s*\|\s*client\s*\|\s*(.*)$',
    dotAll: true,
  );

  @override
  List<String> log(LogEvent event) {
    final timestamp = DateTime.now().toIso8601String();
    final level = event.level.name.toUpperCase();
    var message = event.message.toString();
    var context = 'UNKNOWN';

    final match = _contextPattern.firstMatch(message);
    if (match != null) {
      context = match.group(1) ?? 'UNKNOWN';
      message = match.group(2) ?? message;
    }

    final logRecord = <String, Object?>{
      'timestamp': timestamp,
      'level': level,
      'logger': 'client',
      'context_id': context,
      'execution_id': context,
      'message': message,
    };

    if (event.error != null) {
      logRecord['error'] = event.error.toString();
    }
    if (event.stackTrace != null) {
      logRecord['stack_trace'] = event.stackTrace.toString();
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
      for (final line in event.lines) {
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
